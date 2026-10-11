"""Prepend current completed-state pointers while keeping all historical material."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TEXT='**最新完整结果：** [45CISS全部结果](VS_SEG_COMPLETE_EVIDENCE_RESULT_2026-10-03.md)及[112真实筛选端点](VS_SEG_SELECTION_SENSITIVITY_REAL_RESULT_2026-10-03.md)已完成，原83910/56604实际exit0；58+112统计复核errors=[]。固定HAT−pipelinePCHIP图像误差降低、Dice平均+.036381704（95%区间全正），原负向claim被反证并停止；原网格PCHIP强基线、两标签/1mm带及全部次要结果保留。[新残差相加CPU对照](RESIDUAL_ADDBACK_CPU_RESULT_2026-10-03.md)六开发项297缺层仅2/6达标，独立数组/ROI复核通过，固定候选停止。[两篇新正文](literature/2026-10-03_task_utility_fulltext_reading.md)26题名/139相关块进一步排除图像任务分离宽首创。[创新判断](INNOVATION_DECISION_AFTER_COMPLETE_COHORT_2026-10-03.md)、[后续任务评估器准备](FROZEN_TASK_EVALUATOR_FOLLOWUP_PREPARATION_2026-10-03.md)、[本阶段记录](SESSION_UPDATE_COMPLETE_COHORT_2026-10-03.md)、[公开对话](SESSION_VISIBLE_DIALOGUE_COMPLETE_COHORT_2026-10-03.md)、[最新接续](SESSION_HANDOFF_COMPLETE_COHORT_2026-10-03.md)。这四个已完成CPU任务无需重启；GPU/用户训练/locked IXI test未操作，goal active，新方法独立确认0、暂无可发表新方法claim。下文运行状态为历史时点。'

def main():
    for name in ('README.md','EXPERIMENT_QUEUE.md'):
        p=ROOT/name;value=p.read_text(encoding='utf-8')
        if '最新完整结果：' in value: raise ValueError('Entry already updated; no duplicate prepend')
        head,body=value.split('\n',1);p.write_text(head+'\n\n'+TEXT+'\n\n'+body,encoding='utf-8')
    print('Both entrypoints updated; original historic bodies kept')

if __name__=='__main__': main()
