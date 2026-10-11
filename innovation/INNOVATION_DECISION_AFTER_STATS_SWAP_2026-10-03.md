# 统计互换与全45审计后的创新判断

当前仍没有可发表且经独立确认的新方法claim。研究goal保持active；本批论文、CPU控制和新来源预检已完成，不能用归档验收代替科学确认。

## 新增证据实际说明什么

[三人统计互换](TASK_STATS_SWAP_CPU_PILOT_RESULT_2026-10-03.md)只增加6次CPU前向并完成所有输入/保存预测/30端点复核。固定图像换raw统计，post的JSON full均值仅+.001410324，逐人有负反例；RT+.001523344。三人原post−raw为正而全45为负，所以不能外推为队列损失归因或SR恢复。

[全45统计审计](FULL45_NORMALIZATION_DRIFT_CPU_RESULT_2026-10-03.md)重放90旧数组，无新前向：post std平均−2.4882%，相同anchors归一化scale平均+2.5525%，RMS .026642。scale/RMS对Dice的Spearman接近0，不支持稳定风险排序；其Pearson和offset关联仍只是事后关联，不证明机制或排除非线性响应。

[3篇原始PDF](literature/2026-10-03_masked_normalization_primary_reading.md)直接排除宽归一化/掩膜新意：RN已有known/unknown区域统计，Partial Convolution已有masked convolution、observed compositing及hole污染BN讨论，Normalization-Equivariant Network已有affine架构和argmax分类不变推导及实验。不能把这些重新命名。

[新增3患者5series来源预检](MC_RC_011_013_SOURCE_PREFLIGHT_RESULT_2026-10-03.md)取得3个薄层3D/同网格通过系列，另外2厚层时点阴性保留；没有模型效果、完整身份split或科学确认。提供下一阶段数据准备的实际依据。

## 候选、必要对照与停止条件

| 候选问题 | 本轮决策 | 要求的新增证据 |
| --- | --- | --- |
| anchor-only mean/std独立新方法 | 仅保留为控制；直接先例充分 | 同统计规则训练，所有重建共享observed统计，不把小Dice变化命名为贡献 |
| 任务模型适应后仍存在可修正的缺层损失 | 优先研究的窄问题，未证实 | 6任务模型×5输入矩阵、相同总updates/患者权重/阈值，独立模型与真正未见患者；missing/anchors分别检查 |
| 学习少量局部修改以保护病灶、保留其他缺层收益 | 暂待任务表示能力与来源角色 | 新可观察表示先验证，不使用missing标签或真值crop；旧QDA/LDA/native失败、误差收益等价与随机预算全部作强对照 |
| 归一化等变MRI网络 | 现有架构基线，不能宽首创 | 完整padding/BN/attention性质及重训；报告同域性能损失，不引用去噪PSNR替代分割收益 |
| 按统计漂移挑患者或调anchors模糊 | 当前不启动 | 本轮缺乏稳定单调关系/全队列因果效果，禁止挑最好患者、域或参数挽救旧失败 |

可以准备的窄claim表述是条件句：**在相同真实稀疏observations、相同任务训练预算和已适应的评价网络下，某具体缺层修正是否还能改善未见患者的missing任务端点，并满足完整病灶与体积守卫？** 现在没有方法或效果支持填入“某具体修正”；不能写成论文结论。输入合同区分是验证设计，宽“SR影响任务”“normalize改进分割”“只保anchors”已经有先例。

## 执行顺序

先完成来源/全项目患者身份和角色核验，在任何新模型效果之前冻结训练/验证/确认患者。011/012/013只做了来源预检，保留pending；旧45与旧8整患者只作开发。随后在GPU可用且不干预当前训练时执行[既有矩阵规格](experiments/task_input_contract_matrix_preparation_2026-10-03.json)，保持其未执行、尚未冻结状态，不给缺患者名单的虚构训练命令。

第一轮任务能力必须在独立开发来源评估，不通过则停止该评价器的重建机制归因。若混合训练使差距消失，优先解释为任务曝光敏感，而不能继续宣称必然解剖损失；若适应后仍有稳定缺层损失，再投入具体修正并与raw PCHIP、固定修正、同容量taskloss与同预算随机直接比较。最后才用未参与方法/阈值选择的患者确认，不以原45或新来源预检充数。

所有旧失败继续有效：HAT−pipeline负claim已被完整+.036381704反证；残差相加2/6、order_rms守卫失败、anchors bandwidth fixed平均负、MC-RC native与QDA/LDA保护配置失败。三人微小统计互换不覆盖它们。
