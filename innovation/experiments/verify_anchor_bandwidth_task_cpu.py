"""Independent saved prediction metrics for the anchors-only diagnostic pilot."""
import json,math
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import nibabel as nib
from scipy.ndimage import binary_erosion,distance_transform_edt,generate_binary_structure
from vs_seg_task_cpu_support import ROOT,resource_gate
from vs_seg_full_volume_runtime import decode_source,array_sha,sha
from verify_vs_seg_post_resize_task_cpu import boundary,check,close
OUT=ROOT/'experiments/anchor_bandwidth_task_cpu_pilot'
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')
def verify_saved(case,record,path):
 resource_gate();native,affine,refs=decode_source(case);orientation=nib.orientations.ornt_transform(nib.orientations.io_orientation(affine),nib.orientations.axcodes2ornt('RAS'));can_affine=affine@nib.orientations.inv_ornt_aff(orientation,native.shape);spacing=nib.affines.voxel_sizes(can_affine);check(record['complete'] and not record['cuda_initialized'],'Completed CPU inference required');check(array_sha(native)==record['native_array_sha256'],'Native source identity differs');p=ROOT/record['prediction_file'];check(sha(p)==record['prediction_sha256'],'Saved prediction hash differs')
 with np.load(p) as z:pred=z['prediction_ras'];check(pred.dtype==bool and np.array_equal(z['affine'],can_affine),'Prediction type/grid differs')
 check(array_sha(pred)==record['prediction_array_sha256'],'Saved prediction array differs');last=(native.shape[2]-1)//4*4;slab=np.broadcast_to(np.indices(native.shape,sparse=True)[2]<=last,native.shape);slab=nib.orientations.apply_orientation(slab,orientation)
 for refname,labels in refs.items():
  ref=nib.orientations.apply_orientation(labels,orientation);edge=ref^binary_erosion(ref,structure=generate_binary_structure(3,1),border_value=0);keep=distance_transform_edt(~edge,sampling=spacing)>1
  for domain,mask in [('full',np.ones_like(ref)),('observed_anchor_slab',slab),('exclude_reference_boundary_1mm',keep)]:
   a,b=pred[mask],ref[mask];tp=int(np.count_nonzero(a&b));fp=int(a.sum())-tp;fn=int(b.sum())-tp;reported=record['task_metrics'][refname][domain];den=2*tp+fp+fn;empty=domain=='exclude_reference_boundary_1mm' and not b.any();dice=2*tp/den if den and not empty else None
   for key,value in dict(tp=tp,fp=fp,fn=fn,reference_voxels=tp+fn,prediction_voxels=tp+fp).items():check(value==reported[key],'Actual confusion differs '+key)
   close(dice,reported['dice'],'Saved actual Dice differs')
   if domain=='exclude_reference_boundary_1mm':check(empty==reported['reference_core_empty'] and int((~keep).sum())==reported['excluded_band_voxels'],'Physical core differs')
   if domain=='full':
    signed=fp-fn;close(signed*float(np.prod(spacing)),reported['signed_volume_difference_mm3'],'Volume differs');close(signed/(tp+fn),reported['signed_relative_volume_error'],'Relative volume differs')
   if domain in ('full','observed_anchor_slab'):
    actual=boundary(pred&mask,ref&mask,spacing)
    for key,value in actual.items():
     if isinstance(value,str):check(value==reported['boundary'][key],'Boundary status differs')
     else:close(value,reported['boundary'][key],'Actual full-grid boundary differs')
 proof=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,patient=case['patient'],condition=record['condition'],record_sha256=sha(path),prediction_sha256=sha(p),script_sha256=sha(__file__),errors=[],new_neural_forwards=0,independence='Fresh native decode and physical grid; independently sliced confusion/EDT. Shares old independent boundary helper, source labels and NumPy; no independent cohort/model.')
 out=OUT/('verification_'+path.stem+'.json');write(out,proof);return out
