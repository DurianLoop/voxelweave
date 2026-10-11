"""Preserve pre-edit navigation and original selection bytes, then prepend current entry."""
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/sparse_task_entry_snapshot_2026-10-03'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);receipts=[]
    for name in ('README.md','EXPERIMENT_QUEUE.md'):
        p=ROOT/name;dest=OUT/(name+'.before.txt');dest.write_bytes(p.read_bytes());receipts.append(dict(file=name,snapshot=dest.relative_to(ROOT).as_posix(),sha256=sha(dest)))
    folder=ROOT/'literature/source_cache/sparse_task_joint_fulltexts_2026-10-03';acq=json.loads((folder/'attempt_01.json').read_text(encoding='utf-8'));selection=ROOT/'literature/2026-10-03_sparse_task_joint_selection.md';old=selection.read_text(encoding='utf-8').split('\n正文核读后的追加修正：',1)[0].rstrip('\r\n');candidates=[]
    for newline in ('\n','\r\n'):
        for endings in range(1,4):
            for bom in ('','\ufeff'):candidates.append((bom+old.replace('\r\n','\n').replace('\n',newline)+newline*endings).encode('utf-8'))
    exact=[b for b in candidates if hashlib.sha256(b).hexdigest()==acq['selection_sha256']];assert len(exact)==1
    dest=OUT/'selection_before_addendum.md';dest.write_bytes(exact[0]);receipts.append(dict(file=selection.relative_to(ROOT).as_posix(),snapshot=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),reason='Original source acquisition selection SHA; append-only correction retains the initial bytes here'))
    entry='''**本批最新完成（2026-10-03，稀疏任务CPU训练）：** [4篇原始正文/393文字块](literature/2026-10-03_sparse_task_joint_fulltext_reading.md)明确“各重建输入训练后再比较分割”已有直接先例。[当前40合格/19开发系列与19真实输入](MC_RC_DEVELOPMENT_INPUT_CPU_RESULT_2026-10-03.md)及354observed层/76输入独立复核通过；旧39/18是漏掉002已合格时点的历史生成错误，11/4/8患者角色不变。[两次从头CPU训练/8000updates](MC_RC_SPARSE_TASK_TRAINING_CPU_RESULT_2026-10-03.md)全部实际结束并独立核指标/15个plane重放，主pilot与单病例能力门槛均失败；单病例体积接近但Dice/边界失败。新forward调用13,779/GPU0/科学确认0，不能以弱任务网络评价重建。[创新判断](INNOVATION_DECISION_AFTER_SPARSE_TASK_TRAINING_2026-10-03.md)、[后续准备](SPARSE_TASK_CAPABILITY_AND_MATRIX_NEXT_PREPARATION_2026-10-03.md)、[完整记录](SESSION_UPDATE_SPARSE_TASK_TRAINING_2026-10-03.md)、[对话](SESSION_VISIBLE_DIALOGUE_SPARSE_TASK_2026-10-03.md)、[最新接续](SESSION_HANDOFF_SPARSE_TASK_TRAINING_2026-10-03.md)和[归档验收](SESSION_ARCHIVE_VERIFICATION_SPARSE_TASK_2026-10-03.json)保存成功/失败与未做工作。当前无live CPU队列，6×5未执行，4验证/8确认保留未开效果，goal active/未有可发表且独立确认claim；下方“当前/live/39”仅是历史时点。

'''
    for name in ('README.md','EXPERIMENT_QUEUE.md'):
        p=ROOT/name;text=p.read_text(encoding='utf-8');assert entry not in text;p.write_text(entry+text,encoding='utf-8')
    record=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),snapshots=receipts,complete=True);(OUT/'provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(record,ensure_ascii=False))
if __name__=='__main__':main()
