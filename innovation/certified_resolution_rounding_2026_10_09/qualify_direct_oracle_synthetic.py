"""New direct oracle versus all144 full exact fixtures, independent of the first receipt."""
import json,sys,time,traceback
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from qualify_certified_synthetic import HERE,ROOT,entry,dump,guard
import exact_tensor_reference as oracle
import direct_interval_reference as direct
import certified_resolution as candidate

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();before=guard(started)
    out=HERE/'direct_oracle_synthetic_attempt01';out.mkdir(exist_ok=False)
    prior=HERE/'synthetic_attempt01/receipt.json';q=json.loads(prior.read_text(encoding='utf-8'))
    assert q['complete'] and q['all144_full_synthetic_fields_bitwise_match_exact_tensor_reference']
    for b in q['source_bindings']:assert entry(ROOT/b['path'])==b
    config=json.loads((HERE/'synthetic_attempt01/frozen_config.json').read_text(encoding='utf-8'))
    dump(out/'frozen_config.json',dict(source_bindings=[entry(p) for p in [Path(__file__),HERE/'DIRECT_ORACLE_PROTOCOL.md',HERE/'direct_interval_reference.py',HERE/'exact_tensor_reference.py',HERE/'certified_resolution.py',prior]],fixtures_from=entry(HERE/'synthetic_attempt01/frozen_config.json'),inherits_previous_pass_as_new_oracle_pass=False))
    result=dict(complete=False,errors=[],fields=0,exact_points=0,direct_interval_containment_points=0,direct_fallback_voxels=0,
        patient_arrays_loaded=0,model_arrays_loaded=0,training_updates=0,publication_claim_confirmed=False,goal_status='active')
    try:
        for si,(fine,patch) in enumerate(config['fixture_shapes']):
            pad=[(max(0,k-n)//2,(max(0,k-n)+1)//2) for n,k in zip(fine,patch)]
            grid=dict(unpadded_shape_zrc=fine,padding=pad,realized_spacing_zrc_mm=[.7,.49,.51])
            z,r,c=np.meshgrid(*[np.arange(n,dtype=np.float64) for n in fine],indexing='ij')
            sources={'constant':np.full(fine,2.5,np.float32),'ramp':(z*.11+r*.04-c*.06).astype(np.float32),
                     'signed_texture':(np.sin(z*1.23)+np.cos(r*.73)*8+np.sin(c*.37)*6).astype(np.float32)}
            for name,source in sources.items():
                cache=np.pad(source,pad,mode='constant',constant_values=-.3).astype(np.float32);extent=np.asarray(cache.shape)-patch
                for gi,(start,flips) in enumerate([(np.zeros(3,int),[False]*3),(extent//2,[True,False,True])]):
                    geometry=dict(start=start.tolist(),flips=flips,intensity_scale=1.03,intensity_shift=-.073)
                    for enabled in [False,True]:
                        primitive=dict(enabled=enabled,scale=config['scale'][gi])
                        for mode in config['modes']:
                            guard(started);a,support,meta,intervals=direct.apply_reference(cache,grid,geometry,primitive,mode,patch,True)
                            b,domain,exact=oracle.patch_reference(cache,grid,geometry,primitive,mode,patch)
                            produced,produced_support,pm=candidate.apply(cache,grid,geometry,primitive,mode,patch)
                            assert np.array_equal(a.view(np.uint32),b.view(np.uint32)) and np.array_equal(a.view(np.uint32),produced.view(np.uint32))
                            assert np.array_equal(support,domain.astype(float)) and np.array_equal(support,produced_support)
                            if enabled and exact:
                                lo,hi=intervals['bounds'];lookup=[{int(v):i for i,v in enumerate(axis)} for axis in intervals['local']]
                                for index,value in exact.items():
                                    local=tuple(lookup[a][index[a]] for a in range(3));assert F(float(lo[local]))<=value<=F(float(hi[local]))
                                    result['direct_interval_containment_points']+=1
                            result['fields']+=1;result['exact_points']+=len(exact);result['direct_fallback_voxels']+=meta['direct_exact_fallback_voxels']
            print(json.dumps(dict(specification=si,fields_completed=result['fields'])),flush=True)
        assert result['fields']==144 and result['exact_points']==result['direct_interval_containment_points']==4428
        result.update(complete=True,all144_direct_fields_bitwise_match_exact_oracle_and_candidate=True,new_oracle_real_MRI_qualified=False,training_ready=False)
    except Exception as exc:result['errors'].append(dict(type=type(exc).__name__,message=str(exc)));result['traceback']=traceback.format_exc();traceback.print_exc()
    result.update(resources_before=before,resources_after=guard(started),elapsed_seconds=time.perf_counter()-started,
        source_bindings=[entry(p) for p in [Path(__file__),HERE/'DIRECT_ORACLE_PROTOCOL.md',HERE/'direct_interval_reference.py',HERE/'exact_tensor_reference.py',HERE/'certified_resolution.py',out/'frozen_config.json',prior]])
    dump(out/'receipt.json',result);print(json.dumps({k:v for k,v in result.items() if k!='source_bindings'},ensure_ascii=False),flush=True)
    return int(not result['complete'])

if __name__=='__main__':raise SystemExit(main())
