# 本轮先例带来的可证伪问题和后续实验准备

这是对下一阶段设计的补充，不是新的正式训练冻结，不改变正在运行的两臂、56 FOV 能力评估、三臂资源资格或已冻结端点。当前原训练未结束，新模型效果未知。

本项目已完成共同 observed source 输入资格：direct 两通道与旧 direct 在 19/19 开发完整体积逐位相同，common-projected dense 是有解释价值的新输入顺序控制。输入资格没有测出任务收益。既有更多 native 输入只作诊断上界；旧弱 9 pair、57,600 gain、合成 checkpoint 不进入正式行动标签/收益头。

| 优先级 | 待验证问题 | 原文限制 | 可推翻此候选的结果 |
|---|---|---|---|
| 1 | 同 observed、同容量充分适配后，固定合法修正是否仍有病灶任务净收益，且能由 observed 状态预测？ | joint completion、attention routing 和 defer 均有先例；仅增加模块不够 | 最强静态适配消除余量，或 observed 不能预测净收益，或完整费用下无优势 |
| 2 | 共同投影 dense 与 legacy dense 的顺序差异是否解释 direct/dense 的任务差异？ | 重建/任务耦合已有；输入实施本身不是新临床效应 | 共同 source/geometry/容量后差异消失；保留为混杂控制，不包装成首创 |
| 3 | 收益选择相对同特征/容量的损坏、风险或误差选择，是否在冻结预算下更好？ | MMAR 使用合成 corruption 监督；attention 大小不是行动收益 | 只在额外监督、更多 checkpoint、更多处理或更多推理调用下获胜 |

当前更可信的潜在 claim 表述应是：“在固定 CISS 缺层观测、充分适配的任务模型和完整费用约束下，预测局部合法修正的病灶任务增量，能否在同成本下超过最强静态与风险/defer 控制？”这仍是研究问题。不得使用“首次学习 MRI 动态路由”“首次联合补全和分割”“已证明临床损坏鲁棒性”。最终能否可发表还需效果、独立确认和更完整查新。

## 监督机会要一起配平

后续正式合同需逐臂记录：开发患者/series、每患者完整监督曝光、mask 标签来源、是否使用完整 native MRI 作训练 target、合成 corruption/missing 标记来源、pretraining 来源/更新数、辅助 loss、action label 产生费用以及各组件训练费用。完整 native 可以作为合法训练监督，但不能作为 deployed 输入/动作 ROI，不能给 proposed 单独享有而不给 matched control。不给 corruption 监督的风险 baseline 与有该监督的路由网络的差异，不能称仅目标函数收益。

若后续探索类似 MMAR 的 confidence/attention 输入，其 known availability 来自采样 mask，必须对照朴素 mask-aware direct/normalized convolution；本项目每 4 层的已知缺层不等价于 silent catastrophic multimodal corruption。不能偷偷加入第二 MRI 模态或根据测试标签选 ROI。Synthetic corruptions 仅能在另存开发协议、共同 augmentation 和明确目标后研究；现阶段不扩增原训练难度或冻结观察集。

## checkpoint、容量和曝光要一起配平

MMAR 普通实验每组合各选 checkpoint，corruption 使用 final。这提醒后续所有比较臂必须有同等选择机会、相同选择端点与 validation budget；固定输入研究优先沿原最终模型规则，不改当前模型选择。若未来采用 validation 选择，事先另冻且给全部臂同等机会，记录 evaluated checkpoint 数和 validation 费用。不能挑 proposed 的最优 checkpoint 去比 static 的 final。

“同 backbone”单独不足。记录可训练参数总数、输入通道、共享/专用 encoder、decoder/attention 及 frozen 模块；有模块消融时应区分 capacity/exposure，若归因模块本身需同容量替代和同更新控制。每个合法输入都需要充分任务适配，禁止靠固定不适配 evaluator 显示收益。

## 行动目标和成本的记录粒度

对当前合法状态 s 与动作 a，记录配对真实任务变化 ΔT(a|s) 和完整增量费用 ΔC(a|s)，方向/单位沿后续正式端点合同；净效用为 ΔT−λΔC 或在固定总预算下比较，λ/预算必须在确认前冻结。含观察特征、候选定位、路由、修正、DC、全 FOV task inference、回退/拒绝和共享输入成本，不能把原本需运行的重建/分割当免费。

注意力权重、重建 PSNR、已知 corruption 标签和 baseline uncertainty 可作特征/对照，不能直接充当配对 ΔT 标签。多个局部行动有交互，按真实当前状态重新测，禁止把单动作 gain 相加。双路径 defer、最强静态、同额外训练曝光、同特征/容量风险头、cost/defer/DC、预算随机和 union-aware greedy 均沿既有准备保留，记录零收益与伤害患者。

## 下一医学执行的先后依赖

1. 保持 session 99542，取得原两臂各 19,998 的 final、真实 exit 0 和冻结；不迁移 CPU 配方到 GPU。
2. 原完整 56 FOV 评分；两臂全六能力 gates、四已见患者/九 series 对应门槛及独立 strict，观察真实退出。
3. 满足 RAM/disk 和新增 GPU **8,000,000,000 bytes** 储备后才进入既有三 observed 臂的真实 19-series 资源 attempt 02。尚未执行，不用本轮公开表估训练费用。
4. 根据真实资源另冻充分适配医学预算及长期 runner，记录重启累计成本；已完成的 CPU 累计账原语仅人工 markers 合同，不自动成为正式医学 runner。
5. 固定任务模型/合法动作后实测病灶余量和费用，再决定是否产生新的训练标签/头，不先挑收益再改变 action。
6. 全组件、端点、预算、阈值、checkpoint 冻结后才开未见 8 患者/12 series。4 已见验证不能重新命名为独立确认；locked IXI 继续关闭。

这些条件使假设有机会被推翻。当前仍无经独立确认的可发表 MRI 效应，goal active。
