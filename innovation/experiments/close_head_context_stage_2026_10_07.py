"""Record the actual archive exit and the exact final reply without rewriting the stage manifest."""
import json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
import hashlib
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    archive=ROOT/'SESSION_ARCHIVE_VERIFICATION_HEAD_CONTEXT_2026-10-07.json'
    manifest=ROOT/'literature/head_context_stage_manifest_2026-10-07.json'
    result=json.loads(archive.read_text(encoding='utf-8'))
    assert result['complete'] and not result['errors'] and sha(manifest)==result['manifest_sha256']
    reply=ROOT/'SESSION_FINAL_REPLY_HEAD_CONTEXT_ACTUAL_2026-10-07.md'
    message='''本轮内容已存入[总览](D:/MRI/innovation/SESSION_RESULT_HEAD_CONTEXT_AND_STATISTICS_2026-10-07.md)。

- 新增核读3篇原始论文，完成6个CPU输出层诊断及独立核验。
- 单个开发病例的完整体积Dice达到native **0.678**、PCHIP **0.476**，仍未通过能力门槛；内部统计控制已通过数值预检。
- 优先候选是“充分任务适配后预测具体缺层修正收益”，后续对照和失败记录已备齐。

GPU当前空闲约1.4GB；完整GPU入口已准备，等待8GB启动条件。尚无已确认可发表claim。
'''
    with reply.open('x',encoding='utf-8') as f:f.write(message)
    files=[Path(__file__),reply]
    closure=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
                 archive_tool_exit_observed=0,records_writer_tool_exit_observed=0,
                 archive_file=archive.relative_to(ROOT).as_posix(),archive_sha256=sha(archive),
                 manifest_file=manifest.relative_to(ROOT).as_posix(),manifest_sha256=sha(manifest),
                 final_reply_file=reply.relative_to(ROOT).as_posix(),
                 closing_files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in files],
                 own_live_compute_runs=[],publication_claim_confirmed=False,scientific_confirmation_patients=0,goal_status='active')
    dest=ROOT/'SESSION_CLOSING_RECEIPT_HEAD_CONTEXT_2026-10-07.json'
    with dest.open('x',encoding='utf-8') as f:json.dump(closure,f,ensure_ascii=False,indent=2);f.write('\n')
    for p in closure['closing_files']:assert sha(ROOT/p['path'])==p['sha256']
    print(json.dumps(dict(complete=True,archive_files=result['evidence_files'],final_reply_saved=True,own_live_compute_runs=[])))
if __name__=='__main__':main()
