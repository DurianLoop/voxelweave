# 输入归一化、分割约束 harmonization 与跨中心任务评价：三篇重点正文

实际新增3篇 DOI 身份核对后的公开 JATS 正文，新增 PDF 为0。核读方法、实际任务对照、结果及限制；原文及具体证据块见[阅读登记](source_cache/task_normalization_context_fulltexts_2026-10-03/reading_provenance.json)。没有复现作者实验、视觉核图或核读 supplement。获取不等于阅读，标题返回不等于全文数。Europe PMC 四次503和备用检索原响应均保留；NCBI三个窄查询返回26条题名记录，含重复与非完整论文，不能计作26个独立研究。

## 多中心强度归一化：已有完整训练/测试矩阵

*Generalizable Multi-Site Training and Testing of Deep Neural Networks Using Image Normalization*，ISBI2019，DOI [10.1109/isbi.2019.8759295](https://doi.org/10.1109/isbi.2019.8759295)。[正文](source_cache/task_normalization_context_fulltexts_2026-10-03/multisite_normalization_maintext.txt)，实际读块0000–0024。

Stanford与Yale各300名患者，两台不同厂家3T scanner、T2W前列腺MRI。作者从人工mask的重心选中间轴向2D层，再统一1mm；不是完整3D病灶分割，也不是本合同无需目标真值的slice选择。用3-fold、同一修改U-Net及20,000步分别训练，比较none、min-max、Gaussian mean/std、median/IQR、histogram matching。跨中心、同中心与两中心混合训练实际都比较了。

在Stanford训练、Yale测试的none条件中，作者报告Dice中位数为0；Quantile两中心训练/测试中位数为.944。Table1中Quantile Stanford→Yale为.924、Yale→Stanford为.921；两个中心各自同域为.944/.945。不能把这些2D前列腺数字转成当前CISS肿瘤或固定anchors方案的效果。直方图目标由一个中心全部图像平均得到，正文未明确按每个训练fold重建，因此不能替作者补写严格fold隔离保证。

“改归一化可能改变跨域任务表现”和“混合训练输入改善外推”都有直接先例。作者自己限定只有两中心/2D，3D和其他任务为未来工作。没有本项目的missing逐位保持、只改anchors或固定配对baseline stats控制；有限检索中未见同控制不等于首创。

## SegRenorm：结构条件归一化与独立任务网络评价已有先例

*Segmentation-Renormalized Deep Feature Modulation for Unpaired Image Harmonization*，TMI2021，DOI [10.1109/TMI.2021.3059726](https://doi.org/10.1109/TMI.2021.3059726)。[正文](source_cache/task_normalization_context_fulltexts_2026-10-03/segmentation_harmonization_maintext.txt)。重点0002–0020、0028–0048、0051–0064、0066–0089及0100–0104。

这不是把图像mean/std改成常数。它在CycleGAN生成器每个残差块内先按channel标准化，再由预测分割的CNN embedding通过FiLM产生channel scale/shift，联合segmentation loss、GAN和cycle loss。source及target都需要训练分割标签或伪标签；测试时embedding来自预测mask，不能把它概括为无需任务监督。它直接占位“分割指导的归一化/结构保持生成”。

MS-SEG每scanner5人、三scanner，LOSO；RETOUCH和IXI按患者70/30分。IXI最终241人（74 GE、167 Philips），作者报告18扫描因伪影/强度异常排除；不是241+18名最终评价患者。IXI监督为FAST三组织伪真值，MS/RETOUCH为人工标签。无同一人跨scanner配对，作者明确限制任务/fidelity/噪声敏感度为代理指标。

更直接的先例在0072–0074：作者另训练独立于translation训练的domain-specific分割器，实际比较Source Segmentor→Source Image、Target Segmentor→Target Image、Target Segmentor→Source Image和Target Segmentor→Harmonized Image。MS SA→SV的目标网络跨域Dice为.37，本文harmonized为.50，source同域为.53；IXI WM为.77→.81，source同域为.88。提高并未恢复全部同域表现。Table5中的“upper/lower bound”是作者经验参照，不是数学界，也不能替代同一解剖真值。

视觉吸引力与独立任务响应不一致、segmentation regularization本身不确保鲁棒、slice-wise intensity inconsistency也都在正文讨论。作者指出不能保留全部生物学组间差异，未配对数据不证实真实形态无损；2D切片一致性postprocess是未来方案，不是已验证3D结果。本文不满足本项目observed-preserving合同，不能据它给当前失败anchors干预背书。

## FeTA2024：重建链和site混杂，开放问题已有明确表述

*Advances in automated fetal brain MRI segmentation and biometry: Insights from the FeTA 2024 challenge*，Medical Image Analysis2026，DOI [10.1016/j.media.2026.103941](https://doi.org/10.1016/j.media.2026.103941)。[正文](source_cache/task_normalization_context_fulltexts_2026-10-03/feta2024_maintext.txt)。重点0020–0040、0044–0058、0067–0078、0082–0130、0135–0165。

120训练、180测试case，训练两中心，test含新低场KCL；16有效分割提交，论文分析15队，另7 biometry队。所有输入为多方向T2 SSFSE stacks经过SRR重建、再统一256立方及朝向的体积。KCL原始1.5×1.5×4.5mm，经SVRTK成.8mm各向同性；不能将这些重建体素当原生薄层参考或直接收为本MRI确认集。本轮只读论文，没有下载其患者像素/申请数据。

Dice、HD95、VS、Euler difference共同评价；缺失输出被惩罚，而不是删去失败患者。多数方法Dice约.8–.82，topology排名会不同，更多复杂架构不等于实质收益。低场KCL反而最佳，但作者披露事后选择高质量重建和针对低场的新SVRTK，可能造成正向选择偏差；不证明低场天然优于高场。

site与SRR大多固定组合，所以实际建模使用合并site-SRR变量。RF/SHAP用前三队平均任务指标解释质量、GA、病理、site-SRR；这是关联，不能拆出SRR的独立因果影响。五折RF的解释方差约Dice63±11%、HD9538±18%，作者特别提醒HD95解释受限。高低质量间Dice约.10、病理约.008的差是这个观察队列的相关结果，不是干预效果。

正文0158直接指出：提供raw pre-SRR stacks、系统检查不同重建方案对下游分割的影响仍待研究。宽“SR影响任务稳健性”已被明确提出，当前新意只能来自受控的具体合同、可区分机制或确有效方法。FeTA无法替代当前无运动static CISS删层条件，reference标注本身也基于重建图像。作者提出对surface/clinical用途进一步验证，不能把Euler改善直接称临床收益。

## 当前候选的收窄

| 候选 | 本轮直接先例或本项目反证 | 处置 |
| --- | --- | --- |
| 改MRI强度归一化以改善跨域分割 | ISBI2019已有五策略×多训练/测试域 | 作为强对照，放弃宽首创 |
| 分割条件归一化/结构保持生成 | SegRenorm已有FiLM、联合监督与独立任务评价 | 不能只组合模块命名创新 |
| 冻结或独立任务模型评价生成图像 | SegRenorm、STRESS及既有MRI论文已实际做 | 当前单一冻结模型结果须升级证据，非独立贡献 |
| 观察层不变、重建却反馈改变全volume统计 | 本项目技术预检已证实；带宽恢复pilot失败 | 只保留精确操作链现象，候选anchor-only任务统计需新合同与训练 |
| 相同缺层输入、邻层控制后错误如何分布 | 当前三人fixed条件及事后计数提供软件证据 | 尚非独立科学确认或临床机制，可用于设计跨输入/模型控制 |
| 研究重建链对任务的影响 | FeTA已明确研究缺口，但site-SRR混杂 | 需要在同一原始observations下固定算子，不能仅做跨中心相关性 |

本阶段累计新增8篇重点正文：之前5篇/221证据块，加本3篇；不重复计旧全文或版本。科学目标仍active，当前没有可发表且独立确认的新方法claim。
