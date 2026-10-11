"""Bounded synthetic GPU float32/BF16 preflight, separate from actual-data GPU pilot."""
import contextlib,json,os,sys,time,traceback
from datetime import datetime,timezone
from mc_rc_3d_baseline_v2_2026_10_07 import ROOT,TaskUNet3D,loss,torch,np,sha,resource_guard,SEED
from run_mc_rc_3d_gpu_fit_pilot_2026_10_07 import totals_observation,state_hash
OUT=ROOT/'experiments/mc_rc_3d_tiny_gpu_numerical_attempt04_2026_10_07'
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);path=OUT/'attempt01.json';began=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,status='preparing',errors=[],arms=[],
           actual_synthetic_gpu_updates=0,actual_patient_training_updates=0,patients_read=0,MR_values_loaded=0,
           scientific_confirmation_patients=0,publication_claim_confirmed=False,
           original_full_batch_gpu_contract_changed=False,script_sha256=sha(__file__),
           source_bindings=[dict(path=p,sha256=sha(ROOT/p)) for p in [
               'MC_RC_3D_TINY_GPU_NUMERICAL_PROTOCOL_2026-10-07.md','MC_RC_3D_TINY_GPU_NUMERICAL_ATTEMPT02_ADDENDUM_2026-10-07.md',
               'MC_RC_3D_TINY_GPU_NUMERICAL_ATTEMPT03_ADDENDUM_2026-10-07.md',
               'MC_RC_3D_TINY_GPU_NUMERICAL_ATTEMPT04_ADDENDUM_2026-10-07.md',
               'experiments/probe_mc_rc_3d_tiny_gpu_numerical_v3_2026_10_07.py',
               'experiments/mc_rc_3d_tiny_gpu_numerical_attempt03_2026_10_07/attempt01.json',
               'experiments/probe_mc_rc_3d_tiny_gpu_numerical_v2_2026_10_07.py',
               'experiments/mc_rc_3d_tiny_gpu_numerical_attempt02_2026_10_07/attempt01.json',
               'experiments/probe_mc_rc_3d_tiny_gpu_numerical_2026_10_07.py',
               'experiments/mc_rc_3d_tiny_gpu_numerical_2026_10_07/attempt01.json','experiments/mc_rc_3d_baseline_2026_10_07.py',
               'experiments/mc_rc_3d_baseline_v2_2026_10_07.py','experiments/mc_rc_reference_resources_2026_10_07.py',
               'experiments/run_mc_rc_3d_gpu_fit_pilot_2026_10_07.py']])
    def save():path.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    def guard():
        assert time.perf_counter()-began<=120
        host=resource_guard();free,total=torch.cuda.mem_get_info(0);peak=torch.cuda.max_memory_reserved(0)
        totals=totals_observation()
        observation=dict(host=host,gpu_free_bytes=free,gpu_total_bytes=total,own_gpu_peak_reserved_bytes=peak,totals_observation=totals)
        r.setdefault('resource_observations',[]).append(observation);save()
        assert free>=500_000_000 and totals['free_bytes']>=500_000_000 and peak<=160_000_000
        return observation
    save()
    try:
        r['host_before']=resource_guard();r['gpu_totals_before']=totals_observation();save()
        assert not torch.cuda.is_initialized()
        if r['gpu_totals_before']['free_bytes']<1_300_000_000:
            r['status']='resource_deferred';r['cuda_initialized']=False
            r['finished_utc']=datetime.now(timezone.utc).isoformat();save();print(json.dumps(r));return 3
        r['inherited_cuda_visible_devices']=os.environ.get('CUDA_VISIBLE_DEVICES')
        os.environ['CUDA_VISIBLE_DEVICES']='0'
        r['own_cuda_visible_devices']='0'
        assert torch.cuda.is_available()
        torch.cuda.set_per_process_memory_fraction(.01,0)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
        r['resources_after_cuda_init']=guard()
        torch.manual_seed(SEED);cpu=TaskUNet3D().eval();initial={k:v.clone() for k,v in cpu.state_dict().items()}
        rng=np.random.default_rng(SEED);x=torch.from_numpy(rng.normal(size=(2,1,16,16,16)).astype(np.float32))
        y=torch.zeros_like(x);y[0,0,4:11,9:23,10:24]=1
        r['synthetic_shape']=list(x.shape);r['initial_weights_sha256']=state_hash(initial)
        with torch.no_grad():reference=[o.sigmoid().numpy() for o in cpu(x)]
        gx=x.cuda();gy=y.cuda();guard()
        for mode in ('float32','bf16_autocast'):
            if mode=='bf16_autocast':assert torch.cuda.is_bf16_supported()
            model=TaskUNet3D().cuda();model.load_state_dict(initial,strict=True);model.eval();guard()
            autocast=lambda:torch.autocast('cuda',dtype=torch.bfloat16) if mode=='bf16_autocast' else contextlib.nullcontext()
            torch.cuda.synchronize();started=time.perf_counter()
            with torch.no_grad(),autocast():gpu_outputs=model(gx)
            probabilities=[o.float().sigmoid().cpu().numpy() for o in gpu_outputs]
            error=[float(np.max(np.abs(a-b))) for a,b in zip(probabilities,reference)]
            disagreements=[int(np.count_nonzero((a>=.5)!=(b>=.5))) for a,b in zip(probabilities,reference)]
            if mode=='float32':assert max(error)<=3e-4
            r.setdefault('pre_update_numeric_observations',[]).append(dict(mode=mode,forward_probability_max_absolute_error_by_head=error,forward_threshold_disagreements_by_head=disagreements));save()
            del gpu_outputs
            torch.cuda.empty_cache();guard();model.train();optimizer=torch.optim.SGD(model.parameters(),lr=.001)
            optimizer.zero_grad(set_to_none=True)
            with autocast():outputs=model(gx);objective=loss(outputs,gy)
            assert torch.isfinite(objective);objective.backward()
            assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
            branches={name:max(float(p.grad.abs().max()) for p in module.parameters()) for name,module in
                      [('encoder',model.encoders),('decoder',model.decoders),('ups',model.ups),('heads',model.heads)]}
            assert all(v>0 for v in branches.values());optimizer.step();torch.cuda.synchronize()
            r['actual_synthetic_gpu_updates']+=1
            row=dict(mode=mode,complete=True,updates=1,loss=float(objective.detach()),
                     forward_probability_max_absolute_error_by_head=error,
                     forward_threshold_disagreements_by_head=disagreements,
                     branch_max_gradient=branches,elapsed_seconds=time.perf_counter()-started,resources=guard(),
                     final_weights_sha256=state_hash(model.state_dict()),
                     numeric_scope='tiny synthetic shape; not real full batch peak, speed or clinical fit')
            r['arms'].append(row);save();print(json.dumps(row),flush=True)
            del model,optimizer,outputs,objective,probabilities
            torch.cuda.empty_cache();guard()
        r['status']='completed';r['complete']=len(r['arms'])==2 and r['actual_synthetic_gpu_updates']==2
    except Exception as e:r['status']='failed';r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['cuda_initialized']=torch.cuda.is_initialized();r['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    assert path.stat().st_size<=1_000_000
    print(json.dumps({k:r.get(k) for k in ('status','complete','errors','actual_synthetic_gpu_updates','actual_patient_training_updates')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
