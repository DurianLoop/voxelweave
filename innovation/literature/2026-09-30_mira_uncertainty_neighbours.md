# MIRA 近邻文献核读：误差区间与内在歧义（2026-09-30）

阅读的是本地原文 PDF，不是独立复现。检索快照为 [mira_arxiv_2026-09-30.json](search_snapshots/mira_arxiv_2026-09-30.json)：3 组有上限的 arXiv 查询共 217 个不同条目，不构成系统综述。两个原文均按 arXiv 版本引用，不推断正式录用。与 [Hu 2021 核读](2026-09-30_hu_mira_overlap.md)及本项目原 Related Work 一并判断新意。

## Giannakopoulos 等：Pixelwise Uncertainty Quantification of Accelerated MRI Reconstruction

- 来源：https://arxiv.org/abs/2601.13236v3 ，2026-06-25 版本；[原文 PDF](Pixelwise_Uncertainty_Accelerated_MRI_2026.pdf)，SHA-256 `754e157ed06811e5ef10b1f2183af8e8a333dd6befb3bd699abee3d1afd1075d`。
- 核读：Abstract、Introduction、Methods II.A–E、Tables I–II、Figures 2–7、Results III、Discussion IV、Conclusion V；PDF p.3 的架构/表格已渲染目视核查。
- **任务与输入**：fastMRI brain/knee 多线圈 k-space 的 Cartesian 欠采样，E2E VarNet 先重建；随后两个 U-Net 根据重建图预测真值强度的上下分位数，单独在有 fully sampled 对照的资料上训练，并在留出的校准集用 Hoeffding 风险上界选择共同放大系数。测试时不需要 fully sampled 真值。Brain train 4,469 volumes；validation 1,378 平分为 validation/calibration 各 689；test 558。Knee train 973、calibration 50、test 99。Brain 2/4/6/8/10×、knee 4/6×；不同倍率训练不同模型及固定 mask。
- **直接证据**：Table II 的 brain 4× Pearson `0.91±0.10`，ResM `0.69±0.22`；knee 4× `0.80±0.16` 对 ResM `0.24±0.27`。但是用于相关分析的区间宽度和真实绝对误差图均先作 Gaussian `sigma=2` 模糊；Discussion 明言 brain 4× **未模糊** Pearson 只有 `0.39`（region Pearson `0.84`）。因此不能把表中 `0.91` 当作原始逐像素误差预测精度。论文的 90% 目标区间和相关系数也不是 MSValid 上的覆盖保证。
- **失败边界**：Discussion p.11 承认重建网络若过拟合或“自信且错误”，区间可能不可靠；校准集不代表测试分布时名义覆盖可偏离。方法本身没有自动选择/控制加速倍率的规则。文中的 adaptive sampling 是展望。它做了合成亮病灶 OOD、mask 扰动、换 FI VarNet 重训模块等分析，但没有本项目的患者 T2 层间相位锚点身份干预。
- **对 MIRA 的约束**：不能笼统声称首次提出 MRI 误差图、无真值可靠性评分、统计校准区间或病灶风险提示。MIRA 的可区分对象是固定模型对在同一目标上改变真实锚点集合时，误差可观测比例及响应的变化；这只是审计机制，不等价于该文的部署区间或临床判定。若今后要主张可操作评分，必须与这种监督误差/区间预测在相同数据合同下比较，并报告未模糊图和外部分布覆盖。

## Guo 等：Separating Intrinsic Ambiguity from Estimation Uncertainty in Deep Generative Models for Linear Inverse Problems

- 来源：https://arxiv.org/abs/2605.15050v1 ，2026-05-14；[原文 PDF](Intrinsic_Ambiguity_Inverse_Problems_2026.pdf)，SHA-256 `b2e9233a6716d25208765ec03b5378051f9ae0cad89826952f10f252e3b11df3`。
- 核读：Abstract、Sections 1–6、E/F 附录相关解释；PDF p.7 Figure 3（50 切片 MRI variance 示意）已渲染目视核查。注意主结果并非一个新的 MRI 层间超分模型。
- **方法**：对已知线性算子 `y=Ax+noise`，以 SVD 将 `x` 分为可辨识的 `alpha` 和 null-space `beta`，由条件独立得到 `p(alpha,beta|y)=p(alpha|y)p(beta|alpha)`。Eq. 5 将 `Var(beta|y)` 分为内在歧义的后验平均与估计 `alpha` 所传播的方差。级联模型在有成对真值时用 oracle `alpha*` 条件化 null 模型，针对 `beta` 的范数与峰值/总量比作 simulation-based calibration；SBC 是必要而不充分的校准检查。
- **实验量级和归属**：解析 Gaussian 例检验公式；MRI 是 fastMRI **single-coil knee**、25% Fourier 保留、50 张 held-out 切片的噪声扫掠/空间方差示意（Fig. 3），不是外部队列校准验证。更完整的校准对照在模拟 EEG 源定位：450 个 held-out 样例、共同 DDPM range 搭配 DDPM/VAE null，重建 Pearson `0.698` 与 `0.693`，却有不同且均非均匀的 SBC 排名直方图。不能把 EEG 的数值当作 MRI 结果。
- **局限**：需要成对 `(x,y)` 数据进行直接的内在歧义校准；已知线性前向算子的 range/null 分解最清楚；MRI 图展示的是**模型预测的后验方差分量**，不是患者真值细节的恢复保证。原文说明非线性或未知算子需要新的可辨识定义，临床使用仍需特定任务验证。
- **对 MIRA 的约束**：不能把“测量不可辨识分量”“重建相近而不确定性失校准”或 range/null 分解包装成 MIRA 首创。当前 MRI 项目是 through-plane x4 缺失层、观察到真实锚点的图像插值；没有原文所用的 Fourier 已知算子与后验采样，所以也不能把其形式化分解直接嫁接为 MIRA 的定理。仍值得测试的是：锚点身份对**已定义的成对误差可观测性**和输入响应有多少影响，且该影响在相位、尺度、几何控制后能否保持。

## 对下一步 claim 的决定

现有事前 MSValid 单对照可写为跨来源的、有边界的锚点条件误差可观测现象，不能扩写为全新 MRI 不确定性框架、校准评分、纯锚点身份因果效应或新重建器。优先完成 [共同归一化结果后控制](../MSVALID_COMMON_NORM_PLAN_2026-09-30.md)，再设计外部响应影响探针；投稿前还需解决数据授权/伦理、稿件同步和近邻文献引用。任何现有 confidence/coverage 数值不得移植到不同任务合同。
