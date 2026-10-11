# MRI 扩散与流模型排重笔记（2026-09-30）

本轮结论：**不建议把“PAST 后接少步扩散/rectified flow”“分频扩散”“按厚度或难度增加步数”作为新方法核心。** 这些机制已有直接 MRI 先例，2026 年 DRIFT 尤其接近“强确定性基底 + 残差流细化”。当前值得保留的窄假设是：预测某个固定细化动作相对基底的实际收益/损害，而不是预测难度或不确定性；但这只是待排重、待证伪的研究假设，尚不是已成立创新。

本文没有启动训练。项目事实以 `design/PASTNET_RESEARCH_SUMMARY_2026-09-24.md` 为准：修复数据 control 为 25.567453 dB；四真实锚点、linear coarse + bounded residual、缺失层逐 series 再逐 patient 等权；多数增量不足 0.02 dB；分频读出相对共享读出仅 +0.001613 dB 且 MAE 退化。本文不把这些负结果外推为信息上限，也不预言扩散一定提高 PSNR。

## 1. 来源与阅读边界

页码一律指本地 PDF 的物理页号，即提取文本中的 `=== PDF PAGE n ===`，不是期刊页码。原始论文和提取文本已归档在本目录与 `extracted/`。身份核验日期为 2026-09-30。

| 论文 | 核验身份与官方链接 | 本轮阅读范围 |
|---|---|---|
| Likelihood-Separable Diffusion Inference for Multi-Image MRI Super-Resolution | [arXiv:2601.14030v1](https://arxiv.org/abs/2601.14030v1)，2026-01-20。arXiv 未列会议；在 [CVPR 2026 官方全文列表](https://openaccess.thecvf.com/CVPR2026?day=all) 未检出该标题，Crossref 标题检索亦未返回对应会议记录，因此**不能据本地 CVPR 文件名前缀写成 CVPR 2026 论文**。这不构成未录用证明。 | 全文可得；精读主文 PDF p1–8、方法与实验，未逐项复核全部图像和参考文献。 |
| Scale-Cascaded Diffusion Models for Super-Resolution in Medical Imaging | [arXiv:2601.23201](https://arxiv.org/abs/2601.23201)；[DOI:10.1109/ISBI61048.2026.11515890](https://doi.org/10.1109/ISBI61048.2026.11515890)。Crossref 核实 ISBI 2026 proceedings，2026-04-08。 | 全文 4 页，精读方法及两张结果表。 |
| MRI Super-Resolution with Partial Diffusion Models（PDM） | [DOI:10.1109/TMI.2024.3483109](https://doi.org/10.1109/TMI.2024.3483109)，[IEEE 官方页](https://ieeexplore.ieee.org/document/10720924/)。Crossref 与作者稿首页一致：TMI 44(3), 1194–1205，2025 年 3 月；DOI 含 2024 不等于正式卷期为 2024。 | 本地为 39 页作者稿全文；精读 p9–16 的方法、数据、through-plane 设置及局限，并核对首页与部分表图。 |
| MoEDiff-SR | [arXiv:2504.07308v1](https://arxiv.org/abs/2504.07308v1)，[作者代码](https://github.com/ZWang78/MoEDiff-SR)。本轮只确认预印本；LaTeX 模板页眉不是发表证明。 | 全文可得；定向读 p1–6、p9 的区域门控、训练输入、数据划分与局限，用于排重。 |
| MRI super-resolution reconstruction using efficient diffusion probabilistic model with residual shifting（Res-SRDiff） | [arXiv:2503.01576v2](https://arxiv.org/abs/2503.01576v2)；[DOI:10.1088/1361-6560/ade049](https://doi.org/10.1088/1361-6560/ade049)。Crossref 核实 Physics in Medicine & Biology，2025-06-16。 | 全文可得；定向读 p2、p4–9、p11 的残差迁移与退化，不把摘要性能当本项目复现。 |
| DRIFT: Difficulty-aware Rectified Flows for Through-plane MRI Super-Resolution | [arXiv:2607.16649v1](https://arxiv.org/abs/2607.16649v1)，2026-07-18；[作者项目页](https://yoonseokchoi-ai.github.io/drift-eccv2026/) 标注 ECCV 2026。本轮 [ECVA 官方论文页](https://www.ecva.net/papers.php) 尚显示 ECCV 2024，故写作“作者项目页标注 ECCV 2026，本文核实了预印本全文”，不独立升级为已核实正式 proceedings。 | 下载 35 页 PDF；读主文方法和实验、补充 S1–S4、S10–S13，重点核查难度调度是否等价于收益预测。 |

## 2. 先把任务边界分开

| 方法 | 真正输入/退化 | 能否直接作为当前单 T2 缺失层插值基线 |
|---|---|---|
| Likelihood-Separable MISR | 同一 pulse sequence 的两个/三个独立正交低分辨率体积；Gaussian slice profile 卷积、抽样、噪声；预训练 3D T1 先验 | **不能直接。** 增加正交采集是增加真实信息；当前四锚点不是四个全体积正交观测。可以研究其单观测求解器，但必须换成当前 mask operator，并解决 T1→T2 先验差异。 |
| Scale-Cascaded | 2D 图像的 Laplacian 金字塔、多尺度 EDM2 先验与 DiffPIR；实验 ×2/×4 | **需适配后重训。** 原文没有充分交代 H 的具体实现、各对比序列和图像预处理，不能自作主张标成“相同 through-plane 退化”。 |
| PDM | 主定量实验为 real-valued DICOM 的 in-plane KSZP 合成；另有前列腺 through-plane 定性实验 | **需适配后重训。** 可以只用图像，不要求 raw k-space。其 through-plane 不等价于当前“保留原层、合成被删层”的监督合同。 |
| MoEDiff-SR | 3T T1→7T-like T1；训练使用成对 3T/7T 与 7T bias-field、gradient-nonlinearity correction | **不能直接。** 这是跨场强配对映射，不是单序列保留层插值；不等于推理需多对比，但训练资源显著不同。 |
| Res-SRDiff | 7T T1 maps 三轴 ×4；T2 前列腺 in-plane ×3、through-plane ×2；SimpleITK 图像域重采样 | **需适配后重训。** 不需要 raw k-space，但退化和任务均与当前合同不同。 |
| DRIFT | SLR slice profile 沿轴积分、按厚度重采样、映射回 HR 网格；单幅输入，厚度条件，逐 2D 片预测 | **可做较近的机制参照，但必须明确适配版。** 原始 SLR 退化是去模糊/厚层重建；不能用它替换当前固定保留层数据再直接比较 25.567453 dB。 |

“MRI 论文使用 Fourier/k-space”不等于“需要 raw k-space”：PDM 明确所有输入为 real-valued DICOM（p12），其 KSZP 是由图像合成的实验退化；Res-SRDiff 明确用 SimpleITK.Resample（p11）。Scale-Cascaded 提到复数图像可分别处理实部和虚部（p2），但不能由这句话断言其方法必须有真实复数测量。Likelihood-Separable 和 DRIFT 的 forward model 都可以作用在图像域。

## 3. Likelihood-Separable：真正贡献是组合独立观测，不是生成更多信息

原文 p3 定义同一 pulse sequence 的多个方向采集；p4 将独立观测的负对数似然写成加和，梯度亦可逐观测相加。可用同一个生成先验配合多个不同空间网格的 forward operator，不必显式构造一个庞大联合矩阵。p5 使用超过 70,000 个 T1 脑体积、36 个数据集预训练的非 latent 3D flow 模型，64 个 DDIM 步；定量输入由 HR 模拟 Gaussian slice profile，50 AIBL + 50 SLEEP，4×/8×/16×。

对本项目有用的机制是“观测模型与生成先验分离”，而不是论文中 MISR 的 1–3 dB 数字。当前目标是已采集厚层之间的插值，若 forward operator 是保留层选择矩阵 M，则观测一致性只约束 Mx=y；缺失层完全处于其未观测子空间。把同一组锚点拆成四项似然不会增加信息，也不会自动约束缺失层解剖。

**排重细节：p4 已明确提出可以把 A 拆成独立行、图像区域甚至 norm-preserving wavelet subband。** 因此“锚点分别算似然再加权”或“小波分带 data consistency”不能直接认作新贡献。p8 自述未处理观测间 misalignment 和 multi-contrast；其 multi-image 是同序列多方向，不是用 T1 辅助 T2。

最低验证应是 operator 审计：当前 M 与任何新设计 A 的输入输出是否精确对应现有数据；固定观测层是否真的保持不变；是否有人用生成的正交 reformat 当第二个独立测量。后者是相关伪观测，不能套独立似然的增益解释。

## 4. Scale-Cascaded：不只是小波，但也不能替普通分频包装新意

p2 的贡献包括三个分布：粗尺度 p(x3)、条件差分尺度 p(x2|x3)、p(x1|x2,x3)。细尺度模型学 Laplacian 差分图像；采样时逐尺度修改 forward operator，按约束后的粗尺度输出初始化/条件化细尺度。p3 的公平条件是总计 200 步，而不是每层各 200 步。

原文 p3 Table 2 报 brain ×4 的 DiffPIR 为 24.25 dB、2-level 为 26.53、3-level 为 31.69；但 3-level 同时改变条件信息和采样结构，不能把差值全部解释为“多尺度算子收益”。文章仅四页，H 的插值核、充分训练细节、数据分割粒度等公开文字不完整。不能将结果幅度外推给已成熟的 PAST。

对本项目可迁移的是“先解决某种有物理意义且可测的低维子问题，再条件化其余变量”。如果只是给 residual 加 Haar/Laplacian 分支，既已被本文覆盖，也与本地 wavelet3 和 latent 分频负结果重叠。若再探索，应先限定 through-plane 轴与保留层 mask 的联合分解，证明它与普通 spatial pyramid 有不同约束；单凭“低中频承载 91.22% 误差”不足以证明能学到改进。

## 5. PDM：可以借用开始状态诊断，不能把 histogram KL 当结构保证

p9–10 的观察是 LR/HR 加噪后逐渐接近，因而从 LR 的中间噪声状态开始、跳过高噪声部分。p10–11 用 latent alignment 在加噪轨迹中插值 LR/HR，解决训练从 HR 状态出发、推理从 LR 状态出发的不一致。它不是“在现有输出后调用现成 sampler 就无损加速”：改变 latent alignment 需要相应训练。

p9 使用 256 bins 的像素强度 histogram KL 支持中间态近似；这种统计对空间置换不敏感。两张结构不同但 histogram 相同的图，KL 仍可很低。对于本项目的病灶、边界与层间对应问题，不能据此宣布某个噪声级别已经“解剖等价”。

可做更直接的数学诊断：对一个固定 HR target x 和同维初始图 b，若两者按标准高斯扩散加噪且条件协方差相同，则该配对条件高斯的 KL 为

`KL(q_t(.|x) || q_t(.|b)) = alpha_bar_t / [2(1-alpha_bar_t)] * ||x-b||^2`。

这是配对条件分布的公式，不是边缘数据分布 KL，也不保证最终重建质量。若只对缺失层扩散，范数亦只在该子空间计算。可在训练内数据比较 linear coarse 与冻结 PAST 的噪声起点差距；这能诊断“好基底是否允许更短轨迹”，不能凭公式证明新的 sampler。

**through-plane 实验细节（p15）：** 前列腺 in-plane 0.625 mm、slice spacing 3.6 mm，约 ×6。训练用 coronal acquisition 的 in-plane 图像沿 SI 方向降采样；推理输入 axial acquisition 的 through-plane reformat。另一次 coronal acquisition 只作可能不完全配准的视觉参考，原文明确没有 through-plane HR ground truth。输入还平均 6 张相邻 through-plane 图以匹配厚度。故不能说“推理必需双向扫描”，也不能把其定性展示当本项目缺失层 PSNR 证据。

PDM p12 使用两百万 iteration、batch 8、4 块 RTX8000。其加速是相对原 diffusion 模型，不能视为相对约 1M 参数 PAST 已经高效。

## 6. 两篇补充排重

**MoEDiff-SR：** p3–5 已有基于多尺度 token 的 gate、区域专家、不同专家的任务损失、频率信息与专家融合。p6 给出 184 对 3T/7T T1 体积，以及“slice pairs randomly divided 8:1:1”的表述；患者隔离没有在这段得到确认，所以不借其结果宣称泛化领先。p9 也承认配对资料与跨扫描对齐限制。“边界区域调用扩散专家、平坦区域用快专家”至少在机制层面已有先例。

**Res-SRDiff：** p5–9 用 `e0=xLR−xHR` 改变 forward transition，把目标由纯噪声迁移到 LR 附近；15 步训练、4 步采样。p11 是图像域重采样，不是当前的 pure slice selection。其核心又承接 ResShift：[NeurIPS 2023 原作](https://arxiv.org/abs/2307.12348)、[后续 TPAMI 版本](https://arxiv.org/abs/2403.07319)。因此“残差扩散天然比全图扩散新”或“从 coarse 开始只走四步”都不成立。

## 7. DRIFT 是本轮最需要新增的近邻工作

### 7.1 已覆盖的机制

- PDF p6 / 补充 p19：用 SLR-derived slice profile 沿随机轴卷积、按厚度重采样、映射回 HR grid；不是简单删掉已有层。
- p6–7：输入/目标 inverse thickness 经过 MLP，用 AdaGN 调节网络。
- p7–8：第一阶段 APN 用 Charbonnier + SSIM 学稳定 coarse；冻结 APN 后，第二阶段沿 `s(t)=(1−t)z+t*y` 学 `u=y−z`，本身就是确定性基底之后的 residual rectified flow。输出层零初始化，训练从 identity refinement 开始。
- p8：CETA 对同一 anatomy、相邻厚度 `(T,T−1mm)` 的 endpoint proxy `z+v(t)` 作 L2 一致性；不能再把跨厚度一致性本身当新机制。
- p9：`PAD=1−T_hr/T_i`，`N=clamp(round(15*PAD),0,15)`；计算量来自采集厚度元数据。
- p5：明确是 2D slice-wise，没有显式 3D 卷积或跨片通信；连续性解释来自确定性初始化与共享算子。

本地当前 ×4 保留层任务若所有区间退化比固定，PAD 为常数；物理 gap 与真实 slice thickness 也必须区分，不能把观测间距离自动当连续 slice-profile 宽度。DRIFT 没有要求多对比作为同一输入；HCP/MIND T1、T2 是数据序列，不是据此就能判定多对比条件模型。

### 7.2 结果应怎样读

DRIFT p9–10 用 HCP 890/223、MIND 411/102、IDEAS 110/25 subject-wise 划分；p10 使用 8×A6000 两阶段训练。补充 p22 的 DRIFT-Large 总计 **266.9M** 参数，Small **80.9M**，与 PAST 约 0.992M 不是相同预算。p22 也显示 Small 在 HCP 的 32.65 dB 低于 Large 35.93 dB，不能只引用“更小仍competitive”而忽略容量效应。

真实 fastMRI T2 是 20 个 clinically acquired 5 mm volume，缺乏 isotropic GT；p12–13 / 补充 p32 用 sharpness、NIQE、BRISQUE，不能推断当前缺失层 PSNR 或解剖准确率。自然图像 no-reference 指标与锐度不自动代表临床忠实度。

### 7.3 DRIFT 是否已经做了“预测细化收益”

**没有在本轮读到的全文中找到该机制。** 补充 S10（p28–29）固定 N=8，考察厚度 PAD 与最终 HF-PSNR 的相关；S11（p29–30）额外一次 Stage2 forward 得到 AdaDiffSR-style image difficulty score，考察它与 fixed-thickness 组内 HF-PSNR 的相关，报告 `|r|≤0.04`。Table S3 给 PAD/image-only/hybrid 汇总 PSNR 30.14/28.42/28.38。

这里的标签是**最终重建难度/精度**，不是同一患者、同一区域上 `loss(base)−loss(refined)` 的动作收益；未见 cross-fit 风险差校准、负收益回退、选择性修改损害上界。全文关键字和 S11 阅读只支持这个窄区分，不支持“所有现有文献都没做”。项目页图注一处写“harder regions”，但正文 PAD 仅依赖厚度，不能据项目页宽泛表述将其读成逐像素收益预测。

## 8. 再排除“误差头 + conformal mask”这一包装

以下两篇由 arXiv API 核实题目、版本与摘要，随后获取 HTML 全文并定向读方法和评价段落。没有下载/逐页核查 PDF，故此处引用 HTML 节号，不能伪称已有 PDF 页码验证。

**Image Super-Resolution with Guarantees via Conformalized Generative Models**，[arXiv:2502.09664v3](https://arxiv.org/abs/2502.09664v3)，[HTML 全文](https://arxiv.org/html/2502.09664v3)。arXiv comment 写 “To appear at NeurIPS 2025”；本轮未独立核验正式 proceedings。§2 将任意 SR black-box 与 indecision score 配合，生成可校准的 confidence mask；允许任何满足有界条件的 local similarity metric，不限像素 L1。§3 提供 fidelity error 与 PSNR 等保证；§4 所述 PSNR 是**被信任区域上的 PSNR**。因此不能把“生成后可靠性 mask”“方差驱动 conformal 校准”“控制局部重建误差”再提为新意。

**Trustworthy Endoscopic Super-Resolution**，[arXiv:2604.18001v1](https://arxiv.org/abs/2604.18001v1)，[HTML 全文](https://arxiv.org/html/2604.18001v1)，[代码](https://github.com/jusiro/Endoscopic-CFM)。本轮仅确认预印本。§2.1 的 Reconstruction Error Network 直接利用冻结 SR 模型的中间特征预测 pixel-wise reconstruction error；§2.2 把真实误差按指定 failure level 分成二分类，再通过 conformal risk control 选择 score 阈值以控制 failure FNR。§3 评价 mask 面积、FNR 和 non-rejected regions 的 PSNR；文末明确 marginal coverage、校准样本量、exchangeability 等限制。

**准确区分：** 这两篇主要让用户知道哪些生成区域可以信任，不能把剔除坏区域后计算的 PSNR 当作完整重建图像性能改善。拟议方向若成立，输出仍要是完整 volume，在每个缺失位置选择保留基底或接受细化，并评价完整缺失层风险；标签需是相对基底的增量收益/损害，而不是生成图像的绝对误差。通用 conformal 框架可支持很广的风险定义，因此这种区分也不自动建立新颖性，更不意味着“加 MSE/MAE 双约束”本身就是理论贡献。

## 9. 唯一保留的窄假设：预测动作收益，而非难度

假设：对同一冻结基底 b 和一个事先固定的 refinement 候选 r，四锚点中可观察到的证据足以判断哪些区域的细化能降低误差、哪些区域会损害；同样大的基底误差不必有同样的可纠正性。

令 `e=y−b`、`d=r−b`，平方误差的实际收益为

`g = ||y−b||^2 − ||y−r||^2 = 2<e,d> − ||d||^2`。

所以“误差大/不确定性大”只看到了 e 的大小，收益还取决于 e 与 d 的方向以及修改幅度。这也解释为什么多采样方差或委员会分歧不能直接当可获收益。对于软修改 `b+a*d`，oracle 最优 `a*=clip(<e,d>/||d||^2,0,1)`（d=0 时取 0）。这些都只能用 target 作**诊断标签/上界**，不能进入部署输入。

这是一条任务与评价假设，不是“加一个 learned gain head 就有新颖性”。结合本地 MAE 约束失败记录，研究对象还应包含 `(g_MSE,g_MAE)` 这一对相对基底风险差，而不是只预测 MSE 高收益。仍须查 selective prediction、learning to defer、conditional computation、restoration risk estimation 等一般领域与 2026 新文献；DRIFT S11 只排除了一个最邻近的混淆点，前述两篇 conformal 论文则已经覆盖误差预测与可靠性 mask。

### 最小验证顺序

1. **先固定候选动作，测 oracle utility，不训练 gate。** 使用已经存在且可复算的候选输出；必须是同一退化、锚点和归一化。比较全局不修改、全局固定幅度、患者级 oracle、预先规定 patch 大小的 oracle，均最终重算完整缺失层逐患者等权指标。oracle 若连 +0.10 dB 左右的项目实用门槛都明显够不到，停止此候选；不用复杂 gate 挽救微弱 action。
2. **同时测损害与稳定性。** 看正收益空间占比、最坏患者、MAE、SSIM、tail10、HD95 强度 proxy，保留“proxy 不是解剖质量”的边界。patch 选择后需先融合成整图再评分，不能把局部正项直接相加冒充最终可部署增益。只在旧训练集上做的 oracle 是乐观筛选，不能作为最终 headroom 确证。
3. **只有 oracle 通过，才验证收益可预测。** gate 的标签用实际配对风险差，输入只允许四真实锚点、位置、b/r 可观察特征；对照包括常数接受率、随机但匹配接受率、梯度/纹理复杂度、预测基底误差、分歧/方差。真正要证实的是收益排序与负收益识别，而不是与误差的相关。
4. **校准必须使用未参与生成该残差的患者。** 理想为 patient-level cross-fitting；冻结模型在其曾训练患者上的残差可作低成本否定性筛选，却不支持无偏校准。不得悄悄把 23 名开发 validation 又当独立校准/最终验证。需要预先写清将来的数据分配与可用样本，不能借多轮 threshold 搜索消耗 val 后宣称风险保证。
5. **冻结决策后才进入固定预算模型比较。** 与 always-refine、never-refine 和上述难度 gate 在同一 refiner、同一平均 FLOPs/NFE 下比较。物理 gap OOD 回退只能是事先定义的部署行为；没经过 shift 假设检查时，不能宣传跨域概率保证。

在满足这些条件之前，本轮最坚实成果是：核清任务差异、补齐 DRIFT 排重、把下一步实验目标从“找一个看似新模块”收窄为“证明某个动作有足够且可预测的净收益”。

## 10. 可复查的在线核验记录

在线请求用 requests Session(trust_env=False)，成功返回的来源已归档在 `source_cache/`：`drift_source.html`、`drift_meta_source.html`、`drift_project_source.html`、`drift_ecva_source.html`、`ls_abs_source.html`、`cvpr_source.html`、`ls_crossref_source.html`、`scale_crossref_source.html`、`res_crossref_source.html`。Crossref 的 `scale_crossref_source.html` / `res_crossref_source.html` 实际内容为 JSON，后缀只是保存方式；引文以官方 DOI 和 arXiv 页为准。

DRIFT 新下载全文：[2026_DRIFT.pdf](2026_DRIFT.pdf)；按页提取：`extracted/2026_DRIFT.txt`。本报告不是对其公开代码的复现或可信度认证。

额外两篇 conformal 核验保存为 `conformal_sr_meta.xml`、`2502.09664v3_conformal.html.txt`、`2604.18001v1_conformal.html.txt`。这些是本轮取到的摘要元数据/HTML 方法文本，引用范围已在正文限定。
