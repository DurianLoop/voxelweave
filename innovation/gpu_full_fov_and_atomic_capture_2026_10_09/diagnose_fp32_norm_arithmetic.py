"""Two prospective FP32 normalization forms, complete192-tile inference for each and repeats."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
os.environ['CUDA_VISIBLE_DEVICES']='0'
import sys,time,json,subprocess,gc,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from qualify_full_fov_gpu_cpu import (torch,original_cuda_initializer,read,sha,entry,bind,dump,resource_guard,
 development_cases,lattice,source_image,physical_mr,state_hash,array_sha,np,CheckpointedTaskUNet3D,functional_fov,infer_full_fov_v4)
from fp32_norm_arithmetic_v1 import install
def main():
 os.environ['CUDA_VISIBLE_DEVICES']='0';torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
 started=time.perf_counter();out=HERE/'fp32_norm_arithmetic_attempt01';out.mkdir(exist_ok=False)
 r=dict(complete=False,status='preparing',errors=[],comparisons=[],MRI_arrays_loaded=0,GT_arrays_loaded=0,
  parent_model_arrays_loaded=0,training_updates=0,medical_effect_scored=False,full38_FOV_qualified=False,
  confirmation_patients_opened=False,lockedIXI_opened=False,other_PIDs_enumerated=False,other_PIDs_modified=False,
  original_training_modified=False,publication_claim_confirmed=False,goal_status='active')
 def save():
  temp=out/'receipt.json.tmp';temp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temp.replace(out/'receipt.json')
 def guard(cuda=True):
  v=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
  assert size<20_000_000 and v['workspace_free_bytes']-22_800_000-(20_000_000-size)>=8_000_000_000
  assert time.perf_counter()-started<1800 and torch.get_num_threads()==torch.get_num_interop_threads()==1
  if cuda:
   free,total=torch.cuda.mem_get_info();peak=torch.cuda.max_memory_reserved();assert free>=4_000_000_000 and peak<=2_500_000_000
   v.update(GPU_free_bytes=free,GPU_peak_reserved_bytes=peak)
  return v
 save()
 try:
  r['resources_before']=guard(False)
  ap=HERE/'layerwise_terminal_audit_attempt01/receipt.json';audit=read(ap);assert audit['complete'] and not audit['errors']
  assert audit['all96_batches192_unique_tiles4704_layer_fields_verified'] and audit['first_convolution_max_error']==0
  fp=HERE/'full_fov_attempt01/receipt.json';failed=read(fp);selected=failed['series'][-1];assert selected['case']==2 and not selected['numeric_gate_passed']
  for b in failed['source_bindings']:bind(b)
  c,row=development_cases()[2];assert c['uid']==selected['uid'];image,_=source_image(c,row,'native_reference');grid=lattice(c);cache=physical_mr(image,grid);del image
  assert array_sha(cache)==selected['input_sha256'];r['MRI_arrays_loaded']=1
  pp=ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_2026-10-07.json';parent=next(a for a in read(pp)['arms'] if a['kind']=='native_reference')
  cpfile=ROOT/parent['checkpoint_path'];assert sha(cpfile)==parent['checkpoint_sha256'];cp=torch.load(cpfile,map_location='cpu',weights_only=True)
  assert cp['updates_completed']==19998 and state_hash(cp['state_dict'])==cp['final_weights_sha256'];r['parent_model_arrays_loaded']=1
  sources={Path(__file__),HERE/'FP32_NORM_ARITHMETIC_DIAGNOSIS_PROTOCOL.md',HERE/'fp32_norm_arithmetic_v1.py',ap,fp,pp,cpfile}
  sources.update(bind(b) for b in failed['source_bindings']);sources.update(bind(b) for b in audit['source_bindings'])
  r['source_bindings']=[entry(p) for p in sorted(sources)];save()
  tick=time.perf_counter();reference,imeta=functional_fov(cp['state_dict'],cache,grid,c['native_shape'],lambda:guard(False))
  r['CPU_full_reference_seconds']=time.perf_counter()-tick;r['CPU_reference_sha256']=array_sha(reference)
  assert r['CPU_reference_sha256']==selected['CPU_probability_sha256'] and imeta['float64_coordinate_gate_passed'];save()
  query=subprocess.run(['nvidia-smi','--query-gpu=index,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=20)
  gpu=[list(map(int,v.split(','))) for v in query.stdout.strip().splitlines()];assert len(gpu)==1 and gpu[0][0]==0 and gpu[0][1]>=8192
  r['GPU_aggregate_before']=gpu;torch.cuda._lazy_init=original_cuda_initializer;assert torch.cuda.is_available();free,total=torch.cuda.mem_get_info()
  torch.cuda.set_per_process_memory_fraction(min(.1,2_400_000_000/total));torch.backends.cuda.matmul.allow_tf32=False
  torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
  for mode in ('native','fp32_centered','fp32_affine_addcmul'):
   model=CheckpointedTaskUNet3D();model.load_state_dict(cp['state_dict']);model.eval();model.to('cuda:0')
   if mode!='native':install(model,mode,guard)
   class Wrapped:
    def eval(self):return self
    def __call__(self,x):guard();value=model(x);guard();return value
   hashes=[];seconds=[];original=None
   for repeat in range(1 if mode=='native' else 2):
    tick=time.perf_counter();prob,meta=infer_full_fov_v4(Wrapped(),cache,grid,c['native_shape'],device='cuda:0');torch.cuda.synchronize()
    seconds.append(time.perf_counter()-tick);hashes.append(array_sha(prob));assert meta['total_tiles']==imeta['total_tiles']==192
    if repeat==0:original=prob
    else:assert np.array_equal(prob,original) and hashes[1]==hashes[0]
   error=float(np.max(np.abs(original-reference)));binary=int(np.count_nonzero((original>=.5)!=(reference>=.5)))
   if mode=='native':assert hashes[0]==selected['GPU_probability_sha256'] and error==selected['max_probability_error'] and binary==selected['binary_disagreements']
   q=dict(mode=mode,complete_FOV=True,total_tiles=192,repeats=len(hashes),max_probability_error=error,binary_disagreements=binary,
    probability_sha256=hashes[0],repeat_probability_sha256=hashes[-1],full_pipeline_seconds=seconds,
    strict_probability_binary_gate_passed=error<=3e-6 and binary==0,GPU_peak_reserved_bytes=torch.cuda.max_memory_reserved())
   if mode!='native':q['complete_FOV_repeat_bitwise_equal']=True
   r['comparisons'].append(q);save();print(json.dumps(q),flush=True)
   assert state_hash(model.state_dict())==cp['final_weights_sha256'];del model,prob,original;gc.collect();torch.cuda.empty_cache();guard()
  assert array_sha(cache)==selected['input_sha256']
  for source in r['source_bindings']:bind(source)
  r.update(complete=True,status='completed',coordinate_gate_passed=True,coordinate_error=imeta['float64_coordinate_max_probability_error'],
   qualifying_single_case_candidates=[q['mode'] for q in r['comparisons'] if q['mode']!='native' and q['strict_probability_binary_gate_passed']],resources_after=guard())
 except Exception as e:r.update(status='failed',traceback=traceback.format_exc());r['errors'].append(type(e).__name__+': '+str(e))
 r['elapsed_seconds']=time.perf_counter()-started;save();print(json.dumps({k:r.get(k) for k in ['complete','status','errors','qualifying_single_case_candidates','elapsed_seconds']}),flush=True)
 return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
