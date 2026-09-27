# PAST-Net G081-G085 激进结构实验设计与 Full 指令

日期：2026-08-29  
数据集：fastMRI-brain-T2，固定官方项目内 train/val/test split，x4 体数据插值  
当前起点：G079，PSNR `24.4032 dB`，SSIM `.805964`，MAE `38.4845`  
研究目标：寻找可产生显著结构增益、并能原样迁移到 IXI/NingXia 的机制；`26 dB` 仍是目标，但不是预设结论。

## 1. 为什么不再继续 G079 小幅调参

G076-G080 已经给出三个清楚边界：

1. 三 offset 上的浅 attention 与普通 3D conv 等价，说明简单 latent adapter 容量不是主要矛盾。
2. 双尺度 latent mixer 只有约 `+0.005 dB`，继续添加同类 adapter 不足以缩小到 26 dB 的 `1.5968 dB` 差距。
3. Tail-aware objective 在 24/24 病例提高 PSNR，说明高误差尾部是有效优化信号，但它不能替代新的图像形成机制。

因此 G081-G085 不再只交换 optimizer 或 loss 权重，而是分别改变跨切片对应、坐标表达、推理过程、频率建模和体积生成方式。

## 2. 公平性与防止人为干预

五组实验遵循相同约束：

- 全部从 `full_pastnet_g079_tail_aware160/checkpoints/pastnet_epoch_best.pth` 初始化。
- G079 的 290 个 state tensor 完整映射到新模型，新分支零残差初始化；初始化输出与 G079 最大绝对差为 `0.0`。
- 使用相同训练/验证/测试病例，不读取测试指标控制训练，不按病例名采样，不做 test-time blend。
- 主 loss 保留 G079 的 Charbonnier、MSE、gradient、edge、z consistency 和 top-10% tail MSE，避免用不同目标掩盖结构比较。
- 新模块先单独训练 7-10 轮，再以较低 backbone LR 联合微调；所有版本使用 AdamW、warmup cosine、EMA 和 early stopping。
- full 上限为 140-180 轮，但若验证集在 patience 内停止改善会自动结束，不要求机械跑满。

## 3. 公共主干

五个模型共享已经验证的 G079 基座：

```text
13-channel rich condition for offsets q={1/4,2/4,3/4}
  -> G073 wide MA3 single-offset encoder
  -> H/2 + H/4 latent 3D offset mixer
  -> G079 tail-aware reconstruction base prediction
  -> one aggressive mechanism (G081-G085)
  -> confidence-gated residual correction
```

新增 correction 的最后一层为零初始化。训练开始时模型严格等价于 G079，而不是让随机新模块破坏已经获得的结果。

## 4. G081：PhaseFlow 双向可变形对齐

Profile：`full_pastnet_g081_phase_flow140`  
模型 variant：`ma3ad`  
新增参数：约 `0.080M`，总参数约 `0.884M`

### 4.1 结构

对每个目标 offset，G081 使用 left/right anchors、coarse、phase 和 G079 base prediction 预测两组二维位移场：

```text
[left, right, |right-left|, coarse, phase, base]
  -> half-resolution dilated flow CNN
  -> flow_left(q), flow_right(q), range limited to +/-8 pixels
  -> grid_sample(left), grid_sample(right)
  -> phase-weighted aligned interpolation
  -> residual correction CNN
```

它与旧 anchor gate 的区别是：gate 只能改变不同 anchor 的权重，PhaseFlow 可以改变 anchor feature 的空间采样位置，直接处理脑边界和局部结构在 z 方向上的位移。

### 4.2 假设与风险

- 假设：当前大误差尾部主要来自 anchors 的空间错位，而不是单纯强度误差。
- 成功信号：相对 G079 的 PSNR/MSE 明显改善，并在高 slice-change 病例上更强。
- 失败含义：fastMRI 的 through-plane change 不能被简单二维位移场解释，后续不应继续堆 deformable alignment。
- 风险：flow 可能把出现/消失的解剖结构错误解释为平面运动。

训练上限140轮，前7轮只训练 adapter。base LR `3e-6`，adapter LR `3e-5`。

## 5. G082：Fourier Continuous Coordinate Decoder

Profile：`full_pastnet_g082_coord_inr160`  
模型 variant：`ma3ci`  
总参数约 `1.061M`

### 5.1 结构

G082 不再把三个缺失 offset 当作三个互不相关的类别，而是把 phase 当作连续坐标：

```text
[prev, left, right, next]
  -> shared multi-dilation anchor encoder

q -> [q, sin(pi*q), cos(pi*q), sin(2*pi*q), ..., cos(4*pi*q)]
  -> coordinate encoder

anchor feature + coordinate feature + coarse + G079 base
  -> shared implicit decoder
  -> residual at arbitrary q
```

三个 offset 共用同一个 decoder，结构随 q 连续变化。该设计可直接迁移到 x2/x6 或不同 slice spacing，不需要为每个 offset 新建输出头。

### 5.2 假设与风险

- 假设：离散三 offset 建模浪费了 through-plane trajectory 的连续性，Fourier coordinate 能表达非线性 z 变化。
- 成功信号：三个 offset 都改善，且中心/边缘 offset 差距缩小。
- 失败含义：坐标表达不是瓶颈，主要误差来自缺失的真实三维对应。
- 风险：有限训练 phase 仍只有 `.25/.5/.75`，连续外推能力必须在后续 x2/x6 单独验证。

训练上限160轮，前8轮只训练 adapter。base LR `3e-6`，adapter LR `3e-5`。

## 6. G083：三阶段 Unrolled Error Feedback

Profile：`full_pastnet_g083_unrolled160`  
模型 variant：`ma3ur`  
总参数约 `0.916M`

### 6.1 结构

G083 把一次性预测改为三阶段递归校正。每一阶段把当前三个预测与真实 sparse anchors 拼成五切片局部体积，并计算无需 GT 的 z-curvature feedback：

```text
V_t = [left, pred_1, pred_2, pred_3, right]
curvature_t = V_t[z-1] - 2*V_t[z] + V_t[z+1]

condition feature + curvature_t
  -> 3D ConvGRU state update
  -> residual correction
  -> V_(t+1), repeat 3 stages
```

这不是原 MA3J 的单个 joint head。G083 在每一步用自己的当前输出重新计算误差代理，属于可学习的 unrolled optimization。

### 6.2 假设与风险

- 假设：G079 的残差不是一次前向能完全消除，但可由 anchor-clamped consistency 逐步修正。
- 成功信号：MSE 和 z-structure 指标共同提高，而不只是平滑带来的 SSIM 变化。
- 失败含义：当前 curvature proxy 与真实 reconstruction error 不一致，继续增加迭代次数没有意义。
- 风险：递归模块可能过度平滑，因此 correction scale 限制为 `.18`，z loss 仅轻度提高到 `.015`。

训练上限160轮，前8轮只训练 adapter。base LR `2.5e-6`，adapter LR `3e-5`，gradient clip `.8`。

## 7. G084：FFT Spatial/Frequency Dual Experts

Profile：`full_pastnet_g084_dual_domain140`  
模型 variant：`ma3df`  
总参数约 `0.992M`

### 7.1 结构

G084 对 `[base_1..3, coarse_1..3]` 做显式二维 FFT，并按连续径向 mask 分解为 low/mid/high bands：

```text
spatial expert: raw base/coarse -> dilated residual CNN

frequency expert:
  rFFT2 -> low/mid/high radial bands -> irFFT2
  -> band-aware residual CNN

learned local gate -> spatial correction vs frequency correction
```

与只加 edge loss 不同，这里不同频段在网络输入和专家路径上被显式分开，同时保留空间分支处理非平稳局部结构。

### 7.2 假设与风险

- 假设：G079 的 tail pixels 同时包含低频强度偏差和高频边界误差，一个统一 residual head 难以兼顾。
- 成功信号：PSNR/MSE改善的同时 MAE/Dice 不再像 G079 相对 G078 那样退化。
- 失败含义：固定频带分解没有提供额外可辨识信息，应停止频率专家路线。
- 风险：MRI 边界不是平稳纹理，FFT expert 可能只增加计算量。

训练上限140轮，前7轮只训练 adapter。base LR `3e-6`，adapter LR `3e-5`。

## 8. G085：Anchor-Clamped Volumetric U-Net

Profile：`full_pastnet_g085_volumetric180`  
模型 variant：`ma3vs`  
总参数约 `1.289M`

### 8.1 结构

G085 是本轮最激进版本。它把 G079 三个 base predictions 与左右真实 sparse anchors 组成五切片体积，在 H/W 上两次降采样，在 z 维保持完整分辨率：

```text
base volume   = [left, G079_1, G079_2, G079_3, right]
coarse volume = [left, linear_1, linear_2, linear_3, right]
phase volume  = [0, .25, .50, .75, 1]

3-channel 5-slice volume
  -> 3D encoder at H,W
  -> 3D encoder at H/2,W/2
  -> 3D bottleneck at H/4,W/4
  -> skip-connected 3D decoder
  -> corrections for middle slices only
```

左右 anchors 永不由网络重写，因此约束比旧 MA4W 更强。旧 MA4W 从22通道二维 tensor直接生成9个缺失切片，并在重叠窗口平均，训练任务过宽且破坏了强单切片基线；G085 只修正一个真实 sparse interval 内的三个 G079 predictions，不能与旧 MA4W 混为一谈。

### 8.2 假设与风险

- 假设：真正的三维局部 volume representation 是突破 G079 单切片表征上限所必需的。
- 成功信号：PSNR、SSIM、MSE、z consistency 同时提高，并且三 offset 的误差相关性降低。
- 失败含义：仅五切片局部体积仍不足，下一步需要更长 sparse window 或更强3D encoder，而不是再加输出 refiner。
- 风险：3D卷积最容易过平滑，也最难迁移到 spacing 差异较大的 IXI，因此必须先通过 fastMRI full，再移植。

训练上限180轮，前10轮只训练 adapter。base LR `2e-6`，adapter LR `2.4e-5`，gradient clip `.8`。

## 9. Smoke 与显存验证

五组均实际完成一轮训练、验证、EMA checkpoint 保存/重载、整卷推理、指标计算和 paper table，均为 `skipped_nonfinite=0`。

| Profile | Val loss | 单病例 PSNR | Params(M) | 状态 |
|---|---:|---:|---:|---|
| G081 PhaseFlow | .023727 | 23.6191 | .8836 | passed |
| G082 Fourier-INR | .023725 | 23.6175 | 1.0607 | passed |
| G083 Unrolled | .023897 | 23.6202 | .9161 | passed |
| G084 Dual-domain | .023740 | 23.6182 | .9922 | passed |
| G085 3D U-Net | .023896 | 23.6213 | 1.2887 | passed |

单病例 smoke PSNR 只验证链路，不用于预测 full 排名。正式 loss 下的反向显存测试：G082 batch-1 峰值 `13.996 GiB`，G085 batch-1 峰值 `13.561 GiB`。Batch-2 会达到 `27-28 GiB` 并借用共享显存，因此 full 统一采用 batch-1 / accumulation-16。

## 10. Full 筛选与停止规则

1. 第一比较对象统一为 G079：PSNR `24.4032`、SSIM `.805964`、MAE `38.4845`、MSE `7239.44`。
2. 相对 G079 至少 `+0.10 dB` 且 bootstrap CI 下界大于0，才视为明确结构进步；否则只算微调级变化。
3. 若 PSNR提高但 MAE或Dice显著退化，标记为目标权衡，不直接移植到 IXI。
4. G081/G082/G083/G084/G085 是不同机制，不因前一个失败而跳过后一个。
5. 最优模型进入 IXI/NingXia 时保持机制和训练策略，不按新测试集搜索 blend 权重。
6. 如果五种机制仍全部低于 `+0.10 dB`，应承认 G079 formulation 的局部上限，下一轮不再增加 residual refiner，而是训练独立的长窗口 sparse-volume backbone。

## 11. 运行准备

先在 PowerShell 执行：

```powershell
Set-Location D:\MRI
$py = 'D:\conda\envs\MRI\python.exe'
$env:PYTHONPATH = 'D:\MRI\pre;D:\MRI\baseline;D:\MRI\design;D:\MRI'
```

## 12. 分开的 Full 运行指令

### G081 PhaseFlow

```powershell
& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g081_phase_flow140
& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g081_phase_flow140
```

### G082 Fourier Continuous Coordinate Decoder

```powershell
& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g082_coord_inr160
& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g082_coord_inr160
```

### G083 Unrolled Error Feedback

```powershell
& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g083_unrolled160
& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g083_unrolled160
```

### G084 Spatial/Frequency Dual Experts

```powershell
& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g084_dual_domain140
& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g084_dual_domain140
```

### G085 Anchor-Clamped Volumetric U-Net

```powershell
& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g085_volumetric180
& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g085_volumetric180
```

每组命令完成后再执行下一组。不要并行运行这五个 full；它们都使用同一块GPU，进程并行只会增加显存换页并降低有效吞吐。

## 13. Full 正式结果（2026-09-05）

五组均完成全部训练、24病例 full 测试和 paper table，训练过程 `skipped_nonfinite=0`。

| 版本 | Epoch / best | PSNR | SSIM | MAE | MSE | NCC | Auto Dice |
|---|---:|---:|---:|---:|---:|---:|---:|
| G079 reference | 160 / 160 | 24.4032 | .805964 | 38.4845 | 7239.44 | .936450 | .878679 |
| G081 PhaseFlow | 140 / 140 | 24.4187 | .806575 | 38.4218 | 7216.47 | .936680 | .878846 |
| G082 Fourier-INR | 160 / 118 | 24.4121 | .806234 | 38.4562 | 7223.01 | .936592 | .878892 |
| G083 Unrolled | 160 / 160 | 24.4091 | .806215 | 38.4639 | 7231.33 | .936535 | .878770 |
| **G084 Dual-domain** | **140 / 140** | **24.4423** | **.807311** | **38.3100** | **7173.39** | **.937057** | **.879215** |
| G085 3D U-Net | 180 / 179 | 24.4085 | .806142 | 38.4578 | 7230.79 | .936544 | .878746 |

### 13.1 配对证据

相对 G079：

| 版本 | PSNR差 | PSNR胜例 | SSIM差 | MAE降低 | MSE降低 | 主结论 |
|---|---:|---:|---:|---:|---:|---|
| G081 | +.0156 | 23/24 | +.000610 | .0626 | 22.98 | 对齐有效但幅度小 |
| G082 | +.0089 | 21/24 | +.000270 | .0283 | 16.43 | 连续坐标不是当前主瓶颈 |
| G083 | +.0060 | 19/24 | +.000251 | .0206 | 8.11 | curvature反馈贡献很小 |
| **G084** | **+.0392** | **24/24** | **+.001347** | **.1744** | **66.05** | 唯一全指标、全病例稳定胜出 |
| G085 | +.0053 | 21/24 | +.000178 | .0266 | 8.66 | 输出端局部3D仍不是突破点 |

G084 相对次优 G081 仍在 PSNR、SSIM、MAE、MSE、NCC 上 24/24 全胜，PSNR再提高 `.0236 dB`。因此胜因不能归结为共同训练日程，而应归因于 spatial/frequency expert 的新增信息路径。

### 13.2 收敛与门槛判断

- G084 最优点在最后一轮，末10轮 val loss 继续下降 `2.44e-6`；当前日程尚有少量续训价值。
- G081 同样在末轮最优，但末段下降弱于 G084。
- G082 最优点停在第118轮，继续训练无效。
- G083/G085 即使接近末轮最优，测试收益也只有 `.005-.006 dB`，不足以支持继续扩展。
- 五组都未达到预注册的相对 G079 `+0.10 dB` 门槛。当前纪录 G084 为 `24.4423 dB`，距26 dB仍有 `1.5577 dB`。

### 13.3 决策

1. 保留 G084 的频率分解机制，并做一次60轮低学习率重启，判断未耗尽的收敛是否还能带来实质收益。
2. 不再继续 G082/G083/G085；其机制已获得充分的负面或弱效证据。
3. G081 的显式对齐保留为独立 sparse-window 主干的可选组件，不再作为 G079 后处理。
4. 按第10节预定规则，下一阶段训练独立长窗口主干，而不是继续向 G079 叠加 residual refiner。
