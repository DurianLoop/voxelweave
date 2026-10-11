# MRI 项目续读：创新候选与最小证伪方案（2026-09-30）

## 本轮判断

**最值得优先验证的是“修正是否有用、是否会造成损害”，而不是再给 PAST 增加一种通用特征模块。** 更准确的研究问题是：仅用真实稀疏观测，能否预测一个明确修正方向相对原估计的可获得收益，并据此改善完整缺失层的重建？

但当前还没有经过实验和充分排重确认的核心新方法。本轮反而排除了多种容易重复的方向：确定性基底接少步流、跨平面自监督、共享噪声联合生成、厚度/间距解耦、slice-profile 建模、误差头加 conformal mask，均已有先例。下面的候选必须通过可证伪的小实验，不能直接写成“首次提出”或预期 SOTA。

本轮完成论文原文/代码核读、近期公开检索、项目状态复核，以及一项仅使用已有 validation CSV 的诊断。没有启动训练、读取新的 test 图像或更改旧模型结论。

## 1. 接上当前项目，而不是回到早期设计

| 项目事实 | 本轮复核结论 | 对新方向的约束 |
|---|---|---|
| 修复数据后的 PAST control / wavelet3 | fastMRI validation 为 25.567453 / 25.585002 dB；小波 +0.017549，23/23 患者改善，质量守卫通过，但未达既有 +0.10 门槛 | 小波可作为已有候选；其效应不能被包装为核心性能突破 |
| 方向增强 | 25.656399 dB，比旧数据 control +0.094388；HD95 强度代理显著退化 | PSNR 与结构代价确实冲突；该分支的停止结论保留 |
| 修复版 I3Net | 当前 `completion.json` 已确认 full 完成：300 epochs、best 25.1442674691、test_used=false | 9/24 总结里的“尚未完成”已过时；PAST 预训练、loss、预算不同，不能据此宣称受控架构优越 |
| IXI wavelet3 | 本轮最终复核快照：history 到 epoch73，validation best 32.1764990171；无 full completion 标记或 test115 结果 | 训练期间记录继续更新；9/28 README 的“未启动 FULL”已过时；不能把此 validation 分数减旧 I3Net test 31.3058 |
| 多次局部结构尝试 | geometry、局部对应、长上下文、全局读取、latent 分频等收益很小，部分伴随 MAE 退化 | 先证明新增路径有可利用信息；负结果只约束已试实现/预算，不是信息上限 |

证据入口：

- [9/24 研究总结](../../design/PASTNET_RESEARCH_SUMMARY_2026-09-24.md)
- [I3Net 当前完成记录](../../design/i3net_repaired_reference/runs/full_i3net_repaired_seed3407_vram20/completion.json)
- [IXI 当前训练历史](../../design/pastnet_ixi_wavelet/runs/full_wavelet3_ixi_seed3407/history.csv)
- [方向增强复核](../../design/pastnet_orientation/results/full_review.md)

重新汇总已有 train/validation 几何审计 CSV 得到：

| 数据 | 可用几何 series 数 | x4 真实观测中心间隔中位数 | 中心间隔范围 | 唯一稀疏层数中位数 |
|---|---:|---:|---:|---:|
| fastMRI | 134 | 20.00 mm | 8.00–26.00 mm | 4 |
| IXI | 462 | 5.00 mm | 4.80–5.12 mm | 33 |
| NingXia fold00 train/val | 20 | 17.60 mm | 17.60–24.00 mm | 5 |

来源：[既有几何 CSV](../../design/pastnet_v2/results/domain_audit/per_series.csv)。这是历史 metadata 汇总，未重新访问图像。**同为 x4 不代表同一物理难度；但几何差异不等于已证明造成全部跨域差距。**

现行任务是从原生体积抽层，输入和监督保留原生层响应；抽取每四层只改变中心间隔，不会把输入层厚自动变成四倍。真实厚层去模糊到薄层是另一种监督目标。

## 2. 这轮论文如何改变创新判断

| 文献 | 已有机制或关键发现 | 本项目不能再直接主张的“新意” |
|---|---|---|
| [HiFi-Diff，MLMI 2023](https://doi.org/10.1007/978-3-031-45673-2_3) | 相邻层和连续相对位置条件扩散，混合倍率训练 | 任意 phase、两锚点条件扩散本身 |
| [I3Net，TMI 2024](https://github.com/eeeric-code/I3Net) | 频域、面内/层间交互、cross-view，直接抽层实验 | 再加 FFT/DCT 或跨视图模块本身 |
| [SMORE 后续，SASHIMI 2023](https://doi.org/10.1007/978-3-031-44689-4_12)、[SPTSR 2023](https://doi.org/10.1109/ACCESS.2023.3307577) | 独立层厚与间距、slice profile、gap、训练/推理响应匹配 | “首次区分层厚与 spacing”“首次物理 profile” |
| [Cycle-Consistent，IPMI 2025](https://doi.org/10.1007/978-3-031-96628-6_17) | MRI 正向算子 + DDNM 数据一致性 | 硬投影、零空间生成本身；数据一致不保证缺失解剖正确 |
| [Zero-X21，PRL 2025](https://doi.org/10.1016/j.patrec.2025.06.001) | 作者公开代码为双对比度 LR/HR 监督、条件 INR | 不可按名称解释成 zero-shot 单 T2；辅助对比度不能白加给对照 |
| [Likelihood-Separable，2026 预印本](https://arxiv.org/abs/2601.14030) | 多个独立正交采集的似然组合；还明确讨论子带/行拆分 | 拆锚点/子带似然本身；从同一体积重排出的视图不是新测量 |
| [Scale-Cascaded，ISBI 2026](https://doi.org/10.1109/ISBI61048.2026.11515890) | Laplacian 条件多尺度扩散 | 普通分频、多尺度 residual diffusion |
| [CRIS v2，2026 预印本](https://arxiv.org/abs/2606.15967v2) | 面内自监督、正交条带补全、validity mask、变 gap；非整数比率用 round 后 resample | 跨平面自监督或 uncertainty-weighted fusion 的宽泛提案 |
| [DRIFT，2026 预印本](https://arxiv.org/abs/2607.16649v1) | 确定性 APN 后接 residual rectified flow；厚度条件、端点一致性、按厚度分配步数 | “PAST + 少步 RF”“困难层多算几步” |
| [SliceBridge，2026-09-01 预印本](https://arxiv.org/abs/2609.01827v1) | 区间相关噪声、共享 flow time、同步多层生成；左右各16真实上下文 | 联合生成多缺失层本身；不能迁移其32层输入优势到四锚点任务 |
| [Conformalized GSR，2025](https://arxiv.org/abs/2502.09664)、[Trustworthy Endoscopic SR，2026](https://arxiv.org/abs/2604.18001) | 置信 mask、误差预测头、风险控制 | “预测 error + conformal”本身；仅保留可信区域后的 PSNR 不是完整图像提升 |

书目纠正仅记录在本轮文档，未重命名旧 PDF：本地 HiFi-Diff 的 `CVPR_2023` 前缀错误；Cycle-Consistent 应按 IPMI 2025 引用，PubMed 的 2026 记录不等于 IPMI 2026；Likelihood-Separable 的 CVPR 身份本轮未核实。DRIFT 作者项目页标 ECCV 2026，本轮仅独立核实预印本全文。未核实正式身份不等于证明未录用。

阅读深度并不相同：Zero-X21 是摘要与固定版本作者代码；Cycle-Consistent 是摘要/出版信息与作者后续项目说明；其余原文阅读范围和页码均在分报告列明。检索截至 2026-09-30，非全领域穷尽检索。

## 3. 优先候选：预测修正方向是否有效

### 问题比“再预测误差”更具体

高误差可能来自可修正的系统偏差，也可能来自当前观测下难以识别的细节。给高误差区域更多算力，或让高不确定区域生成更多纹理，未必改善与真值的对应关系。

设固定原估计为 `b`，固定候选修正为 `r`，`δ=r−b`。只考虑一个预定 patch 上的标量混合：

`x_hat(α) = b + αδ,  0 ≤ α ≤ 1`

记 patch 内均值 `m=mean[δ·(y−b)]`、`d=mean[δ²]`，则：

`MSE(b,y) − MSE(b+αδ,y) = 2αm − α²d`。

这个恒等式说明：修正幅度大不等于修正有用；关键是修正方向是否与真实残差对齐。`d` 在推理时可算，`m` 只在训练/评价时有真值可算。候选方法可以用观测、phase、物理间隔和部署可得特征预测 `m`，再研究保守估计 `m_L` 下的 `α=clip(m_L/(d+ε),0,1)`。**二次风险收缩公式本身是常规数学，不是新定理；也没有仅凭此式就成立的跨域保证。**

可能的研究贡献须同时具备：

1. 证明本任务中“当前错误大小”与“某个修正动作的收益”有可重复的区别。
2. 给出比固定混合、按 phase/间距调权、普通误差头、委员会分歧更有效的可观测收益估计。
3. 在完整缺失层上增加重建收益，同时减少 MAE 或结构损害，并检验未见物理间距下的失效边界。

DRIFT 补充 S11 比较的是 image difficulty、厚度难度和混合调度，本轮没有看到这种相对 base 的双指标收益校准；但选择性预测、专家选择、风险收缩、conformal 都有广泛先例，不能由此声称首创。

### 先别做 gate 网络：现有输出的低成本诊断已经限制了它

本轮实际读取旧数据 control 与 orientation 的 23 名患者 validation 指标，用真值决定是否整例换成 orientation。未产生新预测，结果见 [诊断 JSON](2026-09-30_patient_selection_diagnostic.json)。

| 整例选择规则 | 采用候选人数 | 全23人等权 PSNR 变化 | HD95 强度代理变化 |
|---|---:|---:|---:|
| 始终采用 orientation | 23 | +0.09439 dB | +0.15842，变差 |
| 真值选 PSNR 改善者 | 17 | +0.10504 dB | +0.09505，仍变差 |
| 再要求该患者 MAE 不退 | 12 | +0.09472 dB | +0.07483，仍变差 |
| 再要求该患者 SSIM、HD95 代理不退 | 4 | +0.04564 dB | −0.02734，改善 |

**结论：现有两输出的简单病例级开关，不足以支持新的主模型训练。** 仅按 PSNR 的理想选择相对始终 orientation 多约 0.01066 dB，结构退化仍在。逐患者更严格的守卫又缩小收益。这里的守卫比原来群体均值要求严格，不能据此证明所有满足群体要求的方案都不可能改善；这也不是局部融合、连续混合或全部 MRI 模型的上限。

同理，小波对 repair control 已有23/23患者 PSNR 改善，因此仅做病例级 PSNR 回退不会创造新增均值收益。局部或多指标情况尚未由此排除。

这些 oracle 规则使用真值，不能部署；23名患者已反复参与开发，不能用作独立校准或确认。原 orientation 分支继续保持停止，不因该表改写旧晋级结论。

### 最小试验与停止条件

- **空间检查。** 在固定同口径输出上，预先确定 patch 大小、重叠、重组和 `α` 规则，测局部 oracle 相对最佳全局混合的增量，同时保留 MAE 与结构约束。现存 CSV 不含像素级交叉项，不能从这些均值还原局部 oracle；后续需要已有预测或固定权重推理。没有足够空间就停止，不训练选择器。
- **可预测性检查。** 若空间足够，先用小型回归/排序器检验 `m` 或相对损失的可预测性；与固定 α、phase/mm 规则、absolute-error head、RASI 分歧直接比较。误差标签只能来自训练/开发真值，部署输入不能读隐藏目标。
- **评价整个策略。** 选择器、重叠平均、clamp、阈值组成的最终策略必须整体评分；硬切 patch 会产生接缝，修改重组规则后原局部标签/校准不能原封不动沿用。所有缺失层均计分，不能删掉失败区域后报优势。
- **确认隔离。** 干净 OOF 必须覆盖 base、refiner、选择器整条学习链；历史 G086 看过的患者不能通过仅交叉拟合选择器变成独立样本。普通 conformal 的交换性不能自动覆盖 IXI→fastMRI 的物理域转移。
- **实用性。** 后续 full 是否晋级仍须遵守其适用的预登记门槛；当前没有给新候选发放晋级结论。建议先用已有 +0.10 dB 量级审视 oracle 空间，而非为一个 +0.01 dB 选择收益启动大型网络。

## 4. 两个备选方向及优先级

### 备选 A：识别错误的观测模型，而不只满足它

SMORE、ESPRESO、SPTSR、Cycle-Consistent 已能建模或估计 profile。更窄的问题是：多个 profile 都能拟合已观察切片时，能否用独立留出的真实观测识别哪些假设会导致缺失层损害？

最小实验是在可信参考的训练/开发体积上合成已知核族，并故意提供错误核；比较固定核、估计核和候选核集合。将一部分真实观测严格从拟合中排除，测留出观测误差能否预测真正目标层误差。若二者无关系，就不能把观测一致性当缺失层可靠性。

主要困难是本项目 fastMRI x4 只有约4张唯一观测；再留出会显著改变条件间距。当前抽层合同的算子接近选择矩阵 `P`，不能为了研究 PSF 暗中换成厚层模糊任务。故此方向科学价值可能高，但数据条件和成本比收益诊断更苛刻；不是当前首个 full。

### 备选 B：指定输出层响应，而不只指定输出网格

候选问题：同一组输入，既能请求保持原生层厚的插层，也能请求另一明确输出响应，并知道模型对后者的适用边界。本轮未在核读入口里发现完整的独立 `k_in/z_in/k_out/z_out` 查询实现，但不能据此确认领域空白。

核心强基线是“已有高分辨率重建再按所需核卷积/积分”。若直接查询仅等价于这一步，不构成有力方法创新。现有 native 厚层标签也不能证明真实薄层重建正确。暂列备选，不以多一个厚度 token 立项。

## 5. 近期论文可以直接改善哪些评价

- SliceBridge 提示应区分生成层内部与真实锚点边界的 z-gradient **误差**，不是仅奖励平滑；其下游形态指标并未显著区分两个 flow 模型，不能把连贯性收益直接叫临床收益。
- [2026-09-29 超低场审计预印本](https://arxiv.org/abs/2609.36837v1) 提供“本人/他人参考”的频带负对照思路。但直接模型真实性演示只有4名个体，并有配准、checkpoint选择和可计算性限制；其3–4 mm尺度不能移植为本项目上限。
- 本项目 Dice/HD95 是强度代理。若论文要讲解剖恢复，需要可靠分割或明确的结构任务；代理改善本身不能升级为临床诊断收益。

## 6. 后续工作顺序

1. 现有 IXI wavelet 实验按原合同完成并审计，不把本轮阅读带来的想法插入当前训练。
2. 新研究先解决“是否存在足够的局部可修正空间”；本轮病例级选择诊断已显示不宜直接开 gate full。
3. 有空间才检验可预测性；有可预测性才比较收益估计机制；机制成立后再做匹配预算、多 seed、物理间距转移验证。
4. 若局部 oracle 或可预测性失败，保留负结果，转向观测模型失配问题；不在同一批 validation 上无限更换专家救实验。

本轮最实际的收获是缩小了新意范围，并用现有结果否定了一个过于简单的实现。**可以继续推进的研究假设已经具体到标签、推理可用输入、强对照与失败条件；尚没有理由承诺某个新网络一定超过 I3Net。**

## 详细阅读记录与可复核产物

- [插值、自监督、INR 与近期作者项目](2026-09-30_interpolation_prior_art.md)
- [扩散、rectified flow 与 conformal 排重](2026-09-30_diffusion_prior_art.md)
- [slice profile 与层厚/间距先例](2026-09-30_slice_profile_prior_art.md)
- [SliceBridge 与个体真实性核读](2026-09-30_recent_interval_and_faithfulness.md)
- [本轮病例级诊断数据及来源哈希](2026-09-30_patient_selection_diagnostic.json)
- [诊断脚本](../experiments/patient_selection_diagnostic.py)，只读取历史 validation CSV；命令：`python innovation/experiments/patient_selection_diagnostic.py`
- [本轮来源与下载文件登记](2026-09-30_sources.json)

检索以 arXiv 公开 API 的 MRI + through-plane / slice-profile / slice-interpolation 查询，以及 reconstruction/SR + conformal/risk-control 查询为入口，再回到论文、出版机构或作者代码。原始查询响应与网页已归档在 [source_cache](source_cache/) 和 [search_snapshots](search_snapshots/)；部分受限出版社全文未取得的条目明确标注，不将二手摘要当全文。后续五篇补读见[新增论文笔记](2026-09-30_focused_additional_papers.md)。
