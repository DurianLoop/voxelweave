"""Independent two-step synthetic validation for the new stable-reduction numeric version."""
import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import sys,json,time,gc,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'adaptive_acquisition_primary_followup_2026_10_09'))
from resource_guard_v1 import guard,read,entry,bind
sys.path.insert(0,str(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09'))
from qualify_full_fov_gpu_cpu import torch,array_sha,state_hash
from stable_reduction_task_model_v1 import StableReductionTaskUNet3D,stable_production_total_loss
from gin_cpu_differentiable_reference_v2 import FunctionalCPUReference,independent_total_loss,nearest_binary_target
from gin_reference_adapter_v1 import gin,draw_parameters
def main():
 started=time.perf_counter();torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
 out=HERE/'stable_reduction_model_cpu_attempt01';out.mkdir(exist_ok=False)
 r=dict(complete=False,errors=[],steps=[],CPU_optimizer_updates=0,MRI_arrays_loaded=0,GT_arrays_loaded=0,parent_arrays_loaded=0,GPU_calls=0,
  original_FP32_production_qualified=False,complete19series_GPU_qualified=False,medical_effect_scored=False,publication_claim_confirmed=False,goal_status='active')
 def save():(out/'receipt.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 def check():
  v=guard(started);assert not torch.cuda.is_initialized();assert torch.get_num_threads()==torch.get_num_interop_threads()==1;return v
 save()
 try:
  r['resources_before']=check();r['source_bindings']=[entry(p) for p in (Path(__file__),HERE/'STABLE_REDUCTION_MODEL_SYNTHETIC_PROTOCOL_V1.md',HERE/'stable_reduction_task_model_v1.py',HERE/'gin_cpu_differentiable_reference_v2.py',HERE/'gin_cpu_differentiable_reference_v1.py',HERE/'gin_reference_adapter_v1.py',HERE/'stable_norm_math_v2_attempt01/receipt.json',ROOT/'gpu_graph_cost_smoke_2026_10_09/checkpointed_model.py',ROOT/'adaptive_acquisition_primary_followup_2026_10_09/resource_guard_v1.py')]
  torch.manual_seed(20261009);production=StableReductionTaskUNet3D();initial={n:v.detach().clone() for n,v in production.state_dict().items()};reference=FunctionalCPUReference(initial)
  r['initial_state_sha256']=state_hash(initial);assert r['initial_state_sha256']==state_hash(reference.state_dict())=='2f7987cf7b4f1d6160170a304df9b1dd4d6d88bb86f490888a3dd68f50b9f59a'
  shape=(2,1,16,16,16);x=torch.randn(shape,generator=torch.Generator().manual_seed(49));views=[gin(x,draw_parameters(shape,480000+i))[0] for i in range(3)]
  target=(torch.randn(shape,generator=torch.Generator().manual_seed(501))>.8).float();r['input_sha256']=[array_sha(v.numpy()) for v in views];r['synthetic_target_sha256']=array_sha(target.numpy())
  opts=[torch.optim.AdamW(m.parameters(),lr=1e-4,weight_decay=1e-4,betas=(.9,.999),eps=1e-8,foreach=False,fused=False) for m in (production,reference)]
  for step in range(2):
   states=[]
   for index,(model,opt) in enumerate(zip((production,reference),opts)):
    check();opt.zero_grad(set_to_none=True);outputs=[model(v) for v in views]
    for view in outputs:
     for z in view:
      assert z.dtype==torch.float32 and torch.equal(torch.nn.functional.interpolate(target,size=z.shape[2:],mode='nearest-exact'),nearest_binary_target(target,z.shape[2:]))
    value=stable_production_total_loss(outputs,target) if index==0 else independent_total_loss([tuple(z.to(torch.float64) for z in v) for v in outputs],target)
    assert value.dtype==torch.float64;value.backward();check()
    grads={n:p.grad.detach().clone() for n,p in model.named_parameters()};assert all(v.dtype==torch.float32 and torch.isfinite(v).all() for v in grads.values())
    probs=[torch.stack([v[d].detach().sigmoid() for v in outputs]) for d in range(3)]
    opt.step();r['CPU_optimizer_updates']+=1
    states.append(dict(loss=float(value.detach()),gradients=grads,probabilities=probs,params={n:p.detach().clone() for n,p in model.named_parameters()},moments={n:{k:v.detach().clone() for k,v in opt.state[p].items()} for n,p in model.named_parameters()}))
    del outputs,value,grads,probs;gc.collect();check()
   a,b=states;records=[]
   for n in a['params']:
    fields=[dict(field=k,max_error=float((v-b['moments'][n][k]).abs().max())) for k,v in a['moments'][n].items()]
    records.append(dict(name=n,gradient_error=float((a['gradients'][n]-b['gradients'][n]).abs().max()),parameter_error=float((a['params'][n]-b['params'][n]).abs().max()),optimizer_fields=fields))
   maximum=dict(loss=abs(a['loss']-b['loss']),probability=max(float((v-w).abs().max()) for v,w in zip(a['probabilities'],b['probabilities'])),gradient=max(v['gradient_error'] for v in records),parameter=max(v['parameter_error'] for v in records),optimizer_state=max(f['max_error'] for v in records for f in v['optimizer_fields']))
   binary=sum(int(torch.count_nonzero((v>=.5)!=(w>=.5))) for v,w in zip(a['probabilities'],b['probabilities']))
   r['steps'].append(dict(step=step,max_errors=maximum,binary_disagreements=binary,all54_parameters=records,optimizer_fields_compared=162,
    loss_values=[a['loss'],b['loss']],production_weights_sha256=state_hash(a['params']),reference_weights_sha256=state_hash(b['params'])))
   save();print(json.dumps(dict(step=step,max_errors=maximum,binary_disagreements=binary)),flush=True)
   assert max(maximum.values())<=3e-6 and binary==0
   assert r['input_sha256']==[array_sha(v.numpy()) for v in views] and r['synthetic_target_sha256']==array_sha(target.numpy())
   del states,a,b;gc.collect();check()
  for source in r['source_bindings']:bind(source)
  r.update(complete=True,all_two_steps54_parameters162_optimizer_fields_and_allheads_passed=True,CPU_whole_model_forwards=12,CPU_whole_model_backwards=4,resources_after=check())
 except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
 r['CUDA_initialized']=torch.cuda.is_initialized();r['elapsed_seconds']=time.perf_counter()-started;save()
 print(json.dumps({k:r.get(k) for k in ('complete','errors','CPU_optimizer_updates','elapsed_seconds')}),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
