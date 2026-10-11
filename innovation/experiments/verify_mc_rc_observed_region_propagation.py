"""Raw-label verification using explicit neighbors and cropped disk dilation."""
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
import nibabel as nib
import numpy as np
from scipy.ndimage import binary_dilation
from vs_seg_task_cpu_support import resource_gate
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'experiments/mc_rc_observed_region_propagation'
def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):
            h.update(block)
    return h.hexdigest()
def generator(uid,z,kind):
    seed = int(hashlib.sha256(f'20261003|{uid}|{z}|{kind}'.encode()).hexdigest()[:16],16)
    return np.random.Generator(np.random.PCG64(seed))
def disk_dilation(mask,spacing,radius):
    out = np.zeros_like(mask)
    positions = np.nonzero(mask)
    if not len(positions[0]):
        return out
    extent = np.ceil(radius/np.array(spacing)).astype(int)
    dr,dc = np.meshgrid(np.arange(-extent[0],extent[0]+1),np.arange(-extent[1],extent[1]+1),indexing='ij')
    kernel = np.hypot(dr*spacing[0],dc*spacing[1])<=radius+1e-12
    lower = np.maximum([v.min() for v in positions]-extent,0)
    upper = np.minimum(np.array([v.max()+1 for v in positions])+extent,mask.shape)
    slices = tuple(slice(int(a),int(b)) for a,b in zip(lower,upper))
    out[slices] = binary_dilation(mask[slices],structure=kernel)
    return out
def tiles(mask):
    rows,cols = mask.shape
    selected, areas = np.zeros(((rows+31)//32,(cols+31)//32),dtype=bool),np.zeros(((rows+31)//32,(cols+31)//32),dtype=np.int64)
    for i in range(selected.shape[0]):
        for j in range(selected.shape[1]):
            region = mask[i*32:min(rows,(i+1)*32),j*32:min(cols,(j+1)*32)]
            selected[i,j] = bool(np.any(region))
            areas[i,j] = region.size
    return selected,areas
def expanded_tiles(selected,shape):
    out = np.zeros(shape,dtype=bool)
    for i,j in zip(*np.nonzero(selected)):
        out[i*32:min(shape[0],(i+1)*32),j*32:min(shape[1],(j+1)*32)] = True
    return out
def measure(mask,truth,edge):
    selected,_ = tiles(mask)
    expanded = expanded_tiles(selected,mask.shape)
    return dict(roi_voxels=int(np.count_nonzero(mask)),true_positive_voxels=int(np.count_nonzero(mask&truth)),boundary_covered_voxels=int(np.count_nonzero(mask&edge)),selected_tiles=int(selected.sum()),tile_area_voxels=int(expanded.sum()),tile_true_positive_voxels=int(np.count_nonzero(expanded&truth)))
def derived(counts,truth,edge,total):
    roi,tp = counts['roi_voxels'],counts['true_positive_voxels']
    return dict(counts,foreground_recall=tp/truth if truth else None,boundary_recall=counts['boundary_covered_voxels']/edge if edge else None,roi_precision=tp/roi if roi else None,geometric_mask_dice=2*tp/(roi+truth) if roi+truth else None,roi_fraction=roi/total,roi_foreground_inflation=roi/truth if truth else None,tile_foreground_recall=counts['tile_true_positive_voxels']/truth if truth else None,tile_fraction=counts['tile_area_voxels']/total)
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    resource_gate()
    result,contract = read(OUT/'attempt_01.json'),read(OUT/'run_contract.json')
    if not result['complete'] or result['errors']:
        raise ValueError('Await complete original diagnostic; do not restart it')
    path = OUT/'independent_raw_label_roi_verification.json'
    if path.exists():
        raise ValueError('Preserve prior verification; no overwrite')
    errors, records = [],[]
    def check(ok,why):
        if not ok:
            errors.append(why)
    def equal_dict(computed,stored,why):
        check(computed.keys()==stored.keys(),'Metric schema differs '+why)
        for k in computed.keys()&stored.keys():
            a,b = computed[k],stored[k]
            check(a==b if a is None or b is None else abs(a-b)<=1e-12,'Metric differs '+why+' '+k)
    check(sha(OUT/'run_contract.json')==result['run_contract_sha256'],'Contract lineage differs')
    for item in contract['files']:
        check(sha(ROOT/item['path'])==item['sha256'],'Input changed '+item['path'])
    metadata = {}
    for entry in contract['roster']:
        source = entry['source_result']
        if source not in metadata:
            metadata[source] = {r['series_uid']:r for r in read(ROOT/source)['series']}
    verified_series = {}
    for row in result['series']:
        resource_gate()
        uid = row['uid']
        check(sha(ROOT/row['packed_masks_file'])==row['packed_masks_sha256'],'Packed artifact differs '+uid)
        check(sha(ROOT/row['label_file'])==row['label_sha256'],'Raw label hash differs '+uid)
        m = metadata[row['source_result']][uid]
        matrix = np.array(m['grid']['dicom_rcz_from_label_xyz'],dtype=int)
        img = nib.load(ROOT/row['label_file'])
        native = np.zeros(row['native_shape'],dtype=bool)
        foreground = 0
        for start in range(0,img.shape[2],4):
            slab = np.asarray(img.dataobj[:,:,start:start+4])
            check(slab.nbytes<=32000000 and np.isfinite(slab).all() and np.isin(slab,[0,1]).all(),'Raw slab gate differs '+uid)
            coords = np.array(np.nonzero(slab))
            foreground += coords.shape[1]
            coords[2] += start
            mapped = matrix[:3,:3]@coords + matrix[:3,3,None]
            native[tuple(mapped)] = True
        check(foreground==int(native.sum())==m['label_foreground_voxels'],'Raw native mapping/foreground differs '+uid)
        eroded = native.copy()
        for axis in range(3):
            interior,neighbor = [slice(None)]*3,[slice(None)]*3
            interior[axis],neighbor[axis] = slice(1,None),slice(None,-1)
            eroded[tuple(interior)] &= native[tuple(neighbor)]
            interior[axis],neighbor[axis] = slice(None,-1),slice(1,None)
            eroded[tuple(interior)] &= native[tuple(neighbor)]
            for index in (0,-1):
                border = [slice(None)]*3
                border[axis] = index
                eroded[tuple(border)] = False
        boundary = native&~eroded
        del eroded
        rows,cols,planes = native.shape
        anchors = list(range(0,planes,4))
        targets = [z for z in range(anchors[0]+1,anchors[-1]) if z not in anchors]
        check(len(targets)==row['targets'] and [p['z'] for p in row['target_records']]==targets,'Complete target support differs '+uid)
        sums = {method:{key:0 for key in row['methods'][method] if key in ('roi_voxels','true_positive_voxels','boundary_covered_voxels','selected_tiles','tile_area_voxels','tile_true_positive_voxels')} for method in contract['methods']}
        total_truth,total_edges = 0,0
        interval_cache = {}
        with np.load(ROOT/row['packed_masks_file']) as saved:
            check(np.array_equal(saved['targets'],targets) and np.array_equal(saved['native_shape'],native.shape),'Saved target/grid metadata differs '+uid)
            for index,z in enumerate(targets):
                left = max(a for a in anchors if a<z)
                right = min(a for a in anchors if a>z)
                if left not in interval_cache:
                    union = native[:,:,left]|native[:,:,right]
                    interval_cache = {left:(union,{r:disk_dilation(union,row['native_spacing_rcz_mm'][:2],r) for r in (1.,2.,4.)})}
                union,dilated = interval_cache[left]
                primary = dilated[2.]
                random_pixels = np.zeros(rows*cols,dtype=bool)
                random_pixels[generator(uid,z,'pixels').choice(rows*cols,int(primary.sum()),replace=False)] = True
                random_pixels = random_pixels.reshape(rows,cols)
                selected,areas = tiles(primary)
                random_selected = np.zeros(selected.shape,dtype=bool)
                g = generator(uid,z,'tiles')
                for area in sorted(set(areas.ravel().tolist())):
                    indices = np.flatnonzero(areas.ravel()==area)
                    n = int(np.count_nonzero(selected&(areas==area)))
                    random_selected.ravel()[g.choice(indices,n,replace=False)] = True
                random_tiles = expanded_tiles(random_selected,(rows,cols))
                candidates = dict(nearest=native[:,:,left if z-left<=right-z else right],bracket_union=union,union_1mm=dilated[1.],union_2mm=primary,union_4mm=dilated[4.],shifted_union_2mm=np.roll(primary,(rows//2,cols//2),axis=(0,1)),random_pixels_matched_union_2mm=random_pixels,full_plane=np.ones((rows,cols),dtype=bool),random_tiles_matched_union_2mm=random_tiles)
                for name,mask in [('primary_roi_packed',primary),('random_pixels_packed',random_pixels),('random_tiles_packed',random_tiles)]:
                    decoded = np.unpackbits(saved[name][index],bitorder='little')[:rows*cols].reshape(rows,cols).astype(bool)
                    check(np.array_equal(mask,decoded),'All-target packed mask differs '+uid+' '+str(z)+' '+name)
                truth,edge = native[:,:,z],boundary[:,:,z]
                fg,edges = int(truth.sum()),int(edge.sum())
                total_truth += fg
                total_edges += edges
                expected = row['target_records'][index]
                check(expected['truth_foreground_voxels']==fg and expected['truth_boundary_voxels']==edges and expected['left_anchor']==left and expected['right_anchor']==right,'Truth/support metadata differs '+uid+' '+str(z))
                for method,mask in candidates.items():
                    counts = measure(mask,truth,edge)
                    equal_dict(counts,expected['strategies'][method],uid+' '+str(z)+' '+method)
                    for key,value in counts.items():
                        sums[method][key] += value
                check(random_pixels.sum()==primary.sum() and int(random_tiles.sum())==int(expanded_tiles(selected,(rows,cols)).sum()) and selected.sum()==random_selected.sum(),'Random area/count matching differs '+uid+' '+str(z))
        metrics = {method:derived(counts,total_truth,total_edges,len(targets)*rows*cols) for method,counts in sums.items()}
        for method,values in metrics.items():
            equal_dict(values,row['methods'][method],uid+' '+method)
        p = metrics['union_2mm']
        gate = dict(foreground_recall=p['foreground_recall'] is not None and p['foreground_recall']>=.99,boundary_recall=p['boundary_recall'] is not None and p['boundary_recall']>=.99,tile_foreground_recall=p['tile_foreground_recall'] is not None and p['tile_foreground_recall']>=.995,roi_fraction=p['roi_fraction']<=.05,tile_fraction=p['tile_fraction']<=.10)
        check(gate==row['primary_geometric_gates'] and all(gate.values())==row['primary_geometric_gate_passed'],'Primary gate differs '+uid)
        verified_series[uid] = metrics
        records.append(dict(patient=row['patient'],uid=uid,raw_label_foreground_voxels=foreground,missing_targets=len(targets),strategies_verified=len(metrics),primary_gates_passed=all(gate.values())))
        print(json.dumps(records[-1]),flush=True)
    for patient in result['patients']:
        cohort = [r for r in result['series'] if r['patient']==patient['patient']]
        for method,values in patient['series_equal_metrics'].items():
            recomputed = {key:float(np.mean([verified_series[r['uid']][method][key] for r in cohort])) for key in values}
            equal_dict(recomputed,values,patient['patient']+' '+method)
        check(len(cohort)==patient['series'] and patient['all_series_primary_gates_passed']==all(r['primary_geometric_gate_passed'] for r in cohort),'Whole-patient grouping differs')
    check(result['strict_all_series_geometric_gate_passed']==all(r['primary_geometric_gate_passed'] for r in result['series']),'All-series gate differs')
    proof = dict(created_utc=datetime.now(timezone.utc).isoformat(),verification_script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),run_contract_sha256=sha(OUT/'run_contract.json'),counts=dict(series=len(records),patients=len({r['patient'] for r in records}),raw_label_foreground_voxels=sum(r['raw_label_foreground_voxels'] for r in records),missing_targets=sum(r['missing_targets'] for r in records),strategies_per_target=9,packed_masks_per_target=3),scope='all raw-label native pixels, explicit six-neighbor boundary, integer-disk dilation, all target/strategy counts and matched random budget; PCG64 library reused',series=records,errors=errors,strict_all_series_geometric_gate_passed=result['strict_all_series_geometric_gate_passed'],truth_observed_masks_used_as_inputs=True,MR_pixels_decoded=False,gpu_used=False,scientific_independent_validation_patients=0,publication_claim_confirmed=False)
    with path.open('x',encoding='utf-8') as f:
        f.write(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(counts=proof['counts'],errors=errors,strict_all_series_geometric_gate_passed=proof['strict_all_series_geometric_gate_passed'])),flush=True)
    return int(bool(errors))
if __name__=='__main__':
    raise SystemExit(main())
