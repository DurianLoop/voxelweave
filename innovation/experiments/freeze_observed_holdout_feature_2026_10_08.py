"""Bind every feature protocol/source before the first new observed array read."""
import ast
import hashlib
import json
import sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'experiments/observed_holdout_feature_preregistration_2026_10_08.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    assert not DEST.exists()
    paths=[Path(__file__),ROOT/'OBSERVED_HOLDOUT_FEATURE_PROTOCOL_2026-10-08.md']
    paths.extend(ROOT/'experiments'/name for name in (
        'observed_holdout_feature_2026_10_08.py','qualify_observed_holdout_feature_2026_10_08.py',
        'verify_observed_holdout_feature_2026_10_08.py','common_projected_input_audit_2026_10_08.py',
        'common_projected_observed_qualification_2026_10_08/attempt01.json'))
    for p in paths:
        assert p.is_file()
        if p.suffix=='.py':
            ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
    assert not (ROOT/'experiments/observed_holdout_feature_qualification_2026_10_08').exists()
    assert not (ROOT/'experiments/observed_holdout_feature_independent_2026_10_08').exists()
    source=json.loads(paths[-1].read_text(encoding='utf-8'))
    assert source['complete'] and not source['errors'] and len(source['series'])==19
    roots=[]
    for name,digest in (('.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
                        ('environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')):
        p=ROOT.parent/name
        assert sha(p)==digest
        roots.append(dict(path=str(p),sha256=digest,previous_sha256=digest))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in paths],
        target_series=19,target_real_folds=38,fixed_folds=[0,1],first_last_always_retained=True,
        counterfactual_heldout_offset=10000,source_projection_sample_seed=20261008,purpose=812,
        source_projection_random_samples_per_fold_per_anchor=512,source_projection_special_positions='corner/center/opposite corner',
        atol=3e-5,rtol=3e-5,root_files_observed=roots,AST_checks_passed=True,
        medical_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,
        protocol_frozen_before_array_load=True,goal_status='active',publication_claim_confirmed=False)
    with DEST.open('x',encoding='utf-8') as f:
        json.dump(r,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(json.dumps(dict(complete=True,source_bindings=len(paths),target_series=19,target_real_folds=38,
                         medical_arrays_loaded=0,preregistration_sha256=sha(DEST))),flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
