# Design1 PAST-Net 研究收束与交接

更新时间：2026-09-07  
任务：T2 MRI `x4` through-plane interpolation  
状态：fastMRI 开发路线已冻结；IXI 固定候选已通过 smoke、尚未完成 full；NingXia 尚未开始。

> 本目录是 Design1 的唯一交接入口。历史文档已经按阶段集中归档；训练代码、`runs` 和 checkpoint 为保持模块导入及 warm-start 路径稳定，仍保留在原代码包中。结果追溯看 [实验账本](results/experiment_ledger.md)，文件定位看 [ARTIFACT_INDEX.md](ARTIFACT_INDEX.md)，下一代设计看 [SOTA 交接简报](handoff/next_sota_handoff.md)。

## 目录结构

```text
design/design1_pastnet/
  README.md                 # 唯一入口与当前状态
  ARTIFACT_INDEX.md         # 全部代码、run、checkpoint 和文档索引
  code/                     # 实际 Python 包的位置说明
  runs/                     # 实际运行目录与冻结产物说明
  reference/                # Design1 原始蓝图
  experiments/              # 01-07 按时间编号的实验设计与命令
  results/                  # 正式结果、实验账本和滚动研究时间线
  handoff/                  # 下一代 PAST-Net v2 交接简报
```

## 1. 三十秒结论

1. fastMRI 当前最好是 `G086 / full_pastnet_g086_dual_restart60`：PSNR `24.4470`、SSIM `.807465`、MAE `38.2894`、MSE `7165.79`、NCC `.937124`。
2. 它相对本地 I3Net 提高 `+0.4368 dB`，五项主指标均更好；但 fastMRI test-24 已被多轮开发反复查看，只能称为“当前本地开发集最优”，不能再当完全独立的最终测试证据。
3. 从初版 `22.9327` 到 G086 共提高 `+1.5143 dB`。最大的单次结构收益来自 G07 宽多锚点主干；之后多尺度 latent、tail objective 和双域 residual 提供稳定但越来越小的增益。
4. G086 比 G084 只高 `+0.00463 dB`，低于预注册的 `+.03 dB` 续训门槛。继续延长训练、微调学习率或再叠浅 refiner 已无研究价值。
5. IXI 上已有 G07 为 `29.9892 dB`，明显低于 I3Net `31.3058 dB`（`-1.3165 dB`）。这证明 fastMRI 胜出不等于跨数据集 SOTA。
6. IXI G086 仅完成一轮 smoke。正式 profile `full_g086_dual_interval160_test115` 尚无 checkpoint，不能把 smoke 单病例指标写进结论。
7. NingXia 尚无 PAST-Net 正式结果。该数据集的当前门槛是 SwinIR 的 PSNR `23.9513`、SSIM `.7525`、MAE `85.9679`、MSE `32030.55`，以及 HAT 的 NCC `.8933`。
8. 下一步不是继续造 G091-G095 微调，而是先完成固定的 IXI G086 泛化判定，再依据信息上限诊断启动 PAST-Net v2。

## 2. 当前冻结模型

### 2.1 fastMRI 冻结候选

- Profile：`full_pastnet_g086_dual_restart60`
- Checkpoint：`../fastmri_brain_pastnet_2p5d/runs/full_pastnet_g086_dual_restart60/checkpoints/pastnet_epoch_best.pth`
- 初始化：G084 best，低学习率 warmup-cosine restart 60 轮
- Best epoch：54
- 参数路径：`../fastmri_brain_pastnet_2p5d/settings.py`

G086 的有效结构链为：

```text
四个 sparse anchors + phase/validity/difference/curvature 条件
  -> query-specific linear coarse image
  -> shared anchor encoder + phase-conditioned soft fusion
  -> 64-channel / 10-block wide MA3 trunk
  -> two multi-scale spatial context blocks
  -> interval 内 q=.25/.50/.75 的 1/2、1/4 尺度 latent Conv3D interaction
  -> base residual prediction
  -> spatial expert + FFT low/mid/high expert + learned gate
  -> bounded correction + coarse skip
```

损失由 Charbonnier、MSE、gradient、Laplacian edge、轻量 symmetry、z-curvature、residual regularization、top-10% tail MSE 和 base guard 组成。优化器为分组 AdamW，配合 warmup-cosine、EMA 和梯度裁剪。

### 2.2 IXI 固定候选

IXI G086 保留同一机制，但从 IXI G07 初始化：240/240 个张量完成映射，新增模块零残差初始化，初始化输出最大绝对差为 `0.0`。activation checkpointing 将完整反向峰值从 `22.81 GiB` 降到 `11.99 GiB`。

它是一个预先冻结的跨数据集验证，不是新的 IXI 超参搜索。运行命令见第 9 节。

## 3. 研究进程

| 阶段 | 代表版本 | PSNR | 相对上阶段 | 核心结论 |
|---|---|---:|---:|---|
| 初版 residual | v1 full | 22.9327 | - | coarse + bounded residual 可训练，但上下文不足 |
| 多锚点演化 | MA2 | 23.6079 | +.3495 vs extend60 | 外侧锚点提供真实信息 |
| MA3 / joint | MA3JF | 23.9731 | +.3653 vs MA2 | rich condition 有效；joint 微调接近局部上限 |
| 十方向架构筛选 | G07 wide MA3 | 24.2910 | +.3178 vs MA3JF | 容量瓶颈主要在任务匹配的宽主干 |
| 优化与上下文 | G071-G075 | 24.3351 | +.0441 vs G07 | AdamW/cosine/EMA 是稳定卫生项；多尺度 context 有结构信号 |
| latent 与误差尾部 | G079 | 24.4032 | +.0681 vs G071 | 高误差像素尾部是 PSNR 瓶颈，但会牺牲 MAE/Dice |
| 激进机制筛选 | G084 | 24.4423 | +.0392 vs G079 | 空间/频率双专家是最可靠的新机制 |
| 收敛检查 | G086 | 24.4470 | +.0046 vs G084 | 已进入收敛尾部，冻结 |
| 独立窗口主干 | G087-G090 | 最好 24.1089 | -.3334 vs G084 | 从头窗口模型丢失成熟表征；组合复杂度不能替代可优化性 |

完整数值、对照关系和停止理由在 [实验账本](results/experiment_ledger.md)。

## 4. 第一性原理结论

### 4.1 任务本质是条件残差估计

给定稀疏切片 `S0` 与 `S4`，线性插值已经确定大部分低频强度。模型真正需要学习的是：

```text
target(q) = linear_coarse(q) + anatomy_deviation(q) + acquisition_residual(q)
```

因此 coarse skip、受限 residual 和置信度门控比直接生成整张图更稳定。G07 之后所有有效版本都没有推翻这一点。

### 4.2 性能瓶颈不是“参数不够”，而是可辨识信息与归纳偏置

G07 加宽带来 `+.3178 dB`，说明早期确有容量瓶颈；但更深 G08、3D 输出头、INR、recurrent refiner 和继续续训都只有 `0.00x dB`。当 G086 已到 `24.4470` 后，目标 26 dB 还差 `1.553 dB`，等价于在相同 PSNR 定义下再降低约 `30%` 的均方误差。这不是常规 optimizer 或多几十轮能够合理提供的幅度。

下一次大提升必须至少满足一项：引入此前未使用的有效信息、改变跨切片对应建模方式、扩大有效训练分布，或证明当前评价上限仍有足够空间。

### 4.3 多锚点有用，短 token 注意力没有额外价值

四锚点和 phase 条件持续有效；但仅对三个 query offset 做 self-attention 与普通 latent Conv3D 基本相同。三个 token 本身不是 Transformer 的优势场景。未来应把计算用于多尺度空间对应或更长的物理 z 上下文，而不是给三个固定 phase 堆 attention。

### 4.4 频率分解是最可靠的后期结构信号

G084 相对 G079 在 PSNR、SSIM、MAE、MSE、NCC 上 24/24 病例全胜。合理解释是：低频分支处理强度轨迹，中高频分支处理边界和纹理，二者的误差统计不同。该机制应保留，但不应误读为“再堆 FFT 层就能到 26”；它在独立 G089 主干中只有弱 SSIM 信号，说明频率机制依赖成熟空间表征。

### 4.5 tail objective 找到了真问题，也暴露了目标冲突

G079 与 G078 架构相同，仅增加 top-10% tail MSE，就获得 24/24 病例 PSNR 提升和 `+.0650 dB` 均值增益。这是很强的因果证据：少量大误差区域主导当前 MSE/PSNR。

但 MAE 增加 `0.1043`、Dice 下降约 `.00244`。未来不能继续增大 hard top-k 权重，而应使用平滑 CVaR、分位数退火、区域不确定性或频带风险分解，在压制大误差的同时避免全局过修正。

### 4.6 失败的组件组合不会自动变成成功模型

G090 把 Flow、FFT 和 3D bottleneck 同时叠加，反而显著低于 G089。复杂度只在组件各自解决不同且已验证的问题时才有意义。以后所有组合必须遵守“单组件先过门槛，再组合”的顺序。

### 4.7 泛化是当前最大的未解问题

G07 在 fastMRI 超过 I3Net，却在 IXI 落后 `1.3165 dB`。最可能的根因不是单纯训练轮数，而是数据域的 spacing、FOV、方向、噪声、强度归一化和解剖变化速度不同。只在像素 phase `q=.25/.50/.75` 上建模，没有显式表示毫米级 z 距离和采集几何，可能是跨域反转的重要原因。

## 5. 已证实保留、谨慎保留、停止方向

| 级别 | 组件/做法 | 证据与处理 |
|---|---|---|
| 必须保留 | linear coarse + bounded residual | 稳定、任务匹配，是全部强版本共同底座 |
| 必须保留 | rich four-anchor conditioning | MA2/MA3/G07 连续正收益 |
| 必须保留 | wide MA3 mature trunk | 最大单次结构提升，后续 warm-start 核心 |
| 必须保留 | multi-scale spatial/latent context | 小但方向一致；比短 token attention 更有效 |
| 必须保留 | dual-domain residual expert | 后期唯一全主指标稳定提升机制 |
| 优化卫生项 | grouped AdamW + warmup cosine + EMA | 提升小但稳定，不作为创新点 |
| 谨慎重做 | error-tail objective | PSNR 强正证据，但需解决 MAE/Dice 冲突 |
| 谨慎重做 | feature-level deformation | G081 仅微弱正收益；应改为物理坐标、多尺度对应而非输出后修正 |
| 停止 | 强 symmetry / teacher trust region / reliability gate | 无独立收益或限制模型跳出旧解 |
| 停止 | 输出端 3D residual / volumetric U-Net | 只产生微调级收益 |
| 停止 | 三 offset self-attention / coordinate INR / unrolled refiner | 未识别主要误差来源 |
| 停止 | MA4W 与 G087-G090 从头 sparse-window | 明确落后，不用加宽、加轮数救援 |
| 停止 | G084/G086 继续低学习率续训 | `+.00463 dB` 已低于门槛 |

“停止”针对当前实现与证据，不代表这些研究概念永远无效；若重启，必须改变其信息位置或可验证假设，而不是换名字重跑。

## 6. 研究有效性边界

1. fastMRI test-24 已参与多轮方向判断，应在论文中标记为 development test。最终强结论需要新的锁定 holdout、预注册复评或外部数据支持。
2. 不允许按 test case 调 loss、采样权重、checkpoint、blend 系数或后处理。
3. IXI G086 只运行固定 profile；不因 test-115 结果衍生 G086-IXI-v2/v3。
4. NingXia 必须保持 8-fold case-level CV，不能让同一病人的不同 series 跨 train/test。
5. 新架构至少使用 3 seeds；报告均值、标准差、病例配对 bootstrap、win count 和失败病例。
6. PSNR 提升必须同时检查 SSIM、MAE、MSE、NCC、Dice/HD95 与视觉误差图，不以单指标交换临床结构。
7. 参数量、FLOPs、显存和推理时间必须与强 baseline 同口径报告。

## 7. 下一会话的正确顺序

1. 先读本 README、[SOTA 交接简报](handoff/next_sota_handoff.md) 和 [G086 IXI 预注册文档](experiments/07_cross_dataset/ixi_g086_generalization_20260907.md)。
2. 检查 IXI `full_g086_dual_interval160_test115` 是否已有正式 checkpoint；当前快照中没有。
3. 运行唯一固定 IXI full，完成后做 G086 vs G07/I3Net 的 115 病例配对统计。
4. 不论 IXI 结果好坏，都先记录结论，不在 IXI test 上继续搜索。
5. 若 G086 相对 G07 至少 `+.05 dB` 且 PSNR/SSIM/MAE/MSE 同向改善，再实现 NingXia 固定候选。
6. 若 IXI 增益小于 `.05 dB` 或退步，Design1 v1 正式结束；按 [SOTA 交接简报](handoff/next_sota_handoff.md) 的 oracle/误差分解先做诊断，再实现 PAST-Net v2。

## 8. 建议给新会话的起始提示

```text
请先阅读 D:\MRI\design\design1_pastnet\README.md、ARTIFACT_INDEX.md、
results\experiment_ledger.md 和 handoff\next_sota_handoff.md。不要重复 Design1 已否定的微调路线，
不要使用 fastMRI test-24 或 IXI test-115 做后验调参。先检查并完成 README 中唯一待办的
IXI G086 固定泛化验证，然后依据预注册门槛决定是迁移 NingXia，还是启动 PAST-Net v2
的 oracle/error-decomposition 阶段。任何新结构都必须写清新增信息、可证伪假设和停止门槛。
```

## 9. 唯一待运行的现有 Full

```powershell
Set-Location D:\MRI
$py = 'D:\conda\envs\MRI\python.exe'
$env:PYTHONPATH = 'D:\MRI\pre;D:\MRI\baseline;D:\MRI\design;D:\MRI'

& $py -B -m ixi_pastnet_2p5d.run_all --profile full_g086_dual_interval160_test115
& $py -B -m ixi_pastnet_2p5d.paper_table --profile full_g086_dual_interval160_test115
```

不要重跑 G01-G090，也不要继续 G086 fastMRI。现有 Design1 的研究价值已经从“继续找更高单点分数”转为“用冻结候选验证可迁移机制，并为下一代模型确定真正的信息瓶颈”。
