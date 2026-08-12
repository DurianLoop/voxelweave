# T2/x4 published baseline 决策表

更新时间：2026-06-05

本文档用于承接当前主线：只看 `T2`、`x4`、through-plane interpolation。现有主表已经包含 `Linear / Cubic / ResUNet residual / SAINT-style`，下一步不是马上造新方法，而是把 published baselines 的复现优先级、引用边界和落表口径先固定下来。

## 1. 当前事实

| 项目 | 当前结论 |
|---|---|
| 主表数据集 | `IXI-T2 test n=25`、`fastMRI-brain-T2 expanded test n=24`、`NingXia-T2 case-level CV 8 folds` |
| 主表指标 | `PSNR / SSIM / MAE / MSE / NCC` |
| 当前最强 baseline | `SAINT-style` 在三个 T2/x4 数据集上均为当前最优 |
| 必须保留 baseline | `Linear / Cubic`，用于判断传统插值下限和数据集难度 |
| internal baseline | `ResUNet residual`，只能写作 internal CNN residual baseline |
| NingXia 口径 | 优先报告 8-fold 病例级 CV mean/std，不再优先报告旧的单 test case |
| OAI-ZIB 口径 | 当前本地数据是 `0..7` label-like structural data，不进入 MRI intensity 主表 |

## 2. baseline 队列

| Priority | Method | 类型 | 当前建议 | 原因 |
|---|---|---|---|---|
| P0 | I3Net | medical slice synthesis | 跟进同学复现；若 split/预处理一致，优先进统一重跑表 | 与 through-plane slice interpolation 最贴近，论文表格口径也最值得对齐 |
| P0 | SAINT / SAINT-style | medical slice synthesis | 已有 style baseline；下一步补清和原 SAINT 的差异 | 当前最强本地 baseline，也是后续所有方法的参照 |
| P1 | ArSSR | 3D MRI arbitrary-scale INR | 已完成 IXI-T2、fastMRI-brain-T2 expanded 与 NingXia-T2 8-fold CV | 医学 3D MRI、任意尺度、代码公开，适合作为 INR baseline |
| P1 | CycleINR | volumetric medical INR | 已完成 IXI-T2 smoke/mini；mini 与 Linear 几乎持平，暂不扩 fastMRI | CVPR 2024，任意尺度体数据 SR，适合支撑层间连续性叙事 |
| P1 | Zero-X21 | anisotropic MRI inter-slice INR | 先做文献引用和方法定位，暂缓复现 | 2025 方法很贴近各向异性 MRI 层间插值，但代码和实现成本需核对 |
| P2 | SwinIR | 2D Transformer SR | 作为通用 SR 强 baseline，可先跑 2.5D/逐切片版本 | 官方代码成熟，但不是医学 through-plane 专用方法 |
| P2 | HAT | 2D Transformer SR | SwinIR 跑通后再考虑 | 通用 SR 很强但更重，优先级低于医学/INR 方法 |
| P3 | RSTT | video space-time SR | 暂缓，只作跨领域对照 | 任务形式接近相邻帧插值/时空 SR，但迁移到 MRI 需要额外适配 |
| P3 | diffusion variants | diffusion MRI SR | 暂缓系统复现 | 已有 HiFiDiff 尝试显示当前 strict diffusion 不稳，先不把训练资源压到扩散 |

## 3. 复现优先级判断

第一梯队应该是医学 slice/volume 方法：`I3Net / SAINT / ArSSR / CycleINR`。这组最能回答“我们的 T2/x4 层间插值结果是否超过医学图像领域已有强 baseline”。

第二梯队才是通用图像/视频方法：`SwinIR / HAT / RSTT`。它们适合作为“自然图像 SR 或视频时空方法迁移到医学 slice interpolation 是否足够”的对照，但不应抢在医学 baseline 前面。

扩散路线短期不建议作为主投入。已有 strict HiFiDiff 尝试出现强度偏亮和分布不稳定，后续如果重启，应先作为 refinement 或 residual correction，而不是从纯噪声生成完整中间 MRI。

## 4. 统一落表规则

| 情况 | 表格位置 | Source 写法 |
|---|---|---|
| 使用同一数据、同一 split、同一 x4、同一指标脚本重跑 | `experiment_master_table.md` | `ours rerun` 或 `ours reproduction` |
| 论文 reported result，数据集或 split 不一致 | 单独 reported-baseline 文献表 | `reported, not directly comparable` |
| 同学复现但预处理一致 | 统一重跑表，可标注 collaborator | `collaborator rerun` |
| 同学复现但 split/归一化不一致 | 单独备注表，不进入公平主表 | `rerun, protocol differs` |
| 内部工程 baseline | 主表可保留，但不能冒充 published method | `ours internal baseline` |

## 5. 下一个 7 天执行顺序

1. 和同学确认 `I3Net` 的 `IXI-T2 / x4 / split seed3407 / normalization / metric script` 是否一致。
2. 建一个 `reported_baselines_t2.md`，只摘论文原始 reported results，明确标注不可和本地结果直接公平比较。
3. `CycleINR-style` 已完成 `IXI-T2` smoke/mini；由于 mini 没有稳定超过 Linear，暂不投入 fastMRI/full 扩展，除非后续调整实现或训练口径。
4. 如果 INR mini 能稳定超过 Linear/Cubic，再扩到 `fastMRI-brain-T2 expanded`；NingXia 先只做推理/小规模验证。
5. 对当前 `SAINT-style` 补一段方法说明：它是 style reproduction，不是逐细节官方复现。
6. 开始补 `Params / inference time / GPU memory` 的统一脚本，但先只跑现有四个方法，避免指标框架空转。
7. visual QC 优先看 fastMRI 和 NingXia：确认 SAINT-style 的指标提升是否对应真实结构和边界改善。

## 6. 文献来源记录

| Method | 主要来源 | 本项目用途 |
|---|---|---|
| SAINT | Peng et al., CVPR 2020, `SAINT: Spatially Aware Interpolation NeTwork for Medical Slice Synthesis` | 已有 style baseline；需注明不是官方逐细节复现 |
| I3Net | Song et al., IEEE TMI 2024, `I3Net: Inter-Intra-slice Interpolation Network for Medical Slice Synthesis` | 最重要的 published medical slice synthesis baseline |
| ArSSR | Wu et al., `An Arbitrary Scale Super-Resolution Approach for 3D MR Images via Implicit Neural Representation` | 医学 3D MRI INR baseline |
| CycleINR | Fang et al., CVPR 2024, `CycleINR: Cycle Implicit Neural Representation for Arbitrary-Scale Volumetric Super-Resolution of Medical Data` | 任意尺度体数据 SR 与层间连续性对照 |
| Zero-X21 | Pattern Recognition Letters 2025, `Scale-agnostic image feature conditioned INR for multi-modal and multi-planar anisotropic MRI inter-slice interpolation` | 高相关 INR 文献，先引用和分析 |
| SwinIR | Liang et al., `Image Restoration Using Swin Transformer` | 通用 Transformer SR baseline |
| HAT | Chen et al., `Activating More Pixels in Image Super-Resolution Transformer` / HAT | 更强但更重的通用 Transformer SR baseline |
| RSTT | Geng et al., CVPR 2022, `Real-time Spatial Temporal Transformer for Space-Time Video Super-Resolution` | 视频时空方法迁移对照，暂缓 |

## 7. 当前推荐一句话

短期路线建议写成：先用 `I3Net / SAINT / ArSSR / CycleINR` 补齐医学层间插值与体数据 SR 的强 baseline，再用 `SwinIR / HAT / RSTT` 证明通用 SR/视频方法迁移的边界；在这之前不要急着把创新点固定到某个复杂模型上。
## 8. 2026-06-10 CycleINR full update

`CycleINR-style` IXI-T2/full completed: PSNR 26.1120 / SSIM 0.8587 / MAE 34.6777 / MSE 7643.8680 / NCC 0.9318. It consistently beats Cubic, but it does not stably beat Linear. Per-case wins against Linear are PSNR 11/25, SSIM 5/25, MAE 24/25, MSE 11/25, NCC 18/25. Current decision: keep CycleINR-style as a checked but non-priority INR baseline, and do not expand it to fastMRI or NingXia unless the implementation or objective is changed.

## 9. 2026-06-12 SwinIR 2.5D full update

`SwinIR-style 2.5D` IXI-T2/full completed: PSNR 28.7582 / SSIM 0.9060 / MAE 25.6723 / MSE 4585.3369 / NCC 0.9618. It beats Linear and Cubic on all 25/25 cases and all five main metrics. It also beats ResUNet residual, ArSSR-style, and CycleINR-style almost completely in paired per-case comparison.

Compared with SAINT-style, SwinIR-style 2.5D is extremely close but not uniformly better: SAINT remains slightly better on PSNR / MSE / NCC, while SwinIR-style 2.5D is better on SSIM / MAE. Current decision: promote SwinIR-style 2.5D to a first-tier IXI baseline and expand it to fastMRI-brain-T2 expanded next. NingXia 8-fold CV should wait until fastMRI confirms cross-dataset robustness.

## 10. 2026-06-15 SwinIR 2.5D fastMRI-brain-T2 expanded update

`SwinIR-style 2.5D` fastMRI-brain-T2 expanded/full completed on the project x4 protocol, test n=24: PSNR 22.3615 / SSIM 0.7455 / MAE 52.0221 / MSE 11591.7882 / NCC 0.8974. It beats Linear and Cubic on all 24/24 paired test cases and all five main metrics.

Against `ResUNet residual`, SwinIR is slightly stronger but not by a large margin: PSNR wins 17/24, SSIM 23/24, MAE 24/24, MSE 16/24, NCC 14/24. Mean deltas are PSNR +0.1066, SSIM +0.0081, MAE -1.5484, MSE -251.0265, NCC +0.0019.

Against `SAINT-style`, SwinIR does not win on fastMRI: SAINT wins all 24/24 cases on PSNR / SSIM / MAE / MSE / NCC. Current decision: SwinIR-style 2.5D is now a strong general Transformer SR baseline, clearly above ArSSR and ResUNet on fastMRI overall, but SAINT-style remains the strongest T2/x4 baseline. Next step should be SwinIR-style 2.5D NingXia 8-fold CV for three-dataset completeness, followed by method analysis of why SAINT's spatially aware conditioning is more robust on fastMRI.

## 11. 2026-06-15 SwinIR 2.5D NingXia-T2 8-fold CV update

`SwinIR-style 2.5D` NingXia-T2 case-level 8-fold CV completed on the project x4 protocol: PSNR 23.9513 / SSIM 0.7525 / MAE 85.9679 / MSE 32030.5455 / NCC 0.8930. This is the best current mean result on NingXia across all five main metrics.

Against `ArSSR-style` and `ResUNet residual`, SwinIR wins all 8/8 folds on PSNR / SSIM / MAE / MSE / NCC. Against `SAINT-style`, SwinIR is better in mean but not uniformly per fold: PSNR 5/8, SSIM 8/8, MAE 7/8, MSE 5/8, NCC 6/8.

Current decision: SwinIR-style 2.5D is complete across IXI-T2, fastMRI-brain-T2 expanded, and NingXia-T2 8-fold CV. It should be treated as a first-tier baseline together with SAINT-style. SAINT-style remains clearly strongest on fastMRI; SwinIR-style 2.5D is strongest on NingXia mean metrics and remains very close to SAINT on IXI.

## 12. 2026-06-16 SAINT vs SwinIR visual QC and efficiency update

Visual QC completed for `fastMRI-brain-T2 expanded` and `NingXia-T2 case-level CV`. Representative panels are saved under `docx/experiment_notes/visual_qc/saint_vs_swinir`. The visual trend mostly matches the metrics: on fastMRI, SAINT's advantage is visible around ventricles, sulci, and high-contrast outer boundaries; on NingXia, SwinIR's mean advantage is visible in some local contour and bright-structure preservation, but the advantage is not uniform across all cases.

Efficiency profiling completed under the same forward-only 256x256 generated-slice protocol. SAINT-style has 1.1973M parameters, 35.7606 estimated FLOPs(G), 3.0969 ms forward time, and 117.30 MB CUDA peak allocation. SwinIR-style 2.5D has 0.2239M parameters, 28.3682 estimated FLOPs(G), 4.2980 ms forward time, and 251.23 MB CUDA peak allocation. FLOPs for SwinIR are conservative because attention matmul/softmax/normalization are not fully counted by the hook estimator.

Current decision: the first-tier conclusion is unchanged, but the wording should be more precise. SAINT-style is faster and more robust on fastMRI; SwinIR-style 2.5D is parameter-light and strongest on NingXia mean metrics, but has higher forward memory/time under the current implementation.

## 13. 2026-06-16 CycleINR-style three-dataset completion update

`CycleINR-style` has now been completed across all three current T2/x4 main-table datasets.

Main-table results: IXI-T2 26.1120 / 0.8587 / 34.6777 / 7643.8680 / 0.9318; fastMRI-brain-T2 expanded 20.3156 / 0.6577 / 66.0985 / 17743.2358 / 0.8302; NingXia-T2 8-fold CV 22.9009 / 0.6935 / 101.0990 / 40735.3568 / 0.8625.

Current decision: keep CycleINR-style as a completed published INR comparison, but do not prioritize further tuning. On IXI it remains close to Linear; on fastMRI it is essentially tied with ArSSR-style and clearly below ResUNet / SwinIR / SAINT; on NingXia it improves over Linear/Cubic but stays below ArSSR-style and the first-tier baselines.
