# 两篇 MRI 原文核读及项目创新判断

本阶段核读两篇实际取得的原文：MMAR 物理页 1–30，XLSTM-HVED 物理页 1–5，共 35 页完整文字。其中 XLSTM 页 5 为参考文献，方法/结果/图页合计 34 页；MMAR 31–34 尚未完整读。实际查看 23 个不同原文页图，另放大查看 MMAR 七张表的宏平均部分，后者不重复增加页数。原始 PDF、提取、索引、下载与视觉 receipt 均保留；阅读不等于作者代码复现。

## MMAR：损坏感知的特征路由已有 MRI 病灶先例

Jesse Phitidis 等，*Hetero-modal learning and corruption-resistant hetero-modal inference for joint segmentation of white matter hyperintensities and ischaemic stroke lesions in MRI*，arXiv **2610.00553v1**，原文页边日期 2026-09-30。[原文](https://arxiv.org/abs/2610.00553)。目前是所取得版本的论文结果，未据此确认同行评审状态。

页 5–7：私有 Mild Stroke Study 3 数据，先选具有四种 MRI 和两类病灶标签的 **206 患者**，再模拟缺模态训练分布。ISL 人工勾画，WMH 半自动后专家修正；T1w/T2w/FLAIR 为 3D，DWI 为 2D，预处理到 1 mm isotropic。随机患者划分为 **103 train、41 validation、62 test**。Figure 1 的 cortical/lacunar 计数是病灶数，不能当患者分母。Split 2 为 11 完整模态患者 + 4×23 单模态患者；Split 3 为全部 103 患者有 T1w，另分别 34 T2w、34 FLAIR、35 DWI。这是从完整数据人为构造的分布，不是 206 名自然缺模态患者。

页 8–12：U-HeMIS 在各分辨率汇聚 available modalities 的 feature mean/variance；MMAR 改为跨模态、空间、通道的 transformer attention，softmax 后加权融合原始编码特征。缺模态编码被排除，严重损坏但被当作 present 的模态则由路由抑制。P=5、L=8、8 heads，局部窗口注意力。多通道 U-Net 配置到约 91M 参数，与另两种 hetero-modal 方法匹配；specialist 仅约 **16.7M**。所以不能把 hetero-modal 相对 specialist 的全部提升解释为同容量方法收益，更不能跨到本项目同 CISS 观测修正。

页 8 的 checkpoint 规则必须区分：普通 hetero-modal 实验从一次训练为 **15 个输入组合各选 validation Dice 最优 checkpoint**；corruption 实验使用最终 checkpoint。页 26–28 的 attention 分析也用最终 checkpoint 和 validation。此前只根据页首定位不能确定这个规则；完整核读后应以这里为准，不能写成 corruption 按 full-modal 最优 checkpoint 选择。

页 12–15：所有方法使用标准空间/强度/低分辨率及 MRI artefact augmentation。Corruption 另在 dropout 选出的模态中以 50% 概率替换为极端噪声、bias、blur、contrast 等，作用于整幅或随机块。MMAR 额外用**已知训练 corruption 模态集合 K**监督 router attention 向 0，分割与辅助损失 α=.9，按 available fraction 缩放；此缩放只给 MMAR。它是使用合成损坏信息的监督，并非无需损坏信息学会所有临床异常。作者假设初始训练扫描均未损坏。2000 epochs，每 epoch 定义为 103 subjects，AdamW lr .0003/wd .01，batch 2，20 epochs warmup/cosine；validation 每 50 epochs。不能据此猜每个 epoch 的精确更新数、被丢弃 batch 或全流程训练秒数。

页 16、29–30：测试没有真实损坏扫描，模拟 std=10 Gaussian、degree=2 bias 和仅一个角落 voxel 非零的 false-present；训练噪声参数不同，但这仍不能证明真实临床损坏泛化。只用 DSC、单次随机划分、每模型只训练一次，作者明确未系统比较所有 hetero-modal 方法。本文没有冻结预算下完整输入处理/路由/重建/分割成本的对照，未提供同一任务状态的修正动作净收益目标。

页 17、19、20、22–25 的七张表宏平均列已视觉转录并用 Decimal 重算：

| 条件 | 打印 MMAR−U-Net（Dice 百分点） | 打印 MMAR−U-HeMIS | 逐行比较提醒 |
|---|---:|---:|---|
| split 1 普通 missing | +0.55 | +0.04 | specialist 打印均值 51.54，MMAR 50.62 |
| split 2 单模态为主 | −1.85 | +0.80 | MMAR 对 U-Net 的 15 个宏平均组合全部更低 |
| split 3 T1w anchor | +0.29 | +0.68 | MMAR 在 8 个 novel 组合中 6 个超过另两模型 |
| corruption training，explicit missing | +0.84 | −0.57 | 不能只把 corruption 模型和普通模型归为同一条件 |
| false present | +1.37 | +2.62 | MMAR 对 U-Net 13/15 正，对 U-HeMIS 12/15 正 |
| Gaussian | +2.62 | +1.53 | MMAR 对 U-Net 14/15 正，对 U-HeMIS 13/15 正 |
| bias field | +0.86 | +0.51 | MMAR 对 U-Net 10/15 正，对 U-HeMIS 8/15 正 |

打印均值差与逐行 Decimal 差因舍入略有区别，详见 [CPU receipt](table_audit_attempt02/receipt.json)。Tables 4–7 的第 15 行为四模态全部 clean，未施加 missing/corruption；receipt 同时保留排除这一行后的 14 个组合结果。组合重复使用同 62 test patients，不能把 15 或 14 当独立样本做显著性。原文 superscript 来自 one-sided Wilcoxon/Holm-Bonferroni；没有原始患者预测，未自行重建 p 值。

Figure 6 是最高分辨率 16 通道 attention 的**最大投影**；Figure 7 是 validation 的 attention 均值。这些图能展示路由行为，不能当校准的“修正会提高病灶 Dice”的概率，更不能当行动因果收益。输入损坏与多模态融合的宽泛动态加权思路已有直接先例；把现成 attention 插入网络不构成当前已确认创新。

## XLSTM-HVED：缺模态补全与分割特征交互也已有先例

Shenghao Zhu 等，*XLSTM-HVED: Cross-Modal Brain Tumor Segmentation and MRI Reconstruction Method Using Vision XLSTM and Heteromodal Variational Encoder-Decoder*，arXiv **2412.07804v3**，原文页边日期 2025-03-05。[原文](https://arxiv.org/abs/2412.07804)。正文使用 T1/T1ce/T2/FLAIR，缺的是 MRI **模态**，与本项目同一 CISS 的 through-plane 缺层不同。

页 1–3、Figures 1–2：SAVE/MVAE 使用 PoG 融合 latent 并排除缺模态，Vision-LSTM attention 处理共享特征，SFECA/DuSFE 让重建与分割 decoder 特征交互。Figure 1 明确标 KL Loss、Recon Loss、Seg Loss、GAN Loss 和 discriminator；正文没有给出这些损失的完整权重/预训练更新数。页 2 描述预训练时只重建 decoder 活动，其他指定层静态，不据示意图反推各参数组精确训练合同。

页 3 作者报告 BraTS 2024 约 4500 patients、随机 80/20 train/test、batch 2、lr .0001、Tesla V100、72h；未核到患者 ID、另设 validation、重复扫描归并、训练总更新数、pretraining 是否含在 72h、参数匹配和所有比较模型完整费用。4500 是作者所写约数，不能把 3600/900 当本轮已核真实分母。RA-HVED/RMBTS 与本方法称同 backbone，不能据此自动推出同参数、同训练曝光与同完整成本。Table 1 还列 mmformer，未取得代码核实其配方。本文 Table 1/2 报分割 Dice/HD95，未见重建 PSNR/SSIM 或完整预算收益曲线，不能由结论的“重建更好”替代量化证据。

Table 1 已核对全部 15 组合 mmformer/Ours 的 WT/TC/ET Dice 与 HD95；Table 2 六个汇总端点也核。相对 mmformer，Ours 的逐行 Dice 差均值分别为 **WT +0.362、TC +3.1327、ET +0.3433 百分点**，胜/负分别 **11/4、10/5、9/6**。T1-only 的 WT 为 31.42 vs 61.32，差 **−29.90**；TC 差 **−21.16**。HD95 越低越好，WT/TC/ET 胜/负分别 11/4、14/1、15/0。这是异质的输入条件结果，不能称每个指标、每种输入均改善。

复核发现三个打印 Average 与等权条件行均值超出两位小数舍入范围的不一致，原文未解释其权重/分母，保留不擅改：

| Table 1 单元格 | 原文打印 | 15 行等权复算 |
|---|---:|---:|
| Ours WT HD95/mm | 17.86 | 18.0626667 |
| mmformer ET Dice/% | 52.99 | 53.0606667 |
| Ours ET Dice/% | 53.83 | 53.4040000 |

因此不能采用打印差 53.83−52.99=+0.84 作为经逐行复核的 ET 差；相应等权复算为 +0.3433。v1 实际 exit 1、v2 实际 exit 0 及修订理由见 [修订记录](AUDIT_REPAIR.md)。Table 2 去 SAVE/ViLA/SFECA 的打印六端点都退化，但它沿用部分 Table 1 打印汇总；未有等容量替换、等预训练、相同调参机会或患者原始数值，所以不足以独立归因到某模块，也不重建显著性。

## 对本项目的实质约束

两篇原文均限制“缺失补全 + segmentation”“坏输入检测 + attention”“动态分配处理”这些宽泛首创说法。它们没有在本项目固定 observed CISS、同容量充分适配、冻结合法修正与 task model、包含全部行动费用的条件下验证行动净收益。这个具体证据缺口可以作为**待验证问题**，不是查新完成或创新性已证。前轮已读 learning-to-defer、task-adapted reconstruction 仍是必要近邻；本轮不把它们遗漏来扩大 novelty。

实际索引 ID 核对：旧首 8 与新分页 11 无重复，覆盖该窄 joint-title 查询全部 19 个返回；额外 recurrent/attention 查询 5 个，与新分页无重合，两轮这两组查询合计 24 unique identities。本阶段新增 16 个题名摘要，只有本文件两篇进入原文核读，其他 14 仍只有题名摘要。**SERANet 仍未取得**，不是系统综述，不宣称整体领域排重完成。

本轮没有打开 MRI/标签/模型 arrays、没有新医学/GPU forward、没有头拟合、没有原文方法重训；公开表算术不计本项目 MRI 收益。后续准备见 [监督与选择机会控制](SUPERVISION_ROUTING_AND_CHECKPOINT_PREPARATION.md)。现有 terminal training、已执行源、原能力 gates、未见确认及 locked IXI 边界保持原合同。
