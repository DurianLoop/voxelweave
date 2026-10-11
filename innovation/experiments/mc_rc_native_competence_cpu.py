"""Frozen native-vs-observed diagnostic for corrected all-source developer roster."""
from __future__ import annotations
import json,os,sys,time,traceback,zipfile
from datetime import datetime,timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'): os.environ[key]='1'
import nibabel as nib
import numpy as np
import pydicom
import torch
from scipy import ndimage
from vs_seg_task_cpu_support import resource_gate,load_model
from vs_seg_full_volume_runtime import sha,array_sha,load_tuple_inferer,inference
from mc_rc_frozen_predicted_region_cpu import decode_observed,display_from_anchors,task_counts
from mc_rc_observed_region_propagation import score,rates
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/mc_rc_native_competence_cpu'
PLAN=ROOT/'MC_RC_NATIVE_COMPETENCE_CPU_PLAN_2026-10-03.md'
OLD=ROOT/'experiments/mc_rc_frozen_predicted_region_cpu'
ROSTER=ROOT/'experiments/mc_rc_source_denominator_correction/attempt_01.json'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,obj): Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def map_back(ras,case):
 inv=nib.orientations.ornt_transform(nib.orientations.axcodes2ornt('RAS'),nib.orientations.io_orientation(np.array(case['affine_rcz_ras'])))
 return np.ascontiguousarray(nib.orientations.apply_orientation(ras,inv)).astype(bool)
def orient(case): return nib.orientations.ornt_transform(nib.orientations.io_orientation(np.array(case['affine_rcz_ras'])),nib.orientations.axcodes2ornt('RAS'))
def decode_native(case,anchors):
 h=read(ROOT/case['header_file']);by={r['zip_member']:r for r in h['records']}
 shape=case['native_shape'];vol=np.empty(shape,dtype=np.float32);sops=[]
 with zipfile.ZipFile(ROOT/case['mr_zip_file']) as archive:
  for z,member in enumerate(case['ordered_zip_members']):
   with archive.open(member) as f: ds=pydicom.dcmread(f)
   if str(ds.PatientID)!=case['patient'] or str(ds.StudyInstanceUID)!=case['study_uid'] or str(ds.SeriesInstanceUID)!=case['uid'] or str(ds.SOPInstanceUID)!=by[member]['sop_uid'] or str(ds.PhotometricInterpretation)!='MONOCHROME2' or [int(ds.Rows),int(ds.Columns)]!=shape[:2]: raise ValueError('Native MR identity/order/shape differs')
   slope,intercept=float(ds.get('RescaleSlope',1)),float(ds.get('RescaleIntercept',0))
   if not np.isfinite([slope,intercept]).all(): raise ValueError('Native rescale nonfinite')
   vol[:,:,z]=ds.pixel_array.astype(np.float32)*slope+intercept;sops.append(str(ds.SOPInstanceUID))
 if not np.isfinite(vol).all() or not np.array_equal(vol[:,:,::4],anchors): raise ValueError('Native input finite/anchor match differs')
 return vol,sops
def truth(case):
 image=nib.load(ROOT/case['label_file']);matrix=np.array(case['dicom_rcz_from_label_xyz'],dtype=int);native=np.zeros(case['native_shape'],dtype=bool)
 for start in range(0,image.shape[2],4):
  slab=np.asarray(image.dataobj[:,:,start:start+4])
  if slab.nbytes>32000000 or not np.isfinite(slab).all() or not np.isin(slab,[0,1]).all(): raise ValueError('Label slab finite/binary/budget gate failed')
  xyz=np.array(np.nonzero(slab));xyz[2]+=start;rcz=matrix[:3,:3]@xyz+matrix[:3,3,None]
  if (rcz<0).any() or (rcz>=np.array(case['native_shape'])[:,None]).any(): raise ValueError('Raw label extent differs')
  native[tuple(rcz)]=True
 if int(native.sum())!=case['expected_label_foreground_voxels']: raise ValueError('Raw foreground count differs')
 return native
def roi_summary(pred,ref,edge,case,targets):
 r,c,_=ref.shape;sums={key:0 for key in score(np.zeros((r,c),dtype=bool),ref[:,:,0],edge[:,:,0])};rows=[];cache={}
 for z in targets:
  left=z//4*4
  if left not in cache:
   union=pred[:,:,left]|pred[:,:,left+4]
   mask=ndimage.distance_transform_edt(~union,sampling=case['native_spacing_rcz_mm'][:2])<=2.+1e-12 if union.any() else np.zeros((r,c),dtype=bool);cache={left:mask}
  counts=score(cache[left],ref[:,:,z],edge[:,:,z])
  for key,value in counts.items(): sums[key]+=value
  rows.append(dict(z=z,counts=counts))
 fg=sum(int(ref[:,:,z].sum()) for z in targets);boundary=sum(int(edge[:,:,z].sum()) for z in targets)
 m=rates(sums,fg,boundary,len(targets)*r*c)
 gate=bool(m['foreground_recall']>=.99 and m['boundary_recall']>=.99 and m['tile_foreground_recall']>=.995 and m['roi_fraction']<=.05 and m['tile_fraction']<=.10)
 return dict(metrics=m,gate_passed=gate,target_records=rows)
def main():
 sys.stdout.reconfigure(encoding='utf-8');resources=resource_gate();proof_path=OLD/'independent_observed_input_roi_and_model_replay.json'
 proof=read(proof_path);old=read(OLD/'attempt_01.json');roster=read(ROSTER)
 if proof['errors'] or proof['counts']['fresh_neural_replays']!=15 or proof['result_sha256']!=sha(OLD/'attempt_01.json') or not old['complete'] or roster['errors'] or not roster['complete']: raise ValueError('Required complete fifteen-replay or corrected roster proof differs')
 cases=roster['cases'];old_by={r['uid']:r for r in old['series']}
 if len(cases)!=16 or len({r['patient'] for r in cases})!=8: raise ValueError('Frozen 16/8 roster differs')
 paths=[PLAN,Path(__file__),ROSTER,proof_path,OLD/'attempt_01.json',OLD/'run_contract.json',ROOT/'experiments/mc_rc_frozen_predicted_region_cpu.py',ROOT/'experiments/mc_rc_observed_region_propagation.py',ROOT/'experiments/vs_seg_task_cpu_support.py',ROOT/'experiments/vs_seg_full_volume_runtime.py',ROOT/'experiments/vs_seg_001_tuple_equivalence/attempt_01.json',ROOT/'experiments/vs_seg_001_tuple_equivalence/monai_0_4_tuple_inferer.py',ROOT/'data/vs_seg_task_model_release/UNet2d5_Att_Hard_T2_final.zip']
 for row in roster['files']:
  p=ROOT/row['path']
  if sha(p)!=row['sha256']: raise ValueError('Corrected roster input mutated '+row['path'])
  paths.append(p)
 for case in cases:
  if np.prod(case['native_shape'])*4>250000000: raise ValueError('Native float32 budget exceeded')
  if case['in_old_frozen_15']: paths.append(ROOT/old_by[case['uid']]['prediction_file'])
 OUT.mkdir(exist_ok=False)
 contract=dict(created_utc=datetime.now(timezone.utc).isoformat(),cases=cases,developer_only=True,source_scope='corrected 16 qualified series among frozen three source batches',new_forward_count=17,full_native_arrays_decoded_for_reference_only=True,files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(set(paths))])
 write(OUT/'run_contract.json',contract)
 result=dict(created_utc=datetime.now(timezone.utc).isoformat(),run_contract_sha256=sha(OUT/'run_contract.json'),resources=resources,complete=False,series=[],errors=[],gpu_used=False,scientific_independent_validation_patients=0,publication_claim_confirmed=False)
 write(OUT/'attempt_01.json',result);model,runtime=load_model();inferer=load_tuple_inferer();result['model_runtime']=runtime
 for case in cases:
  resource_gate();start=time.perf_counter();row=dict(patient=case['patient'],uid=case['uid'],description=case['description'],complete=False,source_scope='all16_corrected_development',in_old_frozen_15=case['in_old_frozen_15'])
  try:
   anchors,sops=decode_observed(case);sparse_input=display_from_anchors(anchors,case['native_shape'][2]);row.update(observed_array_sha256=array_sha(anchors),raw_pchip_display_array_sha256=array_sha(sparse_input),observed_sop_uids=sops)
   if case['in_old_frozen_15']:
    prior=old_by[case['uid']]
    if row['observed_array_sha256']!=prior['observed_array_sha256'] or row['raw_pchip_display_array_sha256']!=prior['raw_pchip_display_array_sha256'] or sha(ROOT/prior['prediction_file'])!=prior['prediction_sha256']: raise ValueError('Fresh observed input or authenticated sparse prediction differs')
    with np.load(ROOT/prior['prediction_file']) as pack: sparse=pack['prediction_native'].copy()
    row.update(sparse_prediction_file=prior['prediction_file'],sparse_prediction_sha256=prior['prediction_sha256'],sparse_prediction_reused_after_all15_replay=True)
   else:
    sparse=map_back(inference(model,inferer,sparse_input,orient(case)),case);p=OUT/(case['uid']+'_sparse_prediction.npz');np.savez_compressed(p,prediction_native=sparse);row.update(sparse_prediction_file=p.relative_to(ROOT).as_posix(),sparse_prediction_sha256=sha(p),sparse_prediction_reused_after_all15_replay=False)
   row['sparse_prediction_array_sha256']=array_sha(sparse);del sparse_input
   native,sops_all=decode_native(case,anchors);row.update(native_array_sha256=array_sha(native),native_decoded_sop_uids=sops_all,native_planes_decoded=len(sops_all));del anchors
   pred=map_back(inference(model,inferer,native,orient(case)),case);del native
   p=OUT/(case['uid']+'_native_prediction.npz');np.savez_compressed(p,prediction_native=pred);row.update(native_prediction_file=p.relative_to(ROOT).as_posix(),native_prediction_sha256=sha(p),native_prediction_array_sha256=array_sha(pred));write(OUT/(case['uid']+'_predictions_before_label.json'),row)
   ref=truth(case);edge=ref&~ndimage.binary_erosion(ref,structure=ndimage.generate_binary_structure(3,1),border_value=0);n=case['native_shape'][2];targets=[z for z in range(1,(n-1)//4*4) if z%4];regions=dict(full=np.arange(n),observed=np.arange(0,n,4),missing=np.array(targets))
   row['task_competence']={name:{region:task_counts(pr,ref,planes) for region,planes in regions.items()} for name,pr in [('native',pred),('sparse',sparse)]}
   row['roi']={name:roi_summary(pr,ref,edge,case,targets) for name,pr in [('native_anchor_union_2mm',pred),('sparse_anchor_union_2mm',sparse)]}
   if not case['in_old_frozen_15']: row['ideal_anchor_union_2mm']=roi_summary(ref,ref,edge,case,targets)
   if case['in_old_frozen_15']:
    for region in regions:
     if row['task_competence']['sparse'][region]!=old_by[case['uid']]['task_competence'][region]: raise ValueError('Raw label/task counts vs verified sparse source differ')
   row.update(missing_targets=len(targets),missing_dice_native_minus_sparse=row['task_competence']['native']['missing']['dice']-row['task_competence']['sparse']['missing']['dice'],complete=True,seconds=time.perf_counter()-start)
   if torch.cuda.is_initialized(): raise ValueError('Unexpected CUDA initialization')
   del ref,edge,pred,sparse
  except Exception as exc:
   row.update(error=type(exc).__name__+': '+str(exc),traceback=traceback.format_exc(),seconds=time.perf_counter()-start);result['errors'].append(dict(patient=case['patient'],uid=case['uid'],error=row['error']))
  result['series'].append(row);write(OUT/'attempt_01.json',result);print(json.dumps({k:row.get(k) for k in ('patient','uid','complete','missing_dice_native_minus_sparse','seconds','error')}),flush=True)
  if result['errors']: break
 result['complete']=len(result['series'])==16 and all(r['complete'] for r in result['series']) and not result['errors']
 if result['complete']:
  result['patients']=[]
  for patient in sorted({r['patient'] for r in cases}):
   group=[r for r in result['series'] if r['patient']==patient]
   result['patients'].append(dict(patient=patient,series=len(group),series_equal_missing_dice_native_minus_sparse=float(np.mean([r['missing_dice_native_minus_sparse'] for r in group])),series_equal_missing_dice={name:float(np.mean([r['task_competence'][name]['missing']['dice'] for r in group])) for name in ('native','sparse')}))
  result['patient_equal_missing_dice_native_minus_sparse']=float(np.mean([r['series_equal_missing_dice_native_minus_sparse'] for r in result['patients']]))
 result['finished_utc']=datetime.now(timezone.utc).isoformat();write(OUT/'attempt_01.json',result);print(json.dumps(dict(complete=result['complete'],processed_series=len(result['series']),errors=result['errors'])),flush=True)
 return int(not result['complete'])
if __name__=='__main__': raise SystemExit(main())
