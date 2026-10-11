"""One real case: isolate InstanceNorm input/upstream/backend after the worst convolution."""
import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
os.environ['CUDA_VISIBLE_DEVICES']='0'
import sys,time,json,gzip,gc,traceback,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09'))
from qualify_full_fov_gpu_cpu import torch,np,read,entry,bind,resource_guard,state_hash,array_sha,CheckpointedTaskUNet3D,original_cuda_initializer
from mc_rc_3d_19series_common_init_2026_10_07 import development_cases,lattice,source_image,physical_mr,physical_label,read_reference_label,sample_batch,batch_rng
from mc_rc_3d_baseline_2026_10_07 import loss
from diagnose_gin_real_loss_attribution_v1 import decode
from gin_reference_adapter_v1 import gin,mean_target_kl
from gin_cpu_differentiable_reference_v1 import FunctionalCPUReference,independent_total_loss
from torch.nn import functional as F
from torch.utils.checkpoint import checkpoint
TARGET='decoders.2.layers.3';INDEX=1658

class TracedCPU(FunctionalCPUReference):
    def __init__(self,state,observe):super().__init__(state);self.observe=observe;self.view=-1
    def __call__(self,value):
        self.whole_model_calls+=1;stored=[];heads=[]
        def block(tensor,prefix):
            self.block_calls+=1
            for first in (0,3):
                name=f'{prefix}.layers.{first}';incoming=tensor
                tensor=F.conv3d(tensor,self.state[name+'.weight'],padding=1)
                if name==TARGET:self.observe(self.view,"conv",incoming,tensor)
                tensor=F.instance_norm(tensor,None,None,self.state[f'{prefix}.layers.{first+1}.weight'],self.state[f'{prefix}.layers.{first+1}.bias'],True,.1,1e-5)
                if name==TARGET:self.observe(self.view,"norm",None,tensor)
                tensor=F.leaky_relu(tensor,.01,inplace=False)
            return tensor
        def run(tensor,prefix):return checkpoint(lambda x:block(x,prefix),tensor,use_reentrant=False,preserve_rng_state=True)
        for depth in range(4):
            if depth:value=F.max_pool3d(value,2,2)
            value=run(value,f'encoders.{depth}');stored.append(value)
        for depth,skip in enumerate(stored[2::-1]):
            value=F.conv_transpose3d(value,self.state[f'ups.{depth}.weight'],self.state[f'ups.{depth}.bias'],stride=2)
            assert value.shape[2:]==skip.shape[2:]
            value=run(torch.cat([value,skip],1),f'decoders.{depth}')
            heads.append(F.conv3d(value,self.state[f'heads.{depth}.weight'],self.state[f'heads.{depth}.bias']))
        return tuple(heads[::-1])

def coordinate_vjp64(x,dy,coordinate):
    co,ci,*kernel=coordinate;out_sl=[];in_sl=[]
    for size,k in zip(x.shape[2:],kernel):
        low=max(0,1-k);high=min(size,size+1-k)
        out_sl.append(slice(low,high));in_sl.append(slice(low+k-1,high+k-1))
    a=x.numpy()[(slice(None),ci,*in_sl)];b=dy.numpy()[(slice(None),co,*out_sl)]
    return float(np.einsum('ndhw,ndhw->',a,b,dtype=np.float64,casting='safe',optimize=False))

def main():
    started=time.perf_counter();torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
    out=HERE/'gin_real_in_vjp_attempt01';out.mkdir(exist_ok=False)
    r=dict(complete=False,errors=[],MRI_arrays_loaded=0,GT_arrays_loaded=0,parent_arrays_loaded=0,
           CPU_whole_forwards=0,GPU_whole_forwards=0,CPU_whole_backwards=0,GPU_whole_backwards=0,
           CPU_local_VJPs=0,GPU_local_VJPs=0,optimizer_updates=0,
           formal_training_launched=False,full19_qualification_passed=False,medical_effect_scored=False,
           confirmation_patients_opened=False,lockedIXI_opened=False,original_training_modified=False,
           publication_claim_confirmed=False,goal_status='active',local_matrix=[],global_branches=[])
    def save():
        blob=json.dumps(r,ensure_ascii=False,indent=2)+'\n';assert len(blob.encode())<180_000
        p=out/'receipt.json.tmp';p.write_text(blob,encoding='utf-8');p.replace(out/'receipt.json')
    def guard(cuda=False):
        v=resource_guard();caps=((HERE,7_000_000),(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09',20_000_000),(ROOT/'gin_accepted_primary_followup_2026_10_09',6_000_000))
        remaining=22_800_000
        for d,limit in caps:
            size=sum(p.stat().st_size for p in d.rglob('*') if p.is_file());assert size<limit
            remaining+=limit-size
        assert v['workspace_free_bytes']-remaining>=8_000_000_000
        assert time.perf_counter()-started<600 and torch.get_num_threads()==torch.get_num_interop_threads()==1
        v['remaining_all_stage_allowance_bytes']=remaining
        if cuda:
            free,total=torch.cuda.mem_get_info();peak=torch.cuda.max_memory_reserved()
            assert free>=4_000_000_000 and peak<=2_500_000_000
            v.update(GPU_free_bytes=free,GPU_peak_reserved_bytes=peak)
        return v
    save()
    try:
        r['resources_before']=guard();old=HERE/'gin19_real_graph_attempt02';previous=read(old/'receipt.json');cfg=read(old/'frozen_config.json')
        with gzip.open(old/'steps.jsonl.gz','rt',encoding='utf-8') as f:rows=[json.loads(v) for v in f]
        prepared=next(v for v in rows if v['type']=='prepared_three_views' and v['step_index']==0)
        comparison=next(v for v in rows if v['type']=='CPU_GPU_strict_comparison')
        prior_worst=next(v for v in comparison['all54_parameter_comparisons'] if v['name']==TARGET+'.weight')
        assert prior_worst['maximum_parameter_flat_index']==INDEX
        sources=[Path(__file__),HERE/'GIN_REAL_IN_VJP_PROTOCOL_V1.md',HERE/'prepare_gin_real_in_vjp_v1.py',HERE/'diagnose_gin_real_local_vjp_v1.py',HERE/'gin_real_local_vjp_attempt01/receipt.json',old/'receipt.json',old/'frozen_config.json',old/'steps.jsonl.gz',
                 HERE/'gin_cpu_differentiable_reference_v1.py',HERE/'gin_reference_adapter_v1.py',HERE/'diagnose_gin_real_loss_attribution_v1.py',
                 ROOT/'gpu_graph_cost_smoke_2026_10_09/checkpointed_model.py',ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py']
        r['source_bindings']=[entry(p) for p in sources]
        case,row=development_cases()[0];selected=cfg['cases'][0];assert case['uid']==prepared['uid']
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
        assert state_hash(initial)==previous['cold_initial_state_sha256'];r['cold_initial_state_sha256']=state_hash(initial)
        query=subprocess.run(['nvidia-smi','--query-gpu=index,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=20)
        aggregate=[list(map(int,v.split(','))) for v in query.stdout.strip().splitlines()]
        assert len(aggregate)==1 and aggregate[0][0]==0 and aggregate[0][1]>=8192;r['GPU_aggregate_before']=aggregate
        torch.cuda._lazy_init=original_cuda_initializer;os.environ['CUDA_VISIBLE_DEVICES']='0';assert torch.cuda.is_available()
        free,total=torch.cuda.mem_get_info();torch.cuda.set_per_process_memory_fraction(min(.1,2_400_000_000/total))
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
        captured={};global_grad={}
        for device in ('cpu','cuda:0'):
            tick=time.perf_counter();records={};active=[-1]
            def observe(vi,kind,incoming,output):
                q=records.setdefault(vi,{})
                if kind+'_observed' in q:return
                q[kind+'_observed']=True
                if kind=='conv':q.update(x=incoming.detach().cpu().clone(),z=output.detach().cpu().clone())
                else:q['norm_output_sha256']=array_sha(output.detach().cpu().numpy())
                field='dy' if kind=='conv' else 'dn'
                def cotangent(grad):
                    assert field not in q;q[field]=grad.detach().cpu().clone();return grad
                output.register_hook(cotangent);guard(True)
            handles=[]
            if device=='cpu':model=TracedCPU(initial,observe)
            else:
                model=CheckpointedTaskUNet3D();model.load_state_dict(initial);model.to(device);model.train()
                handles.append(model.get_submodule(TARGET).register_forward_hook(lambda mod,args,result:observe(active[0],'conv',args[0],result)))
                handles.append(model.get_submodule('decoders.2.layers.4').register_forward_hook(lambda mod,args,result:observe(active[0],'norm',None,result)))
            assert state_hash(model.state_dict())==r['cold_initial_state_sha256'];torch.cuda.reset_peak_memory_stats()
            with (torch.autograd.graph.save_on_cpu(pin_memory=False) if device!='cpu' else __import__('contextlib').nullcontext()):
                outputs=[]
                for vi,v in enumerate(views):
                    active[0]=vi
                    if device=='cpu':model.view=vi
                    outputs.append(model(v.to(device)));r['CPU_whole_forwards' if device=='cpu' else 'GPU_whole_forwards']+=1;guard(True)
                if device=='cpu':value=independent_total_loss(outputs,y)
                else:
                    final=torch.stack([v[0] for v in outputs]);value=loss(outputs[0],y.to(device))+.1*mean_target_kl(torch.cat((torch.zeros_like(final),final),2))
                value.backward();r['CPU_whole_backwards' if device=='cpu' else 'GPU_whole_backwards']+=1
            torch.cuda.synchronize();assert len(records)==3 and all('dy' in v and 'dn' in v for v in records.values())
            grad=dict(model.named_parameters())[TARGET+'.weight'].grad.detach().cpu().clone();global_grad[device]=grad
            prior=prior_worst['CPU_gradient_at_index' if device=='cpu' else 'GPU_gradient_at_index'];observed=float(grad.reshape(-1)[INDEX])
            q=dict(device=device,loss=float(value.detach()),worst_coordinate_gradient=observed,prior_gradient=prior,
                   prior_gradient_bitwise_reproduced=observed==prior,elapsed_seconds=time.perf_counter()-tick,
                   captures=[dict(view=i,shape=list(rec['x'].shape),input_sha256=array_sha(rec['x'].numpy()),output_sha256=array_sha(rec['z'].numpy()),cotangent_sha256=array_sha(rec['dy'].numpy()),IN_output_cotangent_sha256=array_sha(rec['dn'].numpy()),norm_output_sha256=rec['norm_output_sha256']) for i,rec in sorted(records.items())],resources=guard(True))
            r['global_branches'].append(q);assert q['prior_gradient_bitwise_reproduced'];captured[device]=records;save()
            for h in handles:h.remove()
            del model,outputs,value;gc.collect();torch.cuda.empty_cache();guard(True)
        r['captured_CPU_GPU_differences']=[dict(view=i,
            IN_input_max_error=float((captured['cpu'][i]['z']-captured['cuda:0'][i]['z']).abs().max()),
            IN_output_cotangent_max_error=float((captured['cpu'][i]['dn']-captured['cuda:0'][i]['dn']).abs().max()),
            IN_input_cotangent_max_error=float((captured['cpu'][i]['dy']-captured['cuda:0'][i]['dy']).abs().max())) for i in range(3)]
        weight=initial[TARGET+'.weight'];coordinate=list(np.unravel_index(INDEX,tuple(weight.shape)));r['coordinate']=list(map(int,coordinate))
        gamma=initial['decoders.2.layers.4.weight'];beta=initial['decoders.2.layers.4.bias']
        assert bool((gamma==1).all()) and bool((beta==0).all());r['initial_IN_gamma_one_beta_zero']=True
        r['same_input_upstream_backend_comparisons']=[];r['original_IN_dx_reconstruction']=[]
        for input_device in ('cpu','cuda:0'):
            for cotangent_device in ('cpu','cuda:0'):
                tick=time.perf_counter();backend_rows={d:dict(input_source=input_device,cotangent_source=cotangent_device,backend=d,per_view=[]) for d in ('cpu','cuda:0')}
                for vi in (2,1,0):
                    guard(True);q=captured[input_device][vi];z=q['z'];dn=captured[cotangent_device][vi]['dn']
                    a=z.numpy().astype(np.float64);b=dn.numpy().astype(np.float64);axes=(2,3,4)
                    centered=a-a.mean(axis=axes,keepdims=True);invstd=1/np.sqrt((centered*centered).mean(axis=axes,keepdims=True)+1e-5)
                    xhat=centered*invstd
                    dx64=gamma.numpy()[None,:,None,None,None]*invstd*(b-b.mean(axis=axes,keepdims=True)-xhat*(b*xhat).mean(axis=axes,keepdims=True))
                    independent_coordinate=coordinate_vjp64(q['x'],torch.from_numpy(dx64),coordinate)
                    del a,b,centered,invstd,xhat;local={}
                    for backend in ('cpu','cuda:0'):
                        zz=z.to(backend).detach().requires_grad_(True);dd=dn.to(backend)
                        yn=F.instance_norm(zz,None,None,gamma.to(backend),beta.to(backend),True,.1,1e-5)
                        dx,=torch.autograd.grad(yn,zz,dd);dx=dx.detach().cpu();local[backend]=dx
                        r['CPU_local_VJPs' if backend=='cpu' else 'GPU_local_VJPs']+=1
                        coordinate_value=coordinate_vjp64(q['x'],dx,coordinate)
                        backend_rows[backend]['per_view'].append(dict(view=vi,coordinate_gradient=coordinate_value,
                            independent_float64_coordinate=independent_coordinate,
                            dx_max_error_from_float64=float(np.max(np.abs(dx.numpy()-dx64)))))
                        if input_device==cotangent_device==backend:
                            difference=float((dx-captured[backend][vi]['dy']).abs().max());equal=torch.equal(dx,captured[backend][vi]['dy'])
                            r['original_IN_dx_reconstruction'].append(dict(device=backend,view=vi,max_error=difference,bitwise_equal=equal))
                            assert equal,('IN dx not reproduced',backend,vi,difference)
                        del zz,dd,yn;gc.collect();torch.cuda.empty_cache();guard(True)
                    r['same_input_upstream_backend_comparisons'].append(dict(input_source=input_device,cotangent_source=cotangent_device,view=vi,
                        dx_max_backend_error=float((local['cpu']-local['cuda:0']).abs().max()),
                        coordinate_gradient_backend_error=abs(backend_rows['cpu']['per_view'][-1]['coordinate_gradient']-backend_rows['cuda:0']['per_view'][-1]['coordinate_gradient'])))
                    del dx64,local,dx;gc.collect();guard(True)
                for backend,q in backend_rows.items():
                    q.update(coordinate_gradient_sum=sum(v['coordinate_gradient'] for v in q['per_view']),
                        independent_float64_coordinate_sum=sum(v['independent_float64_coordinate'] for v in q['per_view']),
                        elapsed_seconds=time.perf_counter()-tick,resources=guard(True))
                    r['local_matrix'].append(q);save();print(json.dumps({k:q[k] for k in ('input_source','cotangent_source','backend','coordinate_gradient_sum','independent_float64_coordinate_sum')}),flush=True)
        assert r['CPU_local_VJPs']==r['GPU_local_VJPs']==12 and r['CPU_whole_forwards']==r['GPU_whole_forwards']==3
        assert r['CPU_whole_backwards']==r['GPU_whole_backwards']==1
        for b in r['source_bindings']:bind(b)
        r.update(complete=True,source_patient=case['patient'],source_uid=case['uid'],resources_after=guard(True))
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-started;save();print(json.dumps({k:r[k] for k in ('complete','errors','CPU_whole_forwards','GPU_whole_forwards','CPU_local_VJPs','GPU_local_VJPs','optimizer_updates','elapsed_seconds')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
