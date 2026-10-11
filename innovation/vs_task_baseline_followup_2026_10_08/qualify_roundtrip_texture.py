"""Complete previously specified texture probes; preserve first executed qualification."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,json,time,itertools
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import torch
from label_preserving_roundtrip import apply_roundtrip
from qualify_roundtrip_synthetic import physical,interpolate,SHAPE
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client
def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);torch.set_num_interop_threads(1)
    started=time.perf_counter();resources=client.resource_guard();assert not torch.cuda.is_initialized()
    z,r,c=np.ogrid[:SHAPE[0],:SHAPE[1],:SHAPE[2]]
    checker=((z+r+c)%2).astype(np.float32)
    wide=((z>=20)&(z<=43)&(r>=40)&(r<=87)&(c>=40)&(c<=87)).astype(np.float32)
    points=list(itertools.product(*[(0,n-1) for n in SHAPE]))
    points += [(32,64,64),(0,64,64),(20,40,80),(6,8,9),(8,10,11),(63,64,64),(32,0,0),(32,127,127)]
    points += [tuple(map(int,p)) for p in np.random.default_rng(20261008).integers([0,0,0],SHAPE,size=(16,3))]
    assert len(points)==32
    recipes=[dict(name='single_x15',record=dict(enabled=True,degrees_xyz=[15,0,0],scale=1),pivot=[32,64,64],spacing=[.5,.5,.5]),
        dict(name='three_axis_scale085_anisotropic',record=dict(enabled=True,degrees_xyz=[15,-11,8],scale=.85),pivot=[32,64,64],spacing=[.7,.4,1.2])]
    records=[]
    for name,source in [('checkerboard',checker),('wide_structure',wide)]:
        for recipe in recipes:
            client.resource_guard();assert time.perf_counter()-started<120
            x=source[None,None];y=(x>.5).astype(np.float32);p=recipe['record'];pivot=np.asarray(recipe['pivot']);spacing=recipe['spacing']
            result,label,meta=apply_roundtrip(x,y,[p],[pivot],spacing)
            def first_at(point):return interpolate(physical(point,pivot,spacing,p),lambda i:float(source[i]))
            oracle=[]
            for point in points:
                expected=interpolate(physical(point,pivot,spacing,p,True),first_at);observed=float(result[(0,0,*point)])
                oracle.append(dict(point_zrc=point,oracle=expected,observed=observed,error=abs(expected-observed)))
            error=max(o['error'] for o in oracle);assert error<3e-6 and np.array_equal(label,y) and np.array_equal(x[0,0],source)
            assert np.count_nonzero(result[0,0]-source)>0
            records.append(dict(phantom=name,recipe=recipe,metadata=meta[0],labels_unchanged=True,oracle_fixed_points=oracle,max_fixed_point_error=error,
                changed_voxels=int(np.count_nonzero(result[0,0]-source)),source_mean=float(source.mean()),roundtrip_mean=float(result.mean()),
                source_variance=float(source.var()),roundtrip_variance=float(result.var())))
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],records=records,
        original_roundtrip_protocol_checker_and_wide_phantoms_completed=True,full_medical_probability_FOV_verified=False,
        medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False,
        publication_claim_confirmed=False,goal_status='active',resources=resources,elapsed_seconds=time.perf_counter()-started,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p)) for p in [Path(__file__),HERE/'TABLE_TIME_AND_TEXTURE_FOLLOWUP_PROTOCOL.md',HERE/'ROUNDTRIP_IMAGE_AUGMENTATION_PROTOCOL.md',HERE/'qualify_roundtrip_synthetic.py',HERE/'label_preserving_roundtrip.py',HERE/'roundtrip_synthetic_attempt01/receipt.json']])
    out=HERE/'roundtrip_texture_attempt01';out.mkdir(exist_ok=False);client.dump(out/'receipt.json',receipt)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(dict(complete=True,phantoms=2,recipes=2,max_fixed_point_error=max(r['max_fixed_point_error'] for r in records),elapsed_seconds=receipt['elapsed_seconds'])),flush=True)
if __name__=='__main__':main()
