# Design 3 下一步引导：RASI-Net 可信不确定性感知路线

更新时间：2026-07-06

本文档是在 `design3_rasinet_reliability.md` 和当前第一步代码实现之后的下一阶段执行指南。当前 `rasinet/` 已经完成了 smoke 级别的 prediction、confidence、uncertainty、calibration bins、risk-coverage 和 reliability summary 输出，因此接下来不应该马上扩大训练，而应该先判断“可信性分析是否真的成立”。

## 1. 当前状态

已看到的第一步产物：

```text
rasinet/
  model.py
  losses.py
  metrics.py
  train.py
  run_all.py
  paper_table.py
  runs/smoke/
    model_outputs/
    reliability_outputs/
      residual/
      confidence/
      uncertainty/
    metrics/
      summary_metrics.csv
      summary_reliability.csv
      risk_coverage.csv
      calibration_bins.csv
      per_case_reliability.csv
```

当前 smoke 结果只覆盖 1 个 IXI case，因此它的作用不是证明模型强，而是检查 pipeline 是否能跑通。

目前最重要的信号：

| 指标 | 当前 smoke 观察 | 解释 |
|---|---:|---|
| rasinet PSNR | 26.5408 | 低于 linear 27.4291，说明 reconstruction 还不能作为主模型 |
| pixel error-uncertainty corr | 0.0017 | 几乎没有相关性，uncertainty 还没学到可靠风险 |
| slice error-uncertainty corr | -0.0959 | 单 case 下不稳定，不能下结论 |
| edge error-uncertainty corr | 0.0139 | 边界风险捕捉还很弱 |
| retained MAE at 50% low uncertainty | 21.0002 | 低 uncertainty 区域 MAE 下降，但 risk-coverage 不够单调 |

结论：

```text
RASI-Net 第一阶段代码已跑通，但还没有证明 uncertainty 是可信的。
下一步重点不是扩大 full training，而是先让 uncertainty/correlation/risk-coverage 成立。
```

## 2. 下一阶段总目标

RASI 路线下一步要回答三个问题：

1. uncertainty map 是否和真实 error 有正相关；
2. 低 uncertainty 区域是否确实更可靠；
3. case-level uncertainty 是否能发现失败 case。

如果这三个问题回答不了，RASI-Net 就只是“多输出了一张图”，论文价值不成立。

## 3. P1：不训练或少训练的可靠性验证

优先不要开大训练。先基于已有 baseline prediction 做 post-hoc uncertainty，资源占用很低。

### 3.1 建立三个 uncertainty proxy

建议先实现三个不依赖新训练的 uncertainty proxy：

#### Proxy A：Residual magnitude

```text
U_res = |Y_pred - Y_linear|
```

含义：

- 模型越偏离 linear，说明它做了更强修正；
- 强修正区域可能风险更高；
- 适合所有已有 baseline。

#### Proxy B：Baseline disagreement

用多个已有方法的预测差异：

```text
U_disagree = std([Y_linear, Y_cubic, Y_swinir, Y_hat, Y_i3net, ...])
```

如果部分方法没有保存 prediction，可以先只做：

```text
linear / cubic / rasinet / acsinet
```

后续再补 I3Net/HAT/SwinIR。

#### Proxy C：TTA variance

对同一输入做轻量 test-time augmentation：

```text
identity
flip_lr
flip_ud
flip_lr_ud
```

还原后计算方差：

```text
U_tta = variance(predictions)
```

这需要少量额外推理，但不需要训练。

### 3.2 P1 最小输出

P1 至少输出：

```text
rasinet/runs/posthoc_uncertainty/
  metrics/
    uncertainty_proxy_summary.csv
    risk_coverage_by_proxy.csv
    calibration_by_proxy.csv
    failure_detection_by_proxy.csv
  visual_qc/
    case_xxx_error_uncertainty_overlay.png
```

### 3.3 P1 验收标准

优先看这几个指标：

| 指标 | 合格 | 强 |
|---|---:|---:|
| pixel error-uncertainty corr | > 0.10 | > 0.25 |
| edge error-uncertainty corr | > 0.15 | > 0.30 |
| risk-coverage retained MAE at 50% | 低于全图 MAE 20% | 低于全图 MAE 35% |
| failure detection AUROC | > 0.65 | > 0.80 |

注意：单 case 不看 AUROC，至少要 mini 5 cases，最好 full_test115。

## 4. P2：RASI-Net 小规模校准训练

如果 post-hoc proxy 有价值，再回头训练 RASI-Net uncertainty head。

### 4.1 两阶段训练

不要一开始就重训整个模型。

推荐：

```text
Stage A: freeze reconstruction backbone, train uncertainty/confidence heads
Stage B: unfreeze last few blocks, small lr finetune
```

这样资源占用低，也能避免 reconstruction 指标继续掉。

### 4.2 修改训练目标

当前 smoke 中 uncertainty 相关性几乎为 0，说明 loss 可能还没有逼它学习 error。

建议增强 calibration loss：

```text
E = normalize(|Y - Y_hat|)
U = normalize(U_map)
L_cal = L1(U, stopgrad(E))
```

总损失建议：

```text
L_total =
    L_rec
  + 0.2 * L_unc
  + 0.10 * L_cal
  + 0.05 * L_grad
  + 0.001 * L_res
```

如果 reconstruction 掉太多：

```text
先固定 Y_hat，只训练 U_map
```

## 5. P3：扩到三数据集的低成本分析

RASI 不需要每个数据集都先训练新模型，可以先做 post-hoc。

推荐顺序：

```text
IXI full_test115 prediction cache
fastMRI full prediction cache
NingXia 8-fold prediction cache
```

优先使用已有 baseline 输出。如果没有输出，只跑推理，不重训。

三数据集都要报告：

- error-uncertainty correlation；
- risk-coverage curve；
- failure case detection；
- edge-region reliability；
- case-level uncertainty ranking。

## 6. 论文主张应该怎么转

RASI 路线不要主张：

```text
我们的 RASI-Net 指标最高
```

除非后面真的赢了。

更好的主张：

```text
现有 interpolation 方法只报告平均重建质量，而 RASI 提供 failure-aware 和 region-aware 的可信风险估计。
```

低成本版也能成立：

```text
We provide a reliability evaluation framework and show that uncertainty proxies can detect interpolation failures under domain shift.
```

如果后续 RASI-Net 训练后指标也强，再升级为完整模型论文。

## 7. 当前最具体的下一步

按优先级做：

1. 在 `rasinet/metrics.py` 中统一 proxy 接口：`residual`, `disagreement`, `tta`；
2. 用 IXI mini 5 cases 跑 post-hoc uncertainty；
3. 输出 `risk_coverage_by_proxy.csv`；
4. 画每个 proxy 的 risk-coverage 曲线；
5. 对比 proxy 与 RASI-Net learned uncertainty；
6. 如果 post-hoc proxy 都不相关，先不要扩 full；
7. 如果 residual/disagreement 有明显相关性，再做 IXI full_test115；
8. 最后扩 fastMRI 和 NingXia。

## 8. 不要做的事

暂时不要：

- 直接 full 训练 RASI-Net；
- 把 RASI-Net 当前 smoke 指标放进主表；
- 只展示 uncertainty map，不做 correlation；
- 只看一个 case；
- 用 uncertainty 讲临床可信性但没有 failure detection。

## 9. 阶段性结论

RASI-Net 目前最应该做成“可信性分析框架”，而不是立刻变成主模型。只要能够证明 uncertainty/proxy 与真实错误、失败 case、边界风险有稳定关系，这条线即使不大量训练，也有很强论文增值。

