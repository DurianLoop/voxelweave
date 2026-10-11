"""Metadata and synthetic preflight only; no MRI, no forward, no optimizer updates."""
import ast,collections,json,sys
from datetime import datetime,timezone
from pathlib import Path
from qualify_mc_rc_3d_19series_cpu_low_lr_2026_10_07 import ROOT,stream_for,sha,fixed_cases,torch,np,SEED,sample_batch
from verify_mc_rc_3d_19series_cpu_low_lr_2026_10_07 import independent_batch
OUT=ROOT/'experiments/mc_rc_3d_19series_cpu_entry_preflight_2026_10_07'
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    names=['qualify_mc_rc_3d_19series_cpu_low_lr_2026_10_07.py','verify_mc_rc_3d_19series_cpu_low_lr_2026_10_07.py']
    for name in names:ast.parse((ROOT/'experiments'/name).read_text(encoding='utf-8'))
    cases=[(c,row) for role,c,row in fixed_cases() if role=='development'];flow,orders=stream_for(cases)
    assert len(cases)==19 and len(flow)==33 and len(orders)==11
    counts=collections.Counter(v['patient'] for v in flow);assert set(counts.values())=={3}
    reports=[]
    for shape in ((64,128,128),(65,130,129),(72,136,144)):
        rng=np.random.default_rng(884);image=rng.normal(size=shape).astype(np.float32);label=np.zeros(shape,np.float32)
        label[0,0,0]=1;label[-1,-1,-1]=1;label[shape[0]//2,shape[1]//2,shape[2]//2]=1
        for step in (1,2,11,33):
            x,y,p=sample_batch(image,label,np.random.default_rng(np.random.SeedSequence([SEED,step])))
            xx,yy,pp=independent_batch(image,label,step)
            assert np.array_equal(x.numpy(),xx) and np.array_equal(y.numpy(),yy) and p==pp
            reports.append(dict(shape=list(shape),step=step,primitive=p,independent_batch_arrays_exact=True))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        source_bindings=[dict(path='experiments/'+n,sha256=sha(ROOT/'experiments'/n)) for n in names],
        ast_checks_passed=names,development_series_metadata=19,development_patients_metadata=11,
        expected_resource_steps_per_arm=33,patient_step_counts=dict(counts),frozen_stream=flow,series_orders=orders,
        synthetic_independent_batch_cases=reports,MRI_or_GT_loaded=0,actual_training_updates=0,
        actual_gpu_updates=0,neural_forwards=0,cuda_initialized=torch.cuda.is_initialized(),
        qualification_not_started_by_this_preflight=True,confirmation_patients_opened=False,publication_claim_confirmed=False)
    assert not r['cuda_initialized']
    with (OUT/'attempt01.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:r[k] for k in ['complete','expected_resource_steps_per_arm','patient_step_counts','MRI_or_GT_loaded','neural_forwards']}))
    return 0
if __name__=='__main__':raise SystemExit(main())
