"""Append actual archive exit and live poll after freeze; bind next stage."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    manifest=HERE/'ARCHIVE_MANIFEST.json';proof=HERE/'ARCHIVE_PROOF.json'
    d=json.loads(proof.read_text(encoding='utf-8'))
    assert d['complete'] and not d['errors'] and entry(manifest)['sha256']==d['manifest_sha256']
    output=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__)),entry(manifest),entry(proof),entry(HERE/'DELIVERY.md'),entry(HERE/'NEXT_STAGE_HANDOFF.md')],
        record_stage_observed_chunk='a88437',record_stage_observed_tool_exit=0,
        archive_observed_chunk='34d5f5',archive_observed_tool_exit=0,
        stage_files=d['stage_files'],stage_bytes=d['stage_bytes'],newly_bound_files=d['newly_bound_files'],
        new_evidence_bytes=d['new_evidence_bytes'],cumulative_frozen_evidence_files=d['cumulative_frozen_evidence_files'],
        previous3863_evidence_hashes_unchanged=d['previous3863_evidence_hashes_unchanged'],
        all_source_bindings_verified=d['all_source_bindings_verified'],all_local_links_verified=d['all_local_links_verified'],
        latest_observed_poll=dict(chunk='e5a472',session_id=99542,returned_session_id=99542,terminal_exit=None,
            retained_log_records=[dict(kind='raw_pchip',updates=495,loss=1.3713573217391968,new_updates=20295,cumulative_wall_seconds=46621.498528899974),
                dict(kind='raw_pchip',updates=594,loss=1.355491042137146,new_updates=20394,cumulative_wall_seconds=46849.649997700006),
                dict(kind='raw_pchip',updates=693,loss=1.3234410285949707,new_updates=20493,cumulative_wall_seconds=47085.14940819994)]),
        last_public_progress='归档已通过：本轮新增绑定116个文件，累计3,979个证据文件，上一轮3,863个文件的哈希全部未变。原训练会话仍在运行，最新日志显示PCHIP臂完成693／19,998次更新；完整任务评价还需等待两臂最终完成。',
        current_final_reply_path='paired_task_label_adapter_2026_10_08/DELIVERY.md',
        original_terminal_training_modified=False,original_training_restart_or_migration=False,
        automatic_approval_review_rejections_received=0,
        root_files_unchanged=True,medical_arrays_loaded=0,prediction_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,
        GPU_forwards=0,training_updates=0,head_fits=0,new_final_action_labels_generated=0,
        confirmation_patients_opened=False,lockedIXI_opened=False,
        new_primary_papers_read=2,new_full_text_pages_read=29,visual_pages_reviewed=9,
        actual_new_MRI_task_benefit_measured=False,full_action_cost_measured=False,publication_claim_confirmed=False,goal_status='active',
        next_stage_must_bind=['paired_task_label_adapter_2026_10_08/ARCHIVE_MANIFEST.json',
            'paired_task_label_adapter_2026_10_08/ARCHIVE_PROOF.json',
            'paired_task_label_adapter_2026_10_08/record_post_archive.py',
            'paired_task_label_adapter_2026_10_08/POST_ARCHIVE_OBSERVATIONS.json'],
        archive_not_rewritten_after_success=True)
    with (HERE/'POST_ARCHIVE_OBSERVATIONS.json').open('x',encoding='utf-8') as f:json.dump(output,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,cumulative_frozen_evidence_files=d['cumulative_frozen_evidence_files'],
        archive_observed_tool_exit=0,manifest_sha256=entry(manifest)['sha256'],proof_sha256=entry(proof)['sha256'],
        original_training_terminal_exit=None,goal_status='active'),ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
