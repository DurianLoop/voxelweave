"""Snapshot corrupt entry bytes, then update current stage without editing contracts."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/order_risk_and_phase_entry_snapshot_2026-10-03'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);snapshots=[]
 for name in ('README.md','EXPERIMENT_QUEUE.md','POST_TASK_AND_PHASE_NEXT_VALIDATION_PREPARATION_2026-10-03.md'):
  path=ROOT/name;snapshot=OUT/(Path(name).stem+'_before.txt');snapshot.write_bytes(path.read_bytes());snapshots.append(dict(original=name,snapshot=snapshot.relative_to(ROOT).as_posix(),sha256=sha(snapshot)))
 introduction='**最新完成（2026-10-03）：** [45人post完整任务](VS_SEG_POST_RESIZE_TASK_CPU_RESULT_2026-10-03.md)、[order风险失败](OBSERVABLE_ORDER_RISK_CPU_RESULT_2026-10-03.md)、[45人相位诊断](ANCHOR_BANDWIDTH_DIAGNOSTIC_CPU_RESULT_2026-10-03.md)及[三人12条件任务pilot](ANCHOR_BANDWIDTH_TASK_CPU_PILOT_RESULT_2026-10-03.md)全部完成并复核。JSON full raw/pipeline/post=.74460/.65476/.65284；post anchors fixed平均ΔDice−.00505，不支持带宽恢复解释，固定候选停止。[事后边界计数](ANCHOR_PILOT_BOUNDARY_DECOMPOSITION_CPU_RESULT_2026-10-03.md)与[实际missing输出审计](ANCHOR_PILOT_OUTPUT_DOMAIN_AUDIT_CPU_RESULT_2026-10-03.md)保留反例与身份控制；fixed missing输入不变时三人预测变化288/593/186体素。新增8篇公开正文/415重点块/PDF0，见[追加三篇阅读](literature/2026-10-03_task_normalization_context_fulltext_reading.md)。[创新决策](INNOVATION_DECISION_AFTER_POST_TASK_AND_PHASE_2026-10-03.md)、[后续矩阵准备](POST_TASK_AND_PHASE_NEXT_VALIDATION_PREPARATION_2026-10-03.md)、[完整阶段记录](SESSION_UPDATE_ORDER_RISK_AND_PHASE_2026-10-03.md)、[公开对话](SESSION_VISIBLE_DIALOGUE_ORDER_RISK_AND_PHASE_2026-10-03.md)及[当前接续](SESSION_HANDOFF_ORDER_RISK_AND_PHASE_2026-10-03.md)为最新入口。所有本阶段CPU进程已实际结束；GPU/用户训练/locked IXI test未操作。独立科学确认0，goal active，尚无可发表新方法claim。下文live/未完成字样为历史时点；入口乱码原字节快照保留。'
 for name in ('README.md','EXPERIMENT_QUEUE.md'):
  path=ROOT/name;text=path.read_text(encoding='utf-8');lines=text.splitlines();assert len(lines)>2 and lines[2].startswith('**????')
  lines[2]=introduction;path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 prep=ROOT/'POST_TASK_AND_PHASE_NEXT_VALIDATION_PREPARATION_2026-10-03.md';original=prep.read_text(encoding='utf-8');heading='## 2026-10-03完整pilot后的状态更新\n\n[三人pilot](ANCHOR_BANDWIDTH_TASK_CPU_PILOT_RESULT_2026-10-03.md)及12输入/36端点复核均已完成，不再运行。主要post_fixed−post JSONfull−.00505496、RTfull−.00507443；去1mm带正向但full负向，固定带宽恢复解释停止，不盲扩45。新增边界计数与实际missing预测审计均已完成，无新前向。原文下列“正在执行/尚无结果”等保留为写作时点记录。\n\n[新增三篇直接先例](literature/2026-10-03_task_normalization_context_fulltext_reading.md)证明归一化、多输入训练、分割条件生成与独立任务评价不能宽称首创。优先准备[6模型×5输入矩阵](experiments/task_input_contract_matrix_preparation_2026-10-03.json)：三种训练曝光×full-volume/observed-anchor统计，统一容量/患者权重/20,000拟定updates；比较native、raw、pipeline、post、HAT。anchor-only统计从observed MR计算，无reference labels或missing真值。该规格design_prepared_not_executed_not_frozen，真实训练/验证/未见确认名单及全部参数资格完成后才能冻结，当前没有启动GPU。\n\n[创新判断](INNOVATION_DECISION_AFTER_POST_TASK_AND_PHASE_2026-10-03.md)给出强对照和停止候选；旧45及MC-RC8患者只作开发，FeTA SRR体积不是原生薄层确认源。下一项独立工作是更窄先例与来源资格审计，不重复失败blur/排序候选。\n\n'
 prep.write_text(original.split('\n',1)[0]+'\n\n'+heading+'## 原准备内容（历史时点保留）\n\n'+original.split('\n',1)[1].lstrip(),encoding='utf-8')
 report=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),snapshots=snapshots,updated=[dict(path=name,sha256=sha(ROOT/name)) for name in ('README.md','EXPERIMENT_QUEUE.md','POST_TASK_AND_PHASE_NEXT_VALIDATION_PREPARATION_2026-10-03.md')],scientific_files_or_contracts_modified=False)
 (OUT/'provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(entries_updated=3,snapshots=len(snapshots),errors=[])))
if __name__=='__main__':main()
