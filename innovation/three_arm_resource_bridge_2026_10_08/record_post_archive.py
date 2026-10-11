"""Bind final archive exit and actual live observation in an immutable appendix."""
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
    sys.stdout.reconfigure(encoding='utf-8');manifest=HERE/'ARCHIVE_MANIFEST.json';proof=HERE/'ARCHIVE_PROOF.json'
    q=json.loads(proof.read_text(encoding='utf-8'))
    assert q['complete'] and not q['errors'] and q['manifest_sha256']==entry(manifest)['sha256']
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__)),entry(manifest),entry(proof),entry(HERE/'DELIVERY.md'),entry(HERE/'NEXT_STAGE_HANDOFF.md')],
        record_stage_observed_chunk='15587c',record_stage_observed_tool_exit=0,
        archive_observed_chunk='fb8ced',archive_observed_tool_exit=0,
        stage_files=q['stage_files'],stage_bytes=q['stage_bytes'],newly_bound_files=q['newly_bound_files'],
        new_evidence_bytes=q['new_evidence_bytes'],cumulative_frozen_evidence_files=q['cumulative_frozen_evidence_files'],
        previous3979_evidence_hashes_unchanged=q['previous3979_evidence_hashes_unchanged'],
        all_source_bindings_verified=True,all_local_links_verified=True,
        latest_actual_log=dict(chunk='8e86e5',session_id=99542,kind='raw_pchip',updates=1287,loss=1.209449291229248,
            invocation02_new_updates=21087,cumulative_wall_seconds=48503.188960399944,terminal_exit=None),
        latest_actual_live_poll=dict(chunk='9a44cc',session_id=99542,returned_session_id=99542,new_output_empty=True,terminal_exit=None),
        original_training_terminated_or_restarted_or_migrated=False,original_terminal_training_modified=False,
        last_public_progress='三臂执行准备已归档，累计证据增至4,018个文件，旧证据哈希全部保持。原训练仍在推进；目前完成的是执行路径验证，正式三臂训练、真实动作收益和完整费用还待后续实测。',
        prepared_final_reply='three_arm_resource_bridge_2026_10_08/DELIVERY.md',
        synthetic_resource_updates=12,synthetic_neural_forwards=36,independent_batch_checks=9,
        real_medical_resource_updates=0,real_medical_formal_training_updates=0,medical_arrays_loaded=0,MRI_neural_forwards=0,GPU_forwards=0,
        new_primary_papers_read=0,new_final_action_labels_generated=0,head_fits=0,confirmation_patients_opened=False,lockedIXI_opened=False,
        actual_new_MRI_task_benefit_measured=False,full_action_cost_measured=False,publication_claim_confirmed=False,goal_status='active',
        next_stage_must_bind=['three_arm_resource_bridge_2026_10_08/ARCHIVE_MANIFEST.json',
            'three_arm_resource_bridge_2026_10_08/ARCHIVE_PROOF.json','three_arm_resource_bridge_2026_10_08/record_post_archive.py',
            'three_arm_resource_bridge_2026_10_08/POST_ARCHIVE_OBSERVATIONS.json'],
        archive_not_rewritten_after_success=True,automatic_approval_review_rejections_received=0)
    with (HERE/'POST_ARCHIVE_OBSERVATIONS.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,cumulative_frozen_evidence_files=q['cumulative_frozen_evidence_files'],
        manifest_sha256=entry(manifest)['sha256'],proof_sha256=entry(proof)['sha256'],original_training_terminal_exit=None,goal_status='active'),ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
