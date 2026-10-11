"""Record inherited observed run exit plus current independent verifier exit."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    cert=ROOT/'experiments/mc_rc_3d_paired_resource_workflow_synthetic_2026_10_07/attempt01.json'
    verifier=cert.with_name('independent_attempt01.json');path=ROOT/'SESSION_OBSERVED_EXITS_PAIRED_RESOURCE_WORKFLOW_2026-10-07.json'
    c=json.loads(cert.read_text(encoding='utf-8'));v=json.loads(verifier.read_text(encoding='utf-8'))
    assert c['complete'] and not c['errors'] and all(c['gate'].values())
    assert v['complete'] and not v['errors'] and v['source_sha256']==sha(cert)
    assert c['elapsed_seconds']==45.025657299906015 and v['independent_draw_batches']==3
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        synthetic_observed_tool_exit=0,synthetic_tool_session=14984,synthetic_tool_chunk='d6352c',
        synthetic_exit_observation_source='Inherited actual tool observation supplied in user handoff; not inferred from JSON.',
        synthetic_result_file=cert.relative_to(ROOT).as_posix(),synthetic_result_sha256=sha(cert),
        verifier_observed_tool_exit=0,verifier_tool_chunk='aec550',
        verifier_exit_observation_source='Current exec_command result with explicit PowerShell exit forwarding.',
        verifier_result_file=verifier.relative_to(ROOT).as_posix(),verifier_result_sha256=sha(verifier),
        independent_scope='NumPy input/draw/crop/affine/flip SHA and FOV coverage; no unsaved neural weight replay.',
        real_MRI_resource_qualification_completed=False,publication_claim_confirmed=False)
    with path.open('x',encoding='utf-8') as s:json.dump(r,s,indent=2);s.write('\n')
    print(json.dumps(dict(complete=True,observed_exits_recorded=2)));return 0
if __name__=='__main__':raise SystemExit(main())
