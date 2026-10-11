"""Create a separately versioned entry with observations persisted before qualification assertions."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def main():
    old=ROOT/'preflight_mc_rc_3d_reference_in_2026_10_07.py'
    new=ROOT/'preflight_mc_rc_3d_reference_in_v2_2026_10_07.py';assert not new.exists()
    s=old.read_text(encoding='utf-8')
    s=s.replace('from mc_rc_3d_reference_instance_norm_2026_10_07 import reference_statistics_forward',
                'from mc_rc_3d_reference_instance_norm_v2_2026_10_07 import reference_statistics_forward,reference_norm')
    s=s.replace("OUT=ROOT/'experiments/mc_rc_3d_reference_in_preflight_2026_10_07'", "OUT=ROOT/'experiments/mc_rc_3d_reference_in_preflight_v2_2026_10_07'")
    s=s.replace('def check_self(reference,state):','def check_self(reference,state,persist):')
    s=s.replace("    assert max(r['probability_max_absolute_error_by_head'])", "    persist(dict(shape=list(reference.shape),candidate_self_replay=r,reference_stream_replay=q))\n    assert max(r['probability_max_absolute_error_by_head'])")
    s=s.replace("           source_bindings=[],actual_training_updates=0", "           source_bindings=[],observations_before_assertions=[],primitive_checks=[],actual_training_updates=0")
    s=s.replace("    def guard():", "    def persist(observation):\n        r['observations_before_assertions'].append(observation);save()\n    def guard():")
    s=s.replace("ROOT/'experiments/mc_rc_3d_reference_instance_norm_2026_10_07.py'", "ROOT/'experiments/mc_rc_3d_reference_instance_norm_v2_2026_10_07.py'")
    s=s.replace("        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sources]",
                "        sources += [ROOT/'MC_RC_3D_REFERENCE_IN_NUMERICAL_ADDENDUM_V2_2026-10-07.md',ROOT/'experiments/mc_rc_3d_reference_in_preflight_2026_10_07/attempt01.json',ROOT/'experiments/prepare_reference_in_preflight_v2_2026_10_07.py']\n        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sources]")
    primitive='''        primitive_rng=torch.Generator().manual_seed(SEED+1)
        for shape in ((2,4,8,8,8),(1,3,4,4,4)):
            ref=torch.randn(shape,generator=primitive_rng)
            cand=ref*.7+torch.randn(shape,generator=primitive_rng)*.2+1.7
            gamma=torch.linspace(.8,1.4,shape[1]);beta=torch.linspace(-.3,.2,shape[1])
            with torch.inference_mode():actual,_=reference_norm(cand,ref,gamma,beta)
            nr=ref.numpy().astype(np.float64);nc=cand.numpy().astype(np.float64)
            mean=nr.mean(axis=(2,3,4),keepdims=True);var=nr.var(axis=(2,3,4),keepdims=True)
            expected=(nc-mean)/np.sqrt(var+1e-5)*gamma.numpy()[None,:,None,None,None]+beta.numpy()[None,:,None,None,None]
            error=float(np.max(np.abs(actual.numpy()-expected)))
            check=dict(shape=list(shape),non_identical_inputs=True,max_absolute_error=error,rtol=2e-5,atol=3e-6)
            r['primitive_checks'].append(check);save()
            assert np.allclose(actual.numpy(),expected,rtol=2e-5,atol=3e-6)
'''
    s=s.replace('        generator=torch.Generator().manual_seed(SEED)', primitive+'        generator=torch.Generator().manual_seed(SEED)')
    s=s.replace('check_self(synthetic,state)', 'check_self(synthetic,state,persist)')
    s=s.replace('check_self(reference,state)', 'check_self(reference,state,persist)')
    compile(s,str(new),'exec')
    with new.open('x',encoding='utf-8') as f:f.write(s)
    print(new.name)
if __name__=='__main__':main()
