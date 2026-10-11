# Plan 11 三项补充实验实现报告

日期：2026-08-27

## 完成状态

本轮只实现和验证实验，没有修改两篇论文正文。三项实验均已固化在 `PROTOCOL.md`，代码位于 `scripts`，命令见 `RUN_COMMANDS_ZH.md`。

| 实验 | 实现状态 | 当前结果状态 |
|---|---:|---:|
| 同模型 ×4→×2 受益预测 | 完成 | fastMRI + NingXia 正式分析已完成 |
| IXI 五架构 clean shared/disjoint | 完成 | 五架构一例端到端 smoke 通过；115 例待按命令运行 |
| matched-geometry identity-swap | 完成 | 五架构 smoke 分析通过；正式分析依赖 IXI 115 例结果 |

## 1. 同模型 ×4→×2

正式分析覆盖 598 个“数据集—病例—模型”有效配对、13 个模型。受益严格定义为同一病例、同一模型、同一 common support 上的 `MAE_x4 - MAE_x2`，因此不再把跨模型性能差异误写成采样加密收益。

正式方向汇总：

| 数据集 | 分数 | 正向模型/总模型 | 模型内 Spearman 中位数 |
|---|---|---:|---:|
| fastMRI | Anchor-CV | 13/13 | 0.8513 |
| fastMRI | adjacent MAE | 13/13 | 0.8017 |
| fastMRI | candidate-bank median disagreement | 11/11 | 0.8348 |
| NingXia | Anchor-CV | 12/13 | 0.7267 |
| NingXia | adjacent MAE | 12/13 | 0.7482 |
| NingXia | candidate-bank median disagreement | 10/11 | 0.7098 |

不利方向没有删除：NingXia 的 ResSRDiff 在三个分数上均为负相关，但区间跨零。该事实限制“所有模型普遍成立”的表述，同时不改变“绝大多数模型方向一致”的聚合证据。该实验仍是 retrospective ranking evidence，不是随机化采样的因果效应。

## 2. IXI 五架构 clean shared/disjoint

已接通五个预存 checkpoint 与 115 例 IXI T2 测试集：HAT、SwinIR、I3Net、SAINT、CycleINR。实现包含：

- phase-0 `0,4,8,...` 与完全不重叠的 phase-2 `2,6,10,...`；
- shared control 为 phase-0 水平翻转、预测后映射回原坐标；
- 每例 5 个不看图像值选择的目标，并平衡 `z mod 4 = 1/3`；
- SAINT phase-2 使用全局物理 `z_abs`，不把 phase-2 错当新原点；
- 每模型首例强制复现既有 phase-0 输出；
- IXI int16 NIfTI staging 的缩放/量化对 phase-0、phase-2、输出和 GT 一致复现。

五个 wrapper 的一例复现均达到 `MAE=0, max_abs=0`。这一步修复了直接使用原始浮点体时由 NIfTI staging 差异造成的伪不一致。

单例 smoke 的 balanced observable gain 均为正（约 0.299–0.347），但它只证明管线和方向计算正确，不能用作正式统计结论。CycleINR 是主要耗时项，当前机器约 119 秒/例；正式命令已拆分并支持 `--resume`。

## 3. matched-geometry identity-swap

分析直接复用第 2 项的同一批预测，不进行二次挑选。每一对比较均经过以下门控：同目标、同模型、同 stride、同锚点数量，最近锚点距离多重集均为 `{1,3}`，但 phase-0 与 phase-2 使用互不重叠的物理锚点身份。

实现对 `z mod 4 = 1` 和 `3` 分别求病例内中位数，再等权平均，从而控制左右反射方向。输出同时保留 `residue1-residue3` 差和 `orientation_warning`；若正式结果只集中在一个方向，identity claim 必须降级。

## 4. 解释边界

- 目前只有第 1 项是正式完整结果。
- 第 2、3 项的 smoke 结果不得进入主表或摘要。
- IXI 完成 115 例后，只有五个模型区间全部为正，才支持五架构 universal wording；否则按模型逐项报告。
- matched geometry 是“左右反射等价”，不是完全相同的有符号几何。
- 所有符合冻结协议的负向、零效应和方向警告均保留，以避免 outcome-dependent selection。
