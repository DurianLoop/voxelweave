# IXI-STC：真实六锚点的独立配对探索（2026-10-03）

用户要求继续寻找此前有希望的路线在 IXI 训练。本次重用原 STC 的 SparseTrajectory 实现，不修改任何旧源码、协议、权重或既有负结果。旧 fastMRI extended 对 local 仅 +0.00109 dB，未晋级；orientation 虽 +0.09439 dB，但 HD95/SSIM 退化；LACV +0.01465 dB，质量健康但效应很小。没有任何旧候选已有 IXI 超过 I3Net 的证据。本次依据是适用信息条件发生变化，而非把旧失败改写为成功。

## 唯一主要变量

保留现有 IXI 小波主干、四锚点 rich conditioning、linear coarse、bounded residual、MA3、多尺度 latent 和 dual-domain。初始化固定为已完成的 IXI wavelet3 seed3407 validation best epoch80，SHA256 bee2006a5fde5e006feb42745b7048938c72e008068d7424867f8d0c4dc95acc。初始新增投影为零；local/extended 的全部初始参数逐 tensor 相同，初始化输出都等于该底座。

共同加入原 STC 路径：六槽 [-8,-4,0,4,8,12]，1/4 与 1/8 特征，以查询 phase 为中心拟合加权潜特征值、斜率和曲率，投影到解码前的 latent。local 在编码之前严格屏蔽首尾远端槽；extended 仅解除两槽 mask。两臂模型形状、容量、计算、初始化、采样、优化和损失相同。这样检验的是额外真实观测信息，不能把 extended 对旧小波的收益全部归因于远端信息：必须看 extended 对 local 的配对差异。

fastMRI validation 的短 volume 通常只有四个真实观测，六槽在内部无法增加观测数量；IXI 长 volume 可以提供六个不同真实观测。本包检查 train/val 的实际 valid 数量，不能把重复端点算作新增信息。目标层绝不进入 forward。方向增强和 LACV 不同时叠加。

## 训练与评分

固定原划分404 train、58 validation；仅 T2 x4、256×256、z=0,4,...。每轮 train 无放回抽4000区间，seed*1000+epoch确定；两臂相同。沿用已验证 float32 缓存，不复制16GB数据，不读取 test 图像。effective batch16、microbatch2；checkpoint数在 full 前由 smoke 固定。禁止为了占显存加入无关张量。

两臂分别从固定初始化开始，80轮上限、min30/patience15；AdamW，旧参数lr2e−5、新STC参数lr1e−4，wd2e−5、betas(.9,.99)、warmup5/cosine floor.05、EMA.999、clip1、原完整 objective 不变。仅前3轮冻结旧参数，旧小波 gate 不被当作新参数。80轮是每臂独立预算，不是先训local再把其权重给extended，也不等于从头训练的累计预算。使用既有AMP恢复机制；EMA仅在真实更新后前进。

仅 validation 选 EMA best。PSNR/SSIM 改为与主表一致的每张 GT 强度范围，输出统一 clamp[0,1]、只评缺失层、患者等权；这只是固定指标定义，不参与模型输入。MAE/MSE 仍按归一化强度报告并明确单位；Dice/HD95仍是强度代理，与旧表auto-mask指标不同。没有完整匹配全部指标前，不往旧主表主排名直接塞数值。训练初始测完整58例为共同固定基点。

## 晋级与停止

一个 full.ps1 可顺序运行 local 和 extended，不在24GB GPU同时开两份训练。两臂结束后 report 只读 validation 配对评估：extended 对 local PSNR ≥ +.10 dB、10,000次患者bootstrap CI下界>0、≥60%患者胜出、local最差四分位不退；SSIM/MAE/MSE/NCC/Dice/HD95/tail10均值方向不退；两臂训练时间与峰值显存之比≤1.5。同时extended对共同初始化须≥+.15 dB。任一不满足即停止此路线，不用更长续训、LR sweep或多个后处理救援。

通过仅代表 validation 筛选有效，不等于超过 I3Net 或 SOTA。随后须同口径完整复评 I3Net validation、补齐固定另外两seeds2027/9103的local/extended；机制与质量均通过再锁定最终方案。只有一个训练后test入口也不能自动打开test。本包完全不提供test操作。IXI test115已经在上一轮探索中被查看，不得作为本次挑模型、epoch或超参数的依据；后续确认还须独立数据和匹配基线合同。三seed是IXI适配随机性，固定历史初始化本身不是三次独立预训练。

## 恢复与溯源

所有本包Python/PowerShell/本协议、数据manifest与冻结依赖源码哈希进入运行manifest。full后不改源码或协议。以last.pth为epoch提交点，保存模型/EMA/优化器/scaler/RNG/history及可恢复的best；未提交epoch重跑，不重复已经提交的epoch。日志自动保存。训练、预检查和验证报告分开，full由用户运行，助手自行完成smoke。
