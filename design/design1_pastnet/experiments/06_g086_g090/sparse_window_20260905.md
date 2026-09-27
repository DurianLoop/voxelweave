# PAST-Net G086-G090：从 Refiner 转向独立 Sparse-Window 主干

日期：2026-09-05  
数据集：fastMRI-brain-T2 expanded，x4，固定 train/val/test split  
当前最优：G084，PSNR `24.4423 dB`，SSIM `.807311`，MAE `38.3100`  
目标：验证未收敛收益，并用独立长窗口主干寻找超过 residual-refiner 局部上限的结构增益。

## 1. G081-G085 给出的直接证据

| 版本 | PSNR | 相对 G079 | 结论 |
|---|---:|---:|---|
| G081 PhaseFlow | 24.4187 | +.0156 | 显式对齐有小幅作用 |
| G082 Fourier-INR | 24.4121 | +.0089 | 连续坐标不是当前主瓶颈 |
| G083 Unrolled | 24.4091 | +.0060 | curvature feedback 贡献很小 |
| **G084 Dual-domain** | **24.4423** | **+.0392** | 唯一全指标、24/24病例稳定改善 |
| G085 3D U-Net refiner | 24.4085 | +.0053 | 输出端局部3D修正无明显价值 |

五组都没有达到预设 `+.10 dB` 结构门槛。G084 说明频率分解值得保留，但同时证明“继续在 G079 后面叠浅 refiner”不足以冲击26 dB。下一步按事先规则拆成一条收敛对照和一组独立主干消融。

## 2. 实验矩阵

| 版本 | 类型 | 核心变量 | 初始化 | Epoch上限 |
|---|---|---|---|---:|
| G086 | 收敛对照 | G084低学习率 cosine restart | G084 best | 60 |
| G087 | 新主干基线 | 四anchor多尺度 sparse-window U-Net | 从头训练 | 200 |
| G088 | 新主干对齐 | G087 + PhaseFlow | 从头训练 | 200 |
| G089 | 新主干双域 | G087 + FFT low/mid/high bands | 从头训练 | 200 |
| G090 | 新主干组合 | PhaseFlow + FFT + 3D offset bottleneck | 从头训练 | 220 |

G087-G090全部预测一个 sparse interval 内的三个缺失切片，不调用 G079/G084 prediction，也不加载其 checkpoint。因此它们不是后处理器，而是新的 reconstruction backbone。

## 3. G086：G084 低学习率重启

Profile：`full_pastnet_g086_dual_restart60`

G084 的 best 位于第140轮，末10轮 val loss 仍下降 `2.44e-6`。G086从该 best checkpoint恢复全部权重，使用新的60轮 warmup-cosine 日程：

```text
base LR = 1.5e-6
head LR = 2.25e-6
dual-domain adapter LR = 1.2e-5
warmup = 3 epochs
patience = 25
```

G086只回答收敛问题，不作为新架构。如果它相对 G084低于 `+.03 dB`，就判定 continuation 不值得继续。

## 4. G087：Independent Pyramid Sparse-Window U-Net

Profile：`full_pastnet_g087_sparse_window200`

### 4.1 输入

一个 interval 的17通道唯一条件：

```text
4 anchors: prev, left, right, next
3 linear coarse queries: q=.25,.50,.75
3 phase maps
2 local differences: right-left, abs(right-left)
2 boundary-validity masks
3 outer deltas/curvature
```

### 4.2 主干

```text
17-channel interval tensor
  -> 40-channel full-resolution stem
  -> H/2, 80 channels
  -> H/4, 160 channels
  -> H/8, 240-channel bottleneck
  -> skip-connected decoder
  -> [3 residuals, 3 confidence maps]
  -> coarse_q + confidence_q * residual_q
```

三个 missing offsets 一次联合输出，整个 encoder/decoder 都能利用四个 sparse anchors。它与失败的 MA4W 不同：MA4W要求单个二维模型预测跨三个 interval 的9张缺失切片，并对重叠窗口平均；G087只预测中心真实 anchor pair 内的3张切片，任务边界与推理边界一致。

G087是后续组件的独立基线。若它本身明显低于 G084，说明从强 warm-start 单切片模型切换到从头 window training 的优化代价过大。

## 5. G088：Sparse-Window + PhaseFlow

Profile：`full_pastnet_g088_sparse_flow200`

G088在进入 U-Net 前，对每个 phase 预测 left/right 双向位移场：

```text
[four anchors, coarse_q, phase_q, absdiff, curvature]
  -> half-resolution flow network
  -> warp(left), warp(right)
  -> phase-weighted aligned query
  -> concatenate with the 17-channel base condition
```

与 G081 的区别是，aligned query 从第一层起参与整个新主干，而不是只修正已经完成的 G079 prediction。G088与G087的差异可以直接衡量 backbone-integrated alignment 的价值。

## 6. G089：Sparse-Window + FFT Dual Domain

Profile：`full_pastnet_g089_sparse_dual200`

G089把 G084 的成功机制前移到输入表征：

```text
three coarse query slices
  -> rFFT2
  -> continuous radial low / mid / high masks
  -> irFFT2 for 9 band-specific maps
  -> concatenate with 17-channel sparse-window condition
  -> shared multiscale U-Net
```

G084证明频率分解适合预测后残差；G089检验它能否在编码早期帮助网络分离低频强度轨迹与高频结构变化。G089是本组优先级最高的独立候选。

## 7. G090：Flow + Dual Domain + 3D Offset Bottleneck

Profile：`full_pastnet_g090_sparse_hybrid220`

G090组合 G088/G089，并在 `H/8,W/8` bottleneck 中把共享特征展开为三个 phase token：

```text
shared bottleneck feature
  + learned embeddings for q=.25,.50,.75
  -> depthwise/spatial Conv3D across [q,H,W]
  -> merge three offset features
  -> skip-connected decoder
```

3D交互位于最深层，具有较大面内感受野且显存可控；这与G085在输出图像上做局部3D卷积不同。G090风险最高，只有同时超过G088和G089，才能证明组合与3D bottleneck有额外价值。

## 8. Loss 与优化协议

G087-G090使用完全相同的基础协议，以保证组件消融可解释：

```text
Charbonnier                  1.0
MSE                          0.35
top-10% tail MSE             0.15
gradient                     0.04
Laplacian edge               0.003
z-curvature                  0.012 (G090: 0.015)
coarse residual regularizer  0.0005
reverse symmetry             0.002
```

Optimizer为 AdamW，betas `(0.9,0.99)`，weight decay `5e-5`，EMA `.9995`。G087-G089 LR `1.5e-4`、warmup10；G090 LR `1.2e-4`、warmup12。之后 cosine decay 到初始 LR 的2%。

G087-G090使用真实 batch `16`、accumulation `1`。最重 G090 在完整对称 loss 反向下峰值为 `12.842 GiB`，低于24GB物理显存；这比使用 batch-1 accumulation-16 更充分利用GPU。

## 9. Smoke 验证

所有 smoke 均完成一轮训练、验证、EMA checkpoint保存/重载、整卷推理、指标计算与paper table，`skipped_nonfinite=0`。

| Profile | Val loss | 单病例PSNR | Params(M) | FLOPs/生成切片(G) | 状态 |
|---|---:|---:|---:|---:|---|
| G086 restart | .023562 | 23.6381 | .9922 | 148.86 | passed |
| G087 window | .052986 | 17.5593 | 3.1390 | 11.24 | passed |
| G088 flow | .052704 | 17.5802 | 3.1499 | 11.62 | passed |
| G089 dual | .051686 | 17.6550 | 3.1480 | 11.63 | passed |
| G090 hybrid | .052882 | 17.5892 | 3.4044 | 12.28 | passed |

G087-G090 smoke 从头训练，且 smoke 在第一轮直接使用峰值LR；其单病例PSNR只验证链路，不用于full筛选。正式profile有10-12轮warmup，第一轮LR仅为峰值的 `1/10` 或 `1/12`。

## 10. Full 决策规则

1. G086只与G084比较，`<+.03 dB` 即停止 continuation。
2. G088/G089分别与G087比较，判断对齐和双域输入的独立贡献。
3. G090必须超过 G088 与 G089，否则组合失败，不能用复杂度辩护。
4. 独立主干至少超过 G084 `+.10 dB` 才视为突破 refiner 上限。
5. 进入跨数据集验证的候选必须同时保持 SSIM、MAE、MSE，不接受只提高PSNR但显著损伤结构指标。
6. 不使用测试集blend、病例权重、后验checkpoint挑选或按IXI结果修改模型定义。

## 11. 运行准备

```powershell
Set-Location D:\MRI
$py = 'D:\conda\envs\MRI\python.exe'
$env:PYTHONPATH = 'D:\MRI\pre;D:\MRI\baseline;D:\MRI\design;D:\MRI'
```

## 12. 分开的 Full 运行指令

### G086：G084 continuation

```powershell
& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g086_dual_restart60
& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g086_dual_restart60
```

### G087：Independent sparse-window U-Net

```powershell
& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g087_sparse_window200
& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g087_sparse_window200
```

### G088：Sparse-window + PhaseFlow

```powershell
& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g088_sparse_flow200
& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g088_sparse_flow200
```

### G089：Sparse-window + FFT dual domain

```powershell
& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g089_sparse_dual200
& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g089_sparse_dual200
```

### G090：Sparse-window hybrid

```powershell
& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g090_sparse_hybrid220
& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g090_sparse_hybrid220
```

五组应分开依次运行。G086是低成本收敛检查；独立主干建议按 G087、G089、G088、G090 的信息效率顺序执行，其中G089最直接承接当前正证据。

## 13. 2026-09-07 Full 结果

五组均完成训练、best checkpoint 推理和 test-24 评估，所有 run 的 `skipped_nonfinite=0`。G087-G090 因验证集早停，实际轮数少于上限。

| 版本 | 实际轮数 | Best epoch | PSNR | SSIM | MAE | MSE | NCC | Dice | HD95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| G084 参考 | 140 | 140 | 24.4423 | .807311 | 38.3100 | 7173.39 | .937057 | .879215 | 2.1759 |
| **G086 restart** | 60 | 54 | **24.4470** | **.807465** | **38.2894** | **7165.79** | **.937124** | **.879285** | 2.1714 |
| G087 sparse-window | 83 | 33 | 24.0859 | .790281 | 40.8068 | 7737.20 | .931764 | .877286 | 2.0736 |
| G088 + PhaseFlow | 84 | 34 | 24.0638 | .789472 | 40.9240 | 7742.81 | .931597 | .875127 | 2.0830 |
| G089 + dual-domain | 83 | 33 | 24.1089 | .790968 | 40.7628 | 7686.02 | .932255 | .876577 | **2.0538** |
| G090 hybrid | 97 | 37 | 24.0497 | .789013 | 41.0388 | 7764.13 | .931557 | .874806 | 2.1333 |

## 14. 配对统计与门槛判定

- G086 相对 G084：PSNR `+0.00463 dB`，23/24 病例获胜，bootstrap 95% CI `[+0.00378,+0.00540]`；SSIM、MAE、MSE、NCC 也一致微幅改善。这是统计上稳定、科学上极小的收敛尾差，远低于预设 `+.03 dB` continuation 门槛。
- G089 相对 G087：PSNR `+0.02295 dB`，12/24 获胜，95% CI `[-0.00615,+0.0533]`，不显著；SSIM `+0.000686`，17/24 获胜且区间为正。双域表征仍有弱结构证据，但没有形成可靠 PSNR 增益。
- G088 相对 G087：PSNR `-0.02219 dB`，SSIM `-0.000809`。PhaseFlow 前移到新主干没有复现 G081 的微弱正收益。
- G090 相对 G089：PSNR `-0.05918 dB`，仅6/24获胜，95% CI `[-0.0883,-0.0298]`；SSIM、MAE、MSE、NCC、Dice、HD95均退步。Flow、FFT和3D bottleneck的组合明确失败。
- G089 相对 G084：PSNR `-0.33345 dB`，仅1/24获胜；SSIM 0/24获胜，MAE 0/24获胜。独立 sparse-window 主干没有补回放弃成熟 warm-start 主干造成的优化损失。

## 15. 本轮结论

1. 当前 fastMRI 最优更新为 G086 的 `24.4470 dB`，但它距26 dB仍有 `1.5530 dB`，不能被描述为结构突破。
2. 停止 G084/G086 继续低学习率续训；其收益已经进入千分之几 dB 的收敛尾部。
3. 停止 G087-G090 独立 sparse-window 路线。后续不以增加宽度、轮数或组合失败组件来挽救该主干。
4. 保留唯一可复现的机制证据：成熟多锚点主干上的 tail-aware objective、多尺度 latent interaction 和 FFT dual-domain residual。
5. 冻结 G086 的模型定义与选择规则，下一步直接迁移 IXI 做外部泛化验证；不得根据 IXI test-115 逐病例结果再次调参。

IXI 固定候选的架构、显存验证、预注册门槛与运行指令见 `design/design1_pastnet/experiments/07_cross_dataset/ixi_g086_generalization_20260907.md`。
