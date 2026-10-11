"""Two-step CPU production/reference graph validation before any medical run."""
import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import sys,time,json,gc,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09'))
from qualify_full_fov_gpu_cpu import torch,CheckpointedTaskUNet3D,entry,bind,resource_guard,state_hash,array_sha
from mc_rc_3d_baseline_2026_10_07 import loss
from gin_reference_adapter_v1 import draw_parameters,gin,mean_target_kl
from gin_cpu_differentiable_reference_v1 import FunctionalCPUReference,nearest_binary_target,independent_total_loss

def main():
    started=time.perf_counter();torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
    out=HERE/'gin_cpu_reference_verification_attempt01';out.mkdir(exist_ok=False)
    r=dict(complete=False,errors=[],steps=[],CPU_optimizer_updates=0,MRI_arrays_loaded=0,GT_arrays_loaded=0,
           parent_arrays_loaded=0,CUDA_initialized=False,medical_effect_scored=False,
           complete19series_GPU_three_view_qualified=False,publication_claim_confirmed=False,goal_status='active')
    def save():(out/'receipt.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def guard():
        v=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
        fov=ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09';fs=sum(p.stat().st_size for p in fov.rglob('*') if p.is_file())
        assert size<7_000_000 and fs<20_000_000
        assert v['workspace_free_bytes']-22_800_000-(7_000_000-size)-(20_000_000-fs)>=8_000_000_000
        assert not torch.cuda.is_initialized() and time.perf_counter()-started<180
        assert torch.get_num_threads()==torch.get_num_interop_threads()==1;return v
    save()
    try:
        r['resources_before']=guard();r['source_bindings']=[entry(p) for p in (Path(__file__),HERE/'GIN_CPU_REFERENCE_VERIFICATION_PROTOCOL_V1.md',
             HERE/'gin_cpu_differentiable_reference_v1.py',HERE/'gin_reference_adapter_v1.py',
             ROOT/'gpu_graph_cost_smoke_2026_10_09/checkpointed_model.py',ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py')]
        torch.manual_seed(20261009);production=CheckpointedTaskUNet3D();initial=production.state_dict()
        reference=FunctionalCPUReference(initial);r['initial_state_sha256']=state_hash(initial)
        assert state_hash(reference.state_dict())==r['initial_state_sha256']
        shape=(2,1,16,16,16);x=torch.randn(shape,generator=torch.Generator().manual_seed(49))
        views=[gin(x,draw_parameters(shape,480000+i))[0] for i in range(3)]
        target=(torch.randn(shape,generator=torch.Generator().manual_seed(501))>.8).float()
        hashes=[array_sha(v.numpy()) for v in views];th=array_sha(target.numpy())
        opts=[torch.optim.AdamW(m.parameters(),lr=1e-4,weight_decay=1e-4,betas=(.9,.999),eps=1e-8,foreach=False,fused=False) for m in (production,reference)]
        for step in range(2):
            states=[];costs=[]
            for index,(model,opt) in enumerate(zip((production,reference),opts)):
                guard();tick=time.perf_counter();opt.zero_grad(set_to_none=True)
                outputs=[model(v) for v in views]
                for view in outputs:
                    for z in view:
                        expected=torch.nn.functional.interpolate(target,size=z.shape[2:],mode='nearest-exact')
                        assert torch.equal(expected,nearest_binary_target(target,z.shape[2:]))
                value=(loss(outputs[0],target)+.1*mean_target_kl(torch.cat((torch.zeros_like(torch.stack([v[0] for v in outputs])),
                       torch.stack([v[0] for v in outputs])),2))) if index==0 else independent_total_loss(outputs,target)
                value.backward();guard()
                gradients={n:p.grad.detach().clone() for n,p in model.named_parameters()}
                assert all(torch.isfinite(v).all() for v in gradients.values())
                probabilities=[torch.stack([v[d].detach().sigmoid() for v in outputs]) for d in range(3)]
                opt.step();r['CPU_optimizer_updates']+=1
                params={n:p.detach().clone() for n,p in model.named_parameters()}
                moments={n:{k:v.detach().clone() for k,v in opt.state[p].items()} for n,p in model.named_parameters()}
                states.append(dict(loss=float(value.detach()),gradients=gradients,probabilities=probabilities,params=params,moments=moments))
                costs.append(time.perf_counter()-tick);del outputs,value,gradients,probabilities,params,moments;gc.collect();guard()
            a,b=states;assert a['params'].keys()==b['params'].keys();records=[]
            for n in a['params']:
                fields=[]
                for k,v in a['moments'][n].items():
                    if k=='step':assert torch.equal(v,b['moments'][n][k])
                    fields.append(dict(field=k,max_error=float((v-b['moments'][n][k]).abs().max())))
                records.append(dict(name=n,gradient_error=float((a['gradients'][n]-b['gradients'][n]).abs().max()),
                                    parameter_error=float((a['params'][n]-b['params'][n]).abs().max()),optimizer_fields=fields))
            maxima=dict(loss=abs(a['loss']-b['loss']),probability=max(float((v-w).abs().max()) for v,w in zip(a['probabilities'],b['probabilities'])),
                        gradient=max(v['gradient_error'] for v in records),parameter=max(v['parameter_error'] for v in records),
                        optimizer_state=max(f['max_error'] for v in records for f in v['optimizer_fields']))
            r['steps'].append(dict(step=step,max_errors=maxima,all54_parameters=records,optimizer_fields_compared=sum(len(v['optimizer_fields']) for v in records),
                                  production_reference_step_seconds=costs,target_nearest_exact_equal=True))
            save();print(json.dumps(dict(step=step,max_errors=maxima)),flush=True);assert all(v<=3e-6 for v in maxima.values())
            assert [array_sha(v.numpy()) for v in views]==hashes and array_sha(target.numpy())==th
            del states,a,b;gc.collect();guard()
        for v in r['source_bindings']:bind(v)
        r.update(complete=True,all_two_steps54_parameters162_optimizer_fields_strict_passed=True,
                 functional_CPU_whole_model_calls=reference.whole_model_calls,functional_CPU_block_calls=reference.block_calls,
                 resources_after=guard())
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-started;save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','CPU_optimizer_updates','elapsed_seconds')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
