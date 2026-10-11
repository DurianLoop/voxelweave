"""Create final batch navigation only after complete validated effects and independent replay."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def write(path,text):Path(path).write_text(text.rstrip()+'\n',encoding='utf-8')
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    val=read(ROOT/'experiments/mc_rc_global_local_task_validation_cpu/attempt_01.json')
    proof=read(ROOT/'experiments/mc_rc_global_local_task_validation_cpu/independent_metrics_and_checkpoint_attempt_01.json')
    train=read(ROOT/'experiments/mc_rc_global_local_task_training_cpu/attempt_01.json')
    assert all(r['complete'] and not r['errors'] for r in (train,val,proof))
    gate='通过' if val['capability_gate_passed'] else '失败'
    means=val['aggregate']['raw_pchip']['patient_first_means']
    fmt=lambda v: 'undefined' if v is None else '%.6f'%v
    values='full Dice %s、missing Dice %s、recall %s、absRVE %s'%tuple(fmt(v) for v in (
        means['full']['dice'],means['missing']['dice'],means['full']['recall'],means['full']['absolute_relative_volume_error']))
    calls=sum(r[k] for r in (train,val,proof) for k in ('global_forward_calls','local_forward_calls'))
    entry='**本批最新完成（2026-10-03，全视野任务能力）：** [三篇新正文/334块及旧文19块补读](literature/2026-10-03_global_local_task_fulltext_reading.md)、[loss补充阅读](literature/2026-10-03_task_loss_followup_fulltext_reading.md)均完成；[20,000步CPU训练与四验证人/九系列/18输入](MC_RC_GLOBAL_LOCAL_TASK_CPU_RESULT_2026-10-03.md)完整结束，预写能力门槛'+gate+'，'+values+'。全部18预测独立计数/物理距离与54完整plane重放通过；总模型分支调用'+str(calls)+'，GPU0/科学确认0。[下一试验准备](GLOBAL_LOCAL_TASK_NEXT_PREPARATION_2026-10-03.md)、[创新判断](INNOVATION_DECISION_AFTER_GLOBAL_LOCAL_TASK_2026-10-03.md)、[对话](SESSION_VISIBLE_DIALOGUE_GLOBAL_LOCAL_TASK_2026-10-03.md)、[阶段记录](SESSION_UPDATE_GLOBAL_LOCAL_TASK_2026-10-03.md)和[接续入口](SESSION_HANDOFF_GLOBAL_LOCAL_TASK_2026-10-03.md)为本批入口；尚无可发表且独立确认的新claim。以下历史“当前/live”指其记录时点。'
    for filename in ('README.md','EXPERIMENT_QUEUE.md'):
        path=ROOT/filename;text=path.read_text(encoding='utf-8')
        assert not text.startswith('**本批最新完成（2026-10-03，全视野任务能力）')
        write(path,entry+'\n\n'+text)
    decision='''# 本批创新判断：任务能力先例与真实能力门槛

本批完成三篇原始正文/334文字块、旧 MC-RC 原文19块补读、20,000 CPU 训练、四验证人九系列两输入及54同模型独立几何重放。预写能力门槛%s；%s。独立指标和软件证据通过，不等于创新成功。科学确认0，研究目标active。

| 想法 | 新读与既有项目证据 | 当前决定 |
|---|---|---|
| 全 FOV 定位→局部分割、预测 mask/feature 引导 | VS cascade 与嗅球均有直接先例；本模型为能力基线 | 不宣称架构首创；先核无 GT crop 的完整患者能力 |
| 区域+像素loss、前景采样、控制 FN | Unified Focal Loss 与前述 nnU-Net/Soft spinal/DRIPS 已覆盖；608标签采样显示尺度差异 | 作为后续能力对照；采样统计不证明本模型失败原因 |
| 体积接近但空间错位 | 嗅球正文明确论述，单012只是已有现象的具体反例 | 保留多端点守卫，不作为新规律 |
| 训练曝光×统计×重建残余 | LGE已适应各重建后评任务；旧45CISS/统计互换与强PCHIP限制宽说法 | 仍是值得验证的问题；本轮只做能力，不冒充6×5矩阵 |
| 可观测局部修正保护缺层病灶 | 旧oracle/策略有反例；本轮没有实现新修正 | 先有合格任务模型、公平强基线和适应后残余，再冻结具体方法 |

%s

八确认保留患者角色未改变，未开效果。四验证人已用于本轮能力评价，后续仍叫验证；不能因为结果换人或转确认。第二独立任务模型尚未训练，本轮54plane重放共享architecture，不能算两个独立模型证据。下一工作见 GLOBAL_LOCAL_TASK_NEXT_PREPARATION_2026-10-03.md；没有可发表且独立确认claim。
'''%(gate,values,('能力通过只允许下一步native能力及同预算公平矩阵，不代表新的重建已优于PCHIP。' if val['capability_gate_passed'] else '固定模型能力失败，停止将其作为重建评价器。PCHIP/linear分数差不能用于判定重建路线；下一开发先做拟合性/优化与native能力对照，另立协议。'))
    write(ROOT/'INNOVATION_DECISION_AFTER_GLOBAL_LOCAL_TASK_2026-10-03.md',decision)
    state='''# 当前接续：本批全部CPU进程已结束，科学goal仍active

20,000步981,602参数、11开发/19系列随机初始化训练已完成；四验证人020/022/024/025的九系列×PCHIP/linear共18完整FOV预测完成。预写门槛%s：%s。输入145observed/36条件/九label轴、几何九×三切面、608开发label采样，以及全部计数/cKDTree距离/54完整plane重放均完成。它们不是科学确认，新claim未达到。

本批新文献三篇334块、MC-RC旧文19块补读登记完成，正文/源码/协议/checkpoint/预测/失败与公开对话均放innovation。原44473训练、74374几何、64970监督诊断以及本批验证/复核实际结束；不能重启或覆盖attempt。

约束：不使用GPU，不枚举/操作用户终端训练，不读locked IXI test、不改根环境/.gitignore、不创建/委派代理；所有新增仅innovation。Python D:\\conda\\envs\\MRI\\python.exe -X utf8 -B；数值CPU单线程、自身below-normal，磁盘15GB/可用内存8GB底线。当前11开发19、4验证9、8确认12，合计23人40合格；同人全部时点同角色，旧45CISS只开发。

下一步：%s正式6×5矩阵、完整native控制loader、直接任务/随机分辨率公平对照、具体可观测修正以及八确认人最终证据仍未执行。八保留030/029/019/028/031/026/027/015不可提前开效果；四验证已看过仍只作验证。全FOV、missing/anchors/tail、漏检、边界和体积端点均保留，阈值不在确认集调。

入口：[完整结果](MC_RC_GLOBAL_LOCAL_TASK_CPU_RESULT_2026-10-03.md)、[创新判断](INNOVATION_DECISION_AFTER_GLOBAL_LOCAL_TASK_2026-10-03.md)、[后续准备](GLOBAL_LOCAL_TASK_NEXT_PREPARATION_2026-10-03.md)、[可见对话](SESSION_VISIBLE_DIALOGUE_GLOBAL_LOCAL_TASK_2026-10-03.md)。新stage/global验收检查文件完整性，不代表科研确认。goal不得complete或blocked。
'''%(gate,values,('先按已准备协议实现native控制与正式公平矩阵。' if val['capability_gate_passed'] else '先另写能力开发协议，核同模型单病例可拟合性，再比较固定loss/采样与native能力，不修改本轮失败端点。'))
    write(ROOT/'SESSION_HANDOFF_GLOBAL_LOCAL_TASK_2026-10-03.md',state)
    update='''# 本批阶段记录

已完成：三新原始正文334文字块与MC-RC19块补读；九验证observed包145层/36条件/九label轴证明；无网络几何27完整切面、12物理z与三个合成覆盖条件；只开发标签608采样；20,000真实训练更新；四验证人九系列18完整预测；18组独立指标与54完整原生plane重放。GPU0、隐藏MR未解码、八确认人未开效果。

能力门槛%s；%s。完整endpoint、checkpoint身份与输入/代码/协议SHA在结果和JSON中保存。总模型分支调用%d；不将分支调用数当样本量或科学确认。loss/监督诊断描述既有开发采样，不证明失败原因。

软件准备和科学工作分开计：指标函数从旧模块按AST提取，来源SHA保存，避免双Torch interop初始化；新诊断split绑定最终checkpoint；独立重放共享冻结architecture，不是第二独立训练模型。正式矩阵/native控制/具体新修正仍未实施。

本次常规命令失败保留：AGENTS路径只读检查未找到文件（exit1，无改动）；曾试读错误的旧verifier文件名，后改为实际verify_mc_rc_sparse_task_training_cpu_pilot.py；Windows rg通配路径参数曾报文件名语法，改为目录+glob；一个内嵌Python的PowerShell引号错误导致SyntaxError，改用已保存show脚本/单引号here-string。这些没有产生科学结果或触发训练重启。

公开对话、用户摘要、各计划、失败及后续准备均已存档。论文获取manifest中的actual_reading_completed=false是获取时点记录，正式完成证据另存reading_provenance，不回写原始获取记录。归档验收仅检查来源文件/链接，不计科学证据。研究目标active，无可发表且独立确认新claim。
'''%(gate,values,calls)
    write(ROOT/'SESSION_UPDATE_GLOBAL_LOCAL_TASK_2026-10-03.md',update)
    print(json.dumps(dict(capability_gate_passed=val['capability_gate_passed'],total_model_branch_calls=calls,diagnostic_validation_patients=4,scientific_confirmation_patients=0)))
if __name__=='__main__':main()
