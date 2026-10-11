"""Exact two-stage through-plane interpolation at one frozen failure witness."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,time
from fractions import Fraction as F
import numpy as np
import torch
from diagnose_failed_v2_field import ROOT,HERE,read,entry,dump,guard,bind,development_cases,lattice,source_image,physical_mr,array_sha,QPATH
sys.path.insert(0,str(ROOT/'resolution_degradation_controls_2026_10_08'))
from resolution_control import plan,apply,locations
from independent_resolution import independent_apply

def record(v):return dict(exact=str(v),float=float(v))
def rounded32(v):
    guess=np.float32(float(v));neighbors=[np.nextafter(guess,np.float32(-np.inf)),guess,np.nextafter(guess,np.float32(np.inf))]
    records=[(abs(F(float(x))-v),int(np.asarray(x).view(np.uint32)),x) for x in neighbors]
    distance=min(d for d,b,x in records);tied=[(b,x) for d,b,x in records if d==distance]
    selected=min(tied,key=lambda item:item[0]%2)[1]
    return selected,[dict(value=float(x),bits=b,distance=record(d),nearest=(d==distance)) for d,b,x in records]

def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);started=time.perf_counter();before=guard(started)
    diagnosticpath=HERE/'failed_v2_field_diagnostic_attempt01/receipt.json';diagnostic=read(diagnosticpath)
    assert diagnostic['complete'] and diagnostic['failed_v2_field_reproduced']
    for b in diagnostic['source_bindings']:bind(b)
    f=diagnostic['failed_field'];index=diagnostic['failed_maximum_witness']['index_zrc'];assert index==[15,37,110]
    cases=development_cases();c,row=cases[8];grid=lattice(c);normalized,stats=source_image(c,row,'native_reference');cache=physical_mr(normalized,grid)
    qualification=read(QPATH);ref=next(v for a in qualification['arms'] if a['kind']=='native_reference' for v in a['cache_records'] if v['uid']==c['uid'])
    assert array_sha(cache)==ref['input_sha256'];p=plan(grid,f['primitive'],'throughplane');fine=p['fine_shape_zrc'];coarse=p['coarse_shape_zrc']
    assert fine[1:]==coarse[1:]
    query=[f['geometry']['start'][a]+(k-1-index[a] if f['geometry']['flips'][a] else index[a])-grid['padding'][a][0]
           for a,k in enumerate((64,128,128))]
    assert all(0<=query[a]<fine[a] for a in range(3))
    z=F(query[0]*(coarse[0]-1),fine[0]-1);low=z.numerator//z.denominator;weight=z-low
    values=[]
    for k in [low,low+1]:
        native=F(k*(fine[0]-1),coarse[0]-1);a=native.numerator//native.denominator;w=native-a
        loc=[int(grid['padding'][j][0])+int(query[j]) for j in range(3)]
        loc[0]=int(grid['padding'][0][0])+a;left=F(float(cache[tuple(loc)]))
        loc[0]+=1;right=F(float(cache[tuple(loc)]));value=left*(1-w)+right*w
        values.append(dict(coarse_index=k,native_coordinate=record(native),left=record(left),right=record(right),value=record(value)))
    exact=F(values[0]['value']['exact'])*(1-weight)+F(values[1]['value']['exact'])*weight
    nearest,neighbors=rounded32(exact)
    pad=grid['padding'];source=cache[tuple(slice(int(v[0]),int(v[0])+n) for v,n in zip(pad,fine))].astype(np.float64)
    with torch.inference_mode():
        down=torch.nn.functional.interpolate(torch.from_numpy(source)[None,None],size=coarse,mode='trilinear',align_corners=True)
        normalized_query=[2*float(query[a])/(fine[a]-1)-1 if fine[a]>1 else 0. for a in range(3)]
        sample=torch.tensor(normalized_query[::-1],dtype=torch.float64).reshape(1,1,1,1,3)
        raw=float(torch.nn.functional.grid_sample(down,sample,mode='bilinear',align_corners=True,padding_mode='zeros')[0,0,0,0,0])
    ordinary=np.array([nearest],dtype=np.float32)
    restored=(ordinary*f['geometry']['intensity_scale']+f['geometry']['intensity_shift']).astype(np.float32)[0]
    actual,support,meta=apply(cache,grid,f['geometry'],f['primitive'],'throughplane')
    other,other_support,imeta=independent_apply(cache,grid,f['geometry'],f['primitive'],'throughplane')
    idx=tuple(index);witness=diagnostic['failed_maximum_witness']
    assert float(actual[idx])==witness['pre_production'] and float(other[idx])==witness['pre_independent']
    result=dict(complete=True,errors=[],fixed_witness=index,fine_shape=fine,coarse_shape=coarse,query_fine_zrc=query,
        coarse_coordinate=record(z),coarse_neighbor_values=values,exact_unscaled_two_stage_value=record(exact),
        exact_round_to_float32=float(nearest),round_candidates=neighbors,
        normalized_grid_sample_unscaled_value=raw,normalized_grid_sample_minus_exact=record(F(raw)-exact),
        normalized_grid_sample_round32=float(np.float32(raw)),
        exact_round_then_original_scale_shift=float(restored),production_pre=float(actual[idx]),independent_pre=float(other[idx]),
        exact_round_restored_matches_production=bool(restored==actual[idx]),exact_round_restored_matches_independent=bool(restored==other[idx]),
        normalized_query=normalized_query,unaffected_axis_coarse_coordinates=[record(F(v)) for v in query[1:]],
        MRI_input_arrays_loaded=1,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,training_updates=0,
        full_pipeline_repaired=False,new_production_selected=False,numerical_gate_unchanged=True,
        validation_or_confirmation_opened=False,publication_claim_confirmed=False,goal_status='active',
        source_bindings=[entry(__import__('pathlib').Path(__file__)),entry(HERE/'EXACT_INTERPOLATION_WITNESS_PROTOCOL.md'),entry(diagnosticpath)],
        resources_before=before,resources_after=guard(started),elapsed_seconds=time.perf_counter()-started)
    out=HERE/'exact_interpolation_witness_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',result)
    print(__import__('json').dumps({k:v for k,v in result.items() if k not in ['source_bindings','round_candidates']},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
