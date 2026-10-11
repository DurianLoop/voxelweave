"""Independent NumPy equations and predeclared finite-difference convergence of norm v2."""
import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import sys,time,json,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09'))
from qualify_full_fov_gpu_cpu import torch,np,entry,bind,resource_guard
from gin_cpu_differentiable_reference_v2 import stable_instance_norm

def main():
    started=time.perf_counter();torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
    out=HERE/'stable_norm_math_v2_attempt01';out.mkdir(exist_ok=False)
    r=dict(complete=False,errors=[],MRI_arrays_loaded=0,GT_arrays_loaded=0,CUDA_initialized=False,optimizer_updates=0,
        finite_difference=[],medical_effect_scored=False,full19_qualification_passed=False,publication_claim_confirmed=False,goal_status='active')
    def save():(out/'receipt.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def guard():
        v=resource_guard();remaining=22_800_000
        for p,cap in ((HERE,7_000_000),(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09',20_000_000),(ROOT/'gin_accepted_primary_followup_2026_10_09',6_000_000)):
            size=sum(q.stat().st_size for q in p.rglob('*') if q.is_file());assert size<cap;remaining+=cap-size
        assert v['workspace_free_bytes']-remaining>=8_000_000_000 and time.perf_counter()-started<180 and not torch.cuda.is_initialized();return v
    save()
    try:
        r['resources_before']=guard();r['source_bindings']=[entry(p) for p in (Path(__file__),HERE/'gin_cpu_differentiable_reference_v2.py',HERE/'GIN_HIGH_PRECISION_CPU_REFERENCE_PROTOCOL_V2.md')]
        rng=np.random.default_rng(50002);x=rng.standard_normal((2,3,4,5,6));w=rng.standard_normal(3);b=rng.standard_normal(3);dy=rng.standard_normal(x.shape)
        axes=(2,3,4);centered=x-x.mean(axes,keepdims=True);inv=1/np.sqrt((centered*centered).mean(axes,keepdims=True)+1e-5);xh=centered*inv
        expected=xh*w[None,:,None,None,None]+b[None,:,None,None,None]
        dx=w[None,:,None,None,None]*inv*(dy-dy.mean(axes,keepdims=True)-xh*(dy*xh).mean(axes,keepdims=True))
        dw=(dy*xh).sum((0,2,3,4));db=dy.sum((0,2,3,4))
        tensors=[torch.tensor(a,dtype=torch.float64,requires_grad=True) for a in (x,w,b)]
        y=stable_instance_norm(*tensors,output_dtype=torch.float64);grads=torch.autograd.grad(y,tensors,torch.from_numpy(dy))
        errors=dict(output=float(np.max(np.abs(y.detach().numpy()-expected))),dx=float(np.max(np.abs(grads[0].numpy()-dx))),
                    dgamma=float(np.max(np.abs(grads[1].numpy()-dw))),dbeta=float(np.max(np.abs(grads[2].numpy()-db))))
        r['double_equation_errors']=errors;assert max(errors.values())<=3e-6
        # FP32 variant compares to a fresh float64 equation on the actual rounded inputs.
        tx=[torch.tensor(a,dtype=torch.float32,requires_grad=True) for a in (x,w,b)];td=torch.from_numpy(dy.astype(np.float32))
        fy=stable_instance_norm(*tx);fg=torch.autograd.grad(fy,tx,td)
        xx,ww,bb=[v.detach().numpy().astype(np.float64) for v in tx];dd=td.numpy().astype(np.float64)
        cc=xx-xx.mean(axes,keepdims=True);ii=1/np.sqrt((cc*cc).mean(axes,keepdims=True)+1e-5);hh=cc*ii
        fexpected=[(hh*ww[None,:,None,None,None]+bb[None,:,None,None,None]).astype(np.float32),
            (ww[None,:,None,None,None]*ii*(dd-dd.mean(axes,keepdims=True)-hh*(dd*hh).mean(axes,keepdims=True))).astype(np.float32),
            (dd*hh).sum((0,2,3,4)).astype(np.float32),dd.sum((0,2,3,4)).astype(np.float32)]
        ferr=[float(np.max(np.abs(v.detach().numpy()-e))) for v,e in zip([fy,*fg],fexpected)];r['FP32_cast_output_dx_dgamma_dbeta_errors']=ferr;assert max(ferr)<=3e-6
        def objective(values):
            a,c,d=values;delta=a-a.mean(axes,keepdims=True);normal=delta/np.sqrt((delta*delta).mean(axes,keepdims=True)+1e-5)
            return float(np.einsum('ncijk,ncijk->',dy,normal*c[None,:,None,None,None]+d[None,:,None,None,None],dtype=np.float64,optimize=False))
        for index,base in enumerate((x,w,b)):
            direction=rng.standard_normal(base.shape);direction/=np.linalg.norm(direction)
            analytical=float(np.sum((dx,dw,db)[index]*direction));checks=[]
            for h in (1e-3,1e-4,1e-5):
                plus=[x,w,b];minus=[x,w,b];plus[index]=base+h*direction;minus[index]=base-h*direction
                op=objective(plus);om=objective(minus);fd=(op-om)/(2*h)
                checks.append(dict(h=h,plus=op,minus=om,derivative=fd,analytic_error=abs(fd-analytical)))
            q=dict(parameter=('input','gamma','beta')[index],analytical=analytical,checks=checks);r['finite_difference'].append(q)
            assert checks[-1]['analytic_error']<=1e-8
            if index==0:assert checks[1]['analytic_error']<=checks[0]['analytic_error']*.05+1e-9
        for p in r['source_bindings']:bind(p)
        r.update(complete=True,all_independent_equations_and_small_step_derivatives_passed=True,resources_after=guard())
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-started;save();print(json.dumps({k:r.get(k) for k in ('complete','errors','double_equation_errors','FP32_cast_output_dx_dgamma_dbeta_errors','elapsed_seconds')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
