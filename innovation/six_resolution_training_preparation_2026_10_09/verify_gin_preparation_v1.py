"""Independent synthetic GIN oracle and actual current-environment KL gradient semantics."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
os.environ['CUDA_VISIBLE_DEVICES']='-1'
import sys,time,json,traceback,warnings,gc
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard
import torch,numpy as np
from gin_reference_adapter_v1 import draw_parameters,gin,complementary_mix,mean_target_kl
torch.set_num_threads(1);torch.set_num_interop_threads(1)

def oracle(x,p):
    value=x.astype(np.float32,copy=True)
    for index,layer in enumerate(p['layers']):
        w=layer['weight'].numpy().astype(np.float64);bias=layer['bias'].numpy().astype(np.float64)
        k=layer['k'];batch,outputs,inputs=w.shape[:3];padded=np.pad(value,((0,0),(0,0),*( (k//2,k//2) for _ in range(3)))).astype(np.float64)
        shape=value.shape[2:];result=np.zeros((batch,outputs,*shape),np.float64)
        for n in range(batch):
            for o in range(outputs):
                for c in range(inputs):
                    for z in range(k):
                        for r in range(k):
                            for s in range(k):
                                result[n,o]+=padded[n,c,z:z+shape[0],r:r+shape[1],s:s+shape[2]]*w[n,o,c,z,r,s]
        result=(result+bias).astype(np.float32)
        if index<3:result=np.where(result>=0,result,result*np.float32(.01))
        value=result
    alpha=p['alpha'].numpy();mixed=alpha*value+(np.float32(1)-alpha)*x
    ni=np.sqrt(np.sum(x.astype(np.float64)**2,axis=(1,2,3,4),keepdims=True))
    nm=np.sqrt(np.sum(mixed.astype(np.float64)**2,axis=(1,2,3,4),keepdims=True))
    return (mixed.astype(np.float64)*(1/(nm+1e-5))*ni).astype(np.float32)

def main():
    started=time.perf_counter();out=HERE/'gin_operator_preparation_attempt01';out.mkdir(exist_ok=False)
    r=dict(complete=False,errors=[],records=[],MRI_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
      training_updates=0,author_source_executed=False,CUDA_initialized=False,medical_effect_scored=False,
      full_method_reproduced=False,threeD_IPA_field_qualified=False,confirmation_patients_opened=False,
      lockedIXI_opened=False,original_training_modified=False,publication_claim_confirmed=False,goal_status='active')
    def guard():
        v=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
        assert size<7_000_000 and v['workspace_free_bytes']-42_800_000-(7_000_000-size)>=8_000_000_000
        assert time.perf_counter()-started<180 and not torch.cuda.is_initialized()
        assert torch.get_num_threads()==torch.get_num_interop_threads()==1
        return v
    try:
        r['resources_before']=guard()
        authors=read(HERE/'gin_selected_author_code_attempt01/receipt.json');assert authors['complete']
        sources=[Path(__file__),HERE/'GIN_STRONG_CONTROL_PREPARATION.md',HERE/'gin_reference_adapter_v1.py',HERE/'gin_selected_author_code_attempt01/receipt.json']
        sources+=[bind(v['saved']) for v in authors['records']]
        r['source_bindings']=[entry(p) for p in sources]
        for data_kind in ['signed','zero','constant']:
            shape=(2,1,8,10,12)
            base=torch.randn(shape,generator=torch.Generator().manual_seed(901)) if data_kind=='signed' else torch.full(shape,0. if data_kind=='zero' else .37)
            original=base.clone()
            for seed in range(8):
                guard();p=draw_parameters(shape,seed);y,meta=gin(base,p);repeat,_=gin(base,p);ind=oracle(base.numpy(),p)
                error=float(np.max(np.abs(ind-y.numpy())));assert error<=3e-6,(data_kind,seed,error)
                assert torch.equal(y,repeat) and torch.equal(base,original) and y.shape==base.shape and torch.isfinite(y).all()
                ni=meta['input_norm'].flatten().double();nm=meta['mixed_norm'].flatten().double();norm=torch.linalg.vector_norm(y.reshape(2,-1).double(),dim=1)
                expected=ni*nm/(nm+1e-5);relative=float(((norm-expected).abs()/ni.clamp_min(1)).max());assert relative<=3e-6
                if data_kind=='zero':assert torch.count_nonzero(y)==0
                r['records'].append(dict(data_kind=data_kind,seed=seed,kernels=[v['k'] for v in p['layers']],
                  NumPy_output_max_absolute_error=error,epsilon_scaling_relative_error=relative,
                  replay_bitwise_equal=True,input_bitwise_unchanged=True,shape_finite_gate_passed=True))
                del y,repeat,ind,p;gc.collect()
        a=torch.randn(shape,generator=torch.Generator().manual_seed(400));b=torch.randn(shape,generator=torch.Generator().manual_seed(401))
        w=torch.linspace(0,1,shape[-1]).reshape(1,1,1,1,-1).expand(shape).contiguous();u,v=complementary_mix(a,b,w)
        mix_error=float((u+v-a-b).abs().max());assert mix_error<=3e-6
        assert torch.equal(u[...,0],b[...,0]) and torch.equal(u[...,-1],a[...,-1])
        logits=torch.randn((3,2,2,3,4),generator=torch.Generator().manual_seed(880),dtype=torch.float64,requires_grad=True)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always');attached=mean_target_kl(logits);gradient=torch.autograd.grad(attached,logits)[0]
        detached=mean_target_kl(logits,True);dgradient=torch.autograd.grad(detached,logits)[0]
        z=logits.detach().numpy();exp=np.exp(z-np.max(z,axis=2,keepdims=True));prob=exp/exp.sum(axis=2,keepdims=True);mean=prob.mean(axis=0,keepdims=True)
        reverse=float(np.mean(mean*(np.log(mean)-np.log(prob))));forward=float(np.mean(prob*(np.log(prob)-np.log(mean))))
        assert abs(float(attached.detach())-reverse)<=3e-12 and float(attached.detach())==float(detached.detach())
        delta=float((gradient-dgradient).abs().max());assert delta>1e-6 and abs(reverse-forward)>1e-6
        ix=(0,0,0,1,2);h=1e-6;plus=z.copy();minus=z.copy();plus[ix]+=h;minus[ix]-=h
        def numeric(value):
            exp=np.exp(value-np.max(value,axis=2,keepdims=True));p=exp/exp.sum(axis=2,keepdims=True);m=p.mean(axis=0,keepdims=True)
            return np.mean(m*(np.log(m)-np.log(p)))
        finite=float((numeric(plus)-numeric(minus))/(2*h));grad_error=abs(finite-float(gradient[ix]));assert grad_error<=3e-9
        for source in r['source_bindings']:bind(source)
        r.update(complete=True,complementary_mix_max_error=mix_error,synthetic_cases_completed=len(r['records']),torch_version=torch.__version__,
          consistency=dict(reverse_mean_target_KL=float(attached.detach()),independent_NumPy_reverse_KL=reverse,
            conventional_forward_JS_element_mean=forward,attached_detached_loss_equal=True,
            attached_detached_gradient_max_difference=delta,target_gradient_supported_in_current_environment=True,
            attached_gradient_NumPy_finite_difference_error=grad_error,default_KL_mean_warnings=[str(c.message) for c in caught]),
          resources_after=guard())
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-started;dump(out/'receipt.json',r)
    print(json.dumps({k:r.get(k) for k in ['complete','errors','synthetic_cases_completed','consistency','elapsed_seconds']},ensure_ascii=False),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
