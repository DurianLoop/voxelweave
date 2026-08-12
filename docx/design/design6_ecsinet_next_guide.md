# Design 6 下一步引导：ECSI-Net 高效临床插值路线

更新时间：2026-07-06

本文档是在 `design6_ecsinet_efficiency.md` 和当前 `ixi_ecsinet_2p5d/` 第一阶段代码实现之后的下一步执行指南。ECSI 路线的重点不是马上追最高 PSNR，而是证明它在质量、速度、显存、参数量之间具有更好的 Pareto trade-off。

## 1. 当前状态

已看到的第一步产物：

```text
ixi_ecsinet_2p5d/
  model.py
  train.py
  run_all.py
  paper_table.py
  settings.py
  README.md
```

README 中已经明确：

```text
ECSI-Net 使用 linear coarse interpolation 作为 base prediction，
再由 change-aware mask 控制 lightweight residual correction。
```

这说明第一阶段结构已经对齐 design6 的核心思想。

当前缺的不是再写一个大模型，而是：

```text
效率测量体系 + 最小可用训练结果 + Pareto 表格
```

## 2. 下一阶段总目标

ECSI 接下来要回答：

1. 它到底比 HAT/SMamba/I3Net 快多少；
2. 它到底省多少显存；
3. 它在接近多少质量的情况下实现效率优势；
4. change-aware mask 是否真的减少无效修正；
5. 它能否成为论文里的 efficient clinical interpolation model。

## 3. P1：先做速度和显存 profile

不要先跑 full。先 profile。

### 3.1 必测配置

在 IXI smoke 上测：

| 配置 | channels | blocks | batch |
|---|---:|---:|---:|
| tiny | 32 | 6 | 16/32/64 |
| base | 48 | 8 | 8/16/32 |
| plus | 64 | 10 | 4/8/16 |

记录：

- peak VRAM；
- it/s；
- sec/epoch；
- samples/s；
- train batch max；
- inference ms/slice；
- inference sec/case。

### 3.2 P1 输出文件

建议输出：

```text
ixi_ecsinet_2p5d/runs/profile/
  efficiency_profile.csv
  memory_profile.csv
  inference_profile.csv
  profile_summary.md
```

### 3.3 P1 验收标准

ECSI 要有论文价值，至少要满足：

| 指标 | 最低要求 |
|---|---|
| peak VRAM | 明显低于 HAT/SMamba |
| inference sec/case | 明显低于 HAT/SMamba |
| train it/s | 明显高于 HAT/SMamba |
| batch capacity | 同显存下能用更大 batch |

如果速度没有优势，ECSI 方向就要先优化代码，而不是扩实验。

## 4. P2：跑 IXI smoke/mini 质量验证

profile 通过后再跑质量。

### 4.1 smoke 目标

smoke 只验证：

- 不 NaN；
- prediction 正常；
- mask 不全 0；
- mask 不全 1；
- residual 不爆；
- linear coarse 作为 base 生效。

### 4.2 mini 目标

IXI mini 至少和 Linear/Cubic 比：

| 对比 | 目标 |
|---|---|
| ECSI vs Linear | PSNR/SSIM/NCC 更高，MAE/MSE 更低 |
| ECSI vs Cubic | 全面更好 |
| mask | 结构变化区域更高，背景更低 |
| residual | 不出现大面积伪影 |

mini 输出：

```text
summary_metrics.csv
paper_table.md
mask_statistics.csv
residual_statistics.csv
visual_qc/
```

## 5. P3：建立 efficiency-quality Pareto 表

ECSI 的关键论文图不是单独主表，而是 Pareto。

### 5.1 对比方法

至少包括：

```text
Linear
Cubic
ResUNet
SwinIR
HAT
SMamba
I3Net
ECSI-Tiny
ECSI-Base
```

如果暂时没有所有方法的效率数据，先从已有日志整理：

- train sec/epoch；
- batch；
- peak VRAM；
- total runtime；
- inference time。

### 5.2 表格字段

建议：

| Method | Params | Peak VRAM | Batch | sec/epoch | ms/slice | sec/case | PSNR | SSIM | NCC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|

### 5.3 Pareto 图

至少画两张：

```text
PSNR vs sec/case
PSNR vs peak VRAM
```

如果 ECSI 位于 Pareto frontier，就有清晰论文价值。

## 6. P4：change-aware mask 解释性分析

ECSI 不能只说快，还要说明为什么合理。

### 6.1 mask 统计

保存：

- mask mean；
- mask std；
- mask foreground mean；
- mask background mean；
- mask high-change region mean；
- mask low-change region mean。

### 6.2 mask 与 error/residual 的关系

计算：

```text
corr(mask, |target - linear|)
corr(mask, |prediction - linear|)
corr(mask, image gradient)
```

理想结果：

- mask 在需要修正的区域更高；
- 背景区域更低；
- mask 与 `|target-linear|` 有正相关。

这可以支撑：

```text
ECSI avoids unnecessary computation/correction in easy regions.
```

## 7. P5：扩展策略

ECSI 扩三数据集时按这个顺序：

```text
IXI mini
IXI full_test115
fastMRI full
NingXia CV
```

但在 x2/x6 训练正在跑的时候，不建议开大训练。可以先做：

```text
profile + IXI mini + efficiency table
```

等 GPU 空出来再跑 full。

## 8. 论文主张应该怎么写

ECSI 的主张不是：

```text
我们一定最高 PSNR。
```

更稳的是：

```text
ECSI achieves a better quality-efficiency trade-off for clinical through-plane interpolation.
```

中文：

```text
ECSI 在保持接近第一梯队重建质量的同时，显著降低显存、训练时间和推理时间。
```

如果 NingXia 上也稳，可以补：

```text
轻量 change-aware residual correction 在外部临床数据上更稳健。
```

## 9. 当前最具体的下一步

按顺序做：

1. 在 `ixi_ecsinet_2p5d/train.py` 或 `run_all.py` 中加入 profiling 输出；
2. 跑 smoke profile，不跑 full；
3. 生成 `efficiency_profile.csv`；
4. 跑 IXI mini；
5. 输出 `mask_statistics.csv` 和 `residual_statistics.csv`；
6. 和 Linear/Cubic/ResUNet 的质量和速度对比；
7. 再纳入 HAT/SMamba/I3Net 的日志速度；
8. 形成第一版 Pareto 表。

## 10. 不要做的事

暂时不要：

- 一上来跑 full_test115；
- 不测速度只报质量；
- 不保存 mask/residual 统计；
- 和 HAT/SMamba 比质量但不比资源；
- 让 ECSI 变成另一个重模型。

## 11. 阶段性结论

ECSI 当前最值得做的是效率证据链，而不是盲目扩 full。只要它在 IXI mini 上超过 Linear/Cubic，同时在显存、速度、batch capacity 上明显优于重模型，就已经有资格成为论文里的 efficient branch。后续是否扩三数据集，取决于 Pareto 表是否漂亮。

