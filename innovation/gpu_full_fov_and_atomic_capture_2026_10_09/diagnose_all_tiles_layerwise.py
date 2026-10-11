"""All192 failed-case tiles: independent CPU interpreter, GPU hooks and exact device repeat checks."""
import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
os.environ['CUDA_VISIBLE_DEVICES']='0'
import sys,time,json,gzip,itertools,gc,traceback,subprocess,zlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from qualify_full_fov_gpu_cpu import (torch,original_cuda_initializer,read,sha,entry,bind,dump,resource_guard,
 development_cases,lattice,source_image,physical_mr,state_hash,array_sha,np,CheckpointedTaskUNet3D)
from mc_rc_3d_independent_replay_2026_10_07 import independent_starts,independent_weight,independent_native_resample
from mc_rc_3d_baseline_2026_10_07 import PATCH,tile_plan,blending_weight
from verify_final_lossless_v3 import numpy_native64
from torch.nn import functional as F

def cpu_forward(x,state):
 captures={};skips=[]
 def block(value,prefix):
  for conv,norm,relu in ((0,1,2),(3,4,5)):
   value=F.conv3d(value,state[prefix+f'.layers.{conv}.weight'],padding=1);captures[prefix+f'.layers.{conv}']=value
   value=F.instance_norm(value,weight=state[prefix+f'.layers.{norm}.weight'],bias=state[prefix+f'.layers.{norm}.bias'],use_input_stats=True,eps=1e-5)
   captures[prefix+f'.layers.{norm}']=value
   value=F.leaky_relu(value,negative_slope=.01);captures[prefix+f'.layers.{relu}']=value
  return value
 for level in range(4):
  if level:x=F.max_pool3d(x,2,2)
  x=block(x,'encoders.'+str(level));skips.append(x)
 outputs=[]
 for depth,skip in enumerate(reversed(skips[:-1])):
  x=F.conv_transpose3d(x,state[f'ups.{depth}.weight'],state[f'ups.{depth}.bias'],stride=2);captures[f'ups.{depth}']=x
  x=block(torch.cat((x,skip),dim=1),'decoders.'+str(depth))
  out=F.conv3d(x,state[f'heads.{depth}.weight'],state[f'heads.{depth}.bias']);captures[f'heads.{depth}']=out;outputs.append(out)
 probability=outputs[-1].sigmoid();captures['probability']=probability
 assert len(captures)==49;return probability,captures

def main():
 os.environ['CUDA_VISIBLE_DEVICES']='0';torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
 started=time.perf_counter();out=HERE/'layerwise_all_tiles_attempt01';out.mkdir(exist_ok=False)
 r=dict(complete=False,status='preparing',errors=[],batches_completed=0,unique_tiles=0,
  actual_GPU_tile_forwards=0,actual_CPU_tile_forwards=0,MRI_arrays_loaded=0,GT_arrays_loaded=0,parent_model_arrays_loaded=0,
  training_updates=0,medical_effect_scored=False,validation_pixels_loaded=False,confirmation_patients_opened=False,
  lockedIXI_opened=False,other_PIDs_enumerated=False,other_PIDs_modified=False,original_training_modified=False,
  full38_FOV_qualified=False,publication_claim_confirmed=False,goal_status='active',layer_maxima={})
 def save():
  tmp=out/'receipt.json.tmp';tmp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(out/'receipt.json')
 def guard(cuda=True):
  v=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
  assert size<20_000_000 and v['workspace_free_bytes']-22_800_000-(20_000_000-size)>=8_000_000_000
  assert time.perf_counter()-started<3600 and torch.get_num_threads()==torch.get_num_interop_threads()==1
  if cuda:
   free,total=torch.cuda.mem_get_info();peak=torch.cuda.max_memory_reserved();assert free>=4_000_000_000 and peak<=2_500_000_000
   v.update(GPU_free_bytes=free,GPU_peak_reserved_bytes=peak)
  return v
 save()
 try:
  r['resources_before']=guard(False)
  fp=HERE/'full_fov_attempt01/receipt.json';failed=read(fp);selected=failed['series'][-1]
  assert not failed['complete'] and selected['case']==2 and not selected['numeric_gate_passed']
  for b in failed['source_bindings']:bind(b)
  c,row=development_cases()[2];assert c['uid']==selected['uid']
  image,_=source_image(c,row,'native_reference');grid=lattice(c);cache=physical_mr(image,grid);del image
  assert array_sha(cache)==selected['input_sha256'];r['MRI_arrays_loaded']=1
  pp=ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_2026-10-07.json'
  a=next(v for v in read(pp)['arms'] if v['kind']=='native_reference');cpfile=ROOT/a['checkpoint_path'];assert sha(cpfile)==a['checkpoint_sha256']
  cp=torch.load(cpfile,map_location='cpu',weights_only=True);state=cp['state_dict'];r['parent_model_arrays_loaded']=1
  assert cp['updates_completed']==19998 and state_hash(state)==cp['final_weights_sha256']
  locations,axes=tile_plan(cache.shape);iaxes=independent_starts(cache.shape,PATCH)
  assert axes==iaxes and locations==list(itertools.product(*iaxes)) and len(locations)==192
  sources={Path(__file__),HERE/'FULL_TILE_LAYERWISE_PROTOCOL.md',fp,pp,cpfile,
   ROOT/'experiments/mc_rc_3d_independent_replay_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py'}
  sources.update(bind(b) for b in failed['source_bindings'])
  frozen=dict(patient=c['patient'],uid=c['uid'],case=2,kind='native_reference',expected_unique_tiles=192,
   batch_size=2,expected_batches=96,repeat_per_device=2,expected_layer_fields=49,patch=PATCH,
   axis_starts=axes,source_bindings=[entry(p) for p in sorted(sources)])
  dump(out/'frozen_config.json',frozen);r['source_bindings']=frozen['source_bindings'];save()
  q=subprocess.run(['nvidia-smi','--query-gpu=index,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=20)
  aggregate=[list(map(int,line.split(','))) for line in q.stdout.strip().splitlines()];assert len(aggregate)==1 and aggregate[0][0]==0 and aggregate[0][1]>=8192
  r['GPU_aggregate_before']=aggregate;os.environ['CUDA_VISIBLE_DEVICES']='0';torch.cuda._lazy_init=original_cuda_initializer
  assert torch.cuda.is_available();free,total=torch.cuda.mem_get_info();torch.cuda.set_per_process_memory_fraction(min(.1,2_400_000_000/total))
  torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
  model=CheckpointedTaskUNet3D();model.load_state_dict(state);model.eval();model.to('cuda:0');guard()
  captured={};handles=[];leaf_types=(torch.nn.Conv3d,torch.nn.ConvTranspose3d,torch.nn.InstanceNorm3d,torch.nn.LeakyReLU)
  def hook(name):
   def record(module,inputs,value):captured[name]=value.detach().cpu()
   return record
  for name,module in model.named_modules():
   if isinstance(module,leaf_types):handles.append(module.register_forward_hook(hook(name)))
  assert len(handles)==48
  cw=independent_weight(PATCH);gw=blending_weight(PATCH)
  cn=np.zeros(cache.shape,np.float64);cd=np.zeros_like(cn);gn=np.zeros_like(cn);gd=np.zeros_like(cn)
  journal=out/'batches.jsonl.gz';costs=dict(CPU_repeated_forward=0.,GPU_repeated_forward_and_capture=0.,layer_comparison=0.,full_fov_reconstruction=0.)
  with journal.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',compresslevel=6,mtime=0) as stream,torch.inference_mode():
   for batch,at in enumerate(range(0,len(locations),2)):
    guard();starts=locations[at:at+2];slices=[tuple(slice(s,s+n) for s,n in zip(start,PATCH)) for start in starts]
    x=torch.from_numpy(np.stack([cache[sl] for sl in slices])[:,None])
    tick=time.perf_counter();prob,cc=cpu_forward(x,state);prob2,cc2=cpu_forward(x,state)
    cpu_repeat=all(torch.equal(cc[k],cc2[k]) for k in cc);assert cpu_repeat;del cc2,prob2
    costs['CPU_repeated_forward']+=time.perf_counter()-tick
    tick=time.perf_counter();gx=x.to('cuda:0');captured.clear();outputs=model(gx);gp=outputs[0].sigmoid().cpu();captured['probability']=gp
    gcapt=dict(captured);captured.clear();outputs2=model(gx);gp2=outputs2[0].sigmoid().cpu();captured['probability']=gp2
    gpu_repeat=all(torch.equal(gcapt[k],captured[k]) for k in gcapt);assert gpu_repeat;captured.clear()
    assert set(cc)==set(gcapt) and len(cc)==49;del outputs,outputs2,gp2,gx
    costs['GPU_repeated_forward_and_capture']+=time.perf_counter()-tick
    tick=time.perf_counter();checks=[]
    for name,reference in cc.items():
     candidate=gcapt[name];assert reference.dtype==candidate.dtype==torch.float32 and reference.shape==candidate.shape
     assert torch.isfinite(reference).all() and torch.isfinite(candidate).all()
     diff=(reference-candidate).abs();index=int(diff.flatten().argmax());coord=list(np.unravel_index(index,tuple(diff.shape)))
     maximum=float(diff.max());relative=float((diff/(reference.abs()+1e-6)).max())
     check=dict(name=name,shape=list(reference.shape),elements=reference.numel(),max_absolute_error=maximum,
      mean_absolute_error=float(diff.mean()),max_relative_error_with_1e_6_floor=relative,
      CPU_absolute_max=float(reference.abs().max()),GPU_absolute_max=float(candidate.abs().max()),
      maximum_error_index=list(map(int,coord)),maximum_error_CPU_value=float(reference.flatten()[index]),maximum_error_GPU_value=float(candidate.flatten()[index]))
     checks.append(check)
     previous=r['layer_maxima'].get(name)
     if previous is None or maximum>previous['max_absolute_error']:
      r['layer_maxima'][name]=dict(check,batch=batch,tile_starts=[list(v) for v in starts])
     del diff
    costs['layer_comparison']+=time.perf_counter()-tick
    for sl,cpvalue,gpvalue in zip(slices,prob.numpy()[:,0],gp.numpy()[:,0]):
     cn[sl]+=cpvalue*cw;cd[sl]+=cw;gn[sl]+=gpvalue*gw;gd[sl]+=gw
    record=dict(batch=batch,tile_starts=starts,CPU_all49_fields_repeat_bitwise_equal=cpu_repeat,
     GPU_all49_fields_repeat_bitwise_equal=gpu_repeat,layer_checks=checks,
     CPU_batch_probability_sha256=array_sha(prob.numpy()),GPU_batch_probability_sha256=array_sha(gp.numpy()))
    stream.write((json.dumps(record,separators=(',',':'))+'\n').encode());stream.flush(zlib.Z_SYNC_FLUSH)
    r['batches_completed']+=1;r['unique_tiles']+=len(starts);r['actual_CPU_tile_forwards']+=2*len(starts);r['actual_GPU_tile_forwards']+=2*len(starts)
    if batch%8==0 or batch==95:
     raw.flush();save();print(json.dumps(dict(batches_completed=r['batches_completed'],expected_batches=96,elapsed_seconds=time.perf_counter()-started)),flush=True)
    del x,prob,gp,cc,gcapt,checks;gc.collect();guard();assert journal.stat().st_size<3_000_000
  tick=time.perf_counter();assert cd.min()>0 and gd.min()>0
  crop=tuple(slice(int(lo),int(lo)+int(n)) for (lo,hi),n in zip(grid['padding'],grid['unpadded_shape_zrc']))
  cpu_physical=np.ascontiguousarray((cn/cd)[crop],np.float32);gpu_physical=np.ascontiguousarray((gn/gd)[crop],np.float32)
  cpu_native=independent_native_resample(cpu_physical,c['native_shape'])
  with torch.inference_mode():
   gpu_native=F.interpolate(torch.from_numpy(gpu_physical.astype(np.float64))[None,None],
    size=(c['native_shape'][2],c['native_shape'][0],c['native_shape'][1]),mode='trilinear',align_corners=False)[0,0].numpy().transpose(1,2,0).astype(np.float32)
   coordinate_ref=F.interpolate(torch.from_numpy(cpu_physical.astype(np.float64))[None,None],
    size=(c['native_shape'][2],c['native_shape'][0],c['native_shape'][1]),mode='trilinear',align_corners=False)[0,0].numpy().transpose(1,2,0)
  coordinate_ind=numpy_native64(cpu_physical,c['native_shape']);ce=float(np.max(np.abs(coordinate_ref-coordinate_ind)))
  binary_coordinate=int(np.count_nonzero((coordinate_ref>=.5)!=(coordinate_ind>=.5)))
  cpu_hash=array_sha(cpu_native);gpu_hash=array_sha(gpu_native);assert cpu_hash==selected['CPU_probability_sha256'] and gpu_hash==selected['GPU_probability_sha256']
  maximum=float(np.max(np.abs(cpu_native-gpu_native)));binary=int(np.count_nonzero((cpu_native>=.5)!=(gpu_native>=.5)))
  assert maximum==selected['max_probability_error'] and binary==selected['binary_disagreements'] and ce<=3e-12 and binary_coordinate==0
  costs['full_fov_reconstruction']=time.perf_counter()-tick
  for handle in handles:handle.remove()
  assert state_hash(model.state_dict())==cp['final_weights_sha256'];assert r['batches_completed']==96 and r['unique_tiles']==192
  assert r['actual_GPU_tile_forwards']==r['actual_CPU_tile_forwards']==384
  for b in r['source_bindings']:bind(b)
  r.update(complete=True,status='completed',CPU_GPU_original_fullFOV_hashes_reproduced=True,
   all49_layer_fields_same_device_repeat_bitwise_equal=True,original_failed_probability_error=maximum,
   binary_disagreements=binary,coordinate_error=ce,coordinate_binary_disagreements=binary_coordinate,
   original_probability_gate_passed=False,cost_seconds=costs,journal=entry(journal),frozen_config_sha256=sha(out/'frozen_config.json'),resources_after=guard())
 except Exception as e:r.update(status='failed',traceback=traceback.format_exc());r['errors'].append(type(e).__name__+': '+str(e))
 r['elapsed_seconds']=time.perf_counter()-started;save();print(json.dumps({k:r.get(k) for k in ['complete','status','errors','batches_completed','elapsed_seconds']}),flush=True)
 return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
