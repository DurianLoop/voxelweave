"""Post-manifest actual public reply, latest poll, and actual archive exit receipt."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    manifest=ROOT/'literature/paired_and_calibration_stage_manifest_2026-10-07.json'
    proof=ROOT/'SESSION_ARCHIVE_VERIFICATION_PAIRED_AND_CALIBRATION_2026-10-07.json'
    p=json.loads(proof.read_text(encoding='utf-8'))
    assert p['complete'] and not p['errors'] and p['manifest_sha256']==sha(manifest)
    assert p['stage_files']==105 and p['evidence_files']==1240 and p['previous_frozen_evidence_files_verified']==1130
    actual=ROOT/'SESSION_FINAL_REPLY_PAIRED_AND_CALIBRATION_ACTUAL_2026-10-07.md'
    with actual.open('x',encoding='utf-8') as f:
        f.write('本轮新增核读 **3 篇原文**，完成两项 CPU 探索及独立复核，均已保存到 [本轮记录](D:/MRI/innovation/SESSION_RESULT_PAIRED_AND_CALIBRATION_2026-10-07.md)。\n\n')
        f.write('- 风险校准准确，仍可能选中有害修正；后续必须加入双路径成本对照。\n')
        f.write('- patch 校准可能改变融合后的分割；施加位置要求已写入后续方案。\n\n')
        f.write('现有训练继续运行。GPU 已获授权，但最近查询仅余约 **1.36 GiB**，本轮未启动新 GPU 实验。**可发表 claim 尚未确认**，下一步先完成正式任务能力评价，再验证真实修正收益。\n')
    appendix=ROOT/'SESSION_POST_ARCHIVE_PUBLIC_UPDATE_PAIRED_AND_CALIBRATION_2026-10-07.md'
    with appendix.open('x',encoding='utf-8') as f:
        f.write('# 归档后公开进度原文\n\n')
        f.write('归档已完成：新增 105 份阶段文件，累计 1240 份冻结证据，原有 1130 份 SHA 全部一致。最新训练日志为 native 第 7425 步，仍在运行；GPU 最近查询空闲约 1.36 GiB。后续实验顺序、强对照和失败时的处理条件都已保存。\n\n')
        f.write('该公开更新和实际final答复属于post-manifest appendices，不改此前冻结结果/台账/hand-off。最新actual poll为chunk4bba4d，native7425/new7326/cumulative16098.879282900016秒，仍返回session99542；未观察terminal exit。GPU chunk95b5f4：2026/10/07 20:17:56.151 free1394MiB/total24455MiB/util89%。下一次接续先poll同session99542，不重启/迁移。\n')
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        archive_observed_tool_chunk='0c61e8',archive_observed_tool_exit=0,
        archive_file=proof.relative_to(ROOT).as_posix(),archive_sha256=sha(proof),
        manifest_file=manifest.relative_to(ROOT).as_posix(),manifest_sha256=sha(manifest),
        new_stage_files_frozen=105,cumulative_frozen_evidence_files=1240,stage_bytes=15765078,
        previous1130_evidence_hashes_unchanged=True,metadata_record_observed_tool_exit=0,
        metadata_record_observed_tool_chunk='3ddaae',record_receipt_observed_tool_exit=0,
        record_receipt_observed_tool_chunk='f8bb84',
        new_primary_papers_read=3,successful_primary_PDF_pages=38,complete_selected_pages_read=23,actual_visual_pages=7,
        actual_final_reply_file=actual.relative_to(ROOT).as_posix(),actual_final_reply_sha256=sha(actual),
        post_archive_public_update_file=appendix.relative_to(ROOT).as_posix(),post_archive_public_update_sha256=sha(appendix),
        own_live_training_session=99542,latest_observed_live_poll=dict(chunk='4bba4d',native_update=7425,
            invocation02_new_updates=7326,cumulative_wall_seconds=16098.879282900016,returned_session=99542),
        latest_GPU_query=dict(chunk='95b5f4',timestamp_local='2026/10/07 20:17:56.151',free_MiB=1394,total_MiB=24455,utilization_percent=89),
        PCHIP99_is_historical_not_realtime=True,full_training_observed_tool_exit=None,formal_final_budget_completed=False,
        final_models_evaluated=False,final_execution_closed=False,publication_claim_confirmed=False,
        current_3D_lesion_confirmation_patients=0,whole_project_confirmation_zero_not_claimed=True,
        this_receipt_and_actual_reply_are_post_manifest_appendices=True,goal_status='active',finalize_script_sha256=sha(__file__))
    with (ROOT/'SESSION_CHECKPOINT_RECEIPT_PAIRED_AND_CALIBRATION_2026-10-07.json').open('x',encoding='utf-8') as f:
        json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,archive_tool_exit=0,new_stage_files=105,frozen_evidence_files=1240,
        live_training_session=99542,formal_training_tool_exit=None,goal_status='active')));return 0
if __name__=='__main__':raise SystemExit(main())
