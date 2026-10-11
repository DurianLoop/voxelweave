# CISS、脑肿瘤、胎儿与脊髓超分辨率：方法级近邻核读

本阶段从四个有边界的 Europe PMC/Crossref 查询中筛查 50 条返回记录（25+5+10+10），不等于 50 篇去重论文或全文阅读。随后核读以下四篇公开正文的研究设计、方法、结果、表格文字和讨论；没有下载或复现这些论文的受试者影像。JATS 中部分公式和图片没有完整文字表现，图像本身未逐幅视觉复查；这里只判断输入/任务/评价合同，不能据此重建全部网络或采集物理。

查询与来源：[检索方案](2026-10-02_task_throughplane_collision_search_plan.md)、[检索索引](source_cache/task_throughplane_collision_2026-10-02/attempt_02.json)、[三篇全文及原失败路径](source_cache/task_throughplane_fulltexts_2026-10-02/attempt_01.json)、[脊髓公开替代路径](source_cache/spinal_lesion_alternates_2026-10-02/attempt_01.json)。此前的[指标与任务先例](2026-10-02_task_metric_reading_and_innovation_limits.md)仍适用。这不是系统综述或“首次”优先权证明。

## 1. Katayama 等，2026，CISS 与听神经瘤

论文：*Evaluation of super-resolution deep learning reconstruction on three-dimensional constructive interference in steady state for enhanced visualization of vestibular schwannomas*，DOI [10.1007/s12194-026-01073-7](https://doi.org/10.1007/s12194-026-01073-7)。[正文](source_cache/task_throughplane_fulltexts_2026-10-02/ciss_vs_2026_maintext.txt)，[原 XML](source_cache/task_throughplane_fulltexts_2026-10-02/ciss_vs_2026_jats.xml)。

Methods / Patients：53 人中排除术后 8 人、缺无增强 CISS 6 人，最终 39 人；29 人为 gamma knife 后随访。Methods / Acquisition：Canon 3T，采集矩阵 256×240。Image reconstruction 明说三个方法来自同一 raw data；0.8 mm 层厚相同，SR-DLR 面内间距 0.1667 mm、矩阵 960×960，DLR/ZIP 为 0.25 mm、640×640。SR-DLR 为降噪网络、FFT 后 k-space zero filling、逆 FFT 与第二网络去除插值伪影，是厂商实现。

三个盲法阅片者评 tumor/nerve depiction、sharpness、noise、artifacts、diagnostic acceptability；定量用手工 ROI 的 ERD/ERS、SNR/CNR、组织强度与 CR。Table 1：对 ZIP 的瘤/神经显示评分均改善；对 DLR 只有 reader 2 对显示评分有显著改善。Table 2：ERD 为 3.4/4.0/4.3 mm（SR-DLR/DLR/ZIP）；CNR 为 29.5/29.2/20.5，前两者差异 p=.573；CR 为 7.3/7.0/6.7，对 DLR p=.023。论文只对两个方法比较作 Bonferroni，不在全部指标/读者上作整体校正。

Discussion / Limitations 明说面内提高、没有提高 through-plane；不同矩阵/spacing 混入采样密度贡献；没有评检测性能，瘤直径均值 14.1 mm、范围 3–25 mm。未报告固定自动分割器对人工标签的完整体积 Dice。

碰撞结论：不能声称首次 CISS 超分辨率病灶/脑神经评价、首次同 raw data 公平比较或首次小结构显示改善。本项目 phase-0 四倍抽层、保留观测、恢复内部全部余数、固定自动分割器与完整标签的合同不同，但差异本身不证明创新。本文正向显示结果也不能推翻或证明本项目任务得分降低假设，采集、算法和任务均不同。

## 2. Zhou 等，2022，脑肿瘤 SR、分割特征损失与层间插值

论文：*Super-resolution of brain tumor MRI images based on deep learning*，DOI [10.1002/acm2.13758](https://doi.org/10.1002/acm2.13758)。[正文](source_cache/task_throughplane_fulltexts_2026-10-02/brain_tumor_slice_2022_maintext.txt)，[原 XML](source_cache/task_throughplane_fulltexts_2026-10-02/brain_tumor_slice_2022_jats.xml)。

237 个 glioma 患者含 167 个 1 mm、其他 5 mm 层厚；76 例手工分割用于 UNet fine-tuning；SR 训练/测试段另使用 100 个未标注病例、70/30 划分。单轴位图像先以其前景均值/标准差归一化，再 MATLAB bicubic 四倍面内降采样，512→128；BraTS 240→60。该归一化不是本项目仅观测层估计范围的合同。100、76 与总 237 的完整人员交集、以及所有分割评价划分，在已读正文中没有足够细节可逐患者认证，不能自行补齐。

MRBT-SR-GAN 基于 ESRGAN/RRDB、高/低分辨率路径及任务导向感知损失；UNet 由 BraTS 训练后以本地标注 fine-tune，encoder features 用作感知损失。Methods 写 stage 4，Training settings 又写 stage 1–4；结果有各 stage ablation，不能把文字差异擅自消解成同一个单设置。

Results / Enhanced performance 写的是不同 SR 数据集上训练的 UNet；Table 2 的 WT Dice 为 bicubic .724±.11、MRBT-SR-GAN .786±.10。它不能直接等同于一个完全冻结的同一分割器在重建前后的 .062 增益，更不能当作层间插值的 Dice 改善。

Other modifications / Table 3 已比较 3/5 邻片、1/5 mm spacing；Slice interpolation / Table 4 用上下邻片作输入，并比较 2/4/6 输入片。1 mm 下 PSNR 28.80/28.87/28.88 dB，5 mm 下 21.90/22.54/22.36 dB。表 4 是图像指标，没有同一 through-plane 插值实验的独立任务 Dice；其距离描述也不足以与本项目 6 mm 两观测层中心间隔逐项对齐。Discussion 的复发/扫描时间好处是临床动机，不是已验证的诊断试验。

碰撞结论：分割 encoder 感知损失、脑肿瘤 SR 接分割、邻片数量/距离重要、上下片生成缺片均已有先例。项目可研究固定模型的完整标签误差与强 PCHIP 对照，但不能以“任务损失 + 多邻片”组合充当独立方法创新。

## 3. Sanchez 等，2025，多中心胎儿 SR 的测量偏差

论文：*Biometry and volumetry in multi-centric fetal brain magnetic resonance imaging: assessing the bias of super-resolution reconstruction*，DOI [10.1007/s00247-025-06347-7](https://doi.org/10.1007/s00247-025-06347-7)。[正文](source_cache/task_throughplane_fulltexts_2026-10-02/fetal_srr_bias_2025_maintext.txt)，[原 XML](source_cache/task_throughplane_fulltexts_2026-10-02/fetal_srr_bias_2025_jats.xml)。

三院 1.5/3T，真实 T2 HASTE 多方向厚层输入；NeSVoR .5.0、NiftyMIC .9.0、SVRTK auto-2.2.0 各默认重建 .8 mm isotropic。219 人先因重建质量去掉 74 人，再按 gestational-age bins 得 84 健康胎儿、252 个重建。论文 Population 文段与 acquisition 表的分院计数不完全相同，本笔记不据此重建人员名单；84/252 总数一致。研究目标明确条件于所有方法能得到充分质量重建；低质量时尝试不同 stack combinations，全部不可接受则排除，因此结论不能推广到全输入的失败率或病理胎儿。

四专家进行五项 biometry，低分辨率选最适合的 stack，SR 可以手工 rigid realign；BOUNTI 自动分割 19 区，报告其中五种体积。体积不是对手工真值的 Dice/ASSD。多变量 GAMLSS 调整 GA、rater、subject random effect；Table 2 小差异最大约 .43 mm，小于 .8 mm voxel；Table 3 体积方法差异约 1%，extra-cerebral CSF 约 2.7%。正文的一处百分比换算与实际 mm 量纲不易核对，本笔记只引用 mm 和 voxel 宽度，不重复它的“0.1%”措辞。

6 名选中健康胎儿另做四医生的视觉反馈，非 84 人全体临床试验；NeSVoR 某些 white-matter intensity / blurriness 得分较低，医生没有一致偏好以 SR 替代原始 stack。论文认为总体量化差异不大，同时承认强度改变和病理病例待评。数据不公开，supplementary DOCX 未取得，本阶段不声称补充实验已核读或已复现。

碰撞结论：SR 后的自动测量/体积偏差、定量与医生感受不一致、多中心任务评价已有先例。本项目“小病灶完整覆盖”的对象不同，但不能宣称首次任务与图像分离或首次评估重建偏差。

## 4. Wintergerst 等，ISBI 2025，脊髓病灶与线性对照

论文：*Measuring Impact of Super-Resolution on Spinal Cord MRI Scans: Lesion Detection Sensitivity, Variability, and Clinical Impact*，DOI [10.1109/ISBI60581.2025.10981088](https://doi.org/10.1109/ISBI60581.2025.10981088)。公开 PMC author manuscript，非开放许可全文；只作本地阅读归档。[正文](source_cache/spinal_lesion_alternates_2026-10-02/pmc_efetch_attempt_01_maintext.txt)，[原 XML](source_cache/spinal_lesion_alternates_2026-10-02/pmc_efetch_attempt_01.response)，[公开 HTML](source_cache/spinal_lesion_alternates_2026-10-02/pmc_html_attempt_01.response)。图注与 T1–T3 在 XML floats-group，正文 txt 未含它们，本阶段另从原 XML 核读。

53 名 MS 患者，mFFE .3125×.3125×5 mm、T2 .4878×.4878×2 mm、T2* .2539×.2539×5 mm。四条件：native、linear 至1 mm、linear 至原最佳面内间距、self-SR* 至同一最佳间距；self-SR* 基于 SMORE / ESPRESO slice-gap modeling 与 residual prediction，使用体积内高分辨率面内片 self-supervision。SCT 分割/配准到 PAM50，用冻结公开工具 sct_deepseg_sc、sct_deepseg_lesion 取得 C2–C4 的 SC/lesion volume。严重运动或任一步 preprocessing 失败者被排除；正文/表格未给足每模态最终分母，不能擅称全部 53 人四条件无失败。

Table 3，GM/WM lesion mean 为 101.04/112.09/141.66/182.08 mm³；同患者跨模态 volume STD 为 144.05/78.93/114.28/195.60 mm³。四条件与 EDSS 无显著关联。Discussion 怀疑 SR 可能产生不存在的结构，但没有手工病灶标签验证这个机制。论文用“sensitivity”描述检出体积增加；本笔记将已测量证据称为模型预测的病灶体积变化，不能等同于经真值认证的 true-positive 检测敏感度提高或幻觉增加。

碰撞结论：真实各向异性 MRI 的 self-SR/linear + 冻结自动分割 + 病灶体积/一致性 + 临床相关性已有直接先例。本项目同网格、人工标签 Dice/边界、强 raw/pipeline PCHIP 和输入预算认证能提高证据可信度，但“用了更完整评价”首先是设计质量，尚不是可发表新方法。

## 本项目仍可检验的窄问题

| 候选 | 已有先例排除的宽泛说法 | 本项目额外检验 | 当前证据状态 |
| --- | --- | --- | --- |
| 同观测约束下图像/固定任务方向分离 | 首次 SR 接分割、首次任务评价、首次显示改善 | 45 CISS 的固定 HAT−pipeline PCHIP 双主要终点；raw PCHIP、双标签/范围/边界敏感性 | 已见 001、202 均未支持任务降低；主队列运行中，不能改挑 SwinIR |
| 旧筛选改变所评病灶与模型比较 | 首次小结构/选择偏差提醒 | 全队列与旧资格组保持相同完整预测，另分解四目标抽样的图像差异 | 已验证覆盖组成，方法方向/排名未知；[次要方案](../VS_SEG_SELECTION_SENSITIVITY_PREPARATION_2026-10-02.md)待整队列复查后运行 |
| 预测固定修正是否有收益 | 首次残差、小波、任务损失、conformal 或误差头 | 观测可用特征预测动作收益，强固定混合/误差头对照，后续新来源确认 | 只是[准备](../GPU_FOLLOWUP_TASK_FIDELITY_PREPARATION_2026-10-02.md)，没有模型收益；先过 oracle 与任务缺口门槛 |

目前仍没有独立验证的可发表 claim。论文相似性不应驱使我们换一个更有利的结果；持续保留反证，并把待检验问题写成可以失败的明确比较。

## 来源失败与修复

第一检索脚本遇 GBK，已保留旧版与失败记录并改显式 UTF-8；第二次查询成功。首全文脚本把脊髓 BioC 的 HTTP200 当 XML，实际为服务错误文本，ParseError 已保留。其后 XML 语法/根节点验证使索引明确标未取得全文。此次 NCBI PMC HTML 与 EFetch 成功取得正文，Europe PMC HTML 403 保留；没有绕过认证、付费或登录。三篇原 JATS 和脊髓替代索引各带响应 SHA256，成功下载不自动等于完成阅读或复现。
