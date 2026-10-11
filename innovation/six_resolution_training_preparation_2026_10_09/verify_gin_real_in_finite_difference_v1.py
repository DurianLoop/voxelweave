"""Pure float64 local objective finite differences at the real worst convolution coordinate."""
import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import sys,time,json,gzip,gc,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
from diagnose_gin_real_in_vjp_v1 import torch,np,read,entry,bind,resource_guard,state_hash,array_sha,CheckpointedTaskUNet3D,development_cases,lattice,source_image,physical_mr,physical_label,read_reference_label,sample_batch,batch_rng,decode,gin,TracedCPU,independent_total_loss,TARGET,INDEX
HS=[1e-3,1e-4,1e-5]

def main():
    started=time.perf_counter();torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
    out=HERE/'gin_real_in_finite_difference_attempt01';out.mkdir(exist_ok=False)
    r=dict(complete=False,errors=[],MRI_arrays_loaded=0,GT_arrays_loaded=0,CPU_whole_forwards=0,CPU_whole_backwards=0,
        GPU_whole_forwards=0,optimizer_updates=0,CUDA_initialized=False,finite_difference_h=HS,per_view=[],
        full19_qualification_passed=False,medical_effect_scored=False,publication_claim_confirmed=False,goal_status='active')
    def save():
        blob=json.dumps(r,ensure_ascii=False,indent=2)+'\n';assert len(blob.encode())<60_000
        (out/'receipt.json').write_text(blob,encoding='utf-8')
    def guard():
        v=resource_guard();remaining=22_800_000
        for d,cap in ((HERE,7_000_000),(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09',20_000_000),(ROOT/'gin_accepted_primary_followup_2026_10_09',6_000_000)):
            size=sum(p.stat().st_size for p in d.rglob('*') if p.is_file());assert size<cap;remaining+=cap-size
        assert v['workspace_free_bytes']-remaining>=8_000_000_000 and time.perf_counter()-started<180 and not torch.cuda.is_initialized()
        return v
    save()
    try:
        r['resources_before']=guard();prior=read(HERE/'gin_real_in_vjp_attempt01/receipt.json');assert prior['complete'] and not prior['errors']
        expected=next(v for v in prior['local_matrix'] if v['input_source']==v['cotangent_source']==v['backend']=='cpu')
        source=HERE/'gin19_real_graph_attempt02';cfg=read(source/'frozen_config.json')
        with gzip.open(source/'steps.jsonl.gz','rt',encoding='utf-8') as f:rows=[json.loads(v) for v in f]
        prepared=next(v for v in rows if v['type']=='prepared_three_views' and v['step_index']==0)
        oldcpu=next(v for v in prior['global_branches'] if v['device']=='cpu')
        r['source_bindings']=[entry(p) for p in (Path(__file__),HERE/'GIN_REAL_IN_FINITE_DIFFERENCE_PROTOCOL_V1.md',HERE/'diagnose_gin_real_in_vjp_v1.py',
            HERE/'gin_real_in_vjp_attempt01/receipt.json',source/'steps.jsonl.gz',source/'frozen_config.json',HERE/'gin_cpu_differentiable_reference_v1.py')]
        case,row=development_cases()[0];assert case['uid']==prepared['uid'];grid=lattice(case)
        target=physical_label(read_reference_label(case),grid);r['GT_arrays_loaded']=1
        image,_=source_image(case,row,'native_reference');cache=physical_mr(image,grid);r['MRI_arrays_loaded']=1;del image
        x,y,geo=sample_batch(cache,target,batch_rng(19998+cfg['cases'][0]['scheduled_steps'][0]))
        assert geo==prepared['original_geometry'] and array_sha(y.numpy())==prepared['mother_target_sha256'];views=[]
        for v in prepared['parameters']:
            p=dict(alpha=decode(v['alpha']),layers=[dict(k=l['k'],weight=decode(l['weight']),bias=decode(l['bias'])) for l in v['layers']]);views.append(gin(x,p)[0])
        assert [array_sha(v.numpy()) for v in views]==prepared['view_sha256'];del x,cache,target
        torch.manual_seed(20261009);base=CheckpointedTaskUNet3D();initial={n:v.detach().clone() for n,v in base.state_dict().items()};del base
        assert state_hash(initial)==prior['cold_initial_state_sha256'];records={}
        def observe(vi,kind,incoming,output):
            q=records.setdefault(vi,{})
            if kind in q:return
            q[kind]=True
            if kind=='conv':q.update(x=incoming.detach().clone(),z=output.detach().clone())
            else:
                def h(g):assert 'dn' not in q;q['dn']=g.detach().clone();return g
                output.register_hook(h)
        model=TracedCPU(initial,observe);outputs=[]
        for vi,v in enumerate(views):model.view=vi;outputs.append(model(v));r['CPU_whole_forwards']+=1;guard()
        value=independent_total_loss(outputs,y);value.backward();r['CPU_whole_backwards']=1
        assert float(dict(model.named_parameters())[TARGET+'.weight'].grad.reshape(-1)[INDEX])==oldcpu['prior_gradient']
        for vi,q in records.items():
            old=next(a for a in oldcpu['captures'] if a['view']==vi)
            assert array_sha(q['x'].numpy())==old['input_sha256'] and array_sha(q['z'].numpy())==old['output_sha256'] and array_sha(q['dn'].numpy())==old['IN_output_cotangent_sha256']
        del model,outputs,value,views;gc.collect();guard()
        co,ci,*kernel=prior['coordinate'];assert co==3 and ci==13;totals={h:0. for h in HS}
        for vi,q in sorted(records.items()):
            z=q['z'].numpy()[:,co].astype(np.float64);dn=q['dn'].numpy()[:,co].astype(np.float64)
            direction=np.zeros_like(z);outs=[];ins=[]
            for size,k in zip(z.shape[1:],kernel):
                low=max(0,1-k);high=min(size,size+1-k);outs.append(slice(low,high));ins.append(slice(low+k-1,high+k-1))
            direction[(slice(None),*outs)]=q['x'].numpy()[(slice(None),ci,*ins)]
            analytic=next(a['independent_float64_coordinate'] for a in expected['per_view'] if a['view']==vi)
            def objective(h):
                a=z+h*direction;centered=a-a.mean(axis=(1,2,3),keepdims=True)
                normalized=centered/np.sqrt((centered*centered).mean(axis=(1,2,3),keepdims=True)+1e-5)
                return float(np.einsum('ndhw,ndhw->',dn,normalized,dtype=np.float64,optimize=False))
            checks=[]
            for h in HS:
                plus=objective(h);minus=objective(-h);fd=(plus-minus)/(2*h);totals[h]+=fd
                checks.append(dict(h=h,objective_plus=plus,objective_minus=minus,finite_difference=fd,analytic_error=abs(fd-analytic)))
            r['per_view'].append(dict(view=vi,independent_analytic=analytic,checks=checks));save();guard()
        analytic_total=expected['independent_float64_coordinate_sum'];r['sum_comparisons']=[dict(h=h,finite_difference=totals[h],analytic=analytic_total,error=abs(totals[h]-analytic_total)) for h in HS]
        r['all_three_h_negative_and_error_le1e8']=all(v['finite_difference']<0 and v['error']<=1e-8 for v in r['sum_comparisons'])
        assert r['all_three_h_negative_and_error_le1e8'],r['sum_comparisons']
        for b in r['source_bindings']:bind(b)
        r.update(complete=True,resources_after=guard(),source_patient=case['patient'],source_uid=case['uid'])
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-started;save();print(json.dumps({k:r.get(k) for k in ('complete','errors','sum_comparisons','optimizer_updates','elapsed_seconds')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
