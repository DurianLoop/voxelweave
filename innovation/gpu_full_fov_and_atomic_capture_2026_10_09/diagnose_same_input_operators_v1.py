"""All192 tiles: same CPU tensor to each production GPU leaf, plus explicit pool auxiliary probes."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
os.environ['CUDA_VISIBLE_DEVICES']='0'
import sys,time,json,gzip,itertools,gc,traceback,subprocess,zlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from qualify_full_fov_gpu_cpu import (torch,original_cuda_initializer,read,sha,entry,bind,dump,resource_guard,
 development_cases,lattice,source_image,physical_mr,state_hash,array_sha,np,CheckpointedTaskUNet3D)
from mc_rc_3d_independent_replay_2026_10_07 import independent_starts,independent_weight,independent_native_resample
from mc_rc_3d_baseline_2026_10_07 import PATCH,tile_plan
from verify_final_lossless_v3 import numpy_native64
from torch.nn import functional as F

def cpu_reference_flow(x,state,probe):
 skips=[]
 def block(value,prefix):
  for conv,norm,relu in ((0,1,2),(3,4,5)):
   value=probe(prefix+f'.layers.{conv}',value,lambda q,p=prefix,c=conv:F.conv3d(q,state[p+f'.layers.{c}.weight'],padding=1))
   value=probe(prefix+f'.layers.{norm}',value,lambda q,p=prefix,n=norm:F.instance_norm(q,
    weight=state[p+f'.layers.{n}.weight'],bias=state[p+f'.layers.{n}.bias'],use_input_stats=True,eps=1e-5))
   value=probe(prefix+f'.layers.{relu}',value,lambda q:F.leaky_relu(q,negative_slope=.01))
  return value
 for level in range(4):
  if level:x=probe(f'auxiliary.max_pool.{level}',x,lambda q:F.max_pool3d(q,2,2))
  x=block(x,'encoders.'+str(level));skips.append(x)
 outputs=[]
 for depth,skip in enumerate(reversed(skips[:-1])):
  x=probe(f'ups.{depth}',x,lambda q,d=depth:F.conv_transpose3d(q,state[f'ups.{d}.weight'],state[f'ups.{d}.bias'],stride=2))
  x=block(torch.cat((x,skip),dim=1),'decoders.'+str(depth))
  outputs.append(probe(f'heads.{depth}',x,lambda q,d=depth:F.conv3d(q,state[f'heads.{d}.weight'],state[f'heads.{d}.bias'])))
 return probe('probability',outputs[-1],lambda q:q.sigmoid())

def verify_module_config(name,module):
 if name.startswith('encoders.') or name.startswith('decoders.'):
  index=int(name.rsplit('.',1)[-1])
  if index in (0,3):
   assert isinstance(module,torch.nn.Conv3d) and module.kernel_size==(3,3,3) and module.stride==(1,1,1)
   assert module.padding==(1,1,1) and module.dilation==(1,1,1) and module.groups==1 and module.bias is None
  elif index in (1,4):
   assert isinstance(module,torch.nn.InstanceNorm3d) and module.affine and not module.track_running_stats and module.eps==1e-5
  else:assert index in (2,5) and isinstance(module,torch.nn.LeakyReLU) and module.negative_slope==.01 and not module.inplace
 elif name.startswith('ups.'):
  assert isinstance(module,torch.nn.ConvTranspose3d) and module.kernel_size==(2,2,2) and module.stride==(2,2,2)
  assert module.padding==(0,0,0) and module.output_padding==(0,0,0) and module.dilation==(1,1,1) and module.groups==1
 else:
  assert name.startswith('heads.') and isinstance(module,torch.nn.Conv3d) and module.kernel_size==(1,1,1)
  assert module.padding==(0,0,0) and module.stride==(1,1,1) and module.groups==1

def main():
 os.environ['CUDA_VISIBLE_DEVICES']='0';torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
 started=time.perf_counter();out=HERE/'same_input_operators_attempt01';out.mkdir(exist_ok=False)
 r=dict(complete=False,status='preparing',errors=[],batches_completed=0,unique_tiles=0,primary_fields_completed=0,
  auxiliary_fields_completed=0,actual_CPU_operator_evaluations=0,actual_GPU_operator_evaluations=0,
  MRI_arrays_loaded=0,GT_arrays_loaded=0,parent_model_arrays_loaded=0,training_updates=0,medical_effect_scored=False,
  original_training_modified=False,other_PIDs_enumerated=False,other_PIDs_modified=False,validation_pixels_loaded=False,
  confirmation_patients_opened=False,lockedIXI_opened=False,full38_FOV_qualified=False,training_ready=False,
  publication_claim_confirmed=False,goal_status='active',layer_maxima={})
 def save():
  temp=out/'receipt.json.tmp';temp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temp.replace(out/'receipt.json')
 def guard(cuda=True):
  v=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
  prep=ROOT/'six_resolution_training_preparation_2026_10_09';prep_size=sum(p.stat().st_size for p in prep.rglob('*') if p.is_file())
  assert size<20_000_000 and prep_size<7_000_000
  assert v['workspace_free_bytes']-22_800_000-(20_000_000-size)-(7_000_000-prep_size)>=8_000_000_000
  assert time.perf_counter()-started<3600 and torch.get_num_threads()==torch.get_num_interop_threads()==1
  if cuda:
   free,total=torch.cuda.mem_get_info();peak=torch.cuda.max_memory_reserved();assert free>=4_000_000_000 and peak<=2_500_000_000
   v.update(GPU_free_bytes=free,GPU_peak_reserved_bytes=peak)
  return v
 save()
 try:
  r['resources_before']=guard(False)
  auditp=HERE/'layerwise_terminal_audit_attempt01/receipt.json';audit=read(auditp);assert audit['complete'] and not audit['errors']
  assert audit['all96_batches192_unique_tiles4704_layer_fields_verified']
  fp=HERE/'full_fov_attempt01/receipt.json';failed=read(fp);selected=failed['series'][-1];assert selected['case']==2 and not selected['numeric_gate_passed']
  for b in failed['source_bindings']:bind(b)
  oldp=HERE/'layerwise_all_tiles_attempt01/receipt.json';old=read(oldp);assert old['complete'] and not old['errors']
  oldjournal=bind(old['journal'])
  with gzip.open(oldjournal,'rt',encoding='utf-8') as f:oldrows=[json.loads(line) for line in f]
  assert len(oldrows)==96
  c,row=development_cases()[2];assert c['uid']==selected['uid'];image,_=source_image(c,row,'native_reference');grid=lattice(c);cache=physical_mr(image,grid);del image
  assert array_sha(cache)==selected['input_sha256'];r['MRI_arrays_loaded']=1
  pp=ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_2026-10-07.json';parent=next(a for a in read(pp)['arms'] if a['kind']=='native_reference')
  cpfile=ROOT/parent['checkpoint_path'];assert sha(cpfile)==parent['checkpoint_sha256'];cp=torch.load(cpfile,map_location='cpu',weights_only=True);state=cp['state_dict']
  assert cp['updates_completed']==19998 and state_hash(state)==cp['final_weights_sha256'];r['parent_model_arrays_loaded']=1
  locations,axes=tile_plan(cache.shape);iaxes=independent_starts(cache.shape,PATCH)
  assert axes==iaxes and locations==list(itertools.product(*iaxes)) and len(locations)==192
  sources={Path(__file__),HERE/'MATCHED_INPUT_OPERATOR_EXECUTION_V1.md',HERE/'MATCHED_INPUT_OPERATOR_PROTOCOL.md',fp,pp,cpfile,oldp,oldjournal,auditp}
  sources.update(bind(b) for b in failed['source_bindings']);sources.update(bind(b) for b in old['source_bindings'])
  frozen=dict(case=2,patient=c['patient'],uid=c['uid'],kind='native_reference',expected_unique_tiles=192,batch_size=2,
   expected_batches=96,expected_primary_fields=49,expected_auxiliary_fields=3,repeat_per_operator_device=2,
   axis_starts=axes,patch=PATCH,source_bindings=[entry(p) for p in sorted(sources)])
  dump(out/'frozen_config.json',frozen);r['source_bindings']=frozen['source_bindings'];save()
  query=subprocess.run(['nvidia-smi','--query-gpu=index,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=20)
  gpu=[list(map(int,v.split(','))) for v in query.stdout.strip().splitlines()];assert len(gpu)==1 and gpu[0][0]==0 and gpu[0][1]>=8192
  r['GPU_aggregate_before']=gpu;os.environ['CUDA_VISIBLE_DEVICES']='0';torch.cuda._lazy_init=original_cuda_initializer;assert torch.cuda.is_available()
  free,total=torch.cuda.mem_get_info();torch.cuda.set_per_process_memory_fraction(min(.1,2_400_000_000/total))
  torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
  model=CheckpointedTaskUNet3D();model.load_state_dict(state);model.eval();model.to('cuda:0')
  leaf_types=(torch.nn.Conv3d,torch.nn.ConvTranspose3d,torch.nn.InstanceNorm3d,torch.nn.LeakyReLU)
  modules={name:module for name,module in model.named_modules() if isinstance(module,leaf_types)};assert len(modules)==48
  for name,module in modules.items():verify_module_config(name,module)
  weight=independent_weight(PATCH);numerator=np.zeros(cache.shape,np.float64);denominator=np.zeros_like(numerator)
  costs=dict(CPU_operator_repeats=0.,GPU_transfer_and_operator_repeats=0.,operator_comparison_and_hashing=0.,CPU_fullFOV_mapping=0.)
  journal=out/'operators.jsonl.gz'
  with journal.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',compresslevel=6,mtime=0) as stream,torch.inference_mode():
   for batch,at in enumerate(range(0,192,2)):
    guard();starts=locations[at:at+2];slices=[tuple(slice(s,s+n) for s,n in zip(start,PATCH)) for start in starts]
    checks=[]
    def probe(name,inputs,cpu_operation):
     guard();assert inputs.dtype==torch.float32 and inputs.device.type=='cpu' and not inputs.requires_grad
     tick=time.perf_counter();reference=cpu_operation(inputs);repeat=cpu_operation(inputs)
     cpu_repeat=torch.equal(reference,repeat);assert cpu_repeat;del repeat
     costs['CPU_operator_repeats']+=time.perf_counter()-tick
     tick=time.perf_counter();gx=inputs.to('cuda:0');transferred=gx.cpu();assert torch.equal(inputs,transferred);del transferred
     if name=='probability':gpu_operation=lambda q:q.sigmoid()
     elif name.startswith('auxiliary.max_pool.'):gpu_operation=lambda q:F.max_pool3d(q,2,2)
     else:gpu_operation=modules[name]
     candidate=gpu_operation(gx).cpu();grepeat=gpu_operation(gx).cpu();gpu_repeat=torch.equal(candidate,grepeat);assert gpu_repeat
     del grepeat,gx;costs['GPU_transfer_and_operator_repeats']+=time.perf_counter()-tick
     tick=time.perf_counter();assert reference.dtype==candidate.dtype==torch.float32 and reference.shape==candidate.shape
     assert torch.isfinite(reference).all() and torch.isfinite(candidate).all()
     diff=(reference-candidate).abs();index=int(diff.reshape(-1).argmax());maximum=float(diff.max())
     check=dict(name=name,role='auxiliary_pool' if name.startswith('auxiliary.') else 'primary_leaf_or_probability',
      shape=list(reference.shape),elements=reference.numel(),CPU_input_sha256=array_sha(inputs.numpy()),
      CPU_output_sha256=array_sha(reference.numpy()),GPU_output_sha256=array_sha(candidate.numpy()),
      CPU_operator_repeat_bitwise_equal=cpu_repeat,GPU_operator_repeat_bitwise_equal=gpu_repeat,
      GPU_input_transfer_bitwise_equal=True,max_absolute_error=maximum,mean_absolute_error=float(diff.mean()),
      CPU_absolute_max=float(reference.abs().max()),GPU_absolute_max=float(candidate.abs().max()),
      maximum_error_index=list(map(int,np.unravel_index(index,tuple(diff.shape)))),
      maximum_error_CPU_value=float(reference.reshape(-1)[index]),maximum_error_GPU_value=float(candidate.reshape(-1)[index]))
     checks.append(check)
     previous=r['layer_maxima'].get(name)
     if previous is None or maximum>previous['max_absolute_error']:
      r['layer_maxima'][name]=dict(check,batch=batch,tile_starts=[list(v) for v in starts])
     r['actual_CPU_operator_evaluations']+=2;r['actual_GPU_operator_evaluations']+=2
     costs['operator_comparison_and_hashing']+=time.perf_counter()-tick;del candidate,diff;guard();return reference
    x=torch.from_numpy(np.stack([cache[sl] for sl in slices])[:,None]);prob=cpu_reference_flow(x,state,probe)
    assert len(checks)==52 and len({v['name'] for v in checks})==52
    ph=array_sha(prob.numpy());assert oldrows[batch]['batch']==batch and oldrows[batch]['tile_starts']==[list(v) for v in starts]
    assert ph==oldrows[batch]['CPU_batch_probability_sha256']
    for sl,pvalue in zip(slices,prob.numpy()[:,0]):numerator[sl]+=pvalue*weight;denominator[sl]+=weight
    record=dict(batch=batch,tile_starts=starts,primary_fields=49,auxiliary_fields=3,CPU_batch_probability_sha256=ph,
     CPU_batch_original_probability_sha_reproduced=True,operator_checks=checks)
    stream.write((json.dumps(record,separators=(',',':'))+'\n').encode());stream.flush(zlib.Z_SYNC_FLUSH)
    r['batches_completed']+=1;r['unique_tiles']+=2;r['primary_fields_completed']+=49;r['auxiliary_fields_completed']+=3
    if batch%8==0 or batch==95:
     raw.flush();save();print(json.dumps(dict(batches_completed=r['batches_completed'],expected_batches=96,elapsed_seconds=time.perf_counter()-started)),flush=True)
    del x,prob,checks;gc.collect();guard();assert journal.stat().st_size<3_000_000
  tick=time.perf_counter();assert denominator.min()>0
  crop=tuple(slice(int(lo),int(lo)+int(n)) for (lo,hi),n in zip(grid['padding'],grid['unpadded_shape_zrc']))
  physical=np.ascontiguousarray((numerator/denominator)[crop],np.float32);native=independent_native_resample(physical,c['native_shape'])
  assert array_sha(native)==selected['CPU_probability_sha256']
  coordinate_ref=F.interpolate(torch.from_numpy(physical.astype(np.float64))[None,None],
   size=(c['native_shape'][2],c['native_shape'][0],c['native_shape'][1]),mode='trilinear',align_corners=False)[0,0].numpy().transpose(1,2,0)
  independent=numpy_native64(physical,c['native_shape']);ce=float(np.max(np.abs(coordinate_ref-independent)))
  cb=int(np.count_nonzero((coordinate_ref>=.5)!=(independent>=.5)));assert ce<=3e-12 and cb==0
  costs['CPU_fullFOV_mapping']=time.perf_counter()-tick
  assert state_hash(model.state_dict())==cp['final_weights_sha256'] and array_sha(cache)==selected['input_sha256']
  assert r['batches_completed']==96 and r['unique_tiles']==192 and r['primary_fields_completed']==4704 and r['auxiliary_fields_completed']==288
  assert r['actual_CPU_operator_evaluations']==r['actual_GPU_operator_evaluations']==9984
  for b in r['source_bindings']:bind(b)
  r.update(complete=True,status='completed',CPU_original_all96_batch_probability_hashes_reproduced=True,
   CPU_original_fullFOV_probability_sha256=array_sha(native),CPU_original_fullFOV_hash_reproduced=True,
   same_CPU_input_GPU_native_operators_probed=True,all52_same_device_operator_repeats_bitwise_equal=True,
   new_GPU_whole_model_FOV_run=False,coordinate_error=ce,coordinate_binary_disagreements=cb,
   journal=entry(journal),frozen_config_sha256=sha(out/'frozen_config.json'),cost_seconds=costs,resources_after=guard())
 except Exception as e:r.update(status='failed',traceback=traceback.format_exc());r['errors'].append(type(e).__name__+': '+str(e))
 r['elapsed_seconds']=time.perf_counter()-started;save();print(json.dumps({k:r.get(k) for k in ['complete','status','errors','batches_completed','elapsed_seconds']}),flush=True)
 return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
