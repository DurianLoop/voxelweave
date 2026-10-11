"""Fixed developer-only oracle-anchor ROI diagnostic, with complete costs."""
from __future__ import annotations
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key] = '1'
import numpy as np
from scipy import ndimage
from vs_seg_task_cpu_support import resource_gate
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'experiments/mc_rc_label_anchor_visibility'
OUT = ROOT/'experiments/mc_rc_observed_region_propagation'
PLAN = ROOT/'MC_RC_OBSERVED_REGION_PROPAGATION_PLAN_2026-10-03.md'
METHODS = ['nearest','bracket_union','union_1mm','union_2mm','union_4mm','shifted_union_2mm','random_pixels_matched_union_2mm','full_plane','random_tiles_matched_union_2mm']
SOURCE_PROOFS = {
 'experiments/mc_rc_native_t2_label_gate/label_grid_attempt_01.json':'experiments/mc_rc_native_t2_label_gate/independent_raw_geometry_grid_verification.json',
 'experiments/mc_rc_004_006_native_label_gate/resource_followup_attempt_01.json':'experiments/mc_rc_004_006_native_label_gate/independent_raw_geometry_grid_verification.json',
 'experiments/mc_rc_007_010_native_label_gate/attempt_01.json':'experiments/mc_rc_007_010_native_label_gate/independent_raw_geometry_grid_verification.json',
}
def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):
            h.update(block)
    return h.hexdigest()
def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,obj):
    Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rng(uid,z,kind):
    seed = int(hashlib.sha256(('20261003|%s|%d|%s'%(uid,z,kind)).encode()).hexdigest()[:16],16)
    return np.random.Generator(np.random.PCG64(seed))
def grid(mask):
    r,c = mask.shape
    padded = np.zeros(((r+31)//32*32,(c+31)//32*32),dtype=bool)
    padded[:r,:c] = mask
    return padded.reshape((r+31)//32,32,(c+31)//32,32).any(axis=(1,3))
def expand(selected,shape):
    return np.repeat(np.repeat(selected,32,axis=0),32,axis=1)[:shape[0],:shape[1]]
def score(mask,truth,boundary):
    g = grid(mask)
    tile_mask = expand(g,mask.shape)
    return dict(roi_voxels=int(mask.sum()),true_positive_voxels=int((mask&truth).sum()),boundary_covered_voxels=int((mask&boundary).sum()),selected_tiles=int(g.sum()),tile_area_voxels=int(tile_mask.sum()),tile_true_positive_voxels=int((tile_mask&truth).sum()))
def rates(counts,foreground,boundary,total_area):
    roi,tp = counts['roi_voxels'],counts['true_positive_voxels']
    return dict(counts,foreground_recall=tp/foreground if foreground else None,boundary_recall=counts['boundary_covered_voxels']/boundary if boundary else None,roi_precision=tp/roi if roi else None,geometric_mask_dice=2*tp/(roi+foreground) if roi+foreground else None,roi_fraction=roi/total_area,roi_foreground_inflation=roi/foreground if foreground else None,tile_foreground_recall=counts['tile_true_positive_voxels']/foreground if foreground else None,tile_fraction=counts['tile_area_voxels']/total_area)
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    resources = resource_gate()
    base, prior, verified = read(BASE/'attempt_01.json'),read(BASE/'run_contract.json'),read(BASE/'independent_label_phase_verification.json')
    if not base['complete'] or verified['errors'] or sha(BASE/'attempt_01.json')!=verified['result_sha256'] or len(base['series'])!=15:
        raise ValueError('Prior all-label verification is incomplete or stale')
    inputs = [PLAN,Path(__file__),ROOT/'experiments/vs_seg_task_cpu_support.py',BASE/'attempt_01.json',BASE/'run_contract.json',BASE/'independent_label_phase_verification.json']
    metadata, source_proofs = {}, {}
    for source,proof in SOURCE_PROOFS.items():
        metadata[source] = {r['series_uid']:r for r in read(ROOT/source)['series']}
        p = read(ROOT/proof)
        if p['errors']:
            raise ValueError('Source proof failed ' + proof)
        source_proofs[source] = {r['uid']:r for r in p['series']}
        inputs += [ROOT/source,ROOT/proof]
    roster = []
    for row in base['series']:
        uid,source = row['uid'],row['source_result']
        m = metadata[source][uid]
        if not m['header_and_label_grid_preflight_passed']:
            raise ValueError('Selected source no longer qualified')
        spacing = source_proofs[source][uid].get('native_spacing_rcz_mm')
        if spacing is None:
            spacing = np.linalg.norm(np.array(m['dicom_affine_rcz_ras'])[:3,:3],axis=0).tolist()
        if sha(ROOT/row['component_file'])!=row['component_sha256'] or sha(ROOT/row['label_file'])!=row['label_sha256']:
            raise ValueError('Authenticated component/label hash differs')
        estimate = int(np.prod(row['native_shape']))*7 + len(range(1,row['native_shape'][2]-1))*((row['native_shape'][0]*row['native_shape'][1]+7)//8)*3 + row['native_shape'][0]*row['native_shape'][1]*32
        if estimate>512000000:
            raise ValueError('Prespecified temporary-memory estimate exceeds 512MB')
        roster.append(dict(patient=row['patient'],uid=uid,description=row['description'],source_result=source,label_file=row['label_file'],label_sha256=row['label_sha256'],component_file=row['component_file'],component_sha256=row['component_sha256'],native_shape=row['native_shape'],native_spacing_rcz_mm=spacing,estimated_temporary_bytes=estimate))
        inputs += [ROOT/row['component_file'],ROOT/row['label_file']]
    if [r['uid'] for r in roster]!=prior['selected_uids'] or len({r['patient'] for r in roster})!=8:
        raise ValueError('Frozen 15/8 developer roster differs')
    OUT.mkdir(exist_ok=False)
    contract = dict(created_utc=datetime.now(timezone.utc).isoformat(),developer_only=True,methods=METHODS,primary_method='union_2mm',radii_mm=[1.,2.,4.],phase=0,factor=4,tile_side=32,strict_gate=dict(foreground_recall=.99,boundary_recall=.99,tile_foreground_recall=.995,maximum_roi_fraction=.05,maximum_tile_fraction=.10),seed_protocol='SHA256(20261003|SeriesUID|z|pixels or tiles) first 16 hex; PCG64',roster=roster,excluded_sources=base['excluded_sources'],files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(set(inputs))])
    write(OUT/'run_contract.json',contract)
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(),run_contract_sha256=sha(OUT/'run_contract.json'),resources=resources,complete=False,errors=[],series=[],gpu_used=False,MR_pixels_decoded=False,neural_networks_executed=0,truth_observed_masks_used_as_inputs=True,scientific_independent_validation_patients=0,publication_claim_confirmed=False)
    for entry in roster:
        resource_gate()
        with np.load(ROOT/entry['component_file']) as pack:
            native = pack['connectivity26']>0
        boundary = native & ~ndimage.binary_erosion(native,structure=ndimage.generate_binary_structure(3,1),border_value=0)
        uid = entry['uid']
        r,c,n = native.shape
        last = (n-1)//4*4
        targets = [z for z in range(1,last) if z%4]
        fields = list(score(np.zeros((r,c),dtype=bool),native[:,:,0],boundary[:,:,0]))
        sums = {method:{key:0 for key in fields} for method in METHODS}
        costs = np.array([[min(32,r-i*32)*min(32,c-j*32) for j in range((c+31)//32)] for i in range((r+31)//32)])
        masks = {key:np.empty((len(targets),(r*c+7)//8),dtype=np.uint8) for key in ('primary_roi_packed','random_pixels_packed','random_tiles_packed')}
        rows,truth_count,boundary_count = [],0,0
        interval_cache = {}
        for index,z in enumerate(targets):
            left,right = z//4*4,z//4*4+4
            if left not in interval_cache:
                union = native[:,:,left] | native[:,:,right]
                distance = ndimage.distance_transform_edt(~union,sampling=entry['native_spacing_rcz_mm'][:2]) if union.any() else np.full((r,c),np.inf)
                interval_cache = {left:(union,distance)}
            union,distance = interval_cache[left]
            primary = distance<=2.+1e-12
            random_pixel = np.zeros(r*c,dtype=bool)
            random_pixel[rng(uid,z,'pixels').choice(r*c,size=int(primary.sum()),replace=False)] = True
            random_pixel = random_pixel.reshape(r,c)
            primary_grid = grid(primary)
            random_grid = np.zeros(primary_grid.shape,dtype=bool)
            for area in np.unique(costs):
                eligible = np.flatnonzero(costs.ravel()==area)
                amount = int((primary_grid&(costs==area)).sum())
                # A fresh generator is advanced across size groups, not reseeded per group.
                if area==np.unique(costs)[0]:
                    tile_rng = rng(uid,z,'tiles')
                random_grid.ravel()[tile_rng.choice(eligible,size=amount,replace=False)] = True
            random_tile_mask = expand(random_grid,(r,c))
            methods = dict(nearest=native[:,:,left if z-left<=right-z else right],bracket_union=union,union_1mm=distance<=1.+1e-12,union_2mm=primary,union_4mm=distance<=4.+1e-12,shifted_union_2mm=np.roll(primary,(r//2,c//2),axis=(0,1)),random_pixels_matched_union_2mm=random_pixel,full_plane=np.ones((r,c),dtype=bool),random_tiles_matched_union_2mm=random_tile_mask)
            truth,edge = native[:,:,z],boundary[:,:,z]
            foreground,boundary_voxels = int(truth.sum()),int(edge.sum())
            truth_count += foreground
            boundary_count += boundary_voxels
            scored = {key:score(mask,truth,edge) for key,mask in methods.items()}
            for method,counts in scored.items():
                for key,value in counts.items():
                    sums[method][key] += value
            if scored['random_pixels_matched_union_2mm']['roi_voxels']!=scored['union_2mm']['roi_voxels'] or scored['random_tiles_matched_union_2mm']['roi_voxels']!=scored['union_2mm']['tile_area_voxels'] or scored['random_tiles_matched_union_2mm']['selected_tiles']!=scored['union_2mm']['selected_tiles']:
                raise ValueError('Matched random budget differs')
            rows.append(dict(z=z,residue=z%4,left_anchor=left,right_anchor=right,truth_foreground_voxels=foreground,truth_boundary_voxels=boundary_voxels,strategies=scored))
            for name,mask in [('primary_roi_packed',primary),('random_pixels_packed',random_pixel),('random_tiles_packed',random_tile_mask)]:
                masks[name][index] = np.packbits(mask.ravel(),bitorder='little')
        metrics = {method:rates(counts,truth_count,boundary_count,len(targets)*r*c) for method,counts in sums.items()}
        p = metrics['union_2mm']
        gates = dict(foreground_recall=p['foreground_recall'] is not None and p['foreground_recall']>=.99,boundary_recall=p['boundary_recall'] is not None and p['boundary_recall']>=.99,tile_foreground_recall=p['tile_foreground_recall'] is not None and p['tile_foreground_recall']>=.995,roi_fraction=p['roi_fraction']<=.05,tile_fraction=p['tile_fraction']<=.10)
        path = OUT/(entry['patient']+'_'+uid+'_packed_masks.npz')
        np.savez_compressed(path,targets=np.array(targets),native_shape=np.array(native.shape),**masks)
        record = dict(entry,targets=len(targets),truth_missing_foreground_voxels=truth_count,truth_missing_boundary_voxels=boundary_count,methods=metrics,primary_geometric_gates=gates,primary_geometric_gate_passed=all(gates.values()),packed_masks_file=path.relative_to(ROOT).as_posix(),packed_masks_sha256=sha(path),target_records=rows)
        result['series'].append(record)
        write(OUT/'attempt_01.json',result)
        print(json.dumps(dict(patient=entry['patient'],uid=uid,primary={key:p[key] for key in ('foreground_recall','boundary_recall','roi_fraction','tile_foreground_recall','tile_fraction')},gates=gates)),flush=True)
        del native,boundary,interval_cache,masks
    patients = []
    for patient in sorted({r['patient'] for r in roster}):
        rows = [r for r in result['series'] if r['patient']==patient]
        averages = {method:{key:float(np.mean([r['methods'][method][key] for r in rows])) for key in ('foreground_recall','boundary_recall','roi_fraction','tile_foreground_recall','tile_fraction')} for method in METHODS}
        patients.append(dict(patient=patient,development_only=True,series=len(rows),all_series_primary_gates_passed=all(r['primary_geometric_gate_passed'] for r in rows),series_equal_metrics=averages))
    result.update(complete=len(result['series'])==15,patients=patients,strict_all_series_geometric_gate_passed=all(r['primary_geometric_gate_passed'] for r in result['series']),finished_utc=datetime.now(timezone.utc).isoformat())
    write(OUT/'attempt_01.json',result)
    print(json.dumps(dict(complete=result['complete'],series=len(result['series']),patients=len(patients),strict_all_series_geometric_gate_passed=result['strict_all_series_geometric_gate_passed'])),flush=True)
if __name__=='__main__':
    main()
