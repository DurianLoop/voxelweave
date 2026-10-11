"""Repair previously damaged entry paragraphs; keep original bytes as evidence."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'literature/source_cache/entry_encoding_fix_2026-10-03'
def main():
 OUT.mkdir(exist_ok=False);rows=[]
 messages={
  'README.md':'**最新完成：** [完整native16能力对照](MC_RC_NATIVE_COMPETENCE_CPU_RESULT_2026-10-03.md)及17次独立CPU前向重放通过，完整/稀疏两输入保护ROI均0/16；不能把失败全部归因抽层。[新增真实observed QDA/LDA诊断](MC_RC_ANCHOR_QDA_CPU_RESULT_2026-10-03.md)四模型均0/16、1216个anchor-plane/model及全部864缺层复核errors=[]，固定配置停止。[三篇新正文](literature/2026-10-03_anchor_representation_fulltext_reading.md)共256相关段、55索引响应进一步排除稀疏label/shape传播宽首创。当前16系列/8开发人，独立科学确认0、claim未达成。[创新判断](INNOVATION_DECISION_AFTER_NATIVE_AND_QDA_2026-10-03.md)、[后续准备](MC_RC_NEXT_EVIDENCE_PREPARATION_AFTER_NATIVE_2026-10-03.md)、[阶段记录](SESSION_UPDATE_NATIVE_AND_ANCHOR_2026-10-03.md)、[公开对话](SESSION_VISIBLE_DIALOGUE_NATIVE_AND_ANCHOR_2026-10-03.md)、[接续状态](SESSION_HANDOFF_NATIVE_AND_ANCHOR_ORIGINAL_QUEUE_ACTIVE_2026-10-03.md)。原83910继续；新56604只等它complete后做既有敏感性和真实112端点重算，不重启推断。GPU/用户训练/locked IXI test未触碰，goal active。',
  'EXPERIMENT_QUEUE.md':'最新状态：[native完整对照](MC_RC_NATIVE_COMPETENCE_CPU_RESULT_2026-10-03.md)及[真实观测QDA/LDA](MC_RC_ANCHOR_QDA_CPU_RESULT_2026-10-03.md)全量复核通过但保护区域均失败，固定配置停止。[新准备](MC_RC_NEXT_EVIDENCE_PREPARATION_AFTER_NATIVE_2026-10-03.md)记录表征/动作/未见患者要求。原83910仍执行；56604等待其完整完成后单次原112端点敏感性及真实重算，见[合同](VS_SEG_SELECTION_REAL_REPLAY_PLAN_2026-10-03.md)。下文旧状态为历史，不据部分结果宣称完整科学确认。'}
 for name,message in messages.items():
  p=ROOT/name;raw=p.read_bytes();lines=raw.decode('utf-8').splitlines();old=lines[2]
  if old.count('?')<20: raise ValueError('Expected inherited question-mark damaged paragraph absent; manual review required '+name)
  backup=OUT/(name+'.before.response');backup.write_bytes(raw);lines[2]=message;p.write_text('\n'.join(lines)+'\n',encoding='utf-8');rows.append(dict(path=name,previous_sha256=hashlib.sha256(raw).hexdigest(),backup_file=backup.name,new_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),scope='only top entry paragraph; UTF8 newline normalization'))
 (OUT/'attempt_01.json').write_text(json.dumps(dict(preexisting_literal_question_mark_damage=True,changes=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__': main()
