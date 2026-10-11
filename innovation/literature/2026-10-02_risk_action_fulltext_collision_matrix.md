# 三篇风险方法核读：固定缺层修正还缺什么

本阶段实际新增三篇公开正文的相关方法核读；不是新增三份PDF，也不是62篇全文。原四条Europe PMC查询返回38条记录，SURE/Stein的普通词匹配带来较多无关结果；精确题名补查的三个Crossref查询返回9条、额外Europe PMC查询返回15条，共62条响应记录，含重复和无关论文。检索不是系统综述，排名/无命中不能证明优先权。

方案及原响应：[初始方案](2026-10-02_risk_action_assumptions_search_plan.md)、[精确题名补充](2026-10-02_risk_action_exact_query_addendum.md)、[正文选择](2026-10-02_risk_action_body_selection.md)、[初始检索](source_cache/risk_action_assumptions_2026-10-02/attempt_01.json)、[精确题名检索](source_cache/risk_action_exact_titles_2026-10-02/attempt_01.json)、[首正文失败及ENSURE来源索引](source_cache/risk_action_bodies_2026-10-02/attempt_01.json)、[成功正文与哈希](source_cache/risk_action_bodies_2026-10-02/alternate_attempt_01.json)。

## Ramani等，2012：无真值MRI参数选择并非新概念

*Regularization Parameter Selection for Nonlinear Iterative Image Restoration and MRI Reconstruction Using GCV and SURE-Based Methods*，DOI [10.1109/TIP.2012.2195015](https://doi.org/10.1109/TIP.2012.2195015)，PMC3411925。[结构化正文](source_cache/risk_action_bodies_2026-10-02/gsure_parameter_2012_efetch_attempt_01_maintext.txt)。

已核摘要、引言、观测模型、GCV/SURE风险定义与Theorem 1、随机trace段、实验设计、结果、讨论、表格和图注文字。没有逐项核推IRLS/复数split-Bregman的全部Jacobian递推，也未取得其另置证明/补充材料、未逐幅看图，不声称复现原算法。

正文p010–012的模型是已知线性A、未知确定性x、加性实/复高斯噪声。p034直接写出：A具有非平凡零空间时，该零空间内的信息不可从y及噪声统计取得，完整MSE一般不可估计。Projected-MSE用P=Aᴴ(AAᴴ)†A；Predicted-MSE用A误差；二者不是完整图像风险的同义词。p041说明部分Cartesian k-space下两风险相等，都是在已采样频率上评误差。

Theorem 1估计的是指定WMSE，含已知噪声方差、加权Jacobian trace。文中用IRLS-MIL/split-Bregman和随机±1 trace，golden-section搜索λ。仿真是Shepp-Logan、Brainweb T2及已知回顾性采样；实测是GE phantom的10次独立全采样，另有无RF noise scan估方差，不是患者临床确认。

Table VII的Brainweb T2、40 dB条件：oracle/Predicted-SURE/NGCV为10.58/10.53/10.38 dB。Table VIII的50条径向线：33.03/33.03/32.16 dB；正文/图注的一处NGCV为32.30，与表不完全一致，本报告用表并保留差异。这些实例显示该方法在其条件下接近oracle，不能把近似成功推成任意零空间风险的可识别性证明。

碰撞：不能宣称首次MRI无真值风险估计、首次按风险选参数、首次发现零空间风险不可由观测认证。当前phase-0缺层的δ在观测位置为零，正是要先认证风险目标的情形；把两个SURE值相减也不会自动找回不可观测的误差。

## Aggarwal、Pramanik、Jacob，ICASSP2021：ENSURE的ensemble是采样operator

*ENSURE: Ensemble Stein’s Unbiased Risk Estimator for Unsupervised Learning*，DOI [10.1109/ICASSP39728.2021.9414513](https://doi.org/10.1109/ICASSP39728.2021.9414513)，PMC8323317。[结构化正文](source_cache/risk_action_bodies_2026-10-02/ensure_2021_efetch_attempt_01_maintext.txt)。25个提取段落全部核读，包括表1/图注文字；会议版说证明另见ref21，本阶段未读该证明或另版，不认证其全部定理条件。

p006的ys=Asρ+n包含随机采样s与已知高斯协方差C。p009明确GSURE的投影风险在严重欠采样时对完整MSE近似差；p010–016提出使用不同采样pattern的图像集、加权投影项和Monte Carlo divergence。single-channel采用每频率Bernoulli采样概率；multicoil以CG-SENSE取得投影，并简化density weighting。这里的ensemble不是同一固定观测下HAT/SwinIR两输出的委员会。

p017：3D T2 CUBE、1 mm、12coil、9志愿者，5train/2validation/2test。p018的输入为复数real/imag两通道；6倍k-space欠采样。Table1在σ=.01的model-based框架中，SSDU/ENSURE/supervised PSNR为37.89/38.44/39.31 dB，属于2名测试志愿者的初步重建验证，未报告病灶人工标签任务或逐患者完整风险certificate。p021承认数据规模小。

碰撞：不能宣称首次把采样变化、投影风险和自监督训练相连，也不能把“多phase随机训练”直接命名为新理论。当前固定phase-0病例并不满足多operator训练合同；由观测层再生成插值或重复运行网络不会新增真实观测。本文会议版公式的权重/期望和mask相关估计器条件需另核长稿证明，本阶段不以合成反例宣称推翻ENSURE。

## Janjušević等，2026卷期/2025线上：Rep2Rep需要独立重复噪声

*Self-Supervised Noise Adaptive MRI Denoising via Repetition to Repetition (Rep2Rep) Learning*，DOI [10.1002/mrm.70155](https://doi.org/10.1002/mrm.70155)，PMC13093144。[结构化正文](source_cache/risk_action_bodies_2026-10-02/rep2rep_2026_efetch_attempt_01_maintext.txt)。正文元数据为2025-11-09线上、2026年3月卷期。84个提取段落的正文、结果、限制及图表文字已核读；mrm70155-sup-0001-Supinfo.pdf未下载，图像本身未逐幅视觉复查。

p009–015区分coil间及重建后空间噪声相关性；p018–021区分SURE的特定对角噪声公式与Noise2Noise条件。独立重复可各自含空间相关，仍能抵消跨重复的噪声交叉项；这不意味着同一观测衍生的两模型输出有独立噪声。完整协方差的广义SURE是不同公式，不能把本文对其MC-SURE实现的限制说成所有SURE都无法处理相关噪声。

Rep2Rep以一重复→另一重复训练CDLNet，noise map直接调threshold，推断平均R次后按σ/√R作噪声适配。fastMRI synthetic-noise实验281个multi-slice datasets、253train/validation池和28evaluation；本文没有在这些段落把datasets逐个证明为不同患者，本报告保留其单位。

真实0.55T T2前列腺是73人，53train/validation池、20test；8次重复、同一2倍GRAPPA mask、3 mm slice，readout/repetition优先于phase encoding以保持重复间phase和共同底层信号。模型在128×128patch训练500k步，原文用A100；本阶段未训练。其任务是noise removal，非本项目轴向x4缺层恢复。

真实reader study：2-average denoising对8-average noisy在overall/capsule/artifact的p为.0093/.0278/.0444；kappa=.2343，fair agreement。真实图在train阶段选择20%sharpening与20%dithering，真实无完整noise-free oracle，不能把阅片偏好直接换算成病灶检出真值性能。讨论还承认无法在该回顾性重复抽取中展示减运动伪影，需多重复训练，极端noise OOD仍开放。未来joint reconstruction只是扩展建议。

碰撞：首次利用重复扫描、自监督去噪、噪声适配、重建后相关噪声问题均不成立。取得本文不等于取得它的重复k-space影像；本项目目前没有这份重复CISS/T2观测合同，不能拿两个模型当两次扫描。

## 与现有项目的具体连接

| 项目候选 | 本阶段核清的先例/限制 | 实际可做的下一步 |
| --- | --- | --- |
| 固定动作收益预测 | 无真值选参数已有先例；固定观测可能完全看不到δ的隐藏层风险 | 使用多个已用于设计的患者真值先测动作空间，再比较收益头、普通误差头及固定混合；需要新确认患者 |
| 观测残差作为安全守卫 | 投影风险无法一般认证零空间，保留观测不等于完整风险不变 | 报清风险所在域；不把观测误差相同当missing-slice收益certificate |
| random-phase / ENSURE型自监督 | 多operator训练已有先例，会议版完整证明未核 | 若以后准备此路线，先冻结真实可观测mask、noise模型和训练分布；不把现有fixed phase当已满足 |
| 重复扫描训练/校准 | Rep2Rep需同信号、跨重复噪声独立；空间相关与跨重复相关不同 | 先取得合格公开来源/原始重复及相位信息；当前只有文献，无新增患者数据 |

相关假设已在[合成CPU审计](../RISK_ACTION_ASSUMPTION_CPU_RESULT_2026-10-02.md)独立复算；它支持实验设计排除错误代理，不增加患者验证或方法新颖性。[后续准备](../RISK_ACTION_FOLLOWUP_PREPARATION_2026-10-02.md)将数据、对照和停止条件具体列出。

原2026任意尺度/TTA、knee diffusion、target-driven及Kuestner仍保留其[摘要层状态](2026-10-02_operator_multicontrast_abstract_access_result.md)，本阶段没有偷换成已读正文。

## 访问失败与阅读边界

两个Europe PMC正文500已归档；三个公开NCBI EFetch正文200，均核准确DOI、JATS article/body和正文内容，成功下载之后才分段阅读。三个文件的text-mining/fair-use许可文本保留，只作本地阅读证据，未对外再分发。ENSURE精确DOI的OpenAlex提供PMCID/arXiv线索；没有重复近期arXiv429搜索。eSURE原论文、完整ENSURE证明和Rep2Rep补充仍未核。

几次合并输出超过显示预算，对必要段落重新分块读取；不把被截断的全部递推段落称为逐式核推。原始JATS保留MathML，而提取文字不足以认证所有下标/根号；σ/√R同时按正文协方差1/R核清。临床数据下载、GPU训练或队列主统计均未进入本阶段。
