"""Generate and preregister a separate verifier matching the actual retained-copy layout."""
import ast
import hashlib
import json
import sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'experiments/verify_observed_holdout_feature_2026_10_08.py'
NEW=ROOT/'experiments/verify_observed_holdout_feature_layout_v2_2026_10_08.py'
PRE=ROOT/'experiments/observed_holdout_feature_layout_v2_preregistration_2026_10_08.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def entry(p):
    return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))


def replace(s,a,b):
    assert s.count(a)==1,a[:100]
    return s.replace(a,b)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    assert not NEW.exists() and not PRE.exists()
    oldpre=ROOT/'experiments/observed_holdout_feature_preregistration_2026_10_08.json'
    for b in json.loads(oldpre.read_text(encoding='utf-8'))['source_bindings']:
        assert sha(ROOT/b['path'])==b['sha256'],b['path']
    fail=ROOT/'experiments/observed_holdout_feature_independent_2026_10_08/attempt01.json'
    failed=json.loads(fail.read_text(encoding='utf-8'))
    assert not failed['complete'] and len(failed['series'])==2 and failed['real_folds_verified']==5
    assert failed['medical_observed_packages_loaded']==3
    s=OLD.read_text(encoding='utf-8')
    s=replace(s,"observed_holdout_feature_preregistration_2026_10_08.json'","observed_holdout_feature_layout_v2_preregistration_2026_10_08.json'")
    s=replace(s,"observed_holdout_feature_independent_2026_10_08'","observed_holdout_feature_independent_layout_v2_2026_10_08'")
    s=replace(s,"ROOT/'OBSERVED_HOLDOUT_FEATURE_PROTOCOL_2026-10-08.md'","ROOT/'OBSERVED_HOLDOUT_FEATURE_LAYOUT_V2_PROTOCOL_2026-10-08.md'")
    s=replace(s,'def own_statistics(a):','def original_arbitrary_layout_statistics(a):')
    helper='''def own_statistics(a):
    return original_arbitrary_layout_statistics(np.array(a,copy=True,order='C'))


def statistics_mathematics(a,st):
    flat=np.ascontiguousarray(a,dtype=np.float64).ravel()
    pieces=[flat[i:i+65536] for i in range(0,flat.size,65536)]
    mean=math.fsum(float(piece.sum(dtype=np.float64)) for piece in pieces)/flat.size
    variance=math.fsum(float(np.square(piece-mean).sum(dtype=np.float64)) for piece in pieces)/flat.size
    std=math.sqrt(variance)
    assert math.isclose(mean,st['mean'],rel_tol=1e-12,abs_tol=1e-12)
    assert math.isclose(std,st['population_std'],rel_tol=1e-12,abs_tol=1e-12)
    return dict(mean_abs_error=abs(mean-st['mean']),std_abs_error=abs(std-st['population_std']),
                abs_tol=1e-12,rel_tol=1e-12,passed=True)


'''
    s=replace(s,'def library_projection(a,target,st):',helper+'def library_projection(a,target,st):')
    original="                assert st==recorded['retained_statistics']\n"
    diagnostic='''                assert st==recorded['retained_statistics']
                previous_layout=original_arbitrary_layout_statistics(a[:,:,kept])
                if index==2 and fold==1:
                    assert previous_layout!=recorded['retained_statistics']
                layout_diagnostic=dict(previous_layout_matches_production=previous_layout==st,
                    mean_difference=previous_layout['mean']-st['mean'],
                    std_difference=previous_layout['population_std']-st['population_std'],
                    canonical_C_copy_matches_production=True)
                statistics_check=statistics_mathematics(a[:,:,kept],st)
'''
    s=replace(s,original,diagnostic)
    s=replace(s,'source_projection_check=projection_check,independent_full_heldout_checks=mathematical_checks,',
        'source_projection_check=projection_check,independent_full_heldout_checks=mathematical_checks,\n                    previous_layout_diagnostic=layout_diagnostic,independent_statistics_mathematics=statistics_check,')
    s=replace(s,'model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,',
        'model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,\n        original_v1_failure_retained=True,statistics_C_copy_replay_explicit=True,')
    s=replace(s,'independent_patient_aggregation=True,no_native_GT_or_neural_IO=True)',
        'independent_patient_aggregation=True,no_native_GT_or_neural_IO=True,\n            original_series3_fold1_layout_difference_reproduced=True,independent_statistics_mathematics=True)')
    ast.parse(s,filename=str(NEW))
    with NEW.open('x',encoding='utf-8') as f:
        f.write(s)
    paths=[Path(__file__),OLD,NEW,oldpre,fail,
        ROOT/'OBSERVED_HOLDOUT_FEATURE_PROTOCOL_2026-10-08.md',
        ROOT/'OBSERVED_HOLDOUT_FEATURE_LAYOUT_V2_PROTOCOL_2026-10-08.md',
        ROOT/'experiments/observed_holdout_feature_qualification_2026_10_08/attempt01.json',
        ROOT/'experiments/common_projected_input_audit_2026_10_08.py']
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],source_bindings=[entry(p) for p in paths],
        original_v1_observed_tool_chunk='628031',original_v1_observed_tool_exit=1,original_v1_loaded_packages=3,
        original_v1_verified_folds=5,source_and_prediction_and_score_definition_unchanged=True,
        atol=3e-5,rtol=3e-5,statistics_mathematical_tolerance=1e-12,no_tolerance_widening=True,
        protocol_frozen_before_v2_array_load=True,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,
        goal_status='active',publication_claim_confirmed=False)
    with PRE.open('x',encoding='utf-8') as f:
        json.dump(r,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(json.dumps(dict(complete=True,source_bindings=len(paths),original_failed_attempt_retained=True,
        medical_arrays_loaded=0,preregistration_sha256=sha(PRE))),flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
