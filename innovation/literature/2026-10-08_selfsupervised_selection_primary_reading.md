# 留出观测、自监督重建与动作收益的边界

本轮取得两篇作者原文77物理页，实际文字阅读41页、视觉核看6页。范围见 [reading provenance](selfsupervised_selection_reading_provenance_2026-10-08.json)；未读参考/补充页明确列出。取得/渲染记录保持未读标记，不回改。没有作者训练复现或新MRI自监督实验。

## Noise2Self: Blind Denoising by Self-Supervision

Joshua Batson、Loic Royer，ICML2019。实际作者[arXiv1901.11365](https://arxiv.org/abs/1901.11365) PDF页首v2/8Jun2019，[缓存](source_cache/selfsupervised_selection_primary_2026-10-08/noise2self.pdf)，16物理页；实际正文文字1–8，视觉2、6，9–16未逐页读。

| 物理页 | 原文证据 | 本项目含义 |
|---|---|---|
| 2，定义、Prop1/式2 | f(x)在J的输出不依赖xJ；条件无偏E[x|y]=y，J与补集噪声给定y独立。此时自监督平方风险=clean平方风险+常量噪声方差 | 不是任意masked流程、MRI重建或分割Dice的普遍等价保证 |
| 2，Prop2 | 最优J-invariant预测是E[yJ|xJc] | 移除观测会改变预测器信息范围，不等同充分观测下最优动作 |
| 4，Fig2/式3 | 普通median的自误差不可直接选最优；donut或先替换J再运行g才J-invariant，两者是真正不同函数 | mask必须在会混合heldout值的插值/统计等操作之前定义；不能只在最终tensor上抹值就假定理论成立 |
| 6，推导 | 交叉项因独立与无偏消失；GP相关尺度越长，J-invariant和全信息Bayes预测的差距缩小 | 必须核项目真实噪声与信号/层距条件，不能把相关性直接当修正可获益性 |
| 7，§4.2/5 | 与原观测适当线性组合可提高表现；训练后的普通g直接处理原输入比J-invariant f约好.5dB，图6用g | 训练用heldout损失和部署full-input预测器不同，部署效果仍需实测 |
| 8，Table2/讨论 | natural images、文字、显微镜；ImageNet DnCNN N2S18.7dB、N2T22.0dB，跨域并非完全等效；partition大小有bias-variance取舍 | 不称所有场景达到监督性能，更不是MRI病灶效益证明 |

这是平方误差去噪的条件性结论。未验证本项目已重建/插值MRI的无偏与条件独立，不发行其正式风险证书；也不能拿它推出具体修正的患者分割增益。后续经验效益论文仍可做合法observed特征的预测比较，不额外要求本定理条件。

## Self-Supervised Learning of Physics-Guided Reconstruction Neural Networks without Fully-Sampled Reference Data（SSDU）

Burhaneddin Yaman、Seyed Amir Hossein Hosseini、Steen Moeller、Jutta Ellermann、Kâmil Uğurbil、Mehmet Akçakaya；使用作者[arXiv1912.07669](https://arxiv.org/abs/1912.07669) [PDF缓存](source_cache/selfsupervised_selection_primary_2026-10-08/ssdu.pdf)，61物理页。文字实际读1、2、4–28、36、40、45、46、54、55，共33页；视觉36、40、45、54。正文/单独图页/补充说明分别定位，非61页全读。

| 物理页 | 原文证据 | 本项目含义 |
|---|---|---|
| 6–10，式1/9/10 | 线圈敏感性与partial Fourier编码EΩ；Ω=Θ∪Λ，Θ用于unrolled data consistency，Λ用于k-space loss；测试使用全部Ω | split已采k-space有先例，不等同每4层image-domain输入/未知slice profile，也非任务增益标签 |
| 11–13 | 同592129参数ResNet、10unrolled/10CG，固定归一化L1+L2 loss；Λ分布与ρ做训练内5fold选择；24×24 ACS做ESPIRiT | 架构/实际encoding是复现的一部分，不能称我们的PCHIP或普通3DU-Net为SSDU |
| 14 | 五种knee sequences，train300slices/10或15subjects，test每sequence10不同subjects，R4；TGV仅示例，未覆盖所有test | 不将TGV示例改写成完整队列的强同预算基线 |
| 15–16 | brain19健康受试者，prospectiveR2再retrospectiveR4/6/8；train10/test9；无fully sampled brain reference，不能supervised比较 | 不叫R4/6/8全为真实独立prospective采集；reader评分不是病灶保真或完整thin3D-GT |
| 17–18，Fig5 | Gaussian loss mask优于uniform、ρ=.4最优于所测集合；ΘΛ重叠越多产生更多残留/噪声 | 目标位置不能在data-consistency路径中被直接使用，否则observed self-error不能表示独立预测表现 |
| 19–21 | knee NMSE/SSIM及reader；brain高R变差，R4整体最好 | 非所有场景/所有加速率均等效；非显著差异不等于等效性证明 |
| 25–27 | 丢40%采点不等同实际8倍采集，k-space点mask无须完整readout line；R8自监督受额外数据稀缺挑战；保留4×4高能中心是heuristic | 整层holdout会改变层距，不能照搬随机k-space点或ρ=.4；原known-profile留出失败继续保留 |
| 54–55，SuppFigS8 | image-domain supervised在sagittalT2/axialT2某reader指标更差；k-space supervised较image-domain更优；对照loss不同 | 需保留混合退化和端点差异，不能一概说SR或自监督帮助临床任务 |

原文展示MRI自监督训练的实践价值，没有提出heldout intensity loss与我们paired患者病灶Dice增益之间的等价定理。核读图36分离input/DC与loss；图40含重叠反例；图45/54看到了评分尺度和对照loss/域的差异，未从示例图反算完整队列统计。

## 与当前工作的连接

旧 [known-profile训练内pilot](../KNOWN_PROFILE_HOLDOUT_PILOT_RESULT_2026-10-01.md) 已有留出观测选核失败，不重复计新。新 [19series投影rank和同统计见证](../OBSERVED_PROJECTION_INFORMATION_RESULT_2026-10-08.md) 说明：像素中心映射与非线性预处理会改变有效输入，不能仅凭最后有mask认定条件独立、J-invariance或严格信息等价。

后续可把合法heldout一致性作为一个普通预测特征，需在开发内配对真实动作收益、强任务基线和完整成本比较中验证额外价值；不作无GT任务收益证书。创新和控制准备见 [后续方案](../PROJECTION_AND_SELFSUPERVISED_ACTION_PREPARATION_2026-10-08.md)。
