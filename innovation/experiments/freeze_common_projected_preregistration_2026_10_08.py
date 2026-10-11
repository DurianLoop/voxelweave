"""Freeze new protocols/source before any new observed-array load; no import of models."""
import ast
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT/'experiments/common_projected_observed_preregistration_2026_10_08.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    assert not DEST.exists()
    paths = [ROOT/'COMMON_PROJECTED_OBSERVED_INPUT_PROTOCOL_2026-10-08.md', Path(__file__)]
    paths += [ROOT/'experiments'/name for name in (
        'mc_rc_common_projected_observed_2026_10_08.py',
        'qualify_common_projected_observed_2026_10_08.py',
        'verify_common_projected_observed_2026_10_08.py',
        'common_projected_input_audit_2026_10_08.py',
        'mc_rc_3d_direct_observed_2026_10_07.py', 'mc_rc_observed_only_training_input.py',
        'mc_rc_3d_baseline_2026_10_07.py', 'mc_rc_3d_baseline_v2_2026_10_07.py',
        'mc_rc_reference_resources_2026_10_07.py',
        'mc_rc_3d_direct_observed_qualification_2026_10_07/attempt01.json',
        'mc_rc_3d_direct_observed_independent_2026_10_07/attempt01.json',
        'mc_rc_current_development_input_preparation/attempt_01.json',
        'mc_rc_development_training_input_cpu/attempt_01.json')]
    for p in paths:
        assert p.is_file()
        if p.suffix == '.py':
            ast.parse(p.read_text(encoding='utf-8'), filename=str(p))
    for folder in ('common_projected_observed_qualification_2026_10_08',
                   'common_projected_observed_independent_2026_10_08'):
        assert not (ROOT/'experiments'/folder).exists()
    old = json.loads((ROOT/'experiments/mc_rc_3d_direct_observed_qualification_2026_10_07/attempt01.json').read_text(encoding='utf-8'))
    assert old['complete'] and not old['errors'] and len(old['series']) == 19
    roots = []
    for name, digest in (('.gitignore', '7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
                         ('environment.yml', 'dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')):
        p = ROOT.parent/name
        assert sha(p) == digest
        roots.append(dict(path=str(p), sha256=digest, previous_sha256=digest))
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[],
                  source_bindings=[dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=sha(p)) for p in paths],
                  observed_packages=[{k:s[k] for k in ('patient','uid','observed_package','observed_package_sha256')} for s in old['series']],
                  root_files_observed=roots, AST_checks_passed=True, medical_arrays_loaded=0,
                  neural_forwards=0, GPU_forwards=0, training_updates=0,
                  common_source_protocol_frozen_before_array_load=True, target_series=19,
                  atol=3e-5, rtol=3e-5, each_job_wall_seconds=1200, cpu_threads=1, interop_threads=1,
                  stage_max_saved_bytes=20_000_000, goal_status='active', publication_claim_confirmed=False)
    with DEST.open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps(dict(complete=True, bindings=len(paths), target_series=19, medical_arrays_loaded=0,
                          preregistration_sha256=sha(DEST)), ensure_ascii=False), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
