"""Scientific preprocessing qualification, no MRI/model arrays or neural forwards."""
import hashlib,json,sys,time,traceback
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from augmentation import apply,primitives
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def array_sha(a):return hashlib.sha256(a.tobytes()).hexdigest()

def independent(x,records):
    out=x.astype(np.float64)
    axes=[np.linspace(-1,1,n,dtype=np.float32).astype(np.float64) for n in x.shape[2:]]
    for i,p in enumerate(records):
        a=out[i,0]
        if p['gamma_enabled'] and a.max()>a.min() and a.std()>0:
            b=np.power((a-a.min())/(a.max()-a.min()),p['gamma'])
            if b.std()>0:a[:]=(b-b.mean())*a.std()/b.std()+a.mean()
        if p['bias_enabled']:
            c=np.asarray(p['bias_coefficients'],np.float32).astype(np.float64)
            a*=np.exp(c[0]*axes[0][:,None,None]+c[1]*axes[1][None,:,None]+c[2]*axes[2][None,None,:])
        if p['noise_enabled']:
            # Same explicitly frozen Gaussian draws; formula evaluated in float64.
            noise=np.random.default_rng(p['noise_seed']).standard_normal(a.shape,dtype=np.float32)
            a+=noise.astype(np.float64)*p['noise_std']
    return out

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();dest=HERE/'QUALIFICATION.json'
    assert not dest.exists();r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],checks=[],
        medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,training_updates=0,
        confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False)
    try:
        r['resources_before']=resource_guard()
        rng=np.random.default_rng(20261008);x=rng.standard_normal((2,1,64,128,128),dtype=np.float32)
        target=(rng.random(x.shape)<.01).astype(np.float32);xh=array_sha(x);yh=array_sha(target)
        cases=[]
        for mode in ['identity','gamma','bias','noise','combined','constant','sampled']:
            p=primitives(1)
            if mode!='sampled':
                for z in p:
                    z.update(gamma_enabled=mode in ['gamma','combined','constant'],
                        bias_enabled=mode in ['bias','combined','constant'],noise_enabled=mode in ['noise','combined','constant'])
            a=np.zeros_like(x) if mode=='constant' else x
            result=apply(a,p);repeat=apply(a,p);oracle=independent(a,p)
            error=float(np.max(np.abs(result-oracle)));assert error<=2e-5
            assert np.array_equal(result,repeat) and array_sha(x)==xh and array_sha(target)==yh
            if mode=='identity':assert np.array_equal(x,result)
            cases.append(dict(mode=mode,shape=list(x.shape),max_float64_formula_error=error,
                input_unchanged=True,label_unchanged=True,repeated_exact=True,finite=True,output_sha256=array_sha(result)))
            resource_guard();assert time.perf_counter()-started<120
        for step in range(1,100):
            a=primitives(step);b=primitives(step);assert a==b
            for z in a:
                assert .7<=z['gamma']<=1.5 and 0<=z['noise_std']<=.08
                assert len(z['bias_coefficients'])==3 and max(map(abs,z['bias_coefficients']))<=.3
        r.update(complete=True,checks=cases,deterministic_paired_steps_verified=99,
            full_size_synthetic_samples=2,all_formula_gates_passed=True,resources_after=resource_guard(),
            source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p))
                             for p in [Path(__file__),HERE/'augmentation.py',HERE/'PROTOCOL.md']])
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-started
    with dest.open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps(r),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
