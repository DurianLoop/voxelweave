"""Retain numerical observations before assertions after the first self-replay failed."""
import json,sys
from datetime import datetime,timezone
from mc_rc_3d_baseline_v2_2026_10_07 import ROOT,read,sha,torch,SEED,resource_guard
from mc_rc_3d_independent_replay_2026_10_07 import functional_forward
from mc_rc_3d_reference_instance_norm_2026_10_07 import reference_statistics_forward
from preflight_mc_rc_3d_reference_in_2026_10_07 import compare

def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard()
    out=ROOT/'experiments/mc_rc_3d_reference_in_preflight_2026_10_07/self_replay_numerical_diagnostic01.json';assert not out.exists()
    prod=read(ROOT/'experiments/mc_rc_3d_cpu_fixed_fit_2026_10_07/attempt_01.json')
    base=next(a for a in prod['arms'] if a['kind']=='raw_pchip')
    cp=ROOT/base['checkpoint_file'];assert sha(cp)==base['checkpoint_sha256']
    state=torch.load(cp,map_location='cpu',weights_only=True)['state_dict'];rng=torch.Generator().manual_seed(SEED)
    rows=[]
    for shape in ((2,1,16,16,16),(1,1,32,32,32)):
        x=torch.randn(shape,generator=rng);trace=[]
        with torch.inference_mode():
            ordinary=functional_forward(x,state);candidate,reference=reference_statistics_forward(x,x,state,trace)
        row=dict(shape=list(shape),candidate_vs_ordinary=compare(candidate,ordinary),reference_vs_ordinary=compare(reference,ordinary),layers=trace)
        rows.append(row);print(json.dumps({k:row[k] for k in ('shape','candidate_vs_ordinary','reference_vs_ordinary')}),flush=True)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
           source_bindings=[dict(path=base['checkpoint_file'],sha256=sha(cp)),
                            dict(path='experiments/mc_rc_3d_reference_instance_norm_2026_10_07.py',sha256=sha(ROOT/'experiments/mc_rc_3d_reference_instance_norm_2026_10_07.py'))],
           observations=rows,preflight_qualification_passed=False,actual_training_updates=0,actual_gpu_updates=0,
           real_patient_inputs_opened=False,scientific_confirmation_patients=0,cuda_initialized=torch.cuda.is_initialized())
    assert not r['cuda_initialized']
    with out.open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
if __name__=='__main__':main()
