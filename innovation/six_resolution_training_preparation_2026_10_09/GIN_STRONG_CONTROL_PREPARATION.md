# GIN 强对照：可执行算子准备，不代表完整方法复现

固定公开稿 arXiv:2111.12525v5 和作者仓库 commit d4d5056ded88951fc3967f8f294f4a12420e13c6。arXiv 明确该稿是 early non-peer-reviewed version，期刊 final substantially revised；本准备不宣称读过 TMI final。原下载作者源码仅静态阅读，不导入执行，不安装依赖。

先独立实现已核对的 3D GIN 算子：每样本独立 Gaussian kernel/bias；共享每层核大小从 {1,3} 抽样；4 层、隐藏 2 通道，前三层 LeakyReLU(0.01)、最后一层线性；每样本 Uniform(0,1) 混合后乘 ||input||F/(||mixed||F+1e-5)。局部 CPU generator 与显式固定参数便于重放，不能称与作者 CUDA/全局 RNG 逐位同一随机序列。输入标准化后的负强度允许保留；不凭空裁剪到 [0,1]。

IPA 目前只准备互补混合算子 u=w*a+(1-w)*b，v=(1-w)*a+w*b，w∈[0,1]。测试场为预先给定连续场，不称原 2D B-spline field 或已验证的 3D IPA。作者的 3D GIN 已发布，3D IPA 未随该 commit 发布。AdvBias 内部 order=2 迭代卷积的 3 个 box factors，以及后续 bilinear 上采样，与主文 cubic interpolation 的关系保留为实现差异；不把整个过程无条件命名为 cubic。

作者三视图 consistency 是 KL(mean_probability || each_probability)，KLDivLoss 默认 mean 对全部元素平均，target 在源码未 detach。用当前环境的 synthetic logits 核实其 loss/gradient，并显式比较 detach 与 forward JS，不能把它们当同一目标或推断旧 Torch 的行为。

本轮测试只检查重放、独立 NumPy Gaussian-convolution 公式、shape/有限性/epsilon Frobenius scaling、零输入、输入未修改、互补混合恒等式、loss 方向与当前 Torch 梯度。无医学数据、GT、模型权重、训练更新或 CUDA 初始化。CPU1/interop1/below-normal，RAM/disk 各 8GB，沿 preparation7MB + FOV20MB + other22.8MB 完整存储预算，wall180秒。算子验证不等于医学收益、2992 训练资格或 35904/full38 数值资格。

后续预注册实验：basic、GIN-only、GIN+IPA、GIN+IPA+consistency；每臂保留同患者/series/schedule/母 GT/基本增强/原 binary segmentation loss，不用 GT 构造增强，不按增强效果挑病例。原模型 1-channel head 的分布用 softmax([0,z])，不额外改 head。首次开发能力诊断可用原 parent；严格 LOPO 所有臂必须 cold-init，父模型含全部开发 GT 不可作外折初始化。完整 3D field、当前环境 batch 梯度/内存/全费用、19series 资格尚未执行，保持未就绪。

所有臂同时报告曝光匹配和计算预算匹配：三视图增加的 forward/backward/augmentation 不隐藏；预算匹配时普通臂可获得同预算更多训练/强普通增强，不能故意浪费普通臂费用。建立强 task 能力和真实动作余量后，再比较同信息 action-risk 差、QC/defer、metadata-only、strong static、random 的患者级净收益。4 已见验证不作独立确认，8 未见确认12series 与 lockedIXI 关闭。六医学 gate 和全部概率/强度/坐标/二值阈值不降低。
