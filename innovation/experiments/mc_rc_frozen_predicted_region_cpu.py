"""Only genuine phase0 MR pixels feed a frozen CPU segmenter and ROI rules."""
from __future__ import annotations
import hashlib
import importlib.metadata
import json
import os
import sys
import time
import traceback
import zipfile
from datetime import datetime, timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key] = '1'
import nibabel as nib
import numpy as np
import pydicom
import torch
from scipy.interpolate import PchipInterpolator
from scipy import ndimage
from vs_seg_task_cpu_support import resource_gate,load_model
from vs_seg_full_volume_runtime import array_sha,inference,load_tuple_inferer,sha
from mc_rc_observed_region_propagation import grid,expand,score,rates,rng
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'experiments/mc_rc_frozen_predicted_region_cpu'
PLAN = ROOT/'MC_RC_FROZEN_PREDICTED_REGION_CPU_PLAN_2026-10-03.md'
GEOMETRY = ROOT/'experiments/mc_rc_observed_region_propagation'
HEADER_ROOTS = {
 'experiments/mc_rc_native_t2_label_gate/label_grid_attempt_01.json':'literature/source_cache/mc_rc_three_patient_headers_2026-10-02',
 'experiments/mc_rc_004_006_native_label_gate/resource_followup_attempt_01.json':'literature/source_cache/mc_rc_004_006_native_headers_2026-10-02',
 'experiments/mc_rc_007_010_native_label_gate/attempt_01.json':'literature/source_cache/mc_rc_007_010_native_headers_2026-10-02',
}
METHODS = ['predicted_anchor_union_2mm','predicted_bracket_union','dense_prediction_2mm','shifted_primary','random_pixels_matched_primary','random_tiles_matched_primary']
def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,obj):
    Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def decode_observed(case):
    header = read(ROOT/case['header_file'])
    by_member = {r['zip_member']:r for r in header['records']}
    anchors,sops = [],[]
    with zipfile.ZipFile(ROOT/case['mr_zip_file']) as archive:
        for z in range(0,case['native_shape'][2],4):
            member = case['ordered_zip_members'][z]
            with archive.open(member) as stream:
                ds = pydicom.dcmread(stream)
            prior = by_member[member]
            if str(ds.PatientID)!=case['patient'] or str(ds.StudyInstanceUID)!=case['study_uid'] or str(ds.SeriesInstanceUID)!=case['uid'] or str(ds.SOPInstanceUID)!=prior['sop_uid'] or str(ds.PhotometricInterpretation)!='MONOCHROME2' or [int(ds.Rows),int(ds.Columns)]!=case['native_shape'][:2]:
                raise ValueError('Visible MR identity/order/photometric/dimensions differ')
            slope,intercept = float(ds.get('RescaleSlope',1)),float(ds.get('RescaleIntercept',0))
            if not np.isfinite([slope,intercept]).all():
                raise ValueError('Visible rescale parameters nonfinite')
            plane = ds.pixel_array.astype(np.float32)*slope+intercept
            if not np.isfinite(plane).all():
                raise ValueError('Visible MR pixels nonfinite')
            anchors.append(plane)
            sops.append(str(ds.SOPInstanceUID))
    return np.stack(anchors,axis=2),sops
def display_from_anchors(anchors,n):
    generated = np.zeros((*anchors.shape[:2],n),dtype=np.float32)
    observed = np.arange(0,n,4)
    generated[:,:,observed] = anchors
    last = int(observed[-1])
    for z in range(1,last):
        if not z%4:
            continue
        i,t = z//4,z%4/4
        if i>=1 and i+2<anchors.shape[2]:
            indices = np.arange(i-1,i+3)
            plane = PchipInterpolator(indices*4,anchors[:,:,indices],axis=2)(z)
        else:
            plane = (1-t)*anchors[:,:,i]+t*anchors[:,:,i+1]
        generated[:,:,z] = plane
    generated[:,:,last+1:] = anchors[:,:,-1,None]
    if not np.isfinite(generated).all() or not np.array_equal(generated[:,:,observed],anchors):
        raise ValueError('Observed-only display finite/anchor preservation failed')
    return generated
def dilate(mask,spacing):
    return ndimage.distance_transform_edt(~mask,sampling=spacing)<=2.+1e-12 if mask.any() else np.zeros_like(mask)
def visible_candidates(predicted,spacing,z,uid):
    left,right = z//4*4,z//4*4+4
    union = predicted[:,:,left]|predicted[:,:,right]
    primary = dilate(union,spacing)
    rows,cols = primary.shape
    random_pixels = np.zeros(rows*cols,dtype=bool)
    random_pixels[rng(uid,z,'pixels').choice(rows*cols,int(primary.sum()),replace=False)] = True
    selected = grid(primary)
    areas = np.array([[min(32,rows-i*32)*min(32,cols-j*32) for j in range(selected.shape[1])] for i in range(selected.shape[0])])
    random_selected = np.zeros_like(selected)
    g = rng(uid,z,'tiles')
    for area in np.unique(areas):
        eligible = np.flatnonzero(areas.ravel()==area)
        count = int((selected&(areas==area)).sum())
        random_selected.ravel()[g.choice(eligible,count,replace=False)] = True
    return dict(predicted_anchor_union_2mm=primary,predicted_bracket_union=union,dense_prediction_2mm=dilate(predicted[:,:,z],spacing),shifted_primary=np.roll(primary,(rows//2,cols//2),axis=(0,1)),random_pixels_matched_primary=random_pixels.reshape(rows,cols),random_tiles_matched_primary=expand(random_selected,(rows,cols)))
def task_counts(predicted,truth,planes):
    p,t = predicted[:,:,planes],truth[:,:,planes]
    pp,tt,tp = int(p.sum()),int(t.sum()),int((p&t).sum())
    return dict(predicted_voxels=pp,truth_voxels=tt,true_positive_voxels=tp,dice=2*tp/(pp+tt) if pp+tt else None,recall=tp/tt if tt else None,precision=tp/pp if pp else None)
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    resources = resource_gate()
    geometry,proof = read(GEOMETRY/'attempt_01.json'),read(GEOMETRY/'independent_raw_label_roi_verification.json')
    if not geometry['complete'] or not geometry['strict_all_series_geometric_gate_passed'] or proof['errors'] or sha(GEOMETRY/'attempt_01.json')!=proof['result_sha256']:
        raise ValueError('Ideal-region prerequisite lacks complete independent proof')
    identity_path = ROOT/'experiments/mc_rc_v2_nonpixel_identity/attempt_01.json'
    identity_proof_path = ROOT/'experiments/mc_rc_v2_nonpixel_identity/independent_sqlite_verification.json'
    identity,identity_proof = read(identity_path),read(identity_proof_path)
    if identity_proof['errors'] or sha(identity_path)!=identity_proof['result_sha256'] or len(identity['excluded_shared_patients'])!=58:
        raise ValueError('Official shared-patient exclusion proof differs')
    model_index_path = ROOT/'literature/source_cache/vs_seg_t2_release_logs_2026-10-02/index.json'
    split_path = model_index_path.parent/'split_verification.json'
    model_index,split = read(model_index_path),read(split_path)
    if not all(r['all_subject_lists_equal_to_git_split'] for r in split['logs'].values()) or sha(ROOT/model_index['source'])!=model_index['sha256']:
        raise ValueError('Checkpoint-associated source/split differs')
    paths = [PLAN,Path(__file__),GEOMETRY/'attempt_01.json',GEOMETRY/'run_contract.json',GEOMETRY/'independent_raw_label_roi_verification.json',identity_path,identity_proof_path,model_index_path,split_path,ROOT/model_index['source'],ROOT/'experiments/vs_seg_task_cpu_support.py',ROOT/'experiments/vs_seg_full_volume_runtime.py',ROOT/'experiments/mc_rc_observed_region_propagation.py',ROOT/'literature/source_cache/vs_seg_cpu_compat_sources_2026-10-02/index.json',ROOT/'experiments/vs_seg_001_tuple_equivalence/attempt_01.json',ROOT/'experiments/vs_seg_001_tuple_equivalence/monai_0_4_tuple_inferer.py']
    compat = read(paths[-3])
    paths += [paths[-3].parent/compat['monai_wheel']['file']]
    paths += [ROOT/'tools/vs_seg_cpu_compat'/r['file'] for r in compat['author_sources']]
    cases = []
    for source,folder in HEADER_ROOTS.items():
        ledger = read(ROOT/folder/'attempt_01.json')
        by_uid = {r['source']['SeriesInstanceUID']:r for r in ledger['series']}
        for row in [r for r in geometry['series'] if r['source_result']==source]:
            h = by_uid[row['uid']]
            if row['patient'] not in identity['candidate_nonoverlap_patients']:
                raise ValueError('Patient outside official nonoverlap rule candidates')
            for p,expected in [(ROOT/h['transfer']['file'],h['transfer']['sha256']),(ROOT/folder/h['header_file'],h['header_sha256'])]:
                if sha(p)!=expected:
                    raise ValueError('Source hash differs '+str(p))
                paths.append(p)
            if np.prod(row['native_shape'])*4>250000000 or np.prod([*row['native_shape'][:2],len(range(0,row['native_shape'][2],4))])*4>80000000:
                raise ValueError('Fixed native/anchor array budget exceeded')
            paths += [ROOT/row['component_file'],ROOT/row['label_file'],ROOT/source,ROOT/folder/'attempt_01.json']
            cases.append(dict(patient=row['patient'],uid=row['uid'],description=row['description'],study_uid=h['source']['StudyInstanceUID'],native_shape=row['native_shape'],native_spacing_rcz_mm=row['native_spacing_rcz_mm'],affine_rcz_ras=h['summary']['affine_rcz_ras'],ordered_zip_members=h['summary']['ordered_zip_members'],header_file=(Path(folder)/h['header_file']).as_posix(),header_sha256=h['header_sha256'],mr_zip_file=h['transfer']['file'],mr_zip_sha256=h['transfer']['sha256'],component_file=row['component_file'],component_sha256=row['component_sha256'],label_file=row['label_file'],label_sha256=row['label_sha256']))
    cases.sort(key=lambda r:(r['patient'],r['uid']))
    if [r['uid'] for r in cases]!=[r['uid'] for r in geometry['series']] or len(cases)!=15:
        raise ValueError('Complete developer roster differs')
    OUT.mkdir(exist_ok=False)
    contract = dict(created_utc=datetime.now(timezone.utc).isoformat(),cases=cases,methods=METHODS,primary_method='predicted_anchor_union_2mm',developer_only=True,MR_decode_indices='0,4,... only',MR_hidden_pixels_decoded=False,strict_geometric_gate=read(GEOMETRY/'run_contract.json')['strict_gate'],official_shared_patient_exclusion_rule_checked=True,full_legacy_crosswalk_certified=False,package_versions={p:importlib.metadata.version(p) for p in ('torch','numpy','scipy','nibabel','pydicom')},python_version=sys.version,files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(set(paths))])
    write(OUT/'run_contract.json',contract)
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(),run_contract_sha256=sha(OUT/'run_contract.json'),complete=False,processed_series=0,resources=resources,series=[],errors=[],gpu_used=False,MR_anchor_pixel_arrays_decoded=False,MR_hidden_pixel_arrays_decoded=False,truth_masks_used_as_model_or_ROI_inputs=False,checkpoint_retrained=False,scientific_independent_validation_patients=0,publication_claim_confirmed=False)
    write(OUT/'attempt_01.json',result)
    model,runtime = load_model()
    inferer = load_tuple_inferer()
    result['model_runtime'] = runtime
    write(OUT/'attempt_01.json',result)
    for case in cases:
        resource_gate()
        started = time.perf_counter()
        row = dict(patient=case['patient'],uid=case['uid'],description=case['description'],complete=False)
        try:
            anchors,sops = decode_observed(case)
            display = display_from_anchors(anchors,case['native_shape'][2])
            affine = np.array(case['affine_rcz_ras'])
            orientation = nib.orientations.ornt_transform(nib.orientations.io_orientation(affine),nib.orientations.axcodes2ornt('RAS'))
            prediction_ras = inference(model,inferer,display,orientation)
            inverse = nib.orientations.ornt_transform(nib.orientations.axcodes2ornt('RAS'),nib.orientations.io_orientation(affine))
            predicted = np.ascontiguousarray(nib.orientations.apply_orientation(prediction_ras,inverse)).astype(bool)
            if predicted.shape!=tuple(case['native_shape']) or torch.cuda.is_initialized():
                raise ValueError('Prediction native-grid/CPU gate failed')
            prediction_path = OUT/(case['patient']+'_'+case['uid']+'_native_prediction.npz')
            np.savez_compressed(prediction_path,prediction_native=predicted,orientation_to_ras=orientation,affine_rcz_ras=affine)
            row.update(prediction_file=prediction_path.relative_to(ROOT).as_posix(),prediction_sha256=sha(prediction_path),prediction_array_sha256=array_sha(predicted),observed_array_sha256=array_sha(anchors),raw_pchip_display_array_sha256=array_sha(display),decoded_plane_indices=list(range(0,display.shape[2],4)),decoded_sop_uids=sops,observed_pixels_min=float(anchors.min()),observed_pixels_max=float(anchors.max()),prediction_saved_before_truth_decode=True,CUDA_initialized=False)
            del anchors,display,prediction_ras
            # Truth is decoded only after frozen forward output was saved.
            with np.load(ROOT/case['component_file']) as pack:
                truth = pack['connectivity26']>0
            edge = truth&~ndimage.binary_erosion(truth,structure=ndimage.generate_binary_structure(3,1),border_value=0)
            r,c,n = truth.shape
            targets = [z for z in range(1,(n-1)//4*4) if z%4]
            fields = list(score(np.zeros((r,c),dtype=bool),truth[:,:,0],edge[:,:,0]))
            sums = {method:{key:0 for key in fields} for method in METHODS}
            packed = np.empty((len(targets),(r*c+7)//8),dtype=np.uint8)
            rows,fg,boundary = [],0,0
            for index,z in enumerate(targets):
                candidates = visible_candidates(predicted,case['native_spacing_rcz_mm'][:2],z,case['uid'])
                counts = {method:score(mask,truth[:,:,z],edge[:,:,z]) for method,mask in candidates.items()}
                for method,values in counts.items():
                    for key,value in values.items():
                        sums[method][key] += value
                plane_fg,plane_boundary = int(truth[:,:,z].sum()),int(edge[:,:,z].sum())
                fg += plane_fg
                boundary += plane_boundary
                rows.append(dict(z=z,truth_foreground_voxels=plane_fg,truth_boundary_voxels=plane_boundary,strategies=counts))
                packed[index] = np.packbits(candidates['predicted_anchor_union_2mm'].ravel(),bitorder='little')
            metrics = {method:rates(values,fg,boundary,len(targets)*r*c) for method,values in sums.items()}
            p = metrics['predicted_anchor_union_2mm']
            gates = dict(foreground_recall=p['foreground_recall'] is not None and p['foreground_recall']>=.99,boundary_recall=p['boundary_recall'] is not None and p['boundary_recall']>=.99,tile_foreground_recall=p['tile_foreground_recall'] is not None and p['tile_foreground_recall']>=.995,roi_fraction=p['roi_fraction']<=.05,tile_fraction=p['tile_fraction']<=.10)
            mask_path = OUT/(case['patient']+'_'+case['uid']+'_primary_roi.npz')
            np.savez_compressed(mask_path,targets=np.array(targets),primary_roi_packed=packed,native_shape=np.array(truth.shape))
            row.update(complete=True,targets=len(targets),methods=metrics,primary_gates=gates,primary_gate_passed=all(gates.values()),primary_roi_file=mask_path.relative_to(ROOT).as_posix(),primary_roi_sha256=sha(mask_path),target_records=rows,task_competence=dict(full=task_counts(predicted,truth,np.arange(n)),observed=task_counts(predicted,truth,np.arange(0,n,4)),missing=task_counts(predicted,truth,np.array(targets))))
            result['MR_anchor_pixel_arrays_decoded'] = True
            del truth,edge,predicted,packed
        except Exception as exc:
            row.update(error=type(exc).__name__+': '+str(exc),traceback=traceback.format_exc())
            result['errors'].append(dict(patient=case['patient'],uid=case['uid'],error=row['error']))
        row['seconds'] = time.perf_counter()-started
        result['series'].append(row)
        result['processed_series'] = len(result['series'])
        write(OUT/'attempt_01.json',result)
        print(json.dumps({key:row.get(key) for key in ('patient','uid','complete','primary_gate_passed','task_competence','seconds','error')}),flush=True)
    result['complete'] = len(result['series'])==15 and all(r['complete'] for r in result['series'])
    result['strict_all_series_primary_gate_passed'] = result['complete'] and all(r['primary_gate_passed'] for r in result['series'])
    if result['complete']:
        result['patients'] = []
        for patient in sorted({r['patient'] for r in cases}):
            cohort = [r for r in result['series'] if r['patient']==patient]
            averages = {method:{key:float(np.mean([r['methods'][method][key] for r in cohort])) for key in ('foreground_recall','boundary_recall','roi_fraction','tile_foreground_recall','tile_fraction')} for method in METHODS}
            result['patients'].append(dict(patient=patient,development_only=True,series=len(cohort),all_series_primary_gate_passed=all(r['primary_gate_passed'] for r in cohort),series_equal_metrics=averages))
    result['finished_utc'] = datetime.now(timezone.utc).isoformat()
    write(OUT/'attempt_01.json',result)
    print(json.dumps(dict(complete=result['complete'],processed_series=result['processed_series'],strict_all_series_primary_gate_passed=result['strict_all_series_primary_gate_passed'],errors=result['errors'])),flush=True)
    return int(not result['complete'])
if __name__=='__main__':
    raise SystemExit(main())
