"""Append actual archive exit, final live poll, and remaining visible dialogue."""
import json,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,
    sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
    sys.stdout.reconfigure(encoding='utf-8');manifest=HERE/'ARCHIVE_MANIFEST.json';proof=HERE/'ARCHIVE_PROOF.json'
    q=json.loads(proof.read_text(encoding='utf-8'))
    assert q['complete'] and not q['errors'] and q['manifest_sha256']==entry(manifest)['sha256']
    assert q['cumulative_frozen_evidence_files']==4118 and q['previous4018_evidence_hashes_unchanged']
    final_reply=('已筛查24条摘要、核读2篇原文，并完成CPU数值复核。候选创新点已收窄为：'
        '**同观测、充分任务适配后，仍存在可利用的病灶收益，且计入完整费用后优于强对照**。目前尚未验证成立。\n\n'
        '论文证据、后续实验准备和对话均已保存：[本轮报告](D:/MRI/innovation/mri_decision_policy_prior_art_2026_10_08/RESULT.md)。\n\n'
        'GPU授权已保留，但当前仅约1.4GB空闲；原训练继续运行。')
    comments=[
        '本轮已核读两篇原文的 33 个文字页，并核验 11 页图表；原文、数值复核和后续准备均已保存。接下来校验归档链，确认旧证据未被覆盖。原训练继续运行，当前还没有支持可发表 claim 的强对照结果。',
        '归档校验已通过，累计冻结证据增至 4,118 个文件，旧证据哈希保持一致。原训练仍在推进；最新 GPU 空闲量仍约 1.4 GB。本轮收窄了候选创新点，后续需要用强任务适配、真实病灶收益和完整费用检验它。']
    observations=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__)),entry(manifest),entry(proof),entry(HERE/'DELIVERY.md'),entry(HERE/'NEXT_STAGE_HANDOFF.md')],
        record_stage_observed_chunk='74ab47',record_stage_observed_tool_exit=0,
        archive_observed_chunk='614f67',archive_observed_tool_exit=0,
        stage_files=q['stage_files'],stage_bytes=q['stage_bytes'],newly_bound_files=q['newly_bound_files'],
        new_evidence_bytes=q['new_evidence_bytes'],cumulative_frozen_evidence_files=4118,
        previous4018_evidence_hashes_unchanged=True,all_source_bindings_verified=True,all_local_links_verified=True,
        latest_actual_live_poll=dict(chunk='7d4e5e',session_id=99542,returned_session_id=99542,terminal_exit=None,
            log_records=[dict(kind='raw_pchip',updates=1683,loss=1.0177490711212158,
                invocation02_new_updates=21483,cumulative_wall_seconds=49425.285327399964),
                dict(kind='raw_pchip',updates=1782,loss=0.8840954303741455,
                    invocation02_new_updates=21582,cumulative_wall_seconds=49650.37265399995),
                dict(kind='raw_pchip',updates=1881,loss=1.1730742454528809,
                    invocation02_new_updates=21681,cumulative_wall_seconds=49880.30896069994)]),
        latest_actual_GPU_query=dict(chunk='87173a',exit_code=0,
            csv='2026/10/08 05:40:59.780, 1394 MiB, 24455 MiB, 63 %',
            free_bytes=1461714944,new_job_startup_reserve_bytes=8_000_000_000,reserve_met=False),
        original_training_terminated_or_restarted_or_migrated=False,original_terminal_training_modified=False,
        new_updates_not_raw_arm_count=True,gpu_authorization_retained=True,new_GPU_job_started=False,
        public_progress_after_frozen_dialogue=comments,prepared_final_reply=final_reply,
        new_primary_papers_read=2,new_full_text_pages_read=33,visual_pages_reviewed=11,index_abstracts_screened=24,
        CPU_reported_table_arithmetic_audit_completed=True,medical_arrays_loaded=0,neural_forwards=0,MRI_neural_forwards=0,
        GPU_forwards=0,real_medical_training_updates=0,head_fits=0,new_final_action_labels_generated=0,
        confirmation_patients_opened=False,lockedIXI_opened=False,actual_new_MRI_task_benefit_measured=False,
        full_action_cost_measured=False,publication_claim_confirmed=False,goal_status='active',
        current_goal_turn_classification='progress',next_stage_must_bind=[
            'mri_decision_policy_prior_art_2026_10_08/ARCHIVE_MANIFEST.json',
            'mri_decision_policy_prior_art_2026_10_08/ARCHIVE_PROOF.json',
            'mri_decision_policy_prior_art_2026_10_08/record_post_archive.py',
            'mri_decision_policy_prior_art_2026_10_08/POST_ARCHIVE_OBSERVATIONS.json'],
        archive_not_rewritten_after_success=True,automatic_approval_review_rejections_received=0)
    with (HERE/'POST_ARCHIVE_OBSERVATIONS.json').open('x',encoding='utf-8') as f:
        json.dump(observations,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,cumulative_frozen_evidence_files=4118,
        manifest_sha256=entry(manifest)['sha256'],proof_sha256=entry(proof)['sha256'],
        original_training_terminal_exit=None,goal_status='active'),ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
