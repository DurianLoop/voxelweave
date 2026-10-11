"""Raw ZIP replay and disk-dilation verification for the corrected 16-series study."""
from __future__ import annotations
import json,os,sys,zipfile
from datetime import datetime,timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'): os.environ[key]='1'
import nibabel as nib
import numpy as np
import pydicom
import torch
from vs_seg_task_cpu_support import resource_gate,load_model
from vs_seg_full_volume_runtime import sha,array_sha,inference,load_tuple_inferer
from verify_mc_rc_frozen_predicted_region_cpu import raw_truth,explicit_boundary,hermite_display
from mc_rc_frozen_predicted_region_cpu import display_from_anchors
from verify_mc_rc_observed_region_propagation import disk_dilation,measure,derived
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/mc_rc_native_competence_cpu'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def independent_native(case):
 records=[]
 with zipfile.ZipFile(ROOT/case['mr_zip_file']) as archive:
  for member in archive.infolist():
   if member.is_dir() or not member.filename.lower().endswith('.dcm'): continue
   with archive.open(member) as f: header=pydicom.dcmread(f,stop_before_pixels=True)
   records.append((member.filename,header))
  o=np.asarray(records[0][1].ImageOrientationPatient,dtype=float);normal=np.cross(o[:3],o[3:]);records.sort(key=lambda t:float(np.asarray(t[1].ImagePositionPatient,dtype=float)@normal))
  if [x[0] for x in records]!=case['ordered_zip_members']: raise ValueError('Independent native raw ordering differs')
  volume=np.empty((int(records[0][1].Rows),int(records[0][1].Columns),len(records)),dtype=np.float32);sops=[]
  if list(volume.shape)!=case['native_shape']: raise ValueError('Independent native raw shape differs')
  for z,(name,header) in enumerate(records):
   with archive.open(name) as f: ds=pydicom.dcmread(f)
   if str(ds.PatientID)!=case['patient'] or str(ds.SeriesInstanceUID)!=case['uid'] or str(ds.StudyInstanceUID)!=case['study_uid'] or str(ds.SOPInstanceUID)!=str(header.SOPInstanceUID) or str(ds.PhotometricInterpretation)!='MONOCHROME2': raise ValueError('Independent native raw identity differs')
   volume[:,:,z]=ds.pixel_array.astype(np.float32)*float(ds.get('RescaleSlope',1))+float(ds.get('RescaleIntercept',0));sops.append(str(ds.SOPInstanceUID))
 if not np.isfinite(volume).all(): raise ValueError('Independent native finite gate failed')
 return volume,sops
def explicit_native_prediction(model,inferer,volume,case):
 orientation=nib.orientations.ornt_transform(nib.orientations.io_orientation(np.asarray(case['affine_rcz_ras'])),nib.orientations.axcodes2ornt('RAS'));ras=inference(model,inferer,volume,orientation)
 matrix=np.rint(nib.orientations.inv_ornt_aff(orientation,case['native_shape'])).astype(int);coords=np.array(np.nonzero(ras));out=np.zeros(case['native_shape'],dtype=bool);out[tuple(matrix[:3,:3]@coords+matrix[:3,3,None])]=True
 return out
def competence(pred,ref,planes):
 pp,tt,tp=0,0,0
 for z in planes:
  p,t=pred[:,:,z],ref[:,:,z];pp+=int(np.count_nonzero(p));tt+=int(np.count_nonzero(t));tp+=int(np.count_nonzero(p&t))
 return dict(predicted_voxels=pp,truth_voxels=tt,true_positive_voxels=tp,dice=2*tp/(pp+tt) if pp+tt else None,recall=tp/tt if tt else None,precision=tp/pp if pp else None)
def main():
 sys.stdout.reconfigure(encoding='utf-8');resource_gate();result=read(OUT/'attempt_01.json');contract=read(OUT/'run_contract.json');path=OUT/'independent_native_model_and_roi_replay.json'
 if path.exists(): raise ValueError('Retain successful proof; no blind overwrite')
 if not result['complete'] or result['errors'] or len(result['series'])!=16: raise ValueError('Wait for complete16; no selected success subset verification')
 errors=[];records=[];deltas={};by={r['uid']:r for r in result['series']}
 def check(ok,why):
  if not ok: errors.append(why)
 def equal(a,b,why):
  check(a.keys()==b.keys(),'Schema differs '+why)
  for k in a.keys()&b.keys(): check(a[k]==b[k] if a[k] is None or b[k] is None else abs(a[k]-b[k])<=1e-12,'Metric differs '+why+' '+k)
 for item in contract['files']: check(sha(ROOT/item['path'])==item['sha256'],'Frozen input mutated '+item['path'])
 check(result['run_contract_sha256']==sha(OUT/'run_contract.json'),'Native contract lineage differs')
 model,runtime=load_model();inferer=load_tuple_inferer();forward_count=0
 for case in contract['cases']:
  resource_gate();stored=by[case['uid']];uid=case['uid'];volume,sops=independent_native(case);anchors=volume[:,:,::4].copy()
  check(array_sha(volume)==stored['native_array_sha256'] and sops==stored['native_decoded_sop_uids'],'Independent native all-plane decode differs '+uid)
  check(array_sha(anchors)==stored['observed_array_sha256'] and sops[::4]==stored['observed_sop_uids'],'Independent genuine anchor decode differs '+uid)
  native=explicit_native_prediction(model,inferer,volume,case);forward_count+=1;del volume
  with np.load(ROOT/stored['native_prediction_file']) as pack: native_equal=bool(np.array_equal(native,pack['prediction_native']));check(native_equal,'Independent native fresh forward/explicit coordinates differs '+uid)
  check(array_sha(native)==stored['native_prediction_array_sha256'] and sha(ROOT/stored['native_prediction_file'])==stored['native_prediction_sha256'],'Native prediction hash differs '+uid)
  with np.load(ROOT/stored['sparse_prediction_file']) as pack: sparse=pack['prediction_native'].copy()
  check(array_sha(sparse)==stored['sparse_prediction_array_sha256'] and sha(ROOT/stored['sparse_prediction_file'])==stored['sparse_prediction_sha256'],'Sparse prediction hash differs '+uid)
  display=display_from_anchors(anchors,case['native_shape'][2]);hermite=hermite_display(anchors,case['native_shape'][2]);difference=float(np.max(abs(display-hermite)));tolerance=max(1e-4,float(anchors.max()-anchors.min())*5e-7)
  check(difference<=tolerance and array_sha(display)==stored['raw_pchip_display_array_sha256'],'Independent observed-only Hermite input differs '+uid);del hermite,anchors
  if not case['in_old_frozen_15']:
   replay=explicit_native_prediction(model,inferer,display,case);forward_count+=1;check(np.array_equal(sparse,replay),'Omitted-source sparse fresh replay differs '+uid);del replay
  del display
  ref=raw_truth(case,dict(grid=dict(dicom_rcz_from_label_xyz=case['dicom_rcz_from_label_xyz'])));edge=explicit_boundary(ref);n=ref.shape[2];targets=[z for z in range(1,(n-1)//4*4) if z%4]
  all_comp={name:{region:competence(pred,ref,planes) for region,planes in [('full',range(n)),('observed',range(0,n,4)),('missing',targets)]} for name,pred in [('native',native),('sparse',sparse)]}
  for name in all_comp:
   for region in all_comp[name]: equal(all_comp[name][region],stored['task_competence'][name][region],uid+' '+name+' '+region)
  preds={'native_anchor_union_2mm':native,'sparse_anchor_union_2mm':sparse}
  if not case['in_old_frozen_15']: preds['ideal_anchor_union_2mm']=ref
  for name,pred in preds.items():
   expected=stored['roi'][name] if name in stored['roi'] else stored[name];sums={k:0 for k in expected['target_records'][0]['counts']};fg,boundary=0,0
   for index,z in enumerate(targets):
    left=z//4*4;mask=disk_dilation(pred[:,:,left]|pred[:,:,left+4],case['native_spacing_rcz_mm'][:2],2.);counts=measure(mask,ref[:,:,z],edge[:,:,z]);record=expected['target_records'][index]
    check(record['z']==z,'Target support differs '+uid);equal(counts,record['counts'],uid+' '+name+' z'+str(z))
    for k,v in counts.items(): sums[k]+=v
    fg+=int(ref[:,:,z].sum());boundary+=int(edge[:,:,z].sum())
   metrics=derived(sums,fg,boundary,len(targets)*ref.shape[0]*ref.shape[1]);equal(metrics,expected['metrics'],uid+' '+name)
   gate=bool(metrics['foreground_recall']>=.99 and metrics['boundary_recall']>=.99 and metrics['tile_foreground_recall']>=.995 and metrics['roi_fraction']<=.05 and metrics['tile_fraction']<=.1);check(gate==expected['gate_passed'],'ROI gate differs '+uid+' '+name)
  delta=all_comp['native']['missing']['dice']-all_comp['sparse']['missing']['dice'];check(abs(delta-stored['missing_dice_native_minus_sparse'])<1e-12,'Delta differs '+uid);deltas[uid]=delta
  records.append(dict(patient=case['patient'],uid=uid,raw_native_arrays_decoded=len(sops),missing_targets=len(targets),fresh_native_prediction_bitwise_equal=native_equal,supplement_sparse_replayed=not case['in_old_frozen_15'],maximum_Hermite_display_difference=difference,missing_dice_native_minus_sparse=delta));print(json.dumps(records[-1]),flush=True);del ref,edge,native,sparse
 means=[]
 for patient in result['patients']:
  group=[r for r in records if r['patient']==patient['patient']];mean=float(np.mean([deltas[r['uid']] for r in group]));means.append(mean)
  check(len(group)==patient['series'] and abs(mean-patient['series_equal_missing_dice_native_minus_sparse'])<1e-12,'Whole-patient aggregation differs '+patient['patient'])
  for name in ('native','sparse'):
   v=float(np.mean([by[r['uid']]['task_competence'][name]['missing']['dice'] for r in group]));check(abs(v-patient['series_equal_missing_dice'][name])<1e-12,'Whole-patient condition mean differs '+patient['patient']+' '+name)
 check(abs(float(np.mean(means))-result['patient_equal_missing_dice_native_minus_sparse'])<1e-12,'All-patient mean differs');check(not torch.cuda.is_initialized(),'CUDA initialized')
 proof=dict(created_utc=datetime.now(timezone.utc).isoformat(),verification_script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),run_contract_sha256=sha(OUT/'run_contract.json'),counts=dict(series=len(records),patients=len(means),fresh_neural_replays=forward_count,raw_native_arrays_decoded=sum(r['raw_native_arrays_decoded'] for r in records),missing_targets=sum(r['missing_targets'] for r in records)),model_runtime=runtime,series=records,errors=errors,gpu_used=False,scope='raw ZIP independent sorting/decode, fresh native and supplemental sparse CPU forwards, explicit native mapping, raw-label slabs and physical-offset disk all-target scoring; authenticated author inferer/Pydicom/geometry helper libraries reused',scientific_independent_validation_patients=0,publication_claim_confirmed=False)
 with path.open('x',encoding='utf-8') as f: f.write(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(dict(counts=proof['counts'],errors=errors)),flush=True);return int(bool(errors))
if __name__=='__main__': raise SystemExit(main())
