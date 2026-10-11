"""Three frozen developers x four anchors-only task controls on CPU."""
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
from vs_seg_full_volume_metrics import task_metrics,outside_reference_band
from remind_native_t2_ixi_pair import prepared
from vs_seg_resampling_order_cpu import post_resize
from verify_anchor_bandwidth_task_cpu import verify_saved
OUT=ROOT/'experiments/anchor_bandwidth_task_cpu_pilot'
ROSTER=['VS-SEG-202','VS-SEG-203','VS-SEG-204']
CONDITIONS=['raw_anchor_own','raw_anchor_fixed','post_anchor_own','post_anchor_fixed']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')
def main():
 sys.stdout.reconfigure(encoding='utf-8');resource_gate();postdir=ROOT/'experiments/vs_seg_post_resize_task_cpu';post=read(postdir/'attempt_01.json');postproof=read(postdir/'independent_all_tasks_and_estimates.json');check=post['complete'] and postproof['complete'] and not post['errors'] and not postproof['errors'] and len(post['patients'])==45 and len(postproof['endpoints'])==18 and postproof['result_sha256']==sha(postdir/'attempt_01.json');assert check,'Whole post task completion required';phase=ROOT/'experiments/anchor_bandwidth_diagnostic_cpu';normal=ROOT/'experiments/anchor_normalization_control_cpu_attempt_02';assert read(phase/'independent_gradient_and_identities.json')['complete'] and read(normal/'attempt_01.json')['all_six_fixed_stats_missing_and_tail_bitwise_equal'];gate,original=completion_gate();assert gate['allowed'];coverage=read(ROOT/'experiments/vs_seg_full_volume_coverage/attempt_01.json');old,provenance=load_verified_records(original['main_roster'],{x['patient']:x for x in coverage['patients']});cases={x['patient']:x for x in cases_from_sources()};postrecords={e['patient']:read(ROOT/e['record_file']) for e in post['patients']};OUT.mkdir(exist_ok=False)
 paths={Path(__file__),ROOT/'ANCHOR_BANDWIDTH_TASK_CPU_PILOT_PLAN_2026-10-03.md',ROOT/'experiments/verify_anchor_bandwidth_task_cpu.py',ROOT/'experiments/verify_vs_seg_post_resize_task_cpu.py',ROOT/'experiments/vs_seg_full_volume_runtime.py',ROOT/'experiments/vs_seg_full_volume_metrics.py',ROOT/'experiments/vs_seg_task_cpu_support.py',ROOT/'experiments/vs_seg_resampling_order_cpu.py',phase/'attempt_01.json',phase/'independent_gradient_and_identities.json',normal/'attempt_01.json',postdir/'attempt_01.json',postdir/'independent_all_tasks_and_estimates.json',postdir/'run_contract.json'}
 for f in original['files']:paths.add(ROOT.parent/f['path'])
 for e in post['patients']:
  if e['patient'] in ROSTER:paths.add(ROOT/e['record_file'])
 contract=dict(created_utc=datetime.now(timezone.utc).isoformat(),roster=ROSTER,conditions=CONDITIONS,new_neural_forwards_planned=12,new_method_confirmation_patients=0,deployable_sr_method=False,files=[dict(path=p.relative_to(ROOT.parent).as_posix(),sha256=sha(p)) for p in sorted(paths)])
 write(OUT/'run_contract.json',contract);result=dict(created_utc=datetime.now(timezone.utc).isoformat(),run_contract_sha256=sha(OUT/'run_contract.json'),complete=False,active_stage='loading_cpu_model',patients=[],errors=[],gpu_used=False,new_method_confirmation_patients=0,publication_claim_confirmed=False);write(OUT/'attempt_01.json',result)
 try:
  model,runtime=load_model();infer=load_tuple_inferer();import torch
  from monai.transforms import NormalizeIntensity
  allrecords={}
  for patient in ROSTER:
   resource_gate();native,affine,refs=decode_source(cases[patient]);prep=prepared(native[:,:,::4]);obs=list(range(0,native.shape[2],4));targets=[z for z in range(1,obs[-1]) if z%4];raw=reconstruct('raw_pchip',native,prep,{});mixed,_=post_resize(raw,prep,targets);a=read(ROOT/'experiments/vs_seg_resampling_order_cpu'/f'{patient}.json');assert array_sha(raw)==a['conditions']['raw_pchip']['array_sha256'] and array_sha(mixed)==a['conditions']['post_resize_pchip']['array_sha256'];orientation=nib.orientations.ornt_transform(nib.orientations.io_orientation(affine),nib.orientations.axcodes2ornt('RAS'));can_affine=affine@nib.orientations.inv_ornt_aff(orientation,native.shape);spacing=nib.affines.voxel_sizes(can_affine);slab=np.zeros(native.shape,dtype=bool);slab[:,:,:obs[-1]+1]=True;slab=nib.orientations.apply_orientation(slab,orientation);miss=np.zeros(native.shape,dtype=bool);miss[:,:,targets]=True;miss=nib.orientations.apply_orientation(miss,orientation);rasrefs={k:nib.orientations.apply_orientation(v,orientation) for k,v in refs.items()};records={}
   for basename,base in [('raw',raw),('post',mixed)]:
    changed,_=post_resize(base,prep,obs);assert np.array_equal(changed[:,:,targets],base[:,:,targets]) and np.array_equal(changed[:,:,obs[-1]+1:],base[:,:,obs[-1]+1:]);br=np.ascontiguousarray(nib.orientations.apply_orientation(base,orientation));ar=np.ascontiguousarray(nib.orientations.apply_orientation(changed,orientation));selection=br[None].copy();selected=selection[np.ones(selection.shape,dtype=np.bool_)];mu=np.mean(selected);sigma=np.std(selected);sigma=np.float32(1) if sigma==0 else sigma;base_norm=NormalizeIntensity()(br[None].copy())[0]
    for normname in ('own','fixed'):
     resource_gate();started=time.perf_counter();name=basename+'_anchor_'+normname;normalized=NormalizeIntensity(subtrahend=mu,divisor=sigma)(ar[None].copy()) if normname=='fixed' else NormalizeIntensity()(ar[None].copy());missing_same=np.array_equal(normalized[0][miss],base_norm[miss]);assert normname!='fixed' or missing_same;inputs=torch.from_numpy(np.ascontiguousarray(normalized)).unsqueeze(0)
     with torch.inference_mode():logits=infer.sliding_window_inference(inputs,roi_size=(384,384,64),sw_batch_size=1,predictor=lambda x:model(x)[0],mode='gaussian')
     assert bool(torch.isfinite(logits).all()) and not torch.cuda.is_initialized();pred=logits.argmax(dim=1)[0].numpy().astype(bool);record=dict(patient=patient,condition=name,normalization=normname,baseline=basename,complete=True,runtime=runtime,native_array_sha256=array_sha(native),reconstructed_array_sha256=array_sha(changed),normalized_input_array_sha256=array_sha(normalized),normalization_baseline_mean=float(mu),normalization_baseline_std=float(sigma),missing_network_input_bitwise_equal_to_baseline=missing_same,changes_observed_anchors=True,deployable_sr_method=False,cuda_initialized=torch.cuda.is_initialized(),task_metrics={k:task_metrics(pred,v,spacing,slab,outside_reference_band(v,spacing)) for k,v in rasrefs.items()},observed_indices=obs,unsupported_terminal_indices=list(range(obs[-1]+1,native.shape[2])))
     pp=OUT/(patient+'_'+name+'_prediction.npz')
     with pp.open('xb') as stream:np.savez_compressed(stream,prediction_ras=pred,affine=can_affine)
     record.update(prediction_file=pp.relative_to(ROOT).as_posix(),prediction_sha256=sha(pp),prediction_array_sha256=array_sha(pred),seconds=time.perf_counter()-started);path=OUT/(patient+'_'+name+'.json');write(path,record);vp=verify_saved(cases[patient],record,path);entry=dict(patient=patient,condition=name,file=path.relative_to(ROOT).as_posix(),sha256=sha(path),verification_file=vp.relative_to(ROOT).as_posix(),verification_sha256=sha(vp));result['patients'].append(entry);result['active_stage']='cpu_inference_and_saved_output_verification';write(OUT/'attempt_01.json',result);records[name]=record;print(json.dumps(dict(patient=patient,condition=name,completed_conditions=len(result['patients']),saved_output_verified=True)),flush=True);del logits,inputs,normalized,pred
   allrecords[patient]=records;del native,raw,mixed,changed,br,ar,selection,selected,base_norm,refs,rasrefs,slab,miss
  assert len(result['patients'])==12;analysis=[]
  for ref in ('original_json','rtstruct'):
   for domain in ('full','observed_anchor_slab','exclude_reference_boundary_1mm'):
    for left,right in [('raw_anchor_own','raw'),('raw_anchor_fixed','raw'),('post_anchor_own','post'),('post_anchor_fixed','post'),('raw_anchor_own','raw_anchor_fixed'),('post_anchor_own','post_anchor_fixed')]:
     values=[];undefined=[]
     for p in ROSTER:
      a=allrecords[p][left]['task_metrics'][ref][domain]['dice'];b=(old[p]['raw_pchip']['task_metrics'][ref][domain]['dice'] if right=='raw' else postrecords[p]['task_metrics'][ref][domain]['dice'] if right=='post' else allrecords[p][right]['task_metrics'][ref][domain]['dice'])
      if a is None or b is None:undefined.append(p)
      else:values.append(dict(patient=p,difference=a-b))
     analysis.append(dict(reference=ref,domain=domain,comparison=left+'-'+right,original_denominator=3,defined_n=len(values),undefined_patients=undefined,patient_differences=values,mean=math.fsum(v['difference'] for v in values)/len(values) if values else None,descriptive_development_only=True))
  result.update(complete=True,active_stage='complete',analysis=analysis,new_neural_forwards=12)
 except Exception as exc:result['errors'].append(type(exc).__name__+': '+str(exc));result['traceback']=traceback.format_exc();result['active_stage']='failed'
 result['finished_utc']=datetime.now(timezone.utc).isoformat();write(OUT/'attempt_01.json',result);print(json.dumps({k:result.get(k) for k in ('complete','active_stage','errors','new_neural_forwards')}),flush=True)
 if not result['complete']:raise SystemExit(1)
if __name__=='__main__':main()
