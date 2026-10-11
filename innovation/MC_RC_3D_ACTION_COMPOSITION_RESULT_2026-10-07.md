# 联合动作的真实开发MRI响应及精确指标控制

Observed-only开发001/UID369177、旧已认证PCHIP_last1024、事前固定三个7×7/+.25合成动作，全部8组合已执行。工具session41215/chunk10321c真实exit0。完整16tile/原batch2路径与缓存路径在7非空状态的全tile/physical/native概率逐位一致，baseline重复一致，ABC原production参考一致，全部资格gates通过。无GT/完整native MRI读取，无训练/CUDA，没有读取19series中间效果或四验证/八确认。

| 状态 | 输入改动体素数 | 最终联合推断所需原batch forward |
|---|---:|---:|
| A | 49 | 4 |
| B | 49 | 6 |
| AB | 98 | 6 |
| C | 49 | 1 |
| AC | 98 | 5 |
| BC | 98 | 7 |
| ABC | 147 | 7 |

同面积49的单动作成本分别4/6/1，说明面积不能准确替代这个固定tile计划的成本。AB单项计数相加10、联合6；ABC单项相加11、联合7。独立核验全部8subset的实际batch集合等于singleton集合并集，27个包含关系的边际递减不等式通过；这是固定集合成本的已知coverage结构，不是任务收益子模性或新定理。串行先运行A再修改为AB仍要重算，不把support增量2等同下一步执行成本。

整项资格实验实际116 CPU forward/232tile，含baseline8、repeat8、7完整56、7缓存36、production8；127.3575秒仅本轮同时负载下的单次wall time，不是benchmark。所有7干预的native阈值.5预测变化均0；不可称病灶改善或损伤。

| 概率mixed response `p_ab-p_a-p_b+p0` | full最大绝对值 | 原图支持不相交但同tile同时受影响 |
|---|---:|---|
| AB | 3.3378601e-6 | tile5/6/9/10四个共同影响 |
| AC | 2.2737368e-13 | 0 |
| BC | 2.2737368e-13 | 0 |

AB full RMS仅7.9690863e-9；不能把非零体素859783读成病灶数量或临床损失，也不能只归因IN。第三阶mixed最大1.7053026e-13。独立核验chunkc17d71真实exit0，仅读结果/hash：AC和BC全部16个tile联合概率SHA都等于唯一相关singleton或baseline，所以这些极小native混合残差不代表同tile神经交互。独立脚本未读MRI/GT、0forward。

## 后续病灶效益解释需要的精确反例

合成4voxel，GT=[1,1,0,0]，baseline全预测前景；A移除一个FP、B移除另一个FP，二值改动支持不相交，`pred_AB-pred_A-pred_B+pred0`逐体素严格0，TP/FP/FN均线性相加。

Dice依次为2/3、4/5、4/5、1，因此联合Dice interaction=1-4/5-4/5+2/3=**1/15**，全部来自Dice分式分母，非加性confusion-count残差为0。另1344个有效TP/FP/FN+disjoint-FP-removal情形用精确Fraction核验同一效应；空双方Dice保持undefined、无效additive-count oracle不静默clip。这个解析反例否定“Dice天然边际递减”以及“正Dice交互必是神经上下文协同”，不说明本项目病灶实际动作的收益或其最优策略。

已备通用函数`dice_pair_decomposition`：真实未来fullFOV冻结counts可分出Dice分式耦合与非加性counts残差；残差仍包括二值threshold/支持冲突，不能独占IN机制。病灶效益line确认人数0；旧MIRA外部确认人数另见RESEARCH_SCOPE_CLARIFICATION_2026-10-07.md。

[执行前协议](MC_RC_3D_ACTION_COMPOSITION_PROBE_PROTOCOL_2026-10-07.md) · [真实记录](experiments/mc_rc_3d_action_composition_2026_10_07/attempt01.json) · [独立核验/精确反例](experiments/mc_rc_3d_action_composition_2026_10_07/independent_tile_and_metric_control_attempt01.json) · [成本解释补充](MC_RC_3D_ACTION_COST_INTERPRETATION_ADDENDUM_2026-10-07.md) · [论文阅读](literature/2026-10-07_action_interaction_primary_reading.md)。
