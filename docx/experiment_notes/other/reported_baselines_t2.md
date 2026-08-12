# T2/x4 reported baseline 文献表

更新时间：2026-06-05

本文档只记录论文 reported results 和方法来源，不作为公平主表。凡是没有使用本项目同一 `T2 / x4 / split / preprocessing / metric script` 重跑的结果，都只能标注为 `reported, not directly comparable`。

## 1. 使用原则

| 原则 | 说明 |
|---|---|
| 不混主表 | reported results 不直接放入 `experiment_master_table.md` 的公平比较区 |
| 先记 protocol | 摘数值前必须先记录 dataset、modality、scale、split、normalization、metric definition |
| 优先找代码 | 能复现的优先复现；不能复现的只放 reported-baseline 表 |
| 区分任务 | 2D SR、video interpolation、3D volumetric SR、medical slice synthesis 不能硬写成同任务公平对比 |
| 保留来源 | 每个条目必须有 paper / code / PDF 来源链接 |

## 2. 待摘录条目

| Method | 任务类型 | Source | Code | reported result 是否可直接比较 | 当前动作 |
|---|---|---|---|---|---|
| SAINT | medical slice synthesis | https://openaccess.thecvf.com/content_CVPR_2020/html/Peng_SAINT_Spatially_Aware_Interpolation_NeTwork_for_Medical_Slice_Synthesis_CVPR_2020_paper.html | 待核对 | 否，需核对数据集和 split | 记录原文 protocol；补清本地 style reproduction 差异 |
| I3Net | medical slice synthesis | 本地 PDF：`docx/experiment_notes/reading/I3net.pdf` | 待核对 | 否，除非同学复现口径一致 | 跟进同学 IXI 复现 |
| ArSSR | 3D MRI arbitrary-scale SR / INR | https://arxiv.org/abs/2110.14476 | https://github.com/iwuqing/ArSSR | 否，需本地重跑 | 优先做 IXI-T2 smoke/mini |
| CycleINR | volumetric medical SR / INR | https://openaccess.thecvf.com/content/CVPR2024/html/Fang_CycleINR_Cycle_Implicit_Neural_Representation_for_Arbitrary-Scale_Volumetric_Super-Resolution_of_CVPR_2024_paper.html | 待核对 | 否，需本地重跑 | 优先做方法阅读和代码可用性检查 |
| Zero-X21 | anisotropic MRI inter-slice INR | https://www.sciencedirect.com/science/article/pii/S0167865525002296 | 待核对 | 否 | 先做文献定位，暂缓复现 |
| SwinIR | 2D image restoration / SR | https://arxiv.org/abs/2108.10257 | https://github.com/JingyunLiang/SwinIR | 否，任务不同 | 作为 P2 通用 SR 对照 |
| HAT | 2D image SR Transformer | https://arxiv.org/abs/2205.04437 | https://github.com/XPixelGroup/HAT | 否，任务不同 | SwinIR 跑通后再考虑 |
| RSTT | space-time video SR | https://openaccess.thecvf.com/content/CVPR2022/html/Geng_RSTT_Real-Time_Spatial_Temporal_Transformer_for_Space-Time_Video_Super-Resolution_CVPR_2022_paper.html | 待核对 | 否，任务不同 | 暂缓，只做跨领域方法讨论 |

## 3. 摘录模板

后续每篇论文摘数值时使用下面模板，避免只抄 PSNR/SSIM 而丢掉口径。

| Field | Value |
|---|---|
| Method |  |
| Paper title |  |
| Year / venue |  |
| Dataset |  |
| Modality |  |
| Scale |  |
| Direction |  |
| Train/val/test split |  |
| Input form |  |
| Output form |  |
| Metrics |  |
| Reported PSNR |  |
| Reported SSIM |  |
| Other reported metrics |  |
| Code available |  |
| Directly comparable to our table | No |
| Notes |  |

## 4. 当前判断

reported-baseline 表的作用是帮助决定复现顺序和论文 related work 叙事，不负责证明本地方法优于某篇论文。真正的公平比较必须来自本地统一重跑。
