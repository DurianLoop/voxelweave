# 本批之后的可执行准备与尚未执行项

已完成的CPU队列不重跑：[统计互换6前向](TASK_STATS_SWAP_CPU_PILOT_RESULT_2026-10-03.md)、[全45统计无前向审计](FULL45_NORMALIZATION_DRIFT_CPU_RESULT_2026-10-03.md)、[011/012/013来源资格](MC_RC_011_013_SOURCE_PREFLIGHT_RESULT_2026-10-03.md)。全部生产与复核进程已实际exit，没有live训练/下载队列。GPU未使用，用户终端训练未操作。

| 下一项 | 已准备的真实输入 | 尚缺什么 | 当前状态 |
| --- | --- | --- | --- |
| 来源患者角色冻结 | 71人/159 exact-UID候选CSV、旧8人开发排除、全58共享VS-SEG身份排除、3患者来源预检 | 全项目曝光交叉核验、跨来源身份、全部拟训练来源资格、患者级split | prepared，未冻结 |
| 任务输入/训练曝光矩阵 | observed-only统计定义、3曝光×2统计×5输入规格、已见45人输入/任务对照 | 真训练/验证/未见确认名单、全部augmentation/optimizer/阈值与预算、合格任务网络 | prepared，0训练 |
| 新可观察病灶表示 | 原8患者observed MR/anchor label开发合同、旧QDA/LDA和native反例 | GPU训练、独立开发能力、无missing真值crop的数据流水线 | prepared，未验证 |
| 具体重建修正 | 原raw强基线、全部输入hash、动作/ROI与病灶守卫 | 任务适应后仍有修正空间、新方法而非旧失败参数调整 | 未开放训练 |

后续CPU首先整理患者身份与split候选，不先读取新患者的模型效果。对011/012/013是否归训练、验证或确认，需要根据完整来源人数和patient-group规则先冻结；不能先测试再把表现好的留confirm。相同患者013的三个时点整人一角色，两个厚层时点的源预检阴性保留。

对训练矩阵中的native-reference control，完整reference输入只作能力参照，不能冒充稀疏部署。混合曝光四重建各占同一总update预算的1/4，避免把更多训练作为所谓方法改进。anchor-only统计必须从observed MR获取，与full统计分别在训练/推理一致；随机强度augmentation若采用，应先按合同处理统计再同步变换全部候选。

每种任务网络使用一条事前验证checkpoint规则，不按某个evaluation输入挑模型。主任务为完整missing支持域病灶端点，同时报告anchors、full、tail/undefined及两种标签、真实物理边界与体积；不是只挑1mm带外的有利端点。最终科学确认需新患者与独立任务网络，当前0。

没有GPU启动命令，因为训练/确认名单及参数尚未冻结；没有启动或停止任何用户训练。新来源的原始ZIP、标签和身份记录都已保存，可供下一轮CPU资格整理直接使用。
