"""Recompute the failed full FOV with one fixed CPU reference and two GPU memory layouts."""
import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
os.environ['CUDA_VISIBLE_DEVICES']='0'
import sys,gc,json,time,traceback,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from qualify_full_fov_gpu_cpu import (torch,original_cuda_initializer,read,sha,entry,bind,dump,resource_guard,
 development_cases,lattice,source_image,physical_mr,state_hash,array_sha,QPATH,np,CheckpointedTaskUNet3D,
 GuardedModel,functional_fov,infer_full_fov_v4)

def main():
 torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
 started=time.perf_counter();out=HERE/'layout_diagnosis_attempt01';out.mkdir(exist_ok=False)
 r=dict(complete=False,errors=[],comparisons=[],MRI_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
  training_updates=0,medical_effect_scored=False,validation_pixels_loaded=False,confirmation_patients_opened=False,
  lockedIXI_opened=False,other_PIDs_enumerated=False,other_PIDs_modified=False,original_training_modified=False,
  full38_FOV_qualified=False,publication_claim_confirmed=False,goal_status='active')
 def save():
  tmp=out/'receipt.json.tmp';tmp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(out/'receipt.json')
 def guard(cuda=True):
  v=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
  assert size<20_000_000 and v['workspace_free_bytes']-22_800_000-(20_000_000-size)>=8_000_000_000
  assert time.perf_counter()-started<1800 and torch.get_num_threads()==torch.get_num_interop_threads()==1
  if cuda:
   free,total=torch.cuda.mem_get_info();assert free>=4_000_000_000 and torch.cuda.max_memory_reserved()<=2_500_000_000
   v.update(GPU_free_bytes=free,GPU_peak_reserved_bytes=torch.cuda.max_memory_reserved())
  return v
 save()
 try:
  guard(False);tp=HERE/'ACTUAL_FULL_FOV_FAILED_TERMINAL_TOOL.json';assert read(tp)['exit_code']==1 and 'session_id' not in read(tp)
  fp=HERE/'full_fov_attempt01/receipt.json';failed=read(fp);assert not failed['complete'] and len(failed['series'])==3
  selected=failed['series'][-1];assert not selected['numeric_gate_passed'] and selected['case']==2 and selected['kind']=='native_reference'
  for b in failed['source_bindings']:bind(b)
  c,row=development_cases()[2];assert c['uid']==selected['uid'];tick=time.perf_counter()
  image,_=source_image(c,row,'native_reference');grid=lattice(c);cache=physical_mr(image,grid);del image
  assert array_sha(cache)==selected['input_sha256'];r['MRI_arrays_loaded']=1;r['load_seconds']=time.perf_counter()-tick
  pp=ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_2026-10-07.json';parent=read(pp)
  a=next(v for v in parent['arms'] if v['kind']=='native_reference');cpfile=ROOT/a['checkpoint_path'];assert sha(cpfile)==a['checkpoint_sha256']
  cp=torch.load(cpfile,map_location='cpu',weights_only=True);r['model_arrays_loaded']=1
  assert cp['updates_completed']==19998 and state_hash(cp['state_dict'])==cp['final_weights_sha256']
  sources={Path(__file__),HERE/'FAILED_FOV_DIAGNOSIS_PROTOCOL.md',fp,tp,cpfile,pp}
  sources.update(bind(b) for b in failed['source_bindings'])
  r['source_bindings']=[entry(p) for p in sorted(sources)]
  tick=time.perf_counter();reference,meta=functional_fov(cp['state_dict'],cache,grid,c['native_shape'],lambda:guard(False))
  r['CPU_reference_seconds']=time.perf_counter()-tick;r['CPU_reference_sha256']=array_sha(reference)
  assert r['CPU_reference_sha256']==selected['CPU_probability_sha256'];r['reference_original_hash_reproduced']=True;save()
  q=subprocess.run(['nvidia-smi','--query-gpu=index,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=20)
  gpu=[list(map(int,line.split(','))) for line in q.stdout.strip().splitlines()];assert len(gpu)==1 and gpu[0][1]>=8192
  torch.cuda._lazy_init=original_cuda_initializer;assert torch.cuda.is_available();free,total=torch.cuda.mem_get_info()
  torch.cuda.set_per_process_memory_fraction(min(.1,2_400_000_000/total))
  torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
  for layout in ['contiguous','channels_last_3d']:
   model=CheckpointedTaskUNet3D();model.load_state_dict(cp['state_dict']);model.eval();model.to('cuda:0')
   if layout=='channels_last_3d':model.to(memory_format=torch.channels_last_3d)
   assert state_hash(model.state_dict())==cp['final_weights_sha256']
   class Wrapped:
    def eval(self):return self
    def __call__(self,x):
     guard()
     if layout=='channels_last_3d':x=x.contiguous(memory_format=torch.channels_last_3d)
     value=model(x);guard();return value
   tick=time.perf_counter();prob,pmeta=infer_full_fov_v4(Wrapped(),cache,grid,c['native_shape'],device='cuda:0');torch.cuda.synchronize()
   error=float(np.max(np.abs(prob-reference)));binary=int(np.count_nonzero((prob>=.5)!=(reference>=.5)))
   v=dict(layout=layout,max_probability_error=error,binary_disagreements=binary,
    probability_sha256=array_sha(prob),strict_probability_binary_passed=error<=3e-6 and binary==0,
    GPU_full_pipeline_seconds=time.perf_counter()-tick,peak_reserved_bytes=torch.cuda.max_memory_reserved(),
    complete_native_shape=list(prob.shape),total_tiles=pmeta['total_tiles'])
   if layout=='contiguous':assert v['probability_sha256']==selected['GPU_probability_sha256'];v['original_failed_GPU_hash_reproduced']=True
   r['comparisons'].append(v);save();print(json.dumps(v),flush=True)
   assert state_hash(model.state_dict())==cp['final_weights_sha256'];del model,prob;gc.collect();torch.cuda.empty_cache();guard()
  for b in r['source_bindings']:bind(b)
  r.update(complete=True,status='completed',resources_after=guard(),coordinate_gate_passed=meta['float64_coordinate_gate_passed'])
 except Exception as e:r.update(status='failed',traceback=traceback.format_exc());r['errors'].append(type(e).__name__+': '+str(e))
 r['elapsed_seconds']=time.perf_counter()-started;save();print(json.dumps({k:r[k] for k in ['complete','errors','comparisons','elapsed_seconds']}),flush=True)
 return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
