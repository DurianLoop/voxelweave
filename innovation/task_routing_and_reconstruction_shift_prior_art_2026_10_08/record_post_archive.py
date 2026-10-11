"""Record the real archive completion; preserve frozen evidence unchanged."""
import json,sys,time,hashlib
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard()
    manifest=HERE/'ARCHIVE_MANIFEST.json';proof=HERE/'ARCHIVE_PROOF.json';inp=HERE/'POST_ARCHIVE_INPUT.json'
    q=json.loads(proof.read_text(encoding='utf-8'));a=json.loads(inp.read_text(encoding='utf-8'))
    assert q['complete'] and not q['errors'] and sha(manifest)==q['manifest_sha256']
    assert q['previous4546_evidence_hashes_unchanged'] and q['cumulative_frozen_evidence_files']==4686
    assert a['archive_actual_tool_exit']==0 and a['actual_post_archive_live_poll']['value']['session_id']==99542
    assert 'exit_code' not in a['actual_post_archive_live_poll']['value']
    assert a['actual_goal']['value']['goal']['status']=='active'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
       source_bindings=[entry(p) for p in (Path(__file__),manifest,proof,inp)],
       actual_archive_observed_tool_exit=0,actual_archive_observed_chunk=a['archive_actual_chunk'],
       cumulative_frozen_evidence_files=4686,previous4546_evidence_hashes_unchanged=True,
       latest_actual_live_poll=a['actual_post_archive_live_poll'],latest_actual_GPU_query=a['actual_GPU_query'],
       actual_goal_observation=a['actual_goal'],public_progress_after_archive=a['public_progress_after_archive'],
       original_training_terminal_exit=None,original_training_terminated_or_restarted_or_migrated=False,
       GPU_authorization_retained=True,new_GPU_job_started=False,new_agents_delegated=0,
       new_primary_papers_read=2,new_full_text_pages_read=34,visual_pages_reviewed=15,
       medical_arrays_loaded=0,MRI_neural_forwards=0,real_medical_training_updates=0,
       actual_new_MRI_task_benefit_measured=False,publication_claim_confirmed=False,goal_status='active',
       archive_not_rewritten_after_success=True,automatic_approval_review_rejections_received=0,
       next_stage_must_bind=[p.relative_to(ROOT).as_posix() for p in (manifest,proof,Path(__file__),inp,HERE/'POST_ARCHIVE_OBSERVATIONS.json')])
    with (HERE/'POST_ARCHIVE_OBSERVATIONS.json').open('x',encoding='utf-8') as f:
        json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,manifest_sha256=sha(manifest),proof_sha256=sha(proof),
        cumulative_frozen_evidence_files=4686,original_training_terminal_exit=None,goal_status='active')),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())

