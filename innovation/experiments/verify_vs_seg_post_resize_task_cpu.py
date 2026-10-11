"""Fresh native/grid and full-grid task metrics, no additional network forward."""
import json, math, sys
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import nibabel as nib
from scipy.ndimage import binary_erosion,distance_transform_edt,generate_binary_structure
from vs_seg_task_cpu_support import ROOT,resource_gate
from vs_seg_full_volume_runtime import decode_source,array_sha,sha
OUT=ROOT/'experiments/vs_seg_post_resize_task_cpu'

def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def check(ok,label):
    if not ok: raise ValueError(label)
def close(x,y,label):
    check(x==y if x is None or y is None else math.isclose(x,y,rel_tol=1e-10,abs_tol=1e-12),label)
def write(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')

def boundary(pred,ref,spacing):
    st=generate_binary_structure(3,1);ep=pred^binary_erosion(pred,structure=st,border_value=0);er=ref^binary_erosion(ref,structure=st,border_value=0)
    if not ep.any() or not er.any(): return dict(status='both_empty_undefined' if not ep.any() and not er.any() else 'one_empty_infinite',assd_mm=None,masd_mm=None,hd95_mm=None,prediction_surface_voxels=int(ep.sum()),reference_surface_voxels=int(er.sum()))
    a=distance_transform_edt(~er,sampling=spacing)[ep];b=distance_transform_edt(~ep,sampling=spacing)[er];both=np.concatenate((a,b))
    return dict(status='finite',assd_mm=float(both.mean()),masd_mm=float((a.mean()+b.mean())/2),hd95_mm=float(np.quantile(both,.95)),prediction_surface_voxels=len(a),reference_surface_voxels=len(b))

def verify_one(case,record):
    resource_gate();native,affine,refs=decode_source(case);orientation=nib.orientations.ornt_transform(nib.orientations.io_orientation(affine),nib.orientations.axcodes2ornt('RAS'));can_affine=affine@nib.orientations.inv_ornt_aff(orientation,native.shape);spacing=nib.affines.voxel_sizes(can_affine)
    check(array_sha(native)==record['native_array_sha256'],'Native hash differs');check(record['complete'] and not record['cuda_initialized'],'Task completion/CUDA differs');check(record['source_input_sha256']==sha(ROOT/case['input_file']) and record['reference_masks_sha256']==sha(ROOT/case['masks_file']),'Source/label binding differs')
    p=ROOT/record['prediction_file'];check(sha(p)==record['prediction_sha256'],'Prediction file SHA differs')
    with np.load(p) as archive:
        pred=archive['prediction_ras'];check(pred.dtype==bool,'Prediction dtype differs');check(np.array_equal(archive['affine'],can_affine),'Prediction affine differs')
    check(array_sha(pred)==record['prediction_array_sha256'],'Prediction array SHA differs');check(pred.shape==nib.orientations.apply_orientation(native,orientation).shape,'Prediction RAS shape differs')
    last=(native.shape[2]-1)//4*4;slab=np.indices(native.shape,sparse=True)[2]<=last;slab=np.broadcast_to(slab,native.shape);slab=nib.orientations.apply_orientation(slab,orientation)
    check(record['observed_indices']==list(range(0,native.shape[2],4)),'Observed indices differ');check(record['unsupported_terminal_indices']==list(range(last+1,native.shape[2])),'Tail indices differ')
    for name,labels in refs.items():
        ref=nib.orientations.apply_orientation(labels,orientation);edge=ref^binary_erosion(ref,structure=generate_binary_structure(3,1),border_value=0);keep=distance_transform_edt(~edge,sampling=spacing)>1
        for domain,mask in [('full',np.ones_like(ref)),('observed_anchor_slab',slab),('exclude_reference_boundary_1mm',keep)]:
            a,b=pred[mask],ref[mask];tp=int(np.count_nonzero(np.logical_and(a,b)));fp=int(a.sum())-tp;fn=int(b.sum())-tp;reported=record['task_metrics'][name][domain];denom=2*tp+fp+fn
            for key,value in dict(tp=tp,fp=fp,fn=fn,reference_voxels=tp+fn,prediction_voxels=tp+fp,missed_lesion=bool(tp+fn and not tp+fp)).items(): check(value==reported[key],'Independent '+name+'/'+domain+'/'+key+' differs')
            core_empty=domain=='exclude_reference_boundary_1mm' and not b.any();dice=2*tp/denom if denom and not core_empty else None;close(dice,reported['dice'],'Independent Dice differs')
            if domain=='exclude_reference_boundary_1mm': check(core_empty==reported['reference_core_empty'] and int((~keep).sum())==reported['excluded_band_voxels'],'Reference band differs')
            if domain=='full':
                signed=fp-fn;close(signed*float(np.prod(spacing)),reported['signed_volume_difference_mm3'],'Volume mm3 differs');close(signed/(tp+fn),reported['signed_relative_volume_error'],'Relative volume differs');close(abs(signed)/(tp+fn),reported['absolute_relative_volume_error'],'Absolute volume differs')
            if domain in ('full','observed_anchor_slab'):
                actual=boundary(pred&mask,ref&mask,spacing)
                for key,value in actual.items():
                    if isinstance(value,str): check(value==reported['boundary'][key],'Boundary status differs')
                    else: close(value,reported['boundary'][key],'Full-grid '+domain+'/'+key+' differs')
    proof=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,patient=case['patient'],script_sha256=sha(__file__),record_sha256=sha(OUT/(case['patient']+'.json')),prediction_sha256=sha(p),errors=[],gpu_used=False,new_neural_forwards=0,independence='Fresh authenticated native decoder and RAS grid; independent sliced confusion and full-grid physical EDT metrics; same source labels and spacing library; no scientific cohort/model independence')
    write(OUT/('verification_'+case['patient']+'.json'),proof);return proof

def quantile(values,q):
    pos=(len(values)-1)*q;lo=math.floor(pos);hi=math.ceil(pos);return values[lo]+(pos-lo)*(values[hi]-values[lo])

def verify_analysis(report,records,old):
    check(report['complete'] and len(records)==45 and len(report['analysis'])==18,'Complete all45/all18 required');checked=[]
    for endpoint in report['analysis']:
        ref,domain=endpoint['reference'],endpoint['domain'];left,right=endpoint['comparison'].split('-');values={p:{'post':records[p]['task_metrics'][ref][domain]['dice'],'pipeline':old[p]['pipeline_pchip']['task_metrics'][ref][domain]['dice'],'raw':old[p]['raw_pchip']['task_metrics'][ref][domain]['dice']} for p in report['main_roster']}
        included=[p for p in report['main_roster'] if all(v is not None for v in values[p].values())];check(included==endpoint['included_patients'],'Defined paired roster differs');check([p for p in report['main_roster'] if p not in included]==endpoint['undefined_patients'],'Undefined roster differs')
        delta=[values[p][left]-values[p][right] for p in included]
        for a,b in zip(delta,endpoint['patient_differences']): close(a,b,'Patient task difference differs')
        if delta:
            n=len(delta);draws=np.random.default_rng(20261101).integers(0,n,size=(5000,n));estimates=sorted(math.fsum(delta[int(i)] for i in draw)/n for draw in draws);expected=dict(n=n,mean_difference=math.fsum(delta)/n,negative_patients=sum(v<0 for v in delta),zero_patients=sum(v==0 for v in delta))
            for k,v in expected.items(): close(v,endpoint['estimate'][k],'Task scalar summary differs')
            for a,b in zip([quantile(estimates,q) for q in (.025,.975)],endpoint['estimate']['ci95_percentile']): close(a,b,'Task scalar quantile differs')
        else: check(endpoint['estimate'] is None,'All undefined endpoint filled')
        checked.append({k:endpoint[k] for k in ('reference','domain','comparison')})
    proof=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),run_contract_sha256=sha(OUT/'run_contract.json'),checked_patients=report['main_roster'],endpoints=checked,errors=[],gpu_used=False,new_neural_forwards=0,new_method_confirmation_patients=0,publication_claim_confirmed=False,independence='Independent saved prediction checks and scalar bootstrap/quantiles; shared NumPy RNG and source labels; no new scientific cohort or task model')
    write(OUT/'independent_all_tasks_and_estimates.json',proof);return proof
