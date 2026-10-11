"""Six cross-statistics CPU forwards; image arrays and diagonal baselines fixed."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import json,math,sys,time,traceback
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import nibabel as nib
from vs_seg_task_cpu_support import ROOT,resource_gate,load_model
from vs_seg_full_volume_cohort import cases_from_sources
from vs_seg_full_volume_runtime import decode_source,reconstruct,array_sha,sha,load_tuple_inferer
from vs_seg_selection_sensitivity import completion_gate,load_verified_records
from vs_seg_full_volume_metrics import task_metrics,outside_reference_band,overlap
from remind_native_t2_ixi_pair import prepared
from vs_seg_resampling_order_cpu import post_resize
from verify_anchor_bandwidth_task_cpu import verify_saved
OUT=ROOT/'experiments/task_stats_swap_cpu_pilot'
ROSTER=['VS-SEG-202','VS-SEG-203','VS-SEG-204']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')
def emit(row):
 print(json.dumps(row,ensure_ascii=False),flush=True)
 with (OUT/'stdout.jsonl').open('a',encoding='utf-8') as s:s.write(json.dumps(row,ensure_ascii=False)+'\n')
def main():
 sys.stdout.reconfigure(encoding='utf-8');resource_gate();OUT.mkdir(exist_ok=False)
 postdir=ROOT/'experiments/vs_seg_post_resize_task_cpu';p=read(postdir/'attempt_01.json');q=read(postdir/'independent_all_tasks_and_estimates.json');assert p['complete'] and q['complete'] and not p['errors'] and not q['errors'] and q['result_sha256']==sha(postdir/'attempt_01.json')
 gate,original=completion_gate();assert gate['allowed'];coverage=read(ROOT/'experiments/vs_seg_full_volume_coverage/attempt_01.json');old,provenance=load_verified_records(original['main_roster'],{x['patient']:x for x in coverage['patients']});cases={x['patient']:x for x in cases_from_sources()};postrecords={x:read(postdir/(x+'.json')) for x in ROSTER}
 paths={Path(__file__),ROOT/'TASK_STATS_SWAP_CPU_PILOT_PLAN_2026-10-03.md',ROOT/'experiments/verify_anchor_bandwidth_task_cpu.py',ROOT/'experiments/vs_seg_full_volume_runtime.py',ROOT/'experiments/vs_seg_full_volume_metrics.py',ROOT/'experiments/vs_seg_task_cpu_support.py',ROOT/'experiments/vs_seg_resampling_order_cpu.py',postdir/'attempt_01.json',postdir/'independent_all_tasks_and_estimates.json'}
 for e in original['files']:paths.add(ROOT.parent/e['path'])
 for x in provenance:
  if any(patient in x['file'] for patient in ROSTER):paths.add(ROOT/x['file'])
 for patient in ROSTER:paths.add(postdir/(patient+'.json'))
 contract=dict(created_utc=datetime.now(timezone.utc).isoformat(),roster=ROSTER,conditions=['raw_poststats','post_rawstats'],new_neural_forwards_planned=6,scientific_confirmation_patients=0,deployable_sr_method=False,files=[dict(path=p.relative_to(ROOT.parent).as_posix(),sha256=sha(p)) for p in sorted(paths)])
 write(OUT/'run_contract.json',contract);result=dict(created_utc=datetime.now(timezone.utc).isoformat(),run_contract_sha256=sha(OUT/'run_contract.json'),complete=False,active_stage='loading_cpu_model',patients=[],errors=[],gpu_used=False,new_neural_forwards=0,publication_claim_confirmed=False,scientific_confirmation_patients=0);write(OUT/'attempt_01.json',result)
 try:
  model,runtime=load_model();infer=load_tuple_inferer();import torch
  from monai.transforms import NormalizeIntensity
  allrecords={}
  for patient in ROSTER:
   resource_gate();native,affine,refs=decode_source(cases[patient]);prep=prepared(native[:,:,::4]);obs=list(range(0,native.shape[2],4));targets=[z for z in range(1,obs[-1]) if z%4];raw=reconstruct('raw_pchip',native,prep,{});post,_=post_resize(raw,prep,targets)
   assert array_sha(raw)==old[patient]['raw_pchip']['reconstructed_array_sha256'] and array_sha(post)==postrecords[patient]['reconstructed_array_sha256'];assert np.array_equal(raw[:,:,obs],post[:,:,obs]) and np.array_equal(raw[:,:,obs[-1]+1:],post[:,:,obs[-1]+1:])
   orientation=nib.orientations.ornt_transform(nib.orientations.io_orientation(affine),nib.orientations.axcodes2ornt('RAS'));can_affine=affine@nib.orientations.inv_ornt_aff(orientation,native.shape);spacing=nib.affines.voxel_sizes(can_affine);rasrefs={k:nib.orientations.apply_orientation(v,orientation) for k,v in refs.items()};domain_indices={'observed_anchors':obs,'supported_missing':targets,'unsupported_tail':list(range(obs[-1]+1,native.shape[2]))};domains={}
   for name,zs in domain_indices.items():mask=np.zeros(native.shape,dtype=bool);mask[:,:,zs]=True;domains[name]=nib.orientations.apply_orientation(mask,orientation)
   slab=domains['observed_anchors']|domains['supported_missing'];assert np.all(sum(m.astype(np.uint8) for m in domains.values())==1)
   images={name:np.ascontiguousarray(nib.orientations.apply_orientation(a,orientation)) for name,a in [('raw',raw),('post',post)]};stats={};own={}
   for name,arr in images.items():
    mu=np.mean(arr.ravel());sd=np.std(arr.ravel());sd=np.float32(1) if sd==0 else sd;stats[name]=(mu,sd);own[name]=NormalizeIntensity()(arr[None].copy());assert np.array_equal(own[name],NormalizeIntensity(subtrahend=mu,divisor=sd)(arr[None].copy()))
   diagonals={}
   for name,path in [('raw',ROOT/'experiments/vs_seg_full_volume_cohort/patients'/patient/'raw_pchip_attempt_01.json'),('post',postdir/(patient+'.json'))]:
    x=read(path)
    with np.load(ROOT/x['prediction_file']) as predfile:prediction=predfile['prediction_ras']
    diagonals[name]=dict(record_file=path.relative_to(ROOT).as_posix(),record_sha256=sha(path),normalized_input_array_sha256=array_sha(own[name]),normalization_mean=float(stats[name][0]),normalization_std=float(stats[name][1]),task_metrics=x['task_metrics'],domain_confusion={ref:{d:overlap(prediction,v,m) for d,m in domains.items()} for ref,v in rasrefs.items()})
   records={}
   for image_name,stats_name in [('raw','post'),('post','raw')]:
    resource=resource_gate();started=time.perf_counter();name=image_name+'_'+stats_name+'stats';mu,sd=stats[stats_name];normalized=NormalizeIntensity(subtrahend=mu,divisor=sd)(images[image_name][None].copy());inputs=torch.from_numpy(np.ascontiguousarray(normalized)).unsqueeze(0)
    with torch.inference_mode():logits=infer.sliding_window_inference(inputs,roi_size=(384,384,64),sw_batch_size=1,predictor=lambda x:model(x)[0],mode='gaussian')
    assert bool(torch.isfinite(logits).all()) and not torch.cuda.is_initialized();pred=logits.argmax(dim=1)[0].numpy().astype(bool)
    record=dict(patient=patient,condition=name,complete=True,runtime=runtime,resource_gate=resource,native_array_sha256=array_sha(native),reconstructed_array_sha256=array_sha(raw if image_name=='raw' else post),normalized_input_array_sha256=array_sha(normalized),image_baseline=image_name,statistics_baseline=stats_name,normalization_mean=float(mu),normalization_std=float(sd),all_source_stats={k:dict(mean=float(v[0]),std=float(v[1])) for k,v in stats.items()},diagonals=diagonals,changes_observed_anchors=False,deployable_sr_method=False,cuda_initialized=torch.cuda.is_initialized(),task_metrics={k:task_metrics(pred,v,spacing,slab,outside_reference_band(v,spacing)) for k,v in rasrefs.items()},domain_confusion={ref:{d:overlap(pred,v,m) for d,m in domains.items()} for ref,v in rasrefs.items()},observed_indices=obs,unsupported_terminal_indices=domain_indices['unsupported_tail'])
    pp=OUT/(patient+'_'+name+'_prediction.npz')
    with pp.open('xb') as stream:np.savez_compressed(stream,prediction_ras=pred,affine=can_affine)
    record.update(prediction_file=pp.relative_to(ROOT).as_posix(),prediction_sha256=sha(pp),prediction_array_sha256=array_sha(pred),seconds=time.perf_counter()-started);path=OUT/(patient+'_'+name+'.json');write(path,record)
    # Existing independent saved-metric code; only output directory is changed process-locally.
    import verify_anchor_bandwidth_task_cpu as verification_module
    verification_module.OUT=OUT;vp=verify_saved(cases[patient],record,path)
    result['patients'].append(dict(patient=patient,condition=name,file=path.relative_to(ROOT).as_posix(),sha256=sha(path),verification_file=vp.relative_to(ROOT).as_posix(),verification_sha256=sha(vp)));result['new_neural_forwards']+=1;result['active_stage']='cpu_cross_stats_and_saved_output_verification';write(OUT/'attempt_01.json',result);records[name]=record;emit(dict(patient=patient,condition=name,completed_conditions=len(result['patients']),saved_prediction_verified=True,seconds=record['seconds']));del logits,inputs,normalized,pred
   allrecords[patient]=records;del native,raw,post,images,own,refs,rasrefs,domains,slab,prediction
  assert len(result['patients'])==6;analysis=[]
  names=['post_rawstats-post_poststats','raw_poststats-raw_rawstats','post_rawstats-raw_rawstats','post_poststats-raw_poststats','normalization_image_interaction']
  for ref in ('original_json','rtstruct'):
   for domain in ('full','observed_anchor_slab','exclude_reference_boundary_1mm'):
    for comparison in names:
     values=[];undefined=[]
     for patient in ROSTER:
      rows=allrecords[patient];v={'raw_rawstats':old[patient]['raw_pchip']['task_metrics'][ref][domain]['dice'],'post_poststats':postrecords[patient]['task_metrics'][ref][domain]['dice'],**{k:x['task_metrics'][ref][domain]['dice'] for k,x in rows.items()}}
      if comparison=='normalization_image_interaction':selected=list(v.values());delta=(v['post_poststats']-v['post_rawstats'])-(v['raw_poststats']-v['raw_rawstats']) if all(x is not None for x in selected) else None
      else:left,right=comparison.split('-');delta=v[left]-v[right] if v[left] is not None and v[right] is not None else None
      if delta is None:undefined.append(patient)
      else:values.append(dict(patient=patient,difference=delta))
     analysis.append(dict(reference=ref,domain=domain,comparison=comparison,original_denominator=3,defined_n=len(values),undefined_patients=undefined,patient_differences=values,mean=math.fsum(x['difference'] for x in values)/len(values) if values else None,descriptive_development_only=True))
  result.update(complete=True,active_stage='complete',analysis=analysis,new_neural_forwards=6)
 except Exception as exc:result['errors'].append(type(exc).__name__+': '+str(exc));result['traceback']=traceback.format_exc();result['active_stage']='failed'
 result['finished_utc']=datetime.now(timezone.utc).isoformat();write(OUT/'attempt_01.json',result);emit({k:result.get(k) for k in ('complete','active_stage','errors','new_neural_forwards')})
 if not result['complete']:raise SystemExit(1)
if __name__=='__main__':main()
