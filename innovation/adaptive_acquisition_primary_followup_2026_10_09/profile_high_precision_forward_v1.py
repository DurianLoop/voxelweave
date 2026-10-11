"""Read-only module hooks locate the old fullpatch OOM; no optimizer or medical reads."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
os.environ['CUDA_VISIBLE_DEVICES']='0';os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
import sys,time,json,traceback,subprocess
from pathlib import Path
from resource_guard_v1 import HERE,ROOT,guard,read,entry,bind
PREP=ROOT/'six_resolution_training_preparation_2026_10_09';sys.path.insert(0,str(PREP))
sys.path.insert(0,str(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09'))
from qualify_full_fov_gpu_cpu import torch,original_cuda_initializer,array_sha,state_hash
from high_precision_task_model_v2 import HighPrecisionTaskUNet3D
from gin_reference_adapter_v1 import gin,draw_parameters
def main():
 start=time.perf_counter();torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
 out=HERE/'high_precision_forward_profile_attempt01';out.mkdir(exist_ok=False)
 r=dict(complete=False,errors=[],events=[],GPU_forward_started=0,GPU_forward_completed=0,optimizer_updates=0,backward_calls=0,
  MRI_arrays_loaded=0,GT_arrays_loaded=0,parent_arrays_loaded=0,other_PIDs_enumerated=False,other_PIDs_modified=False,original_training_modified=False,publication_claim_confirmed=False,goal_status='active')
 def save():
  tmp=out/'receipt.json.tmp';tmp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(out/'receipt.json')
 def check():
  v=guard(start,180)
  if torch.cuda.is_initialized():
   free,total=torch.cuda.mem_get_info();peak=torch.cuda.max_memory_reserved();assert free>=4000000000 and peak<=2500000000
   v.update(GPU_free_bytes=free,GPU_peak_reserved_bytes=peak)
  return v
 save()
 try:
  r['resources_before']=check();old=read(PREP/'high_precision_fullpatch_cost_attempt01/receipt.json');assert not old['complete'] and old['synthetic_GPU_optimizer_updates']==0
  r['source_bindings']=[entry(p) for p in (Path(__file__),HERE/'ROUND52_GPU_MEMORY_PROFILE_PROTOCOL.md',PREP/'high_precision_fullpatch_cost_attempt01/receipt.json',PREP/'high_precision_task_model_v1.py',PREP/'high_precision_task_model_v2.py')]
  shape=(2,1,64,128,128);x=torch.randn(shape,generator=torch.Generator().manual_seed(991));view=gin(x,draw_parameters(shape,801))[0];del x
  r['input_sha256']=array_sha(view.numpy());assert r['input_sha256']==old['view_sha256'][0]
  query=subprocess.run(['nvidia-smi','--query-gpu=index,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=20)
  gpu=[list(map(int,line.split(','))) for line in query.stdout.strip().splitlines()];r['GPU_aggregate_before']=gpu;assert len(gpu)==1 and gpu[0][0]==0 and gpu[0][1]>=8192
  assert not torch.cuda.is_initialized();os.environ['CUDA_VISIBLE_DEVICES']='0';torch.cuda._lazy_init=original_cuda_initializer;assert torch.cuda.is_available()
  free,total=torch.cuda.mem_get_info();torch.cuda.set_per_process_memory_fraction(min(.1,2400000000/total))
  torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True;torch.use_deterministic_algorithms(True)
  torch.manual_seed(20261009);model=HighPrecisionTaskUNet3D();r['initial_sha256']=state_hash(model.state_dict());assert r['initial_sha256']==old['initial_state_sha256'];model.to('cuda:0')
  def event(name,phase,values):
   torch.cuda.synchronize();check();tensors=[v for v in values if isinstance(v,torch.Tensor)]
   r['events'].append(dict(layer=name,phase=phase,shapes=[list(v.shape) for v in tensors],dtypes=[str(v.dtype) for v in tensors],allocated=torch.cuda.memory_allocated(),reserved=torch.cuda.memory_reserved(),peak_reserved=torch.cuda.max_memory_reserved(),elapsed_seconds=time.perf_counter()-start));save()
  for name,module in model.named_modules():
   if name and not list(module.children()):
    module.register_forward_pre_hook(lambda mod,args,name=name:event(name,'before',args))
    module.register_forward_hook(lambda mod,args,result,name=name:event(name,'after',(result,)))
  r['GPU_forward_started']=1;save();outputs=model(view.to('cuda:0'));torch.cuda.synchronize();r['GPU_forward_completed']=1
  assert r['input_sha256']==array_sha(view.numpy())
  for b in r['source_bindings']:bind(b)
  r.update(complete=True,resources_after=check())
 except Exception as e:
  r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
  if torch.cuda.is_initialized():r['GPU_peak_reserved_bytes_on_failure']=torch.cuda.max_memory_reserved()
 r.update(elapsed_seconds=time.perf_counter()-start,CUDA_initialized=torch.cuda.is_initialized());save()
 print(json.dumps(dict(complete=r['complete'],errors=r['errors'],last_events=r['events'][-6:],GPU_forward_completed=r['GPU_forward_completed'],optimizer_updates=0,elapsed_seconds=r['elapsed_seconds'])),flush=True)
 return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
