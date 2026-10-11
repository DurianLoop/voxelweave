"""All-source replay: independent observed ordering, Hermite, voxel orientation."""
from __future__ import annotations
import hashlib
import json
import os
import sys
import zipfile
from datetime import datetime,timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key] = '1'
import nibabel as nib
import numpy as np
import pydicom
import torch
from vs_seg_task_cpu_support import resource_gate,load_model
from vs_seg_full_volume_runtime import array_sha,inference,load_tuple_inferer
from mc_rc_frozen_predicted_region_cpu import display_from_anchors
from verify_mc_rc_observed_region_propagation import disk_dilation,tiles,expanded_tiles,measure,derived,generator
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'experiments/mc_rc_frozen_predicted_region_cpu'
def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):
            h.update(b)
    return h.hexdigest()
def independently_decode(case):
    records = []
    with zipfile.ZipFile(ROOT/case['mr_zip_file']) as archive:
        for member in archive.infolist():
            if not member.filename.lower().endswith('.dcm') or member.is_dir():
                continue
            with archive.open(member) as f:
                ds = pydicom.dcmread(f,stop_before_pixels=True)
            records.append((member.filename,ds))
        orient = np.array(records[0][1].ImageOrientationPatient,dtype=float)
        normal = np.cross(orient[:3],orient[3:])
        records.sort(key=lambda r:float(np.array(r[1].ImagePositionPatient,dtype=float)@normal))
        if [name for name,ds in records]!=case['ordered_zip_members'] or len(records)!=case['native_shape'][2]:
            raise ValueError('Independent raw header ordering/count differs')
        arrays,sops = [],[]
        for index in range(0,len(records),4):
            name,header = records[index]
            with archive.open(name) as f:
                ds = pydicom.dcmread(f)
            if str(ds.SOPInstanceUID)!=str(header.SOPInstanceUID) or str(ds.PatientID)!=case['patient'] or str(ds.SeriesInstanceUID)!=case['uid'] or str(ds.StudyInstanceUID)!=case['study_uid'] or str(ds.PhotometricInterpretation)!='MONOCHROME2':
                raise ValueError('Independent visible identity differs')
            arrays.append(ds.pixel_array.astype(np.float32)*float(ds.get('RescaleSlope',1))+float(ds.get('RescaleIntercept',0)))
            sops.append(str(ds.SOPInstanceUID))
    return np.stack(arrays,axis=2),sops,len(records)
def hermite_display(anchors,n):
    out = np.zeros((*anchors.shape[:2],n),dtype=np.float32)
    observed = list(range(0,n,4))
    out[:,:,observed] = anchors
    for z in range(1,observed[-1]):
        if not z%4:
            continue
        i,t = z//4,(z%4)/4
        if i<1 or i+2>=anchors.shape[2]:
            plane = (1-t)*anchors[:,:,i].astype(np.float64)+t*anchors[:,:,i+1].astype(np.float64)
        else:
            y = anchors[:,:,i-1:i+3].astype(np.float64)
            d0,d1,d2 = np.moveaxis(np.diff(y,axis=2),2,0)
            m1 = np.divide(2*d0*d1,d0+d1,out=np.zeros_like(d0),where=(d0*d1)>0)
            m2 = np.divide(2*d1*d2,d1+d2,out=np.zeros_like(d1),where=(d1*d2)>0)
            plane = (2*t**3-3*t*t+1)*y[:,:,1]+(t**3-2*t*t+t)*m1+(-2*t**3+3*t*t)*y[:,:,2]+(t**3-t*t)*m2
        out[:,:,z] = plane
    out[:,:,observed[-1]+1:] = anchors[:,:,-1,None]
    return out
def explicit_boundary(native):
    core = native.copy()
    for axis in range(3):
        for sign in (-1,1):
            target,neighbor = [slice(None)]*3,[slice(None)]*3
            target[axis] = slice(1,None) if sign==-1 else slice(None,-1)
            neighbor[axis] = slice(None,-1) if sign==-1 else slice(1,None)
            core[tuple(target)] &= native[tuple(neighbor)]
        for index in (0,-1):
            border = [slice(None)]*3
            border[axis] = index
            core[tuple(border)] = False
    return native&~core
def raw_truth(case,metadata):
    img = nib.load(ROOT/case['label_file'])
    transform = np.array(metadata['grid']['dicom_rcz_from_label_xyz'],dtype=int)
    native = np.zeros(case['native_shape'],dtype=bool)
    for start in range(0,img.shape[2],4):
        slab = np.asarray(img.dataobj[:,:,start:start+4])
        if slab.nbytes>32000000 or not np.isfinite(slab).all() or not np.isin(slab,[0,1]).all():
            raise ValueError('Independent raw label slab gate differs')
        xyz = np.array(np.nonzero(slab))
        xyz[2] += start
        native[tuple(transform[:3,:3]@xyz+transform[:3,3,None])] = True
    return native
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    resource_gate()
    result,contract = read(OUT/'attempt_01.json'),read(OUT/'run_contract.json')
    if not result['complete'] or result['errors'] or len(result['series'])!=15:
        raise ValueError('Await terminal complete15 primary session; no partial-cohort verification')
    path = OUT/'independent_observed_input_roi_and_model_replay.json'
    if path.exists():
        raise ValueError('Retain previous proof; no blind replay/overwrite')
    errors,records,verified_metrics = [],[],{}
    def check(ok,why):
        if not ok:
            errors.append(why)
    def equal(a,b,why):
        check(a.keys()==b.keys(),'Schema differs '+why)
        for key in a.keys()&b.keys():
            check(a[key]==b[key] if a[key] is None or b[key] is None else abs(a[key]-b[key])<=1e-12,'Metric differs '+why+' '+key)
    for item in contract['files']:
        check(sha(ROOT/item['path'])==item['sha256'],'Frozen input changed '+item['path'])
    check(sha(OUT/'run_contract.json')==result['run_contract_sha256'],'Primary contract lineage differs')
    geometry = read(ROOT/'experiments/mc_rc_observed_region_propagation/attempt_01.json')
    sources = {r['uid']:r['source_result'] for r in geometry['series']}
    metadata = {}
    for source in set(sources.values()):
        metadata.update({r['series_uid']:r for r in read(ROOT/source)['series']})
    by_uid = {r['uid']:r for r in result['series']}
    model,runtime = load_model()
    inferer = load_tuple_inferer()
    for case in contract['cases']:
        resource_gate()
        uid,stored = case['uid'],by_uid[case['uid']]
        anchors,sops,headers = independently_decode(case)
        check(array_sha(anchors)==stored['observed_array_sha256'] and sops==stored['decoded_sop_uids'],'Independent genuine-anchor decode differs '+uid)
        display = display_from_anchors(anchors,case['native_shape'][2])
        independent = hermite_display(anchors,case['native_shape'][2])
        max_error = float(np.max(abs(display-independent)))
        tolerance = max(1e-4,float(anchors.max()-anchors.min())*5e-7)
        check(max_error<=tolerance and array_sha(display)==stored['raw_pchip_display_array_sha256'],'Independent Hermite/exact task input differs '+uid)
        check(np.array_equal(display[:,:,::4],anchors),'Fresh display modified real observations '+uid)
        affine = np.array(case['affine_rcz_ras'])
        orientation = nib.orientations.ornt_transform(nib.orientations.io_orientation(affine),nib.orientations.axcodes2ornt('RAS'))
        pred_ras = inference(model,inferer,display,orientation)
        transform = np.rint(nib.orientations.inv_ornt_aff(orientation,case['native_shape'])).astype(int)
        coords = np.array(np.nonzero(pred_ras))
        native_prediction = np.zeros(case['native_shape'],dtype=bool)
        native_prediction[tuple(transform[:3,:3]@coords+transform[:3,3,None])] = True
        with np.load(ROOT/stored['prediction_file']) as pack:
            predicted = pack['prediction_native']
            replay_equal = bool(np.array_equal(native_prediction,predicted))
            check(replay_equal and array_sha(predicted)==stored['prediction_array_sha256'],'Fresh CPU forward/explicit native voxel mapping differs '+uid)
        check(sha(ROOT/stored['prediction_file'])==stored['prediction_sha256'] and not torch.cuda.is_initialized(),'Prediction artifact/CPU proof differs '+uid)
        del display,independent,anchors,pred_ras,native_prediction
        truth = raw_truth(case,metadata[uid])
        edge = explicit_boundary(truth)
        r,c,n = truth.shape
        targets = [z for z in range(1,(n-1)//4*4) if z%4]
        sums = {method:{key:0 for key in ('roi_voxels','true_positive_voxels','boundary_covered_voxels','selected_tiles','tile_area_voxels','tile_true_positive_voxels')} for method in contract['methods']}
        fg,edges = 0,0
        with np.load(ROOT/stored['primary_roi_file']) as pack:
            check(np.array_equal(pack['targets'],targets),'Packed target support differs '+uid)
            for index,z in enumerate(targets):
                left,right = z//4*4,z//4*4+4
                union = predicted[:,:,left]|predicted[:,:,right]
                primary = disk_dilation(union,case['native_spacing_rcz_mm'][:2],2.)
                selected,areas = tiles(primary)
                random_selected = np.zeros_like(selected)
                g = generator(uid,z,'tiles')
                for area in np.unique(areas):
                    eligible = np.flatnonzero(areas.ravel()==area)
                    count = int((selected&(areas==area)).sum())
                    random_selected.ravel()[g.choice(eligible,count,replace=False)] = True
                random_pixels = np.zeros(r*c,dtype=bool)
                random_pixels[generator(uid,z,'pixels').choice(r*c,int(primary.sum()),replace=False)] = True
                candidates = dict(predicted_anchor_union_2mm=primary,predicted_bracket_union=union,dense_prediction_2mm=disk_dilation(predicted[:,:,z],case['native_spacing_rcz_mm'][:2],2.),shifted_primary=np.roll(primary,(r//2,c//2),axis=(0,1)),random_pixels_matched_primary=random_pixels.reshape(r,c),random_tiles_matched_primary=expanded_tiles(random_selected,(r,c)))
                decoded = np.unpackbits(pack['primary_roi_packed'][index],bitorder='little')[:r*c].reshape(r,c).astype(bool)
                check(np.array_equal(decoded,primary),'Independent all-target primary ROI differs '+uid+' '+str(z))
                expected = stored['target_records'][index]
                fg += int(truth[:,:,z].sum())
                edges += int(edge[:,:,z].sum())
                check(expected['truth_foreground_voxels']==int(truth[:,:,z].sum()) and expected['truth_boundary_voxels']==int(edge[:,:,z].sum()),'Independent raw truth/edge differs '+uid)
                for method,mask in candidates.items():
                    counts = measure(mask,truth[:,:,z],edge[:,:,z])
                    equal(counts,expected['strategies'][method],uid+' '+str(z)+' '+method)
                    for key,value in counts.items():
                        sums[method][key] += value
        metrics = {method:derived(values,fg,edges,len(targets)*r*c) for method,values in sums.items()}
        for method,values in metrics.items():
            equal(values,stored['methods'][method],uid+' '+method)
        for region,planes in [('full',np.arange(n)),('observed',np.arange(0,n,4)),('missing',np.array(targets))]:
            pred,ref = predicted[:,:,planes],truth[:,:,planes]
            pp,tt,tp = int(pred.sum()),int(ref.sum()),int((pred&ref).sum())
            values = dict(predicted_voxels=pp,truth_voxels=tt,true_positive_voxels=tp,dice=2*tp/(pp+tt) if pp+tt else None,recall=tp/tt if tt else None,precision=tp/pp if pp else None)
            equal(values,stored['task_competence'][region],uid+' competence '+region)
        p = metrics['predicted_anchor_union_2mm']
        gate = bool(p['foreground_recall']>=.99 and p['boundary_recall']>=.99 and p['tile_foreground_recall']>=.995 and p['roi_fraction']<=.05 and p['tile_fraction']<=.10)
        check(gate==stored['primary_gate_passed'],'Independent primary gate differs '+uid)
        verified_metrics[uid] = metrics
        records.append(dict(patient=case['patient'],uid=uid,raw_headers_checked=headers,observed_arrays_decoded=len(sops),missing_targets=len(targets),maximum_Hermite_display_difference=max_error,Hermite_tolerance=tolerance,fresh_model_replay_bitwise_prediction_equal=replay_equal,primary_gate_passed=gate))
        print(json.dumps(records[-1]),flush=True)
    for patient in result['patients']:
        cohort = [r for r in result['series'] if r['patient']==patient['patient']]
        for method,values in patient['series_equal_metrics'].items():
            recomputed = {key:float(np.mean([verified_metrics[r['uid']][method][key] for r in cohort])) for key in values}
            equal(recomputed,values,patient['patient']+' '+method)
        check(patient['series']==len(cohort) and patient['all_series_primary_gate_passed']==all(r['primary_gate_passed'] for r in cohort),'Whole-patient grouping differs '+patient['patient'])
    check(result['strict_all_series_primary_gate_passed']==all(r['primary_gate_passed'] for r in records),'All-series primary outcome differs')
    proof = dict(created_utc=datetime.now(timezone.utc).isoformat(),verification_script_sha256=sha(__file__),geometry_verifier_helper_sha256=sha(ROOT/'experiments/verify_mc_rc_observed_region_propagation.py'),result_sha256=sha(OUT/'attempt_01.json'),run_contract_sha256=sha(OUT/'run_contract.json'),model_runtime=runtime,counts=dict(series=len(records),patients=len({r['patient'] for r in records}),fresh_neural_replays=len(records),raw_headers_checked=sum(r['raw_headers_checked'] for r in records),genuine_observed_arrays_decoded=sum(r['observed_arrays_decoded'] for r in records),missing_targets=sum(r['missing_targets'] for r in records),strategies_per_target=6),series=records,errors=errors,scope='independent raw-anchor ordering/Hermite, exact verified-input frozen forward replay, explicit native voxel mapping and all ROI/raw-label scoring; author inferer, Pydicom and PCG64 libraries reused',MR_hidden_pixel_arrays_decoded=False,gpu_used=False,truth_masks_used_as_model_or_ROI_inputs=False,strict_all_series_primary_gate_passed=result['strict_all_series_primary_gate_passed'],scientific_independent_validation_patients=0,publication_claim_confirmed=False)
    with path.open('x',encoding='utf-8') as f:
        f.write(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(counts=proof['counts'],errors=errors,strict_all_series_primary_gate_passed=proof['strict_all_series_primary_gate_passed'])),flush=True)
    return int(bool(errors))
if __name__=='__main__':
    raise SystemExit(main())
