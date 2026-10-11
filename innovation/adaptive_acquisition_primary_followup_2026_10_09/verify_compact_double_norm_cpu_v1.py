"""Independent CPU explicit-variance autograd and NumPy directional finite differences."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,time,json,traceback
from pathlib import Path
from resource_guard_v1 import HERE,ROOT,guard,entry,bind
sys.path.insert(0,str(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09'))
from qualify_full_fov_gpu_cpu import torch,np,array_sha
from compact_double_norm_v1 import CompactDoubleNormFunction
def main():
 start=time.perf_counter();torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
 out=HERE/'compact_double_norm_cpu_attempt01';out.mkdir(exist_ok=False)
 r=dict(complete=False,errors=[],cases=[],finite_difference=[],MRI_arrays_loaded=0,GT_arrays_loaded=0,parent_arrays_loaded=0,optimizer_updates=0,GPU_calls=0,publication_claim_confirmed=False,goal_status='active')
 def save():
  tmp=out/'receipt.json.tmp';tmp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(out/'receipt.json')
 save()
 try:
  r['resources_before']=guard(start);assert not torch.cuda.is_initialized();r['source_bindings']=[entry(p) for p in (Path(__file__),HERE/'COMPACT_DOUBLE_NORM_PROTOCOL_V1.md',HERE/'compact_double_norm_v1.py')]
  rng=np.random.default_rng(52001);shape=(2,3,4,5,6);axes=(2,3,4)
  for case in ('random','constant','nearconstant','sparse'):
   x=rng.standard_normal(shape)
   if case=='constant':x=np.ones(shape)*.7
   elif case=='nearconstant':x=.7+1e-6*x
   elif case=='sparse':x=np.where(rng.random(shape)<.1,x,0)
   for dtype in (torch.float64,torch.float32):
    w=rng.standard_normal(3);b=rng.standard_normal(3);dy=rng.standard_normal(shape)
    values=[torch.tensor(x,dtype=torch.float64,requires_grad=True),torch.tensor(w,dtype=dtype,requires_grad=True),torch.tensor(b,dtype=dtype,requires_grad=True)]
    independent=[v.detach().clone().requires_grad_() for v in values]
    y=CompactDoubleNormFunction.apply(*values,1e-5)
    xx,ww,bb=independent;centered=xx-xx.mean(axes,keepdim=True);variance=(centered*centered).mean(axes,keepdim=True)
    other=centered*torch.rsqrt(variance+1e-5)*ww.to(torch.float64).reshape(1,-1,1,1,1)+bb.to(torch.float64).reshape(1,-1,1,1,1)
    grads=torch.autograd.grad(y,values,torch.from_numpy(dy));refs=torch.autograd.grad(other,independent,torch.from_numpy(dy))
    errors={key:float((a-c).detach().abs().max()) for key,a,c in zip(('output','dx','dgamma','dbeta'),(y,*grads),(other,*refs))}
    assert max(errors.values())<=3e-6
    r['cases'].append(dict(case=case,affine_dtype=str(dtype),max_errors=errors,input_sha256=array_sha(x),upstream_sha256=array_sha(dy)))
    if dtype!=torch.float64:continue
    actual=[v.detach().numpy().copy() for v in values]
    def objective(v):
     xx,ww,bb=v;delta=xx-xx.mean(axes,keepdims=True);normal=delta/np.sqrt((delta*delta).mean(axes,keepdims=True)+1e-5)
     return float(np.sum(dy*(normal*ww[None,:,None,None,None]+bb[None,:,None,None,None]),dtype=np.float64))
    for index in range(3):
     direction=rng.standard_normal(actual[index].shape);direction/=np.linalg.norm(direction)
     if index==0 and case in ('constant','nearconstant'):direction*=1e-3
     analytical=float(np.sum(grads[index].numpy()*direction));checks=[]
     for h in (1e-3,1e-4,1e-5):
      plus=[v.copy() for v in actual];minus=[v.copy() for v in actual];plus[index]+=h*direction;minus[index]-=h*direction
      op,om=objective(plus),objective(minus);derivative=(op-om)/(2*h)
      checks.append(dict(h=h,plus=op,minus=om,derivative=derivative,analytic_error=abs(derivative-analytical)))
     r['finite_difference'].append(dict(case=case,parameter=('input','gamma','beta')[index],direction_norm=float(np.linalg.norm(direction)),analytical=analytical,checks=checks));save();assert checks[-1]['analytic_error']<=1e-8
  for source in r['source_bindings']:bind(source)
  assert len(r['cases'])==8 and len(r['finite_difference'])==12 and not torch.cuda.is_initialized()
  r.update(complete=True,all_eight_forward_and_VJP_cases_passed=True,all_twelve_small_step_finite_differences_passed=True,resources_after=guard(start))
 except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
 r['elapsed_seconds']=time.perf_counter()-start;r['CUDA_initialized']=torch.cuda.is_initialized();save();print(json.dumps(dict(complete=r['complete'],errors=r['errors'],cases=r['cases'],finite_differences_completed=len(r['finite_difference']),elapsed_seconds=r['elapsed_seconds'])),flush=True)
 return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
