# 自研模型设计总览表

更新时间：2026-07-06

本文档汇总 `docx/design/` 下 6 个自研方向，重点回答三个问题：

1. 每个方向能不能单独支撑一篇论文；
2. 是否需要训练新模型，以及计算资源占用大不大；
3. 哪些方向可以优先做，不妨碍当前 x2 / x6 训练。

## 1. 总体判断

这 6 个 design 理论上都可以单独发展成论文，但成熟度和资源成本不一样。

更准确地说：

| Design | 能否单独成文 | 判断 |
|---|---|---|
| Design 1 PAST-Net | 可以 | 标准“新模型冲 SOTA”论文，最像主模型论文 |
| Design 2 FAST-Net | 可以 | 高效轻量模型论文，适合做 efficiency-quality trade-off |
| Design 3 RASI-Net | 很可以 | 可信医学 AI / uncertainty 方向，顶刊认可度高 |
| Design 4 SCPI-Net | 很可以 | 连续尺度 / 任意倍率插值，问题定义更有新意 |
| Design 5 ACSI-Net | 很可以 | 解剖一致性 / 3D coherence，医学影像顶刊友好 |
| Design 6 ECSI-Net | 可以 | 临床高效部署 / Pareto frontier，适合应用导向论文 |

其中最有“另辟蹊径”潜力的是：

```text
Design 3 RASI-Net
Design 4 SCPI-Net
Design 5 ACSI-Net
```

最适合不影响当前 x2 / x6 训练、马上推进的是：

```text
Design 5 ACSI-Net 的评价分析版
Design 6 ECSI-Net 的效率分析版
Design 3 RASI-Net 的 post-hoc uncertainty 版
```

## 2. 文件命名

| 编号 | 新文件名 | 方向 |
|---|---|---|
| Design 1 | `design1_pastnet_sota.md` | PAST-Net，phase-aware structure transfer，冲三数据集 SOTA |
| Design 2 | `design2_fastnet_efficient_sota.md` | FAST-Net，轻量高效，尽量接近 SOTA |
| Design 3 | `design3_rasinet_reliability.md` | RASI-Net，可信不确定性感知插值 |
| Design 4 | `design4_scpinet_scale_continuous.md` | SCPI-Net，连续尺度 / 任意 phase 插值 |
| Design 5 | `design5_acsinet_anatomy_consistency.md` | ACSI-Net，解剖一致性 / 3D coherence |
| Design 6 | `design6_ecsinet_efficiency.md` | ECSI-Net，高效临床插值 / Pareto frontier |

## 3. 是否需要训练与资源优先级

| 优先级 | Design | 先做版本 | 是否需要训练新模型 | 计算资源 | 是否影响 x2/x6 训练 | 近期建议 |
|---|---|---|---|---|---|---|
| P0 | Design 5 ACSI-Net | 3D consistency 评价版 | 否 | 很低 | 几乎不影响 | 先基于已有预测结果做 z-gradient、z-Laplacian、inter-slice NCC、sagittal/coronal QC |
| P0 | Design 6 ECSI-Net | 效率 / Pareto 分析版 | 否 | 很低 | 几乎不影响 | 先整理参数量、显存、训练时间、推理时间、sec/case，画 quality-efficiency 表 |
| P1 | Design 3 RASI-Net | post-hoc uncertainty 版 | 否或只需少量推理 | 低 | 基本不影响 | 用 residual、TTA variance、baseline disagreement 做 uncertainty proxy |
| P2 | Design 2 FAST-Net | Tiny / Base 轻量训练版 | 是 | 低到中 | 会占 GPU，但可控 | x2/x6 间隙或夜间跑 IXI smoke/mini |
| P3 | Design 1 PAST-Net | 主模型训练版 | 是 | 中到高 | 会明显占 GPU | 等当前多倍率 baseline 稳定后再开 |
| P4 | Design 4 SCPI-Net | 多尺度联合训练版 | 是 | 高 | 会和 x2/x6 强相关 | 等 x2/x4/x6 数据与 baseline 跑完整后再做 |

## 4. 每个方向的单篇论文潜力

| Design | 单篇论文主题 | 顶会/顶刊认可点 | 最关键实验 | 风险 |
|---|---|---|---|---|
| Design 1 PAST-Net | 面向 T2 through-plane interpolation 的 phase-aware structure transfer 主模型 | 任务专用结构，三数据集 SOTA，x2/x4/x6 大表 | 三数据集主表、消融、visual QC | 需要训练资源，必须真赢强 baseline |
| Design 2 FAST-Net | 高效轻量 T2 层间插值模型 | 接近 SOTA 且显存/速度明显优 | efficiency table、Pareto curve、三数据集指标 | 如果指标太低，只能做辅助模型 |
| Design 3 RASI-Net | 可信不确定性感知医学层间插值 | 不只预测图像，还能提示错误风险 | error-uncertainty correlation、risk-coverage、failure detection | uncertainty 可能学成常数，需要校准 |
| Design 4 SCPI-Net | 连续尺度 MRI slice interpolation | 一个模型统一 x2/x4/x6，甚至 unseen scale | multi-scale joint training、cross-scale generalization | 训练成本高，多尺度混训可能互相拖累 |
| Design 5 ACSI-Net | 解剖一致性 3D volume interpolation | 从 2D slice 指标提升到 3D anatomy coherence | z-gradient、z-Laplacian、sagittal/coronal QC、downstream stability | 主表 PSNR 未必第一，需要讲清 3D 价值 |
| Design 6 ECSI-Net | 临床高效层间插值与部署友好模型 | 质量-效率 Pareto frontier，临床批量处理友好 | 参数量、显存、sec/case、吞吐、NingXia 稳定性 | 如果速度优势不明显，贡献会变弱 |

## 5. 不训练或少训练的可立即推进任务

| 任务 | 来源 design | 是否训练 | 需要已有结果 | 输出物 |
|---|---|---|---|---|
| 3D z-axis consistency analysis | Design 5 | 否 | 需要 prediction 或重新推理 | `z_gradient_error.csv`, `z_laplacian_error.csv`, sagittal/coronal QC |
| Efficiency audit | Design 6 | 否 | 训练日志和少量测速 | `efficiency_table.md`, Pareto plot |
| Post-hoc uncertainty analysis | Design 3 | 否或少量推理 | prediction/coarse/target | risk-coverage curve, uncertainty-error correlation |
| Failure case ranking | Design 3/5 | 否 | case-level metrics | worst-case list, visual QC |
| Per-offset consistency analysis | Design 4/5 | 否 | x2/x4/x6 或 x4 per-offset results | per-phase/per-offset table |

## 6. 当前最推荐执行顺序

在不打断 x2 / x6 训练的前提下，建议顺序：

```text
1. Design 5 ACSI-Net 评价版
2. Design 6 ECSI-Net 效率分析版
3. Design 3 RASI-Net post-hoc uncertainty 版
4. Design 2 FAST-Net Tiny smoke
5. Design 1 PAST-Net 主模型
6. Design 4 SCPI-Net 多尺度统一模型
```

原因：

1. 前三项基本不需要训练新模型；
2. 可以立刻增强论文深度；
3. 不占用当前 x2/x6 baseline 的 GPU；
4. 先得到分析结果后，反过来能指导真正新模型怎么设计；
5. 等多倍率结果完整后，再做 SCPI-Net 会更稳。

## 7. 论文层面的组合策略

如果最后只做一篇大论文，可以把方向组合成：

```text
主模型：PAST-Net 或 FAST-Net
可信性：RASI analysis
连续尺度：SCPI extension
解剖一致性：ACSI evaluation
效率：ECSI Pareto analysis
```

如果拆成多篇论文，推荐拆法：

| 论文 | 主线 |
|---|---|
| Paper A | PAST-Net / FAST-Net：新模型与三数据集 SOTA |
| Paper B | RASI-Net：可信不确定性感知医学插值 |
| Paper C | SCPI-Net：连续尺度 x2/x4/x6 统一插值 |
| Paper D | ACSI-Net：解剖一致性和 3D volume coherence |
| Paper E | ECSI-Net：高效临床部署和 Pareto frontier |

实际执行时，不建议同时开太多训练型论文。更稳的做法是先用低成本分析型方向扩大论文深度，再决定哪个模型方向值得投入 GPU。

