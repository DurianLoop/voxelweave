# 从旧label资格接入正式动作实验

本准备可在原训练运行期间完成；不是新MRI效果、已测完整cost或已资格化head训练。沿用[真实17特征/label合同](../OBSERVED_FEATURE_TO_ACTION_UTILITY_PREPARATION_2026-10-08.md)、[强适配准备](../TASK_ADAPTED_ACTION_UTILITY_NEXT_PREPARATION_2026-10-08.md)、[同容量双输出准备](../task_utility_patient_exposure_2026_10_08/MATCHED_HEAD_AND_LABEL_PREPARATION.md)、[原56FOV入口结果](../MC_RC_3D_FINAL_EVALUATION_ENTRY_PREPARATION_RESULT_2026-10-07.md)。不回改上述冻结文件。

## 正式数据源和对象

旧qualification只支持同一个checkpoint的PCHIP/linear。正式方案须另存v2模块/新attempt，明确一个task checkpoint用于所有action/state，或明确路径各自task-adapted checkpoint且分开解释。不能删除checkpoint匹配约束后静默跨模型配对。每条路径登记合法输入source/input SHA、该任务网训练/调参患者角色、端点定义与完整原FOV coverage；以patient+UID+state+action连接，不按row顺序。

native_reference含更多隐藏native观测，不是可部署action。当前native与PCHIP两臂用于能力参照，绝不填成selector增益标签。正式legacy dense、direct、common-projected基线只用相同合法observed，按旧监督/容量/初始化/增强/预算合同充分适配。候选修正的定位只能来自observed或部署可用task状态，不能GT定位。修正前后及状态连续组合均在相同端点下独立评分；joint动作不由单动作ΔQ相加产生。

## 成本字段连接，不补造旧费用

保持旧full_action_cost=null。正式成本分两本账：模型/denoiser/selector训练和动作label生成是研究成本；实际部署完整患者是另一账，不能将前者抹掉或将训练label生成算成在线免费探测。部署账记录既有九相位及父级perf_counter墙时：启动、数据IO、定位、特征/selector、动作生成、transfer、任务推理、组合、后处理/失败。CPU或GPU同步边界、设备、dtype、batch、warm/cold和并发条件都固定且留档。

真实成本必须与产生分数的run/patient/UID/state/action/source/task SHA同源绑定。九个相位可含重叠或包含关系，保存起止与嵌套树；完整耗时以父级区间为准，不能把重叠计时求和。shared启动/公共特征只记一次；患者各series所需费用全合并。计时audit/落盘若不属于部署产品的实际输出，另列研究开销和含该开销总墙时，预先说明主要预算口径。

observed-feature或task probe即便最终defer也已耗费时间，必须付费。若候选图/候选task outputs是selector特征，它们在决策前已计算，费用计入所有患者，不宣称通过选择省下这些计算。只有确实未执行的后续动作才可省成本；增量成本来自当前state的真实执行、缓存共享由union过程实测，不能从独立单动作耗时相减外推。

## 新label的学习资格

真实label bundle需要完整11开发患者/19series固定集合、所有固定动作/状态和所有负/零/失败，且生产与独立计数重放都过。患者utility沿用现有complete-panel规则：患者内series等权、患者间等权；undefined不置0、不删患者。新的label可称task-in-sample开发标签；目前task训练见过11开发患者，head-only LOPO只能开发选择，不能宣称整个pipeline患者外。

cost/defer双条件成本与(m,g)输出都用真监督、同总容量和正则/优化/信息，保留等价loss控制；ΔQ回归与Pr(ΔQ>0)不互换。baseline-only risk是辅助控制，不能替代固定最佳action、两路径cost/defer、DC-based及既有SafeRestore特征/全候选计算控制。若task能力或可修正余量失败，停止拟合并保留负结果。

最终八未见患者/12series须待全部方法/端点/checkpoint/action/budget冻结后一次确认。已见4/9继续用于开发审查；locked IXI不开；旧MIRA/MSValid84记录不改。原终端训练未结束时不要读取中间checkpoint做效果选择。
