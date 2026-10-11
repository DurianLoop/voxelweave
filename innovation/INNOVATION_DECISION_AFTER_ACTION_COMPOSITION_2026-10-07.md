# 本轮创新判断与后续执行准备

最优先的科学问题仍是充分适配后是否存在可预测、可部署、同预算的病灶修正余量。当前19series共同初始化CPU训练继续，不能从单001旧模型的合成干预推断未来充分任务能力/真实SR效益。旧MIRA机制有外部确认，当前病灶效益尚无保留确认，两个范围明确区分。

| 候选主张 | 本轮排重/反证 | 留下的可检验问题 |
|---|---|---|
| 新的联合收益/成本greedy | Gözcü2018 Algorithm1已有精确形式；Sanchez2020已有候选/训练minibatch | 在严格observed和公平适配/实际端到端预算下，具体MRI病灶余量是否稳定 |
| greedy/lazy pruning有通用近似保证 | adaptive monotone/submodular未成立；部署GT不作反馈；联合coverage成本不是理论可加item cost | 先测真实效益的有限组合和边际，不把经验检验升级全局定理 |
| MRI局部动作收益自动相加 | AB概率有数值mixed响应但二值变化0；联合成本6而单项10 | 真实动作的最终联合效果要全FOV直接测，不能用单项label相加 |
| 正Dice联合interaction说明神经协同 | disjoint二值/混淆矩阵完全可加仍有1/15正interaction | 分离Dice分式、threshold/支持碰撞、神经/后续数值耦合；可预测的剩余实际效益才有研究价值 |
| 首创参考IN、局部cache、diffusion-step cache | SIGE/DeltaCNN/DeepCache前阶段已有 | 保留为已知计算实现/对照，不以资格通过当新病灶方法 |
| 充分任务训练使SR先前收益消失的受控结果 | 当前还未得到两个19998最后模型结果 | 若同observed强PCHIP/直接task解释原提升，完整公开零/负结果，评估是否有独立benchmark价值 |

## 立即接续事项

1. **继续同session99542**，不要启动替代训练。当前CPU float32/共同初始化/GT和增强流/LR和预算不改；GPU只在新独立协议及8GB可用门槛下启动。已有训练必须真实terminal exit0、每臂19998/总39996，再写原final-exit receipt、执行原56FOV评价及独立重放。训练未完成、损失下降、软件gates均不能提前通过任务资格。
2. 完整记录native与observed PCHIP能力；若原四验证gate任一失败，先排查能力与数据/实现合同。不要开放8确认、挑开发正病例、更换阈值救结论或把native差距叫SR收益。
3. 原能力通过后，先在11开发范围做同observed直接task和matched-init SR-task充分适配。全输入/监督/参数/更新/teacher/label计算成本匹配；强PCHIP、Linear及原SR系统均保留。四已见验证不得被重新称全新确认。
4. 只有真实observed生成候选且有修正余量时，冻结候选支持/组合规则/主指标。每患者候选都用GT-free observed信息生成，不能用本次人工中心/邻近/角落干预或病灶GT框直接充当可部署动作。先small fixed subset lattice真实跑empty/single/pair/union，所有最终评价使用完整FOV。
5. 每pair同步存概率mixed响应、二值mixed变化、TP/FP/FN，以及`dice_pair_decomposition`的分式项/非加性counts项。效益仍以完整patient-first Dice/recall/RVE等原端点评价；不要改主端点追求显著。后续坐标/动作冲突、重采样/normalization导致全局变化时由实际输入差分重定成本，不能仅拿面积或旧footprint。
6. 对照至少包括无动作、固定动作、同实际预算random、普通risk/error、同feature/capacity收益defer/双路径cost、union重新评价greedy；静态singleton排名与成本proxy只作错误假设对照。候选枚举/局部模型/GT label/策略训练/生成/搬运/cache warmup都记实际资源，不能只对最终少几个forward。
7. 开发/四已见验证选择完成后，再冻结用于八保留确认和第二独立任务网络的完整配方。要报告全分母、空/失败、患者CI与负结果；任务端点若无稳定余量或联合aware策略不优于已知对照，停止正向策略claim，不扩张无标签阳性队列。

## 未立即验证的准备

- 真病灶联合收益与神经交互：依赖充分任务资格及真实GT-free候选，当前没有测；现成精确counts分解和bitwise窗口审计可以接入。
- 正式GPU配方：用户已允许，但最近free1394MiB不满足既定门槛。当前正式CPU运行不迁移；新GPU实验需共同初始化、真实resource qualification、独立冻结配方，既有用户终端进程不操作。
- 旧MIRA发表缺口：Kuestner论文全文仍缺，作者代码已读，不重复计；纯原始采集身份未隔离，外部响应预测/guard仍负。只保留有来源/模型边界的context audit，不冒称临床风险证书。

本轮没有确认新可发表claim，goal保持active。最有价值的新约束是：必须测真实联合效益并排除指标自身制造的interaction，而不是仅证明网络输出非加性或cache减少调用。
