"""Two synthetic GPU updates vs two independent CPU updates under existing gates."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
os.environ['CUDA_VISIBLE_DEVICES']='0';os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
import sys,json,time,gc,traceback,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'adaptive_acquisition_primary_followup_2026_10_09'))
from resource_guard_v1 import guard,entry,bind,read,dump
sys.path.insert(0,str(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09'))
from qualify_full_fov_gpu_cpu import torch,original_cuda_initializer,array_sha,state_hash
from high_precision_task_model_v2 import HighPrecisionTaskUNet3D,stable_production_total_loss
from high_precision_cpu_reference_v1 import FunctionalCPUReference,independent_total_loss
from gin_reference_adapter_v1 import gin,draw_parameters
def main():
 started=time.perf_counter();torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
 out=HERE/'high_precision_model_gpu_attempt04';out.mkdir(exist_ok=False)
 r=dict(complete=False,errors=[],steps=[],synthetic_CPU_optimizer_updates=0,synthetic_GPU_optimizer_updates=0,
  MRI_arrays_loaded=0,GT_arrays_loaded=0,parent_arrays_loaded=0,original_training_modified=False,
  other_PIDs_enumerated=False,other_PIDs_modified=False,confirmation_patients_opened=False,lockedIXI_opened=False,
  graph_precision='FP64',parameter_precision='FP32',original_FP32_production_qualified=False,
  complete19series_GPU_qualified=False,full_resolution_qualified=False,formal_medical_training_launched=False,
  medical_effect_scored=False,publication_claim_confirmed=False,goal_status='active')
 def save():
  temp=out/'receipt.json.tmp';temp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temp.replace(out/'receipt.json')
 def check():
  v=guard(started,360);assert torch.get_num_threads()==torch.get_num_interop_threads()==1
  if torch.cuda.is_initialized():
   free,total=torch.cuda.mem_get_info();peak=torch.cuda.max_memory_reserved();assert free>=4000000000 and peak<=2500000000
   v.update(GPU_free_bytes=free,GPU_peak_reserved_bytes=peak,GPU_allocator_max_bytes=min(total*.1,2400000000))
  return v
 save()
 try:
  r['resources_before']=check();prior=read(HERE/'high_precision_model_cpu_attempt01/receipt.json')
  assert prior['complete'] and not prior['errors'] and prior['CPU_optimizer_updates']==4 and len(prior['steps'])==2
  pool=read(HERE/'disjoint_pool_cpu_attempt01/receipt.json');assert pool['complete'] and not pool['errors']
  for step in prior['steps']:assert max(step['max_errors'].values())<=3e-6 and step['binary_disagreements']==0
  r['source_bindings']=[entry(p) for p in (Path(__file__),HERE/'HIGH_PRECISION_GPU_SYNTHETIC_PROTOCOL_V4.md',HERE/'high_precision_model_cpu_attempt01/receipt.json',HERE/'high_precision_task_model_v1.py',HERE/'high_precision_task_model_v2.py',HERE/'disjoint_pool_cpu_attempt01/receipt.json',HERE/'high_precision_cpu_reference_v1.py',HERE/'stable_reduction_task_model_v1.py',HERE/'gin_cpu_differentiable_reference_v1.py',HERE/'gin_reference_adapter_v1.py',ROOT/'adaptive_acquisition_primary_followup_2026_10_09/resource_guard_v1.py')]
  torch.manual_seed(20261009);production=HighPrecisionTaskUNet3D();initial={n:v.detach().clone() for n,v in production.state_dict().items()};reference=FunctionalCPUReference(initial)
  r['initial_state_sha256']=state_hash(initial);assert r['initial_state_sha256']==prior['initial_state_sha256']==state_hash(reference.state_dict())
  shape=(2,1,16,16,16);x=torch.randn(shape,generator=torch.Generator().manual_seed(49));views=[gin(x,draw_parameters(shape,480000+i))[0] for i in range(3)]
  target=(torch.randn(shape,generator=torch.Generator().manual_seed(501))>.8).float()
  r['input_sha256']=[array_sha(v.numpy()) for v in views];r['synthetic_target_sha256']=array_sha(target.numpy())
  assert r['input_sha256']==prior['input_sha256'] and r['synthetic_target_sha256']==prior['synthetic_target_sha256']
  query=subprocess.run(['nvidia-smi','--query-gpu=index,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=20)
  gpu=[list(map(int,line.split(','))) for line in query.stdout.strip().splitlines()]
  r['GPU_aggregate_before']=gpu;assert len(gpu)==1 and gpu[0][0]==0 and gpu[0][1]>=8192
  assert not torch.cuda.is_initialized();r['CUDA_VISIBLE_DEVICES_after_CPU_imports']=os.environ.get('CUDA_VISIBLE_DEVICES');os.environ['CUDA_VISIBLE_DEVICES']='0';r['CUDA_VISIBLE_DEVICES_at_GPU_admission']=os.environ['CUDA_VISIBLE_DEVICES'];r['torch_version']=str(torch.__version__);r['torch_CUDA_version']=torch.version.cuda;torch.cuda._lazy_init=original_cuda_initializer;assert torch.cuda.is_available()
  free,total=torch.cuda.mem_get_info();torch.cuda.set_per_process_memory_fraction(min(.1,2400000000/total))
  torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True;torch.use_deterministic_algorithms(True)
  production.to('cuda:0');torch.cuda.synchronize();check()
  opts=[torch.optim.AdamW(m.parameters(),lr=1e-4,weight_decay=1e-4,betas=(.9,.999),eps=1e-8,foreach=False,fused=False) for m in (production,reference)]
  gpuviews=[v.to('cuda:0') for v in views];gputarget=target.to('cuda:0')
  for step in range(2):
   states=[]
   for index,(model,opt) in enumerate(zip((production,reference),opts)):
    check();tick=time.perf_counter();opt.zero_grad(set_to_none=True);outputs=[model(v) for v in (gpuviews if index==0 else views)]
    assert all(z.dtype==torch.float64 for head in outputs for z in head)
    value=stable_production_total_loss(outputs,gputarget) if index==0 else independent_total_loss(outputs,target)
    assert value.dtype==torch.float64 and torch.isfinite(value);value.backward()
    if index==0:torch.cuda.synchronize()
    check();grads={n:p.grad.detach().cpu().clone() for n,p in model.named_parameters()}
    assert len(grads)==54 and all(v.dtype==torch.float32 and torch.isfinite(v).all() for v in grads.values())
    probs=[torch.stack([v[d].detach().sigmoid().cpu() for v in outputs]) for d in range(3)]
    opt.step();r['synthetic_GPU_optimizer_updates' if index==0 else 'synthetic_CPU_optimizer_updates']+=1
    if index==0:torch.cuda.synchronize()
    states.append(dict(loss=float(value.detach()),gradients=grads,probabilities=probs,params={n:p.detach().cpu().clone() for n,p in model.named_parameters()},moments={n:{k:v.detach().cpu().clone() for k,v in opt.state[p].items()} for n,p in model.named_parameters()},seconds=time.perf_counter()-tick))
    del outputs,value,grads,probs;gc.collect();check();save()
   a,b=states;records=[]
   for n in a['params']:
    fields=[dict(field=k,max_error=float((v-b['moments'][n][k]).abs().max())) for k,v in a['moments'][n].items()]
    records.append(dict(name=n,gradient_error=float((a['gradients'][n]-b['gradients'][n]).abs().max()),parameter_error=float((a['params'][n]-b['params'][n]).abs().max()),optimizer_fields=fields))
   maximum=dict(loss=abs(a['loss']-b['loss']),probability=max(float((v-w).abs().max()) for v,w in zip(a['probabilities'],b['probabilities'])),gradient=max(v['gradient_error'] for v in records),parameter=max(v['parameter_error'] for v in records),optimizer_state=max(f['max_error'] for v in records for f in v['optimizer_fields']))
   binary=sum(int(torch.count_nonzero((v>=.5)!=(w>=.5))) for v,w in zip(a['probabilities'],b['probabilities']))
   r['steps'].append(dict(step=step,max_errors=maximum,binary_disagreements=binary,all54_parameters=records,optimizer_fields_compared=162,loss_values=[a['loss'],b['loss']],GPU_weights_sha256=state_hash(a['params']),CPU_weights_sha256=state_hash(b['params']),GPU_branch_seconds=a['seconds'],CPU_branch_seconds=b['seconds']))
   save();print(json.dumps(dict(step=step,max_errors=maximum,binary_disagreements=binary)),flush=True)
   assert max(maximum.values())<=3e-6 and binary==0
   assert r['input_sha256']==[array_sha(v.numpy()) for v in views] and r['synthetic_target_sha256']==array_sha(target.numpy())
   del states,a,b;gc.collect();check()
  for s in r['source_bindings']:bind(s)
  r.update(complete=True,all_two_synthetic_GPU_CPU_steps_passed=True,resources_after=check())
 except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
 r.update(CUDA_initialized=torch.cuda.is_initialized(),elapsed_seconds=time.perf_counter()-started);save()
 print(json.dumps({k:r.get(k) for k in ('complete','errors','synthetic_GPU_optimizer_updates','synthetic_CPU_optimizer_updates','elapsed_seconds')}),flush=True)
 return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
