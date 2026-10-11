# ROUND51：论文约束与新的人工数值分支

本轮取得两步人工 GPU/CPU 一致性验证，但尚无独立确认的医学收益或可发表 claim。新的高精度分支在真实训练 patch 的人工成本测试中首路前向 OOM；原 FP32 production、全尺寸和 19-series 资格均未因此通过。用户原终端训练进程未被枚举或修改。

接续摘要全文、当前可见用户指令、公开进度和可恢复工具返回均已保存。旧工具对象无法恢复的部分按来源注明，未补造。

## 论文与作者代码带来的研究决定

| 文献/材料 | 这轮核查得到的约束 | 对本项目的决定 |
| --- | --- | --- |
| [Swin UNETR 固定 v2](https://arxiv.org/html/2111.14791v2) | CT 预训练权重用于 CT；四个 MRI 任务 from scratch。补读 Algorithm S.1 全部22行。 | 可作为强架构/自监督基线的先例，不能据此宣称 CT 预训练改善当前 MRI。 |
| [BrainSegFounder 固定 v3](https://arxiv.org/html/2406.10395v3) | UKB T1w/T2-FLAIR、BraTS 四模态，另有单 T1 实验；ATLAS 比较不采用五折，100幅训练集图像参与调参。 | 脑 MRI 预训练值得后续比较；普通单 T2/VS 的适用性、预训练患者重合与算力费用必须另验。 |
| [Greedy 作者当前 commit](https://github.com/Timsey/pg_mri/tree/d4e4164c5e7d13e57391f8a932ffd81958995dcd) | 已测动作 logits 设为 -1e7；MI notebook 有正确负熵；optimizer 更新在完整 trajectory 后；target 使用完整 GT 的统计量，质量评分据此反归一化。 | 修正仅依据 HTML 排版造成的疑问；模拟评价的 GT 统计不自动等于部署泄漏。不能把 mask 造成的概率变化当成任务信息收益。 |

独立从原生 HTML 单元格核查：Swin 数据表合计 **5010**（4761训练、249验证），正文写5050；训练迭代主文450K、附录45K，原因未知。BrainSegFounder Table4 的 one-stage-small 五折均值为 **0.90842**，表中写0.9110；同一 Fold2 在 Table4/Table8 为0.9055/0.9186。Table9 40% SwinU 的显示值均值为0.89396，表中0.8937，超出显示舍入界限。UKB 主表41400与训练表43369、ATLAS655与段落665、ATLAS stage2 LR3e-3与文字5e-3也保留为版本内不一致，不推断原因或作者实验真假。

新两篇全部抽取文字阅读由收到的接续摘要报告；本次恢复并逐块核验了 BrainSegFounder 前两个阅读工具块。其余原阅读工具对象未恢复，阅读来源区别保存在 scope receipt。图像像素、参考条目、PDF、作者训练和曲线均未据此认证；Greedy current commit 也不是已认证的发表时版本。

## 已执行的数值探索

原 stable_reduction 人工 step0 仍失败：parameter差 **3.4603290259838104e-6 > 3e-6**，step1未执行。独立定位逐一复现54参数与162state误差；最坏坐标 decoders.0.layers.0.weight[38,119,2,2,1]，两梯度9.021903224493144e-9与1.0362100510974415e-8，同为正值。NumPy FP64 AdamW首步公式预测全部参数，最大偏差6.839822219717462e-8；这解释本次人工更新的放大，不证明真实模型的所有误差都同源。

新 high_precision 分支保留54个FP32参数与原 AdamW 超参数，卷积、归一化、中间张量和loss用FP64；不调eps、不钳制梯度、不降门槛。CPU两步通过，参数更新差均为0。GPU实现另用不重叠2³窗口 max，CPU随机/全相等/重复最大值、FP32/FP64共6项检查的输出和全输入VJP bitwise一致，保留严格 deterministic algorithms。

人工GPU attempt04 对独立CPU两步通过：最大loss差2.868119297616545e-9、概率差2.043908542415096e-8、gradient差1.862645149230957e-9、parameter差 **1.4901161193847656e-8**、optimizer-state差4.656612873077393e-10；binary差0。GPU peak_reserved **1262485504 bytes**，结束时free22560112640 bytes。

随后同分支、原训练patch (2,1,64,128,128)、顺序三人工view的成本测试 **c4be7c exit1**：第一路forward开始后OOM，0路forward完成、0次optimizer update，peak_reserved2191523840 bytes。GPU实际仍有20.15GiB空闲；限制来自本进程既定allocator预算。没有全尺寸CPU对照，不能称全尺寸数值通过。

失败保留：PowerShell脚本生成引号失败、缺失脚本启动、bs4未安装的读取失败、GPU v1周期receipt独占创建失败、GPU v2本进程CUDA可见性被CPU import设为-1、GPU v3 native max-pool严格确定性失败、独立auditor v1语法失败。均另版本修复，不编辑已执行源码。GPU v1只保存初始receipt，末次写入异常遮蔽原内存异常；其精确optimizer计数不可恢复。已记录人工CPU更新10、GPU更新2，不能据此声称全轮实际总数已精确恢复。新增医学训练0，MRI/GT/parent数组读取0。

## 创新候选与可证伪条件

优先候选仍是：**在固定已观测的稀疏MRI和相同计算预算下，部署时可见的信息是否能预测处理动作的实际患者分割收益，并超过强静态方案、metadata-only、SSC/一致性和同信息risk-difference。** 这是待检验的任务级假设；联合动作、RL、自监督预训练、3D架构和条件互信息已有先例或经典定义，本身不构成新方法。

先恢复达到六医学门槛的强task；若合法动作的开发集oracle没有正余量，终止该候选。若oracle有余量，再冻结动作集合/成本、患者平均顺序、开发选择、cold-init严格LOPO与所有同信息控制。在动作可用性/历史相同的分层内做图像信息置乱；若效果仅由mask/metadata解释，放弃图像信息增益表述。最终8未见确认患者12series只在完整合同冻结后开启一次，4已见验证患者9series不能充当新独立确认。

候选二是受相同预算约束的动作组合交互，必须超过强单动作、静态组合、固定顺序、一步greedy及random，并通过患者级确认；现有联合选择文献使其不宜直接包装成新算法。外部BrainSegFounder可作为后续强task基线，先核查模态、许可/来源、患者重合、数据权限和真实推理/训练费用，不直接替换模型或下载权重。

## 已准备但仍待执行

1. 不重启正在运行的 full35904 pipeline；最新观测仅为prefix，终态后独立审核。
2. 为高精度分支新建减少归一化临时张量、解析VJP与activation recomputation/offload的版本；重新从独立CPU方程与有限差分开始，不继承旧资格。真实patch首路forward内也须降低峰值，仅减少三view同时驻留不足以证明可行。
3. 再跑同预算完整人工patch三view/两步、独立全尺寸关系与费用预估；通过后才进入真实全图/19-series及正式训练依赖链。原六臂104156359-byte预算不得借用为新数值分支的费用证据。
4. 主候选E1/E2以及外部预训练比较已写入新的future registry；医学实验均处于pending。

详细证据见 [新表格算术](../adaptive_acquisition_primary_followup_2026_10_09/foundation_table_arithmetic_attempt01/receipt.json)、[阅读来源范围](../adaptive_acquisition_primary_followup_2026_10_09/foundation_reading_scope_attempt01/receipt.json)、[独立核查](../adaptive_acquisition_primary_followup_2026_10_09/independent_round51_audit_attempt02/receipt.json)、[人工GPU结果](high_precision_model_gpu_attempt04/receipt.json)、[全patch成本失败](high_precision_fullpatch_cost_attempt01/receipt.json)。goal保持active。
