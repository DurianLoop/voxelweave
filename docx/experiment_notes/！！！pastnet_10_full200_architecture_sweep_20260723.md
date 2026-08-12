# PAST-Net fastMRI full-200 十方案架构推进计划

日期：2026-07-23

目标：在不做 test-set 作弊、不做手工 blend、不用 I3Net 输出作为推理输入的前提下，基于前序 PAST-Net 试验经验，设计 10 个可直接运行的 fastMRI-brain-T2 expanded x4 full-200 方案。每个方案都是后续可能迁移到 IXI / NingXia 的架构或训练机制尝试，而不是为了 fastMRI 单表临时硬凑。

## 基本原则

1. 不按 test case 做规则分支，不做 case-specific correction。
2. 不使用测试集指标来动态选择 epoch、blend 权重或后处理强度。
3. 不把 I3Net 预测图作为训练或推理输入。
4. 允许从自家 PAST-Net checkpoint warm-start，因为这是正常 continuation / architecture transfer。
5. smoke/mini 仍只作为筛选证据；本轮按你的要求直接给 full-200 指令。
6. 后续若某方案在 fastMRI 上赢，仍必须在 IXI / NingXia 上复测泛化，才能当主方法。

## 前序经验提炼

已有结果显示，真正有效的路线是：

```text
PAST-Net v1 -> extend60 -> MA2 -> MA3 -> MA3JF
```

fastMRI full 上 PSNR 从 22.9327 提升到 23.9731，距离 I3Net 24.0102 只剩 0.0371 dB。这个提升主要来自多锚点、rich temporal features、local residual refinement 和 joint three-offset head，而不是单纯堆大模型。

同时也有明确负经验：

1. MA4W 大 window 版本参数更多，但 full 退化到 23.5719，说明容量并不是主要瓶颈。
2. MA3C / MA3CG / MA3J / MA3JF 的 mini 差异极小，说明小幅 loss 微调很难带来 26 dB 级别突破。
3. Blend probe 可以略超 I3Net，但它只能证明误差互补，不能作为主方法 claim。

因此本轮 10 个方案按低风险到高风险排序：前 6 个围绕 MA3JF / MA3J / MA3C 做可泛化机制改良，后 4 个测试容量和 window 方向是否还有救。

## 模型架构解析总览

现有 PAST-Net fastMRI 包里，本轮实际可用的主干不是 10 套完全孤立代码，而是 4 类可复用架构组件。10 个方案是在这些组件上改变训练对象、loss 约束、容量和 warm-start 路线。

### A. MA3 single-slice rich multi-anchor backbone

对应 `model_variant="ma3"`，实现类是 `PASTNetMultiAnchor2p5D`。它一次预测一个目标切片，但每个样本不只看左右 anchor，而是使用 13 通道 rich multi-anchor 条件：

```text
[prev_anchor, left, right, next_anchor,
 coarse, phase,
 right-left, abs(right-left),
 prev_valid, next_valid,
 left-prev_anchor, next_anchor-right,
 sparse_curvature]
```

模型内部结构是：

```text
5 个图像分支共享 slice_encoder:
  prev / left / right / next / coarse

aux_encoder:
  phase / diff / absdiff / valid masks / deltas / curvature

phase-aware spatial gate:
  输出 prev, left, right, next, coarse 五路空间权重

fuse + LocalStructureBlock stack + LongRangeMixer:
  做局部结构恢复和较大范围上下文混合

decoder:
  输出 residual 和 confidence

detail_refiner:
  使用 left + right - 2 * coarse 的局部上下文，补 temporal local residual

最终:
  prediction = coarse + confidence * (residual_scale * residual + refine_scale * detail_residual)
```

这类结构的优点是稳定、直接、可泛化；缺点是三个缺失 offset 仍是逐切片预测，interval 内相互约束不够。G07/G08 就是测试这个 backbone 是否还受容量限制。

### B. MA3C / MA3CG interval-consistency single-slice model

对应 `model_variant="ma3c"` / `model_variant="ma3cg"`。模型主体仍是 MA3 single-slice backbone，但 dataloader 改成 interval stack：一个 `S0-S4` interval 同时取 offset 1/2/3 的条件、coarse 和 target。

训练时会把三个 offset flatten 后送进同一个 MA3 backbone，再把输出重新组装成：

```text
[S0, pred_S1, pred_S2, pred_S3, S4]
```

然后加入 z-curvature consistency：

```text
L_z = | curvature_z(pred_window) - curvature_z(target_window) |
```

MA3CG 额外加入 teacher trust-region，用已有 MA3 checkpoint 的预测作为软约束，目标是防止 consistency 训练把已学到的强单切片重建能力破坏掉。

这类结构的优点是比 MA3 更重视 z 方向连续性，泛化逻辑也干净；缺点是它并没有真正联合建模三个 offset，只是在 loss 层面约束 interval。

### C. MA3J / MA3JF joint three-offset residual head

对应 `model_variant="ma3j"`，实现类是 `PASTNetMA3Joint2p5D`。它是目前最接近“真正 interval-level”的路线。

MA3J 的输入是 `(B, 3, 13, H, W)`，也就是同一个 interval 内 offset 1/2/3 的 rich multi-anchor 条件栈。结构分两段：

```text
single branch:
  对每个 offset 调用 MA3 backbone，得到 base prediction

joint head:
  输入 [base_S1, base_S2, base_S3,
       coarse_S1, coarse_S2, coarse_S3,
       phase_S1, phase_S2, phase_S3,
       left, right, prev_anchor, next_anchor,
       diff, absdiff, sparse_curvature]

  输出 3 个 joint correction + 3 个 joint confidence

最终:
  prediction = base + joint_confidence * joint_scale * tanh(correction)
```

joint head 最后一层零初始化，所以从 MA3 checkpoint 启动时不会一开始破坏 base prediction，而是逐渐学习跨 offset 的 residual correction。MA3JF 是当前表现最强的 MA3J fine-tune 版本，核心特征是冻结 backbone、放大 joint_scale、提高 MSE 权重，主要校准 joint residual。

这类结构的优点是同时利用 MA3 的稳定单切片能力和 interval-level correction；缺点是如果 joint head 过强，可能会对 fastMRI 特定误差形态过拟合。

### D. MA4W window-level multi-output model

对应 `model_variant="ma4w"`，实现类是 `PASTNetMA4Window2p5D`。它不是预测一个 `S0-S4` interval，而是在 13-slice window 内使用 4 个 sparse anchors：

```text
anchors: [S0, S4, S8, S12]
missing targets: [S1,S2,S3,S5,S6,S7,S9,S10,S11]
```

输入通道：

```text
[4 sparse anchors, 9 linear coarse missing slices, 9 phase maps]
```

模型结构：

```text
stem(cond_window)
anchor_encoder(4 anchors)
coarse_encoder(9 coarse slices)
fuse([stem, anchor_feat, coarse_feat])
LocalStructureBlock stack + LongRangeMixer
decoder -> 9 residual + 9 confidence
prediction = coarse_stack + confidence * residual_scale * residual
```

MA4W 是真正 multi-output window 模型，但之前 `full_ma4w_150` 明显退化，说明它容易过改、过平滑或优化目标不稳。G09/G10 只作为救援实验：降低 residual_scale、减少 window 密度、加强 residual/z consistency，而不是继续盲目加大。

## 十个方案的结构差异表

| 方案 | Profile | 架构族 | 输入/输出 | Head | Warm-start | 主要约束 | 风险点 |
|---|---|---|---|---|---|---|---|
| G01 | `full_pastnet_g01_ma3jf_cal200` | MA3J | interval 3-offset 输入，3-output | joint residual head only | `full_ma3jf_150` | teacher + MSE + z | 只校准 head，上限可能低 |
| G02 | `full_pastnet_g02_ma3j_unfrozen200` | MA3J | interval 3-offset 输入，3-output | full MA3J | `full_ma3jf_150` | low-lr full-model + z | 可能轻微过拟合 fastMRI |
| G03 | `full_pastnet_g03_ma3j_sym200` | MA3J | interval 3-offset 输入，3-output | full MA3J | `full_ma3jf_150` | symmetry + z + residual | PSNR 可能不最高，但泛化更稳 |
| G04 | `full_pastnet_g04_ma3c_z200` | MA3C | interval stack，逐 offset 输出 | MA3 single-slice | `full_ma3_psnr_ft60` | strong z-curvature | z 约束过强可能平滑 |
| G05 | `full_pastnet_g05_ma3cg_soft200` | MA3CG | interval stack，逐 offset 输出 | MA3 single-slice | `full_ma3_psnr_ft60` | soft teacher + z | teacher 过强会保守 |
| G06 | `full_pastnet_g06_ma3j_zstrong200` | MA3J | interval 3-offset 输入，3-output | joint residual head | `full_ma3_psnr_ft60` | strong z + joint | joint head 重新学习，波动较大 |
| G07 | `full_pastnet_g07_ma3_wide200` | MA3 | single target 输入，single output | residual/confidence | none | wider backbone | 从头训练，成本较高 |
| G08 | `full_pastnet_g08_ma3_deep200` | MA3 | single target 输入，single output | residual/confidence | none | deeper backbone | 优化更慢 |
| G09 | `full_pastnet_g09_ma4w_lite200` | MA4W | 13-slice window，9-output | 9 residual/confidence | none | constrained residual + z | MA4W 路线已负一次 |
| G10 | `full_pastnet_g10_ma4w_rescue200` | MA4W | 13-slice window，9-output | 9 residual/confidence | none | stronger z + lower residual | 最高风险救援 |

## 方案 1：G01 MA3JF calibration continuation

Profile：`full_pastnet_g01_ma3jf_cal200`

风险：低。

思路：从当前最强正式非 blend 结果 `full_ma3jf_150` 继续训练 200 epoch，但冻结 backbone，只校准 joint head，并加入轻量 teacher trust-region。这个方案不是为了大幅改结构，而是检查 MA3JF 是否还有稳定余量，同时降低破坏已有泛化特征的风险。

关键设置：

| 项目 | 值 |
|---|---:|
| model_variant | `ma3j` |
| init | `full_ma3jf_150` best |
| epochs | 200 |
| lr | 3e-5 |
| freeze_backbone | true |
| lambda_mse | 0.55 |
| lambda_teacher | 0.10 |
| joint_scale | 0.45 |

预期：可能小幅提升 PSNR/MSE，风险是上限较低，因为只训练 joint head。

## 方案 2：G02 MA3J unfrozen low-lr continuation

Profile：`full_pastnet_g02_ma3j_unfrozen200`

风险：低到中。

思路：仍从 `full_ma3jf_150` 出发，但不冻结 backbone，用更低学习率进行全模型微调。它测试的是：MA3JF 目前是否因为冻结策略限制了 backbone 与 joint head 的协同。

关键设置：

| 项目 | 值 |
|---|---:|
| model_variant | `ma3j` |
| init | `full_ma3jf_150` best |
| epochs | 200 |
| lr | 2e-5 |
| freeze_backbone | false |
| lambda_mse | 0.45 |
| lambda_z | 0.03 |
| joint_scale | 0.35 |

预期：如果 backbone 还有可迁移余量，可能比 G01 更强；风险是过拟合 fastMRI，NingXia 泛化可能下降。

## 方案 3：G03 MA3J symmetry-restored generalization

Profile：`full_pastnet_g03_ma3j_sym200`

风险：中。

思路：MA3JF 为了 PSNR 去掉了 symmetry loss。这个方案把轻量 symmetry 和更保守 residual 重新加回来，目标不是只冲 fastMRI PSNR，而是让左右方向一致性更适合后续 IXI / NingXia 泛化。

关键设置：

| 项目 | 值 |
|---|---:|
| model_variant | `ma3j` |
| init | `full_ma3jf_150` best |
| epochs | 200 |
| lr | 2e-5 |
| lambda_sym | 0.002 |
| lambda_mse | 0.35 |
| lambda_z | 0.04 |
| joint_scale | 0.25 |

预期：PSNR 不一定最高，但若 SSIM/MAE/NCC 更稳，很适合成为泛化候选。

## 方案 4：G04 MA3C strong z-curvature consistency

Profile：`full_pastnet_g04_ma3c_z200`

风险：中。

思路：MA3C 保持单切片预测形式，但使用 interval stack 训练，把 z-curvature consistency 加强到 0.08。它测试的是：不引入 joint head 的情况下，仅靠 interval-level consistency 能否改善 MSE / NCC。

关键设置：

| 项目 | 值 |
|---|---:|
| model_variant | `ma3c` |
| init | `full_ma3_psnr_ft60` best |
| epochs | 200 |
| lr | 2e-5 |
| lambda_z | 0.08 |
| lambda_sym | 0.001 |
| lambda_mse | 0.35 |

预期：如果 hard cases 的问题来自 z-direction 不连续，这个方案会有收益；风险是 z loss 过强会拉平局部细节。

## 方案 5：G05 MA3CG soft teacher trust-region

Profile：`full_pastnet_g05_ma3cg_soft200`

风险：中。

思路：之前 MA3CG 的 guarded teacher 有潜力但容易太保守。这个版本不冻结 backbone，teacher 权重降到 0.15，只作为 trust-region 正则，不让模型完全贴住旧 MA3。

关键设置：

| 项目 | 值 |
|---|---:|
| model_variant | `ma3cg` |
| init | `full_ma3_psnr_ft60` best |
| epochs | 200 |
| lr | 1e-5 |
| freeze_backbone | false |
| lambda_teacher | 0.15 |
| lambda_z | 0.03 |

预期：比冻结式 CG 更可能走出旧模型局部最优；风险是学习率太低时收益有限。

## 方案 6：G06 MA3J strong-z interval joint model

Profile：`full_pastnet_g06_ma3j_zstrong200`

风险：中到高。

思路：从 MA3 checkpoint 初始化 joint head，而不是从 MA3JF 继续。它强化 z consistency，保留 joint three-offset 预测，让模型直接学习 interval 内三个 offset 的一致残差。

关键设置：

| 项目 | 值 |
|---|---:|
| model_variant | `ma3j` |
| init | `full_ma3_psnr_ft60` best |
| epochs | 200 |
| lr | 3e-5 |
| lambda_z | 0.08 |
| lambda_mse | 0.40 |
| joint_scale | 0.30 |

预期：比 G01/G02 更像“结构重新组织”，可能改善 MSE；风险是 joint head 学不好会拖累单切片强项。

## 方案 7：G07 MA3 wide from scratch

Profile：`full_pastnet_g07_ma3_wide200`

风险：高。

思路：MA4W 证明盲目大 window 不行，但还没证明 MA3 backbone 本身容量上限。这个方案把 MA3 扩到 base 64 / 10 blocks，从头 full 训练 200 epoch，测试 rich multi-anchor 单切片路线是否受容量限制。

关键设置：

| 项目 | 值 |
|---|---:|
| model_variant | `ma3` |
| init | none |
| epochs | 200 |
| base_channels | 64 |
| num_blocks | 10 |
| lr | 1.5e-4 |

预期：若容量是真瓶颈，会提升；风险是训练成本较大，而且从头训练可能不如 warm-start 稳。

## 方案 8：G08 MA3 deep from scratch

Profile：`full_pastnet_g08_ma3_deep200`

风险：高。

思路：与 G07 不同，这个方案保持 width 48，但把 depth 增到 14 blocks。它更偏向扩大 effective receptive field 与非线性表达，而不是增加每层通道。

关键设置：

| 项目 | 值 |
|---|---:|
| model_variant | `ma3` |
| init | none |
| epochs | 200 |
| base_channels | 48 |
| num_blocks | 14 |
| lr | 1.2e-4 |

预期：可能比 wide 更省显存，泛化也可能更稳；风险是优化更慢，200 epoch 才能看出趋势。

## 方案 9：G09 MA4W lite constrained window

Profile：`full_pastnet_g09_ma4w_lite200`

风险：高。

思路：原 MA4W 大模型失败，可能是 residual 修改太激进、window 采样太密、MSE 权重过强。这个方案做 lite window：base 64 / 8 blocks、residual_scale 0.35、window_step 2，并加强 residual regularization。

关键设置：

| 项目 | 值 |
|---|---:|
| model_variant | `ma4w` |
| init | none |
| epochs | 200 |
| base_channels | 64 |
| num_blocks | 8 |
| residual_scale | 0.35 |
| lambda_z | 0.06 |
| window_step | 2 |

预期：若 MA4W 失败原因是过拟合和过改，这个版本有机会恢复；风险是 window 模型本身可能不适合当前数据。

## 方案 10：G10 MA4W rescue strong consistency

Profile：`full_pastnet_g10_ma4w_rescue200`

风险：最高。

思路：这是 MA4W 的最后一次救援实验。相比 G09，它稍微加宽到 base 80 / 10 blocks，但 residual_scale 进一步降到 0.25，并把 z consistency 提到 0.10，强制它学习连续 interval，而不是生成式乱修。

关键设置：

| 项目 | 值 |
|---|---:|
| model_variant | `ma4w` |
| init | none |
| epochs | 200 |
| base_channels | 80 |
| num_blocks | 10 |
| residual_scale | 0.25 |
| lambda_z | 0.10 |
| window_step | 2 |

预期：如果 window-level 一次预测仍然失败，就基本可以放弃 MA4W 主线，把资源回到 MA3J / interval-level joint route。

## 推荐执行顺序

如果 GPU 可以并行，优先跑 1、2、3、6，因为它们最接近当前最强 MA3JF / MA3J 路线。其次跑 4、5，补 interval consistency 证据。7、8、9、10 属于高风险架构探索，可以和低风险组并行，但不建议把它们作为唯一主线。

推荐第一批：

```text
G01, G02, G03, G06
```

推荐第二批：

```text
G04, G05
```

高风险补充：

```text
G07, G08, G09, G10
```

## Smoke 一轮验证结果

2026-07-24 已为 10 个方案补齐对应 smoke profile，并逐个实际运行：

```text
run_all --profile smoke_pastnet_gXX_...
paper_table --profile smoke_pastnet_gXX_...
```

10 个 smoke profile 均已通过，且都生成了：

```text
summary_metrics.csv
paper_table.csv
paper_table.md
```

验证结果如下。这里的 smoke 只用于确认代码链路、模型 shape、warm-start、loss、评估和 paper table 都能跑通，不用于判断 full 方案强弱。

| Smoke profile | Method | Cases | PSNR | SSIM | 说明 |
|---|---|---:|---:|---:|---|
| `smoke_pastnet_g01_ma3jf_cal` | `pastnet_ma3j` | 1 | 23.3761 | 0.7835 | MA3JF checkpoint + frozen joint calibration 跑通 |
| `smoke_pastnet_g02_ma3j_unfrozen` | `pastnet_ma3j` | 1 | 23.3789 | 0.7832 | MA3JF checkpoint + full MA3J unfrozen 跑通 |
| `smoke_pastnet_g03_ma3j_sym` | `pastnet_ma3j` | 1 | 23.2954 | 0.7801 | MA3J + symmetry/z consistency 跑通 |
| `smoke_pastnet_g04_ma3c_z` | `pastnet_ma3c` | 1 | 23.3190 | 0.7785 | MA3C interval consistency 跑通 |
| `smoke_pastnet_g05_ma3cg_soft` | `pastnet_ma3cg` | 1 | 23.3256 | 0.7804 | MA3CG soft teacher trust-region 跑通 |
| `smoke_pastnet_g06_ma3j_zstrong` | `pastnet_ma3j` | 1 | 23.3193 | 0.7795 | MA3 -> MA3J joint head warm-start 跑通 |
| `smoke_pastnet_g07_ma3_wide` | `pastnet_ma3` | 1 | 17.6338 | 0.5255 | wide MA3 from scratch 跑通；一轮指标低是正常的 |
| `smoke_pastnet_g08_ma3_deep` | `pastnet_ma3` | 1 | 17.5750 | 0.4459 | deep MA3 from scratch 跑通；一轮指标低是正常的 |
| `smoke_pastnet_g09_ma4w_lite` | `pastnet_ma4w` | 1 | 17.5571 | 0.5241 | constrained MA4W window 跑通 |
| `smoke_pastnet_g10_ma4w_rescue` | `pastnet_ma4w` | 1 | 17.5585 | 0.5246 | MA4W rescue 跑通 |

本轮验证时还修复了一个真实 bug：MA3J teacher trust-region 若从 MA3J checkpoint 初始化，teacher 本身也是 joint interval 模型，必须接收 5D interval stack；原代码把它当单切片 teacher 喂 4D tensor，会导致维度错误。现在已在 `train.py` 中区分 MA3J teacher 和 MA3 single-slice teacher。

## 运行指令

本文档按 `！！！multiscale_x2_x6_all_baseline_commands.md` 的风格，只列可复制执行的运行入口。建议每次只跑一个 profile，跑完确认：

```text
design/fastmri_brain_pastnet_2p5d/runs/<profile>/metrics/summary_metrics.csv
design/fastmri_brain_pastnet_2p5d/runs/<profile>/metrics/paper_table.csv
design/fastmri_brain_pastnet_2p5d/runs/<profile>/metrics/paper_table.md
```

再跑下一个。

先设置环境：

```powershell
Set-Location D:\MRI
$py = 'D:\conda\envs\MRI\python.exe'
$env:PYTHONPATH = 'D:\MRI\pre;D:\MRI\baseline;D:\MRI\design;D:\MRI'

$fastmriData = 'D:\MRI\dataset\fastMRI_brain_T2\processed'
$env:FASTMRI_BRAIN_PASTNET_DATA_ROOT = $fastmriData
$env:FASTMRI_BRAIN_PASTNET_RUN_ROOT = 'D:\MRI\design\fastmri_brain_pastnet_2p5d\runs'
```

### 已验证 smoke 指令

下面 10 组 smoke 指令已经逐个跑通过。以后如果换机器、换路径或改代码，建议先跑 smoke 再跑 full-200。

```powershell
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile smoke_pastnet_g01_ma3jf_cal
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile smoke_pastnet_g01_ma3jf_cal

D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile smoke_pastnet_g02_ma3j_unfrozen
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile smoke_pastnet_g02_ma3j_unfrozen

D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile smoke_pastnet_g03_ma3j_sym
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile smoke_pastnet_g03_ma3j_sym

D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile smoke_pastnet_g04_ma3c_z
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile smoke_pastnet_g04_ma3c_z

D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile smoke_pastnet_g05_ma3cg_soft
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile smoke_pastnet_g05_ma3cg_soft

D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile smoke_pastnet_g06_ma3j_zstrong
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile smoke_pastnet_g06_ma3j_zstrong

D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile smoke_pastnet_g07_ma3_wide
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile smoke_pastnet_g07_ma3_wide

D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile smoke_pastnet_g08_ma3_deep
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile smoke_pastnet_g08_ma3_deep

D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile smoke_pastnet_g09_ma4w_lite
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile smoke_pastnet_g09_ma4w_lite

D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile smoke_pastnet_g10_ma4w_rescue
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile smoke_pastnet_g10_ma4w_rescue
```

### Full-200 指令

### G01 MA3JF calibration continuation

```powershell
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g01_ma3jf_cal200
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g01_ma3jf_cal200
```

### G02 MA3J unfrozen low-lr continuation

```powershell
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g02_ma3j_unfrozen200
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g02_ma3j_unfrozen200
```

### G03 MA3J symmetry-restored generalization

```powershell
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g03_ma3j_sym200
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g03_ma3j_sym200
```

### G04 MA3C strong z-curvature consistency

```powershell
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g04_ma3c_z200
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g04_ma3c_z200
```

### G05 MA3CG soft teacher trust-region

```powershell
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g05_ma3cg_soft200
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g05_ma3cg_soft200
```

### G06 MA3J strong-z interval joint model

```powershell
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g06_ma3j_zstrong200
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g06_ma3j_zstrong200
```

### G07 MA3 wide from scratch

```powershell
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g07_ma3_wide200
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g07_ma3_wide200
```

### G08 MA3 deep from scratch

```powershell
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g08_ma3_deep200
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g08_ma3_deep200
```

### G09 MA4W lite constrained window

```powershell
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g09_ma4w_lite200
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g09_ma4w_lite200
```

### G10 MA4W rescue strong consistency

```powershell
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g10_ma4w_rescue200
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g10_ma4w_rescue200
```
