"""Independent integer modular rank certificates and rational local-PCHIP witness."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):
    os.environ[key] = '1'
import hashlib
import json
import math
import sys
import time
import traceback
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
import numpy as np
from mc_rc_reference_resources_2026_10_07 import resource_guard

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'experiments/observed_projection_information_2026_10_08/attempt01.json'
META = ROOT/'experiments/mc_rc_3d_direct_observed_qualification_2026_10_07/attempt01.json'
OUT = SOURCE.parent/'independent_modular_rational_attempt01.json'
PRIMES = (1000003,1000033)


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def entry(p):
    return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,
                sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def integer_matrix(n,m,columns):
    matrix=np.zeros((m,len(columns)),np.int64)
    lookup={int(v):i for i,v in enumerate(columns)}
    denominator=2*m
    for j in range(m):
        q=(2*j+1)*n-m
        if q<0:
            pieces=[(0,denominator)]
        elif q>=denominator*(n-1):
            pieces=[(n-1,denominator)]
        else:
            left,remainder=divmod(q,denominator)
            pieces=[(left,denominator-remainder),(left+1,remainder)]
        for column,value in pieces:
            if column in lookup:
                matrix[j,lookup[column]]+=value
    return matrix


def modular_rank(matrix,prime):
    a=matrix.copy()%prime
    row=0
    for column in range(a.shape[1]):
        candidates=np.flatnonzero(a[row:,column])
        if not len(candidates):
            continue
        pivot=row+int(candidates[0])
        a[[row,pivot]]=a[[pivot,row]]
        a[row]=(a[row]*pow(int(a[row,column]),-1,prime))%prime
        affected=row+1+np.flatnonzero(a[row+1:,column])
        if len(affected):
            a[affected]=(a[affected]-a[affected,column,None]*a[row])%prime
        row+=1
        if row==a.shape[0]:
            break
    return row


def fill_local(anchor_rows):
    filled=[]
    for row in anchor_rows:
        a=[Fraction(v) for v in row]
        slopes=[]
        d=[(a[i+1]-a[i])/4 for i in range(3)]
        for left,right in zip(d,d[1:]):
            slopes.append(Fraction(0) if left*right<=0 else 2*left*right/(left+right))
        values=[]
        for z in range(16):
            if z>=12:
                value=a[3]
            elif z%4==0:
                value=a[z//4]
            else:
                interval=z//4
                t=Fraction(z%4,4)
                if interval!=1:
                    value=(1-t)*a[interval]+t*a[interval+1]
                else:
                    value=(2*t**3-3*t**2+1)*a[1]+(t**3-2*t**2+t)*4*slopes[0]+(-2*t**3+3*t**2)*a[2]+(t**3-t**2)*4*slopes[1]
            values.append(value)
        filled.append(values)
    return filled


def project(field, native_r):
    rz=integer_matrix(16,12,list(range(16)))
    rr=integer_matrix(native_r,2,list(range(native_r)))
    output=[]
    for jz in range(12):
        plane=[]
        for jr in range(2):
            total=Fraction(0)
            for z in np.flatnonzero(rz[jz]):
                for r in np.flatnonzero(rr[jr]):
                    total+=Fraction(int(rz[jz,z])*int(rr[jr,r]),24*4)*field[int(r)][int(z)]
            plane.append([float(total)/math.sqrt(1.5)])
        output.append(plane)
    return np.asarray(output,np.float64)


def witness_check(actual):
    definitions={
        'A':[[0,0,3,3],[0,2,1,3],[0,1,2,3],[0,1,2,3]],
        'C':[[0,0,1,3],[0,2,3,3],[0,1,2,3],[0,1,2,3]]}
    errors={}
    expected={}
    for name,anchors in definitions.items():
        values=[Fraction(v) for row in anchors for v in row]
        mean=sum(values)/16
        variance=sum((v-mean)**2 for v in values)/16
        assert mean==variance==Fraction(3,2)
        got=actual['variants'][name]
        assert np.array_equal(np.asarray(got['original_observed']['values'])[:,0,:],np.asarray(anchors))
        assert got['statistics']['mean']==float(mean) and math.isclose(got['statistics']['population_std'],math.sqrt(float(variance)),abs_tol=1e-14)
        observed=[0,4,8,12]
        sparse=[[Fraction(0)]*16 for _ in range(4)]
        mask=[[Fraction(0)]*16 for _ in range(4)]
        for row in range(4):
            for i,z in enumerate(observed):
                sparse[row][z]=Fraction(anchors[row][i])-mean
                mask[row][z]=Fraction(1)
        dense=[[v-mean for v in row] for row in fill_local(anchors)]
        projected_anchors=[[Fraction(anchors[2*r][i]+anchors[2*r+1][i],2) for i in range(4)] for r in range(2)]
        common=[[v-mean for v in row] for row in fill_local(projected_anchors)]
        fields=dict(numerator=project(sparse,4),availability=project(mask,4)*math.sqrt(1.5),
                    native_pchip_then_projection=project(dense,4),projection_then_local_pchip=project(common,2))
        for key,value in fields.items():
            # project() uses denominator 24*4 for both r=4 and r=2; target r is fixed at 2.
            observed_value=np.asarray(got[key]['values'],np.float64)
            delta=float(np.max(np.abs(value-observed_value)))
            assert np.allclose(value,observed_value,atol=1e-5,rtol=1e-5),(name,key,delta)
            errors[name+'/'+key]=delta
        expected[name]=fields
    assert np.array_equal(expected['A']['numerator'],expected['C']['numerator'])
    assert np.array_equal(expected['A']['availability'],expected['C']['availability'])
    assert np.array_equal(expected['A']['projection_then_local_pchip'],expected['C']['projection_then_local_pchip'])
    difference=float(np.max(np.abs(expected['A']['native_pchip_then_projection']-expected['C']['native_pchip_then_projection'])))
    assert difference>1e-5
    assert math.isclose(difference,actual['comparison']['native_pchip_then_projection']['max_abs_difference'],abs_tol=1e-5)
    return dict(independent_max_errors=errors,independent_native_pchip_difference=difference,
                same_observed_statistics_and_direct_input_verified=True,synthetic_only=True)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    assert not OUT.exists()
    started=time.perf_counter()
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],
        source_bindings=[entry(p) for p in (Path(__file__),SOURCE,META,
            ROOT/'OBSERVED_PROJECTION_INFORMATION_PROTOCOL_V2_2026-10-08.md')],
        production_code_imported=False, SciPy_or_Torch_imported=False,
        medical_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,
        validation_data_read=False,confirmation_patients_opened=False,publication_claim_confirmed=False,
        primes=list(PRIMES),axis_certificates=[])
    try:
        result['resources_before']=resource_guard()
        source,metadata=read(SOURCE),read(META)
        assert source['complete'] and not source['errors'] and len(source['series'])==19
        for axis in source['axes']:
            n,m=axis['native_length'],axis['physical_length']
            integer=integer_matrix(n,m,axis['source_columns'])
            for i,stored in enumerate(axis['rows']):
                encoded={int(col):Fraction(num,den) for col,num,den in stored}
                expected={int(col):Fraction(int(integer[i,col]),2*m) for col in np.flatnonzero(integer[i])}
                assert encoded==expected
            bound=min(integer.shape)
            ranks=[modular_rank(integer,p) for p in PRIMES]
            assert all((2*m)%p for p in PRIMES) and ranks==[bound,bound]
            assert axis['rank']==bound
            zero_columns=[axis['source_columns'][i] for i in range(integer.shape[1]) if not integer[:,i].any()]
            assert zero_columns==axis['zero_source_columns']
            result['axis_certificates'].append(dict(id=axis['id'],integer_denominator=2*m,upper_bound=bound,
                modular_ranks=ranks,rational_rank_certified=bound,coefficient_rows_verified=len(axis['rows'])))
            assert time.perf_counter()-started<600
        meta={(s['patient'],s['uid']):s for s in metadata['series']}
        for row in source['series']:
            reference=meta[(row['patient'],row['uid'])]
            assert row['native_shape_zrc']==reference['grid']['native_shape_zrc'] and row['physical_shape_zrc']==reference['grid']['unpadded_shape_zrc']
            axes=[source['axes'][i] for i in row['axis_ids_zrc']]
            assert axes[0]['source_columns']==reference['observed_indices']
            for i,axis in enumerate(axes):
                assert (axis['native_length'],axis['physical_length'])==(row['native_shape_zrc'][i],row['physical_shape_zrc'][i])
                if i:
                    assert axis['source_columns']==list(range(row['native_shape_zrc'][i]))
            dimension=len(reference['observed_indices'])*row['native_shape_zrc'][1]*row['native_shape_zrc'][2]
            rank=math.prod(axis['rank'] for axis in axes)
            assert (dimension,rank,dimension-rank)==(row['observed_unknown_intensities'],row['projected_numerator_real_rank'],row['nullity'])
            assert row['axis_ranks_zrc']==[axis['rank'] for axis in axes]
        people=sorted({s['patient'] for s in source['series']})
        patient_ratios=[]
        for person in people:
            selected=[s for s in source['series'] if s['patient']==person]
            dimension=sum(s['observed_unknown_intensities'] for s in selected)
            rank=sum(s['projected_numerator_real_rank'] for s in selected)
            ratio=Fraction(rank,dimension)
            stored=next(s for s in source['patient_workloads'] if s['patient']==person)
            assert (stored['dimension'],stored['rank'])==(dimension,rank)
            assert Fraction(stored['retained_dimension_fraction']['exact'])==ratio
            patient_ratios.append(ratio)
        combined=sum(patient_ratios)/len(people)
        summary=source['summary']
        assert summary['series_with_nonzero_nullity']==sum(s['nullity']>0 for s in source['series'])
        assert summary['observed_z_full_column_rank_series']==sum(s['axis_ranks_zrc'][0]==len(meta[(s['patient'],s['uid'])]['observed_indices']) for s in source['series'])
        assert summary['observed_unknown_intensities_total']==sum(s['observed_unknown_intensities'] for s in source['series'])
        assert summary['projected_numerator_real_rank_total']==sum(s['projected_numerator_real_rank'] for s in source['series'])
        assert Fraction(summary['patient_workload_equal_retained_dimension_fraction']['exact'])==combined
        assert math.isclose(summary['patient_workload_equal_retained_dimension_fraction']['value'],float(combined),abs_tol=1e-14)
        result['witness']=witness_check(source['synthetic_witness'])
        result.update(complete=True,checked_unique_axis_maps=len(source['axes']),checked_series=19,
            checked_patients=11,summary=source['summary'],real_linear_rank_only=True,
            float32_inverse_or_condition_number_certified=False,actual_task_benefit_measured=False)
        result['resources_after']=resource_guard()
        assert time.perf_counter()-started<600
    except Exception as error:
        result['errors'].append(type(error).__name__+': '+str(error))
        result['traceback']=traceback.format_exc()
    result['elapsed_seconds']=time.perf_counter()-started
    result['finished_utc']=datetime.now(timezone.utc).isoformat()
    with OUT.open('x',encoding='utf-8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:result.get(k) for k in ('complete','errors','checked_unique_axis_maps','checked_series','witness','elapsed_seconds')},ensure_ascii=False),flush=True)
    return 0 if result['complete'] else 1


if __name__=='__main__':
    raise SystemExit(main())
