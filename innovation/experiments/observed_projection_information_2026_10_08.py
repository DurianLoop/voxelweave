"""Exact metadata projection ranks and a synthetic witness using the real input module."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):
    os.environ[key] = '1'
import hashlib
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
import numpy as np
from mc_rc_3d_direct_observed_2026_10_07 import physical_fields
from mc_rc_observed_only_training_input import ObservedMRI, reconstruct, stats
from mc_rc_3d_baseline_v2_2026_10_07 import torch
from mc_rc_reference_resources_2026_10_07 import resource_guard

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'experiments/mc_rc_3d_direct_observed_qualification_2026_10_07/attempt01.json'
PROOF = ROOT/'experiments/mc_rc_3d_direct_observed_independent_2026_10_07/attempt01.json'
OUT = ROOT/'experiments/observed_projection_information_2026_10_08'
PROTOCOL = ROOT/'OBSERVED_PROJECTION_INFORMATION_PROTOCOL_V2_2026-10-08.md'


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def entry(p):
    return dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def rows(n, m, columns):
    lookup = {column:i for i,column in enumerate(columns)}
    matrix = []
    for j in range(m):
        point = max(Fraction(0), min(Fraction(n-1), Fraction((2*j+1)*n-m, 2*m)))
        left = point.numerator//point.denominator
        alpha = point-left
        row = {}
        for column, weight in ((left,1-alpha),(min(left+1,n-1),alpha)):
            if weight and column in lookup:
                k = lookup[column]
                row[k] = row.get(k,Fraction(0))+weight
        matrix.append(row)
    return matrix


def exact_rank(matrix):
    basis = {}
    for original in matrix:
        row = dict(original)
        while row:
            pivot = min(row)
            if pivot not in basis:
                scale = row[pivot]
                basis[pivot] = {k:v/scale for k,v in row.items()}
                break
            scale = row[pivot]
            for k,value in basis[pivot].items():
                row[k] = row.get(k,Fraction(0))-scale*value
                if row[k] == 0:
                    row.pop(k,None)
    return len(basis)


def array_record(x):
    a = np.ascontiguousarray(x)
    return dict(shape=list(a.shape), dtype=a.dtype.str, values=a.tolist(), sha256=hashlib.sha256(a.tobytes()).hexdigest())


def synthetic_witness():
    variants = {
        'A':np.array([[0,0,3,3],[0,2,1,3],[0,1,2,3],[0,1,2,3]],np.float32)[:,None,:],
        'C':np.array([[0,0,1,3],[0,2,3,3],[0,1,2,3],[0,1,2,3]],np.float32)[:,None,:]}
    grid = dict(native_shape_zrc=[16,4,1], unpadded_shape_zrc=[12,2,1], padding=[[0,0],[0,0],[0,0]])
    projected_grid = dict(native_shape_zrc=[16,2,1], unpadded_shape_zrc=[12,2,1], padding=[[0,0],[0,0],[0,0]])
    outputs = {}
    for name, value in variants.items():
        observed = ObservedMRI(value,(0,4,8,12),16,tuple(map(tuple,np.eye(4))),(),())
        fields, st, native_hashes = physical_fields(observed,grid)
        projected = np.stack((value[:2].mean(0),value[2:].mean(0))).astype(np.float32)
        projected_obs = ObservedMRI(projected,(0,4,8,12),16,tuple(map(tuple,np.eye(4))),(),())
        common_raw = reconstruct(projected_obs,'raw_pchip')
        # The common source statistics are the original observed statistics, equal across A/C.
        normalized = ((common_raw.astype(np.float64)-st['mean'])/st['divisor']).astype(np.float32)
        image = torch.from_numpy(np.ascontiguousarray(normalized.transpose(2,0,1)))[None,None]
        common = torch.nn.functional.interpolate(image,size=[12,2,1],mode='trilinear',align_corners=False)[0,0].numpy()
        outputs[name] = dict(statistics=st, original_observed=array_record(value), projected_observed=array_record(projected),
            numerator=array_record(fields['numerator']), availability=array_record(fields['availability']),
            native_pchip_then_projection=array_record(fields['dense']), projection_then_local_pchip=array_record(common),
            native_field_hashes=native_hashes)
    assert outputs['A']['statistics'] == outputs['C']['statistics']
    assert outputs['A']['statistics']['mean'] == 1.5 and abs(outputs['A']['statistics']['population_std']**2-1.5)<1e-14
    a,c = outputs['A'],outputs['C']
    compare = {}
    for key in ('numerator','availability','projected_observed','native_pchip_then_projection','projection_then_local_pchip'):
        x,y = (np.asarray(v[key]['values'],dtype=np.float32) for v in (a,c))
        compare[key] = dict(bitwise_equal=bool(np.array_equal(x,y)),max_abs_difference=float(np.max(np.abs(x-y))))
    assert compare['numerator']['bitwise_equal'] and compare['availability']['bitwise_equal']
    assert compare['projected_observed']['bitwise_equal'] and compare['projection_then_local_pchip']['bitwise_equal']
    assert not compare['native_pchip_then_projection']['bitwise_equal'] and compare['native_pchip_then_projection']['max_abs_difference']>1e-5
    return dict(native_shape_rcz=[4,1,16], physical_shape_zrc=[12,2,1], observed_indices=[0,4,8,12],
                actual_original_local_pchip_with_linear_boundary_fallback=True,
                variants=outputs, comparison=compare, synthetic_only=True, task_benefit_measured=False)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(exist_ok=False)
    started = time.perf_counter()
    r = dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],
        source_bindings=[entry(p) for p in (Path(__file__),SOURCE,PROOF,PROTOCOL,
            ROOT/'OBSERVED_PROJECTION_INFORMATION_PROTOCOL_2026-10-08.md',
            ROOT/'experiments/mc_rc_3d_direct_observed_2026_10_07.py',
            ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',
            ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py',
            ROOT/'experiments/mc_rc_observed_only_training_input.py')],
        medical_arrays_loaded=0, model_arrays_loaded=0, neural_forwards=0, GPU_forwards=0,
        training_updates=0, validation_data_read=False, confirmation_patients_opened=False,
        locked_IXI_opened=False, publication_claim_confirmed=False, axes=[], series=[],
        float32_inverse_or_condition_number_certified=False, actual_task_benefit_measured=False,
        physical_PCHIP_total_information_rank_claimed=False)
    try:
        r['resources_before'] = resource_guard()
        assert not torch.cuda.is_initialized() and torch.get_num_threads()==torch.get_num_interop_threads()==1
        source, proof = read(SOURCE), read(PROOF)
        assert source['complete'] and proof['complete'] and not source['errors'] and not proof['errors']
        assert len(source['series'])==19 and len({s['patient'] for s in source['series']})==11
        cache = {}
        for s in source['series']:
            grid = s['grid']; nshape=grid['native_shape_zrc']; mshape=grid['unpadded_shape_zrc']
            assert nshape == [s['native_shape_rcz'][2],*s['native_shape_rcz'][:2]]
            axis_ids = []
            ranks = []
            for axis,(n,m) in enumerate(zip(nshape,mshape)):
                columns = tuple(s['observed_indices']) if axis==0 else tuple(range(n))
                key = n,m,columns
                if key not in cache:
                    matrix = rows(n,m,columns)
                    rank = exact_rank(matrix)
                    nonzero = set().union(*(set(row) for row in matrix))
                    record = dict(id=len(r['axes']), native_length=n, physical_length=m,
                        source_columns=list(columns), unknown_columns=len(columns), rank=rank,
                        zero_source_columns=[columns[i] for i in range(len(columns)) if i not in nonzero],
                        full_dimension_upper_bound=min(m,len(columns)),
                        rows=[[[col,v.numerator,v.denominator] for col,v in sorted(row.items())] for row in matrix])
                    cache[key] = record
                    r['axes'].append(record)
                record = cache[key]
                axis_ids.append(record['id']); ranks.append(record['rank'])
            dimension = int(len(s['observed_indices'])*nshape[1]*nshape[2])
            rank = int(ranks[0]*ranks[1]*ranks[2])
            r['series'].append(dict(patient=s['patient'],uid=s['uid'],native_shape_zrc=nshape,
                physical_shape_zrc=mshape,axis_ids_zrc=axis_ids,axis_ranks_zrc=ranks,
                observed_unknown_intensities=dimension,projected_numerator_real_rank=rank,
                nullity=dimension-rank,retained_dimension_fraction=dict(exact=str(Fraction(rank,dimension)),value=rank/dimension),
                all_observed_z_columns_retained=ranks[0]==len(s['observed_indices']),
                fixed_zero_padding_does_not_change_rank=True))
            assert time.perf_counter()-started<600
        patient_rows = []
        for p in sorted({s['patient'] for s in r['series']}):
            subset=[s for s in r['series'] if s['patient']==p]
            dimension=sum(s['observed_unknown_intensities'] for s in subset)
            rank=sum(s['projected_numerator_real_rank'] for s in subset)
            patient_rows.append(dict(patient=p,dimension=dimension,rank=rank,
                retained_dimension_fraction=dict(exact=str(Fraction(rank,dimension)),value=rank/dimension)))
        r['patient_workloads'] = patient_rows
        ratio=sum(Fraction(v['rank'],v['dimension']) for v in patient_rows)/11
        r['summary'] = dict(series_with_nonzero_nullity=sum(s['nullity']>0 for s in r['series']),
            observed_z_full_column_rank_series=sum(s['all_observed_z_columns_retained'] for s in r['series']),
            observed_unknown_intensities_total=sum(s['observed_unknown_intensities'] for s in r['series']),
            projected_numerator_real_rank_total=sum(s['projected_numerator_real_rank'] for s in r['series']),
            patient_workload_equal_retained_dimension_fraction=dict(exact=str(ratio),value=float(ratio)),
            unique_axis_maps=len(r['axes']))
        r['synthetic_witness'] = synthetic_witness()
        r['resources_after'] = resource_guard()
        assert time.perf_counter()-started<600 and not torch.cuda.is_initialized()
        r['complete'] = True
    except Exception as error:
        r['errors'].append(type(error).__name__+': '+str(error))
        r['traceback'] = traceback.format_exc()
    r['elapsed_seconds'] = time.perf_counter()-started
    r['finished_utc'] = datetime.now(timezone.utc).isoformat()
    with (OUT/'attempt01.json').open('x',encoding='utf-8') as f:
        json.dump(r,f,ensure_ascii=False,indent=2); f.write('\n')
    assert sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())<20_000_000
    print(json.dumps({k:r.get(k) for k in ('complete','errors','summary','elapsed_seconds')},ensure_ascii=False),flush=True)
    return 0 if r['complete'] else 1


if __name__=='__main__':
    raise SystemExit(main())
