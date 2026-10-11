"""One prospective fullpatch three-view artificial cost test, no medical data."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
os.environ['CUDA_VISIBLE_DEVICES']='0';os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
import sys,time,json,gc,traceback,subprocess
from pathlib import Path
STAGE=Path(__file__).resolve().parent;ROOT=STAGE.parent;HERE=ROOT/'six_resolution_training_preparation_2026_10_09';sys.path.insert(0,str(HERE))
sys.path.insert(0,str(ROOT/'adaptive_acquisition_primary_followup_2026_10_09'))
from resource_guard_v1 import guard,read,entry,bind
sys.path.insert(0,str(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09'))
from qualify_full_fov_gpu_cpu import torch,original_cuda_initializer,array_sha,state_hash
from audited_saved_cpu_v1 import CpuSavedTensorAudit
from compact_norm_task_model_v1 import HighPrecisionTaskUNet3D,stable_production_total_loss
from gin_reference_adapter_v1 import gin,draw_parameters
def main():
 start=time.perf_counter();torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
 out=STAGE/'compact_norm_fullpatch_cost_attempt01';out.mkdir(exist_ok=False)
 r=dict(complete=False,errors=[],phase='preparing',fullpatch_graph_completed=False,synthetic_GPU_optimizer_updates=0,forward_calls_started=0,forward_calls_completed=0,
  MRI_arrays_loaded=0,GT_arrays_loaded=0,parent_arrays_loaded=0,confirmation_patients_opened=False,lockedIXI_opened=False,other_PIDs_enumerated=False,other_PIDs_modified=False,original_training_modified=False,
  CPU_fullpatch_reference_run=False,fullpatch_numerical_qualification_passed=False,complete19series_GPU_qualified=False,
  formal_medical_training_launched=False,medical_effect_scored=False,publication_claim_confirmed=False,goal_status='active')
 def save():
  tmp=out/'receipt.json.tmp';tmp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(out/'receipt.json')
 def check():
  v=guard(start,360);assert torch.get_num_threads()==torch.get_num_interop_threads()==1
  if torch.cuda.is_initialized():
   free,total=torch.cuda.mem_get_info();peak=torch.cuda.max_memory_reserved();assert free>=4000000000 and peak<=2500000000
   v.update(GPU_free_bytes=free,GPU_peak_reserved_bytes=peak)
  return v
 save()
 try:
  r['resources_before']=check();q=read(STAGE/'compact_norm_offload_small_attempt01/receipt.json');a=read(ROOT/'adaptive_acquisition_primary_followup_2026_10_09/independent_round51_audit_attempt02/receipt.json')
  assert q['complete'] and a['complete'] and not q['errors'] and not a['errors']
  r['source_bindings']=[entry(p) for p in (Path(__file__),STAGE/'COMPACT_NORM_FULLPATCH_COST_PROTOCOL_V1.md',STAGE/'compact_norm_offload_small_attempt01/receipt.json',ROOT/'adaptive_acquisition_primary_followup_2026_10_09/independent_round51_audit_attempt02/receipt.json',HERE/'high_precision_task_model_v1.py',HERE/'high_precision_task_model_v2.py',STAGE/'compact_norm_task_model_v1.py',STAGE/'compact_double_norm_v1.py',STAGE/'audited_saved_cpu_v1.py',HERE/'stable_reduction_task_model_v1.py',HERE/'gin_reference_adapter_v1.py')]
  shape=(2,1,64,128,128);r['artificial_input_shape']=list(shape);r['phase']='artificial_CPU_GIN_preparation';save();tick=time.perf_counter()
  x=torch.randn(shape,generator=torch.Generator().manual_seed(991));views=[gin(x,draw_parameters(shape,801+i))[0] for i in range(3)];del x
  r['view_sha256']=[array_sha(v.numpy()) for v in views];r['GIN_CPU_seconds']=time.perf_counter()-tick
  z,row,col=torch.meshgrid(torch.arange(64),torch.arange(128),torch.arange(128),indexing='ij')
  target=(((z-31.5)/16).square()+((row-63.5)/24).square()+((col-63.5)/24).square()<1).float()[None,None].repeat(2,1,1,1,1);del z,row,col
  r['target_sha256']=array_sha(target.numpy());check()
  query=subprocess.run(['nvidia-smi','--query-gpu=index,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=20)
  gpu=[list(map(int,line.split(','))) for line in query.stdout.strip().splitlines()];r['GPU_aggregate_before']=gpu;assert len(gpu)==1 and gpu[0][0]==0 and gpu[0][1]>=8192
  assert not torch.cuda.is_initialized();r['CUDA_VISIBLE_DEVICES_after_CPU_imports']=os.environ.get('CUDA_VISIBLE_DEVICES');os.environ['CUDA_VISIBLE_DEVICES']='0';torch.cuda._lazy_init=original_cuda_initializer;assert torch.cuda.is_available()
  free,total=torch.cuda.mem_get_info();torch.cuda.set_per_process_memory_fraction(min(.1,2400000000/total));r['allocator_bytes_max']=min(.1*total,2400000000)
  torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True;torch.use_deterministic_algorithms(True)
  torch.manual_seed(20261009);model=HighPrecisionTaskUNet3D();r['initial_state_sha256']=state_hash(model.state_dict());assert r['initial_state_sha256']==q['initial_state_sha256'];model.to('cuda:0')
  opt=torch.optim.AdamW(model.parameters(),lr=1e-4,weight_decay=1e-4,betas=(.9,.999),eps=1e-8,foreach=False,fused=False);opt.zero_grad(set_to_none=True);outputs=[];gt=target.to('cuda:0');tick=time.perf_counter()
  audit=CpuSavedTensorAudit(array_sha,check)
  with audit.context():
   for index,view in enumerate(views):
    r['phase']=f'GPU_forward_view_{index}';r['forward_calls_started']+=1;save();check()
    outputs.append(model(view.to('cuda:0')));torch.cuda.synchronize();r['forward_calls_completed']+=1;check();save()
   r['phase']='GPU_loss_and_backward';save();value=stable_production_total_loss(outputs,gt);assert torch.isfinite(value);r['loss']=float(value.detach());value.backward();torch.cuda.synchronize();check()
   assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
  r['phase']='GPU_AdamW';save();opt.step();r['synthetic_GPU_optimizer_updates']+=1;torch.cuda.synchronize();check()
  r.update(fullpatch_graph_completed=True,GPU_full_graph_seconds=time.perf_counter()-tick);r.update(audit.write(out/'saved_tensor_journal.jsonl.gz'));r['saved_tensor_journal']=entry(out/'saved_tensor_journal.jsonl.gz')
  assert r['view_sha256']==[array_sha(v.numpy()) for v in views] and r['target_sha256']==array_sha(target.numpy())
  for b in r['source_bindings']:bind(b)
  r.update(complete=True,phase='completed',resources_after=check())
 except Exception as e:
  r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
  if 'audit' in locals() and audit.records and audit.unpacks:
   r.update(audit.write(out/'failure_saved_tensor_journal.jsonl.gz'));r['failure_saved_tensor_journal']=entry(out/'failure_saved_tensor_journal.jsonl.gz')
  if torch.cuda.is_initialized():r['GPU_peak_reserved_bytes_on_failure']=torch.cuda.max_memory_reserved();r['GPU_free_bytes_on_failure']=torch.cuda.mem_get_info()[0]
 r.update(elapsed_seconds=time.perf_counter()-start,CUDA_initialized=torch.cuda.is_initialized());save()
 print(json.dumps({k:r.get(k) for k in ('complete','errors','phase','forward_calls_started','forward_calls_completed','synthetic_GPU_optimizer_updates','GPU_peak_reserved_bytes_on_failure','elapsed_seconds')}),flush=True)
 return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
