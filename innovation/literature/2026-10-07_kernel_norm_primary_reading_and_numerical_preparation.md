# KernelNorm 原文补读与局部算子准备

Nasirigerdeh、Torkzadehmahani、Rueckert、Kaissis，*Kernel Normalized Convolutional Networks*，TMLR 02/2024；本地固定原稿为 [arXiv2205.10089v4](https://arxiv.org/pdf/2205.10089v4)，2024-03-04，21物理页。[本地原文](source_cache/kernel_normalization_primary_2026-10-07/kernel_norm.pdf)，SHA256 `8aeadfc4c3b3708e641eebb62ca2ed32e5e0958e8b7aaf16984b42f6dc4a7e9d`。

本阶段前半段已定向阅读物理页2–13、19–21；接续中补读页1、14–18，并重核页5、6、13。累计21页可提取文字已读，页17/18的巨量水平空白经压缩后重新完整输出；提取文字不能恢复架构图连接关系。物理页4、6、12、21已渲染并实际 view_image 核读，其他图像/曲线像素没有完整视觉核读。获取与旧三篇报告保持不变；本篇单独追加登记，不能回写旧报告的阅读状态或重复计算那三篇。

## 与本项目直接相关的算子边界

页4 Eq1–3：每个统计单元包含卷积窗口内的**全部输入通道**；zero padding 被纳入单元。训练先对单元施加 dropout，再从 dropout 后的单元计算均值和总体方差，用它们归一化原始单元。这与普通 feature dropout 之后卷积不同。仅实现 dropout=0 并不是作者完整训练配方。

页5 Eq4、页6 Eq5/Algorithm1：归一化窗口与卷积核匹配；bias 在归一化和点积之后加。计算高效形式为 `(conv(U,W) − mean(U′)·sum(W))/sqrt(var(U′)+eps) + bias`。作者实现统计使用 unfold 与 var_mean；我们的初版用平均池化求二阶矩，属于不同的数值实现，不能将本地失败归咎于论文作者实现。

页5明确统计窗口可以重叠，KernelNorm 单独的输出尺寸不必等于输入尺寸；KNConv 则将每个归一化单元汇聚为一个卷积输出。不能把 KernelNorm 等同于逐体素单次局部标准化。页6–7/17–18为专门 KNResNet 架构，替换1×1层、调整通道和过渡块；作者分类 KNConv/KernelNorm dropout=.05/.25，分割为.1/.5。我们只准备3D、dropout=0、无groups/dilation的单层算子，未复现这些网络。

## 实验与资源证据的适用范围

作者评估是 CIFAR-100、ImageNet、Cityscapes 与差分隐私图像分类；不能搬成 MRI 病灶收益。页12把 normalization 与 dropout 分开做 CIFAR-100 的消融（71.48%、78.32%、80.18%），说明仅使用确定性算子也不能声称复现作者完整收益。

页21 Table6的速度用8张A40、每卡batch32；Table7的显存用单A6000、batch32：KNResNet-50为13.6GB，BN CUDA为5.7GB、PyTorch primitives为8.2GB。Table8又显示 stride 和空间尺寸显著影响开销。以上只是作者2D实验数据，不能作为本机3D任务的显存/时间资格。显式窗口3D训练可能代价很大，应先做整网资源估计与实际资格。

## 已执行的合成探索

原矩差/输出差实现的 [原资格](../experiments/mc_rc_3d_local_kernel_normalization_2026_10_07/attempt01.json) 保留：4例float64通过，float32的常量2和offset1000失败（最大误差0.0001884848、0.58210845）。这不是 MRI 反证，也不是作者论文实现的反证。

另立执行前 [数值补充协议](../MC_RC_3D_LOCAL_NORMALIZATION_NUMERICAL_ADDENDUM_2026-10-07.md)，比较固定窗口pivot中心化后的显式实现与独立NumPy逐窗口公式；所有float32中间计算保持float32。原4例外加入offset1e6、near_constant_2，另核stride2与padding0。 [新资格](../experiments/mc_rc_3d_local_kernel_normalization_centered_2026_10_07/attempt01.json) 实际exit0、complete=true、errors=[]，16个输出对照、input/weight/bias梯度及两精度局部性均过预定门槛；float32最大输出误差6.19465e-7，float64最大误差1.98512e-10。float32最大梯度误差3.31453e-7；两精度full/crop interior和远处扰动误差均0。

扩展压力例的原矩差实现也保留：offset1e6的float64误差0.00103677、float32误差1261.10；near_constant_2的float32误差0.00417598。原4例的失败没有因新实现通过而改判。结果支持直接中心化在这些**合成样本**上避免了严重数值消减；没有证明所有输入上稳定，也没有证明可负担真实整网训练。

任务网络训练更新0、MRI/GT读取0、CUDA未初始化。第一次调用误用了默认 `D:\conda\python.exe`，缺nibabel并在导入阶段退出1，输出目录尚未创建、更新0；随后使用既有 `D:\conda\envs\MRI\python.exe -X utf8 -B` 成功，未安装或修改根环境。一次文本输出的GBK编码异常也已记录并以UTF8输出修正。

## 创新判断和后续

局部统计、3D扩展、稳定中心化实现都作为已知方法/工程准备，不能独立包装首创。当前IN整图依赖问题可由局部有限统计算子作机制对照，但仍需要完整网络感受野的halo、下采样格点对齐和正确外边界；单层局部性不证明整个U-Net精确分块等价。

下一步只有在任务基线训练能力与真实资源合格后，才事前冻结从头训练的普通IN/固定统计/已知局部统计对照。使用相同病例、监督、预算和原gate，报告额外计算/显存，不用旧checkpoint直接替换算子比较“方法优劣”。剩余动作收益预测候选仍须超过强PCHIP和同observed直接任务，并排除SafeRestore/MoEDiff等先例覆盖；本篇不提供新的独立科学确认。
