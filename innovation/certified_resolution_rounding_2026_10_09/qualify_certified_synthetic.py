"""Full tiny-fixture rational verification and independent float32 midpoint tests."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import hashlib,json,sys,time,traceback
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import certified_resolution as candidate
import exact_tensor_reference as oracle
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard

def entry(path):return dict(path=path.relative_to(ROOT).as_posix(),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
def dump(path,value):
    with path.open('x',encoding='utf-8') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
def guard(started):
    r=resource_guard();assert time.perf_counter()-started<900
    assert r['workspace_free_bytes']-2_000_000-3_000_000-2_800_000>=8_000_000_000
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000
    return r

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();before=guard(started)
    out=HERE/'synthetic_attempt01';out.mkdir(exist_ok=False)
    definitions=[((1,1,1),(3,5,7)),((1,5,7),(3,5,7)),((3,5,7),(3,5,7)),((7,9,11),(3,5,7))]
    frozen=dict(fixture_shapes=definitions,textures=['constant','ramp','signed_texture'],geometries=['low_origin','center_flips'],
        enabled=[False,True],modes=['throughplane','inplane','allaxes'],scale=[.85,1.15],
        image_gate=3e-6,coordinate_gate=3e-12,binary_gate=0,wall_seconds=900,source_bindings=[entry(p) for p in [Path(__file__),HERE/'PROTOCOL.md',HERE/'certified_resolution.py',HERE/'exact_tensor_reference.py']])
    dump(out/'frozen_config.json',frozen)
    result=dict(complete=False,errors=[],synthetic_fields=[],rounding_cases=0,synthetic_fields_completed=0,
        exact_target_points_verified=0,interval_containment_points_verified=0,exact_fallback_voxels=0,
        medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,training_updates=0,
        confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active')
    try:
        rng=np.random.default_rng(20261009)
        values=[np.float32(0),np.float32(1e-40),np.float32(1e-20),np.float32(.5),np.float32(14.829792976379395),np.float32(1e10),np.float32(1e30)]
        values.extend(np.asarray(rng.uniform(-100,100,64),dtype=np.float32))
        for value in values:
            high=np.nextafter(value,np.float32(np.inf));mid=(F(float(value))+F(float(high)))/2
            for exact in [F(float(value)),mid-F(1,2**200),mid,mid+F(1,2**200),F(float(high))]:
                a=candidate.round_fraction32(exact);b=oracle.nearest_float32(exact)
                assert int(np.asarray(a).view(np.uint32))==int(np.asarray(b).view(np.uint32)),(value,str(exact),a,b)
                result['rounding_cases']+=1
        for si,(fine,patch) in enumerate(definitions):
            pad=[(max(0,k-n)//2,(max(0,k-n)+1)//2) for n,k in zip(fine,patch)]
            grid=dict(unpadded_shape_zrc=list(fine),padding=pad,realized_spacing_zrc_mm=[.7,.49,.51])
            z,r,c=np.meshgrid(*[np.arange(n,dtype=np.float64) for n in fine],indexing='ij')
            sources={'constant':np.full(fine,2.5,np.float32),'ramp':(z*.11+r*.04-c*.06).astype(np.float32),
                     'signed_texture':(np.sin(z*1.23)+np.cos(r*.73)*8+np.sin(c*.37)*6).astype(np.float32)}
            for name,source in sources.items():
                cache=np.pad(source,pad,mode='constant',constant_values=-.3).astype(np.float32)
                extent=np.asarray(cache.shape)-patch
                for gi,(start,flips) in enumerate([(np.zeros(3,int),[False]*3),(extent//2,[True,False,True])]):
                    geometry=dict(start=start.tolist(),flips=flips,intensity_scale=1.03,intensity_shift=-.073)
                    for enabled in [False,True]:
                        primitive=dict(enabled=enabled,scale=frozen['scale'][gi])
                        for mode in frozen['modes']:
                            guard(started);a,support,meta,intervals=candidate.apply(cache,grid,geometry,primitive,mode,patch,True)
                            b,domain,exact=oracle.patch_reference(cache,grid,geometry,primitive,mode,patch)
                            assert np.array_equal(support.astype(bool),domain) and np.array_equal(support,domain.astype(float))
                            assert np.array_equal(a.view(np.uint32),b.view(np.uint32)),(si,name,gi,enabled,mode,float(np.max(np.abs(a-b))))
                            if enabled and exact:
                                lo,hi=intervals['bounds'];local_lookup=[{int(v):i for i,v in enumerate(axis)} for axis in intervals['local']]
                                for index,value in exact.items():
                                    local=tuple(local_lookup[a][index[a]] for a in range(3))
                                    assert F(float(lo[local]))<=value<=F(float(hi[local])),(si,name,mode,index)
                                    result['interval_containment_points_verified']+=1
                            result['exact_target_points_verified']+=len(exact)
                            result['exact_fallback_voxels']+=meta['exact_fallback_voxels']
                            result['synthetic_fields_completed']+=1
                            result['synthetic_fields'].append(dict(specification=si,texture=name,geometry=gi,enabled=enabled,mode=mode,
                                target_voxels=int(a.size),validity_voxels=int(domain.sum()),image_max_error=0,bitwise_image_disagreements=0,
                                interval_exact_containment_verified=bool(enabled),source=meta))
            print(json.dumps(dict(specification=si,fields_completed=result['synthetic_fields_completed'],exact_points=result['exact_target_points_verified'])),flush=True)
        assert result['synthetic_fields_completed']==144 and result['rounding_cases']==355
        # Raw interpolation tests preserve difficult tiny magnitudes, without medical normalization or gamma.
        tiny=np.array([0.,1e-40,-1e-40,1e-20,-1e-20,1e20,-1e20,1e30,-1e30],dtype=np.float32).reshape(1,3,3)
        queries=[np.arange(n) for n in tiny.shape];raw,meta,(lo,hi)=candidate.interpolate(tiny,(1,2,2),queries,True)
        for index in np.ndindex(*tiny.shape):
            exact=oracle.point(tiny,(1,2,2),index);expected=oracle.nearest_float32(exact)
            assert int(np.asarray(raw[index]).view(np.uint32))==int(np.asarray(expected).view(np.uint32))
            assert F(float(lo[index]))<=exact<=F(float(hi[index]))
        result.update(complete=True,all144_full_synthetic_fields_bitwise_match_exact_tensor_reference=True,
            all355_independent_rounding_cases_verified=True,nine_tiny_and_dynamic_range_raw_points_verified=True,
            mathematical_fixture_interval_containment_verified=True,
            ordinary_resolution_candidate_not_yet_real_MRI_qualified=True,training_ready=False)
    except Exception as exc:
        result['errors'].append(dict(type=type(exc).__name__,message=str(exc)));result['traceback']=traceback.format_exc();traceback.print_exc()
    result.update(source_bindings=[entry(p) for p in [Path(__file__),HERE/'PROTOCOL.md',HERE/'certified_resolution.py',HERE/'exact_tensor_reference.py',out/'frozen_config.json']],
        resources_before=before,resources_after=guard(started),elapsed_seconds=time.perf_counter()-started)
    dump(out/'receipt.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['synthetic_fields','source_bindings']},ensure_ascii=False),flush=True)
    return int(not result['complete'])

if __name__=='__main__':raise SystemExit(main())
