# 稀疏轨迹上下文：独立双臂协议（2026-09-11）

本协议在任何本分支 full 之前登记。旧 geometry、correspondence-only 均已停止，门槛和结果不变。本文件、本包 Python、full.ps1 及原 v2 Python 哈希写入每次运行 manifest；full 后不得修改这些文件继续使用原运行。

## 问题与核心模型

原 G086 将四槽锚点同位置融合。fastMRI validation 23 例均为 16 层，x4 网格只有 4 个不同观测：首尾区间的局部窗口仅覆盖其中 3 个，中间覆盖 4 个。六槽 `[-8,-4,0,4,8,12]` 在首尾能补齐已采集但窗口遗漏的第四层，不能称为获得六个真实观测。

新模型 PAST-Net STC（Sparse Trajectory Context）以原 G086 为初始化，保留 linear coarse、bounded residual、四锚点条件、64 通道 MA3、原多尺度 latent 和 dual-domain residual。唯一新增结构是解码前的稀疏轨迹上下文路径：

1. 六槽真实观测在 1/4、1/8 分辨率用共享小型 2D encoder 编码；无效或被隐藏的槽先置零，并在聚合中严格屏蔽。
2. 对每个查询 q，以稀疏采样间隔为单位构造 `d_i = offset_i/4 - q`。固定权重 `valid_i exp(-0.5(d_i/2)^2)`，对基 `[1,d,d²]` 解带 ridge 的 3×3 加权最小二乘，ridge 对角 `[0,.001,.001]`。
3. 保留查询位置的特征值、带符号斜率、二次项三个通道组；值项减去 linear coarse 的编码。两个尺度与有效数量、phase 一起融合为上下文，零初始化投影注入原 MA3 body 之前。

这些是**潜在特征的多项式摘要**，不是毫米导数，也不假设真实解剖严格服从二次曲线。无外推输出，无新增 flow、FFT、3D、物理 FiLM、attention 或 loss；沿用原输出约束。零初始化用于严格保持 G086 初始函数；前两次失败不能单独证明零初始化有问题。

相对 G086，extended 臂真正新增的是局部窗口之外的真实强度观测；local 臂只改变表示。网络看到的 target 始终只用于损失。归一化仍取相同完整稀疏网格的 min/max，因此两臂的归一化标量相同；局部对照沿用旧合同，不能声称它连远端的标量范围信息也完全未见。

## 诊断依据与限制

训练集患者按 SHA256 排序交替分成 56 名拟合、55 名诊断患者，未读取 validation/test。固定 32×32、ridge=.001 的像素线性低频探针，extended 对 local 的患者均值 MSE 由 .002609482 降到 .002581096，下降 1.0878%；50/55 获益，患者 bootstrap 95% MSE 降幅区间 `[.000017914,.000039993]`。原始表在 `results/train_information_probe/`。

这只是低容量估计器对额外观测可用性的训练内证据；不是 G086 残差的可预测性证明，不是 full PSNR 增益，也不是信息论上限。探针的子集患者虽未拟合探针，仍属于历史 G086 训练集。旧全局“四个观测”描述需限定：train 有一例 32 层、顺序异常且 geometry unknown，继续按既有 manifest 保留；validation 全为 16 层。

## 实验次序：一次只改变一个主要变量

共同使用原 RECIPE：G086 原始 checkpoint、seed3407、同样 112 训练 series/23 validation 患者、观测归一化、有效 batch16、AdamW、80 轮上限、前3轮冻结旧参数、warmup cosine、EMA、原 loss 和早停。两个新臂都使用六槽 loader 和完全相同参数形状、初始化、采样顺序。local 只在新上下文中屏蔽槽0/5；旧四锚点输入两臂逐位相同。

**E1：trajectory_local 对既有 control。** 仅增加轨迹表示路径，建立容量对照。不是候选晋级：若相同 seed 的完整 validation PSNR 低于旧 control 超过 .02 dB，或 forward 时间/显存超过 1.5 倍，停止整个 STC 分支。通过只允许进行信息消融，不代表证明创新有效。E1 full 由用户执行。

**E2：trajectory_extended 对 trajectory_local。** 仅开放六槽中额外的真实观测；重新从相同 G086 初始化训练，不加载 E1 best。入口核验 E1 完成、哈希和健康条件。不改变结构、loss、学习率或预算。

E2 晋级要求同时满足：

- 对 local：患者等权 PSNR 增益 ≥ .10 dB，10,000 次患者配对 bootstrap 95% 下界 > 0，≥60% 患者改善，local 最差四分位不退；SSIM、MAE、MSE、NCC、Dice/HD95 强度 proxy 均值方向不退；forward 时间、峰值显存各 ≤1.5 倍。
- 对原 control：同样全套 guard，PSNR 总增益 ≥ .15 dB，沿用原真实 context 总效应要求，不以小幅显著替代实用收益。
- 预先报告 boundary/centre、phase、真实 anchor 数/索引跨度；这些辅助切片不能代替总体门槛。中心区间输入集合相同，训练后中心差异可能来自全局权重适应，不能称为中心新增信息。

任一失败停止，不加学习率 sweep、续训、频率头或风险 loss 救援。重复使用 validation 已产生选择适应性；单 seed 的 CI 仅是开发筛选，非独立确认。

## 晋级之后与外部边界

只有 E2 通过才按固定另外两 seed2027/9103 补齐 control/local/extended，总计每臂3 seeds；以患者和 seed 配对统计重新核验同门槛并报告各 seed、质量、参数量、部分算子 FLOPs、完整训练时长、吞吐、峰值 allocated/reserved 和 forward 效率。3 seeds 只表示从同一历史 G086 出发的独立 v2 优化，不代表独立 v1 预训练。

最终3 seed候选通过后另行实现并冻结外部注册，才按 IXI/NingXia 既定患者 split 训练和复评；当前 pilot 入口拒绝外部训练和测试，没有可用的候选锁。fastMRI test24 始终仅是历史 development test。Dice/HD95 为强度阈值 proxy，不能冒充临床分割质量。无 SOTA 承诺。

## 资源与执行

24GB 卡使用 microbatch2、累积8，checkpoint 前5个 MA3 blocks；新上下文主要在 64²/32² 计算。助手在给 full 指令前执行真实 256² smoke、两次优化步稳定性及显存测量；如超过安全预算，只能在 full 前固定新的 checkpoint 数，两臂相同。

先执行 `full.ps1 -Variant trajectory_local -Seed 3407`；用户完成后助手核验并决定是否给 E2 的独立指令，不自动串行启动两个 full。
