"""Same real CPU logits: original vs independent loss; reproduce prior first CPU AdamW."""
import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import sys,time,json,gzip,base64,gc,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09'))
from qualify_full_fov_gpu_cpu import torch,np,read,entry,bind,resource_guard,state_hash,array_sha,CheckpointedTaskUNet3D
from mc_rc_3d_19series_common_init_2026_10_07 import development_cases,lattice,source_image,physical_mr,physical_label,read_reference_label,sample_batch,batch_rng
from mc_rc_3d_baseline_2026_10_07 import loss
sys.path.insert(0,str(ROOT/'development_optimizer_coverage_2026_10_09'))
from qualify_all_development_optimizer import optimizer_hash
from gin_reference_adapter_v1 import gin,mean_target_kl
from gin_cpu_differentiable_reference_v1 import FunctionalCPUReference,independent_total_loss

def decode(v):
    a=np.frombuffer(base64.b64decode(v['payload_base64']),dtype='<f4').reshape(v['shape']).copy()
    assert array_sha(a)==v['sha256'];return torch.from_numpy(a)

def main():
    started=time.perf_counter();torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
    out=HERE/'gin_real_loss_attribution_attempt01';out.mkdir(exist_ok=False)
    r=dict(complete=False,errors=[],MRI_arrays_loaded=0,GT_arrays_loaded=0,CPU_diagnostic_optimizer_updates=0,GPU_optimizer_updates=0,
           parameter_comparisons=[],original_worst_coordinate_checks=[],CUDA_initialized=False,
           full19_qualification_passed=False,medical_effect_scored=False,publication_claim_confirmed=False,goal_status='active')
    def save():(out/'receipt.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def guard():
        v=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
        fov=ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09';fs=sum(p.stat().st_size for p in fov.rglob('*') if p.is_file())
        assert size<7_000_000 and fs<20_000_000
        assert v['workspace_free_bytes']-22_800_000-(7_000_000-size)-(20_000_000-fs)>=8_000_000_000
        assert time.perf_counter()-started<180 and not torch.cuda.is_initialized();return v
    save()
    try:
        r['resources_before']=guard();old=HERE/'gin19_real_graph_attempt02'
        previous=read(old/'receipt.json');cfg=read(old/'frozen_config.json');assert not previous['complete'] and previous['GPU_optimizer_updates']==2
        with gzip.open(old/'steps.jsonl.gz','rt',encoding='utf-8') as f:rows=[json.loads(v) for v in f]
        prepared=next(v for v in rows if v['type']=='prepared_three_views' and v['step_index']==0)
        old_cpu=next(v for v in rows if v['type']=='actual_two_step_optimizer' and v['device']=='cpu' and v['step']==0)
        comparison=next(v for v in rows if v['type']=='CPU_GPU_strict_comparison')
        r['source_bindings']=[entry(p) for p in (Path(__file__),HERE/'GIN_REAL_LOSS_ATTRIBUTION_PROTOCOL_V1.md',old/'receipt.json',old/'frozen_config.json',old/'steps.jsonl.gz',
                  HERE/'gin_cpu_differentiable_reference_v1.py',HERE/'gin_reference_adapter_v1.py',ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py')]
        case,row=development_cases()[0];selected=cfg['cases'][0];assert case['uid']==prepared['uid'] and case['patient']==prepared['patient']
        grid=lattice(case);target=physical_label(read_reference_label(case),grid);r['GT_arrays_loaded']=1
        image,_=source_image(case,row,'native_reference');cache=physical_mr(image,grid);r['MRI_arrays_loaded']=1;del image
        x,y,geometry=sample_batch(cache,target,batch_rng(19998+selected['scheduled_steps'][0]))
        assert geometry==prepared['original_geometry'] and array_sha(y.numpy())==prepared['mother_target_sha256']
        views=[]
        for v in prepared['parameters']:
            p=dict(alpha=decode(v['alpha']),layers=[dict(k=l['k'],weight=decode(l['weight']),bias=decode(l['bias'])) for l in v['layers']])
            views.append(gin(x,p)[0])
        assert [array_sha(v.numpy()) for v in views]==prepared['view_sha256'];del target,cache,x
        torch.manual_seed(20261009);base=CheckpointedTaskUNet3D();initial={n:v.detach().clone() for n,v in base.state_dict().items()};del base
        assert state_hash(initial)==previous['cold_initial_state_sha256'];model=FunctionalCPUReference(initial)
        tick=time.perf_counter();outputs=[]
        for i,v in enumerate(views):outputs.append(model(v));guard();print(json.dumps(dict(CPU_view_forward_completed=i,elapsed_seconds=time.perf_counter()-started)),flush=True)
        r['CPU_graph_forward_seconds']=time.perf_counter()-tick
        final=torch.stack([v[0] for v in outputs]);primary=loss(outputs[0],y)+.1*mean_target_kl(torch.cat((torch.zeros_like(final),final),2))
        independent=independent_total_loss(outputs,y);assert float(independent.detach())==old_cpu['loss']
        r.update(primary_loss=float(primary.detach()),independent_loss=float(independent.detach()),independent_old_loss_bitwise_reproduced=True)
        names=list(model.state);params=list(model.parameters());tick=time.perf_counter()
        primary_grads=torch.autograd.grad(primary,params,retain_graph=True);guard()
        r['primary_loss_gradient_seconds']=time.perf_counter()-tick;tick=time.perf_counter()
        independent_grads=torch.autograd.grad(independent,params);guard();r['independent_loss_gradient_seconds']=time.perf_counter()-tick
        pairs=[]
        for gradients in (primary_grads,independent_grads):
            clone=FunctionalCPUReference(initial);opt=torch.optim.AdamW(clone.parameters(),lr=1e-4,weight_decay=1e-4,betas=(.9,.999),eps=1e-8,foreach=False,fused=False)
            for (_,p),g in zip(clone.named_parameters(),gradients):p.grad=g.detach().clone()
            opt.step();r['CPU_diagnostic_optimizer_updates']+=1
            pairs.append(dict(params={n:p.detach().clone() for n,p in clone.named_parameters()},
                              moments={n:{k:v.detach().clone() for k,v in opt.state[p].items()} for n,p in clone.named_parameters()},
                              state_sha256=state_hash(clone.state_dict()),optimizer_sha256=optimizer_hash(opt,clone)))
            del clone,opt;gc.collect();guard()
        assert pairs[1]['state_sha256']==old_cpu['ending_state_sha256'] and pairs[1]['optimizer_sha256']==old_cpu['optimizer_state_sha256']
        r['independent_original_CPU_step0_model_and_optimizer_hashes_reproduced']=True
        for i,n in enumerate(names):
            a,b=pairs;fields=[]
            for k,v in a['moments'][n].items():
                if k=='step':assert torch.equal(v,b['moments'][n][k])
                fields.append(dict(field=k,max_error=float((v-b['moments'][n][k]).abs().max())))
            r['parameter_comparisons'].append(dict(name=n,gradient_error=float((primary_grads[i]-independent_grads[i]).abs().max()),
                                                  parameter_error=float((a['params'][n]-b['params'][n]).abs().max()),optimizer_fields=fields))
        worst=sorted(comparison['all54_parameter_comparisons'],key=lambda v:v['parameter_error'],reverse=True)[:3]
        for oldrow in worst:
            n=oldrow['name'];index=oldrow['maximum_parameter_flat_index'];i=names.index(n)
            pg=float(primary_grads[i].reshape(-1)[index]);ig=float(independent_grads[i].reshape(-1)[index])
            assert ig==oldrow['CPU_gradient_at_index']
            r['original_worst_coordinate_checks'].append(dict(original=oldrow,CPU_primary_gradient=pg,CPU_independent_gradient=ig,
                   CPU_loss_formula_gradient_difference=abs(pg-ig),CPU_loss_formulas_gradient_sign_equal=(pg>=0)==(ig>=0),
                   GPU_previous_gradient=oldrow['GPU_gradient_at_index'],
                   CPU_primary_parameter=float(pairs[0]['params'][n].reshape(-1)[index]),
                   CPU_independent_parameter=float(pairs[1]['params'][n].reshape(-1)[index])))
        r.update(max_CPU_loss_formula_gradient_difference=max(v['gradient_error'] for v in r['parameter_comparisons']),
                 max_CPU_loss_formula_parameter_difference=max(v['parameter_error'] for v in r['parameter_comparisons']),
                 max_CPU_loss_formula_optimizer_difference=max(f['max_error'] for v in r['parameter_comparisons'] for f in v['optimizer_fields']),
                 source_CPU_case=case['patient'],source_CPU_uid=case['uid'],complete=True,resources_after=guard())
        for b in r['source_bindings']:bind(b)
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-started;save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','CPU_diagnostic_optimizer_updates','max_CPU_loss_formula_gradient_difference',
           'max_CPU_loss_formula_parameter_difference','independent_original_CPU_step0_model_and_optimizer_hashes_reproduced','elapsed_seconds')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
