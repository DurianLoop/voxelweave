"""Append actual final archive exit, live observations, and remaining public text."""
import sys,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,
    sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
    sys.stdout.reconfigure(encoding='utf-8');manifest=HERE/'ARCHIVE_MANIFEST.json';proof=HERE/'ARCHIVE_PROOF.json'
    q=json.loads(proof.read_text(encoding='utf-8'))
    assert q['complete'] and not q['errors'] and q['manifest_sha256']==entry(manifest)['sha256']
    assert q['previous4118_evidence_hashes_unchanged'] and q['cumulative_frozen_evidence_files']==4397
    progress=[
        'CPU 复核已确认：MASC 的“20.7% MSE 降低”相对的是 Random，对该指标更强的静态对照则约为 15.3%；博士论文也确有最终端点与轨迹汇总排名反转。这些改变了后续对照设计，但仍是论文证据。接下来保存来源、失败记录和对话，校验本轮归档。',
        '本轮已归档，累计冻结证据增至 4,397 个文件，旧证据哈希保持一致。后续会重点检验：给静态路径充分且等量的适配后，动态选择是否仍有病灶收益。原训练继续运行，未见确认集仍保持关闭。']
    final_reply=('新增核读了 MASC 和博士论文相关章节，并完成 CPU 数值复核。后续关键比较已明确：'
        '**静态路径获得充分且等量适配后，动态选择是否仍有病灶收益及完整费用优势**。\n\n'
        '原文、实验准备和对话已归档：[本轮报告](D:/MRI/innovation/mri_joint_static_controls_prior_art_2026_10_08/RESULT.md)。\n\n'
        '原训练继续运行，未见确认集未开启；可发表 claim 尚未成立。')
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__)),entry(manifest),entry(proof),entry(HERE/'DELIVERY.md'),entry(HERE/'NEXT_STAGE_HANDOFF.md')],
        generate_archive_entry_observed_chunk='7e2dd3',generate_archive_entry_observed_tool_exit=0,
        record_stage_observed_chunk='4df0c2',record_stage_observed_tool_exit=0,
        archive_observed_chunk='06b1cb',archive_observed_tool_exit=0,
        stage_files=q['stage_files'],stage_bytes=q['stage_bytes'],newly_bound_files=q['newly_bound_files'],
        new_evidence_bytes=q['new_evidence_bytes'],cumulative_frozen_evidence_files=4397,
        previous4118_evidence_hashes_unchanged=True,all_source_bindings_verified=True,all_local_links_verified=True,
        latest_actual_live_poll=dict(chunk='a81a11',session_id=99542,returned_session_id=99542,terminal_exit=None,
            log_records=[dict(kind='raw_pchip',updates=2178,loss=0.9285483956336975,
                invocation02_new_updates=21978,cumulative_wall_seconds=50587.36492570001),
                dict(kind='raw_pchip',updates=2277,loss=1.1219292879104614,
                    invocation02_new_updates=22077,cumulative_wall_seconds=50823.40213639999),
                dict(kind='raw_pchip',updates=2376,loss=1.113839864730835,
                    invocation02_new_updates=22176,cumulative_wall_seconds=51058.75775550003)]),
        latest_actual_GPU_query=dict(chunk='fa921f',exit_code=0,
            csv='2026/10/08 06:01:39.657, 1394 MiB, 24455 MiB, 90 %',
            free_bytes=1461714944,new_job_startup_reserve_bytes=8_000_000_000,reserve_met=False),
        goal_actual_observation=dict(objective='一直研究探索验证下去，直到达成一个可发表的claim，注意不要动我现在终端训练的进程',
            status='active',tokensUsed=39081925,timeUsedSeconds=251675),
        original_training_terminated_or_restarted_or_migrated=False,original_terminal_training_modified=False,
        new_updates_not_raw_arm_count=True,gpu_authorization_retained=True,new_GPU_job_started=False,
        public_progress_after_frozen_dialogue=progress,prepared_final_reply=final_reply,
        new_primary_sources_read=2,new_primary_papers_read=2,new_full_text_pages_read=44,
        main_text_pages_read=39,ancillary_frontmatter_pages_read=5,visual_pages_reviewed=12,
        known_download_failures_retained=True,thesis_ETag_match=False,thesis_local_source_version_identity_passed=True,
        CPU_reported_table_audit_completed=True,medical_arrays_loaded=0,neural_forwards=0,MRI_neural_forwards=0,
        GPU_forwards=0,real_medical_training_updates=0,head_fits=0,new_final_action_labels_generated=0,
        confirmation_patients_opened=False,lockedIXI_opened=False,actual_new_MRI_task_benefit_measured=False,
        full_action_cost_measured=False,publication_claim_confirmed=False,goal_status='active',
        current_goal_turn_classification='progress',next_stage_must_bind=[
            'mri_joint_static_controls_prior_art_2026_10_08/ARCHIVE_MANIFEST.json',
            'mri_joint_static_controls_prior_art_2026_10_08/ARCHIVE_PROOF.json',
            'mri_joint_static_controls_prior_art_2026_10_08/record_post_archive.py',
            'mri_joint_static_controls_prior_art_2026_10_08/POST_ARCHIVE_OBSERVATIONS.json'],
        archive_not_rewritten_after_success=True,automatic_approval_review_rejections_received=0)
    with (HERE/'POST_ARCHIVE_OBSERVATIONS.json').open('x',encoding='utf-8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,cumulative_frozen_evidence_files=4397,
        manifest_sha256=entry(manifest)['sha256'],proof_sha256=entry(proof)['sha256'],
        original_training_terminal_exit=None,goal_status='active'),ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
