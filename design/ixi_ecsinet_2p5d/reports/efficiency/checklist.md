# Design 6 ECSI-Net 完整验收与结果决策清单

更新时间：2026-07-15

总目标：把 Design 6 从当前第一版 ECSI-Net 代码推进为具有完整证据链的高效临床 T2 层间插值方案。ECSI-Net 的成功标准不是单项 PSNR 第一，而是在可接受的重建质量下，形成参数量、显存、训练吞吐和整卷推理速度上的明确 Pareto 优势，并证明 change-aware mask 没有退化。

当前路线定位：

> ECSI-Net 使用 linear coarse interpolation 作为基础预测，通过 change-aware mask 控制轻量残差修正；论文主张应聚焦 quality-efficiency trade-off 和临床批量处理效率，而不是无条件宣称重建 SOTA。

本文标记约定：

- `[验收]`：必须检查并留下证据的节点。
- `[决策]`：只能根据上一阶段的实际结果选择后续路线。
- `[阻断]`：条件不满足时禁止扩大实验规模或形成论文结论。
- `[证据]`：完成节点时必须保存的文件、数值或图像。
- `[x]`：已由当前代码或现有文件确认。
- `[ ]`：尚未执行、尚无产物，或尚未通过验收。

文档和代码位置：

- 设计稿：`D:\MRI\docx\design\design6_ecsinet_efficiency.md`
- 下一步指南：`D:\MRI\docx\design\design6_ecsinet_next_guide.md`
- 模型包：`D:\MRI\design\ixi_ecsinet_2p5d\`
- 运行输出：`D:\MRI\design\ixi_ecsinet_2p5d\runs\`
- 效率报告：`D:\MRI\design\ixi_ecsinet_2p5d\reports\efficiency\`

## 0. 当前状态快照

- [x] 已建立独立 ECSI-Net 包，未修改已有 baseline。
- [x] 核心文件存在：`model.py`、`settings.py`、`train.py`、`run_all.py`、`paper_table.py`、`README.md`。
- [x] 外部四通道输入 `[L, R, C, P]` 会在模型内部扩展为 `[L, R, C, P, D, A]`。
- [x] 输出符合 `Y_hat = C + M * R`。
- [x] 模型包含轻量 stem、depthwise E-Block、ECA、mask branch 和 residual head。
- [x] mask 末层使用负 bias 初始化，训练初期偏向 linear coarse。
- [x] 当前 profile 包含 `smoke`、`mini`、`profile32_b6`、`profile48_b8`、`full`、`full_test115`、`full_test115_x2`、`full_test115_x6`。
- [x] `paper_table.py` 已能计算参数量和卷积/线性层 FLOPs 估计。
- [ ] 当前没有 `runs/` 目录，因此没有任何真实训练、推理或数据集结果可标记为已验收。
- [x] 已新增统一效率 profiling 能力：`efficiency.py`，可生成 `efficiency_profile.csv`、`memory_profile.csv`、`inference_profile.csv`、环境 JSON 和 summary。
- [x] 已新增 checkpoint 后 mask/residual 分析能力：`acceptance.py`，可生成 `mask_statistics.csv`、`residual_statistics.csv`、correlation 和 visual QC。
- [x] 已新增可恢复的一键执行器：`one_click.py` 和双击入口 `run_acceptance.cmd`。
- [x] 2026-07-15 静态验收通过，报告位于 `reports/efficiency/static_validation.md`。
- [x] 一键执行器核心测试 `11/11` 通过。
- [ ] 2026-07-15 GPU 预检被阻断：检测到外部计算进程，显存占用约 `18158/24455 MiB`；未启动 profile、smoke 或 mini。
- [ ] 尚无 ECSI-Net 的 fastMRI-brain-T2 独立包。
- [ ] 尚未把 `ecsinet` 接入 NingXia case-level CV runner。

当前证据边界：静态结构已对齐设计稿；真实速度、显存、质量、mask 行为和跨数据集稳定性均未验收。

## 1. 方向、主张与比较口径锁定

- [x] 确认主任务为 T2 through-plane interpolation。
- [x] 确认第一主尺度为 x4；x2/x6 是扩展验证，不应先于 x4 主证据链。
- [x] 确认 ECSI-Net 主线是 efficient reconstruction model，不是 post-hoc analysis。
- [x] 确认 linear coarse 是基础预测，不作为需要“击败”的学习模型主对手。
- [ ] `[验收]` 锁定论文级主要比较方法：I3Net、HAT、SwinIR、SMamba；Linear/Cubic/ResUNet 作为参考。
- [ ] `[验收]` 锁定效率测试硬件、CUDA/PyTorch 版本、输入尺寸、AMP 设置和计时协议。
- [ ] `[验收]` 锁定质量比较的数据划分、case 数、倍率和 generated-slice 评价范围。
- [ ] `[验收]` 在查看主结果前登记第一版判断阈值，避免结果出来后移动标准。

建议使用以下预登记阈值：

| 维度 | 强通过 | 可继续 | 不通过 |
|---|---:|---:|---:|
| 相对第一梯队 PSNR 差距 | `<= 0.30 dB` | `(0.30, 0.50] dB` | `> 0.50 dB` |
| 相对 HAT/SMamba 整卷推理加速 | `>= 2.0x` | `[1.5x, 2.0x)` | `< 1.5x` |
| 相对 I3Net 整卷推理加速 | `>= 1.5x` | `[1.2x, 1.5x)` | `< 1.2x` |
| 相对重模型 peak VRAM | `<= 60%` | `(60%, 75%]` | `> 75%` |
| 相对重模型参数量 | `<= 25%` | `(25%, 40%]` | `> 40%` |

说明：这些是 ECSI 路线的暂定论文放行阈值，不替代统计检验。若硬件或比较模型改变，必须在运行前修改并记录原因。

- [ ] `[决策 D1]` 如果能满足“质量可继续”且至少两项效率指标强通过，保留独立 ECSI 论文路线。
- [ ] `[决策 D1]` 如果质量强通过但速度优势不足，先优化实现和计时路径，不立即扩三数据集。
- [ ] `[决策 D1]` 如果速度强通过但 PSNR 差距超过 `0.50 dB`，降级为 efficient variant，并优先调整容量。
- [ ] `[阻断 B1]` 如果既无质量接近性又无显著效率优势，停止 full/跨数据集扩张，重新审视模型定位。

## 2. 代码与配置静态验收

- [x] `[验收]` 对 `model.py`、`settings.py`、`train.py`、`run_all.py`、`paper_table.py`、`acceptance.py`、`efficiency.py`、`one_click.py` 做 AST 解析。
- [x] `[验收]` 在 MRI conda 环境中导入 `ixi_ecsinet_2p5d.run_all` 和 `ixi_ecsinet_2p5d.paper_table`。
- [x] `[验收]` 以 4 通道随机输入执行 forward，输出 shape 为 `2 x 1 x 16 x 16`。
- [x] `[验收]` 以 6 通道随机输入执行 forward，输出 shape 为 `2 x 1 x 16 x 16`。
- [x] `[验收]` 检查 `return_parts=True` 返回 `recon`、`residual`、`correction`、`mask`、`coarse`、`change`、`coarse_grad`。
- [x] `[验收]` 数值验证 `recon == coarse + mask * residual`，容差 `atol <= 1e-6`。
- [x] `[验收]` 验证 `mask` 全部位于 `[0, 1]`。
- [x] `[验收]` 验证随机 batch loss 有限，且包含 `l1`、`grad`、`residual_l1`、`mask_mean`、`mask_prior_l1`。
- [x] `[验收]` 验证 checkpoint 保存并能由 `ECSINetInterpolator` 重新加载。
- [x] `[验收]` 验证 checkpoint stride 与推理 stride 不一致时明确报错。
- [x] `[验收]` 检查 x4/x2/x6 profile 的 stride 和输出目录互不覆盖；batch/case 数仍需在真实 run manifest 中复核。
- [x] `[证据]` 保存静态验收记录：`reports/efficiency/static_validation.md` 和 `static_validation.json`。

- [x] `[阻断 B2]` 已解除：forward、loss、checkpoint round-trip 均通过。

## 3. Profiling 测量体系验收

### 3.1 必须补齐的测量能力

- [x] `[验收]` 新增统一 profiling 入口，已覆盖合成训练吞吐和模型纯推理；整卷端到端推理将在 checkpoint 生成后补测。
- [x] `[验收]` profiling 入口可记录模型参数量、MACs、FLOPs，并写清计算定义；真实 256x256 数值待 GPU 预检通过后生成。
- [ ] `[验收]` 记录 peak allocated VRAM 和 peak reserved VRAM。
- [ ] `[验收]` 记录训练 `it/s`、`samples/s`、`sec/epoch`。
- [ ] `[验收]` 记录 batch=1 的 `ms/generated slice`。
- [ ] `[验收]` 记录代表性 whole volume 的 `sec/case`。
- [ ] `[验收]` 测试最大可训练 batch；OOM 只作为容量边界记录，不视为整个任务失败。
- [ ] `[验收]` 训练和推理分别记录 AMP on/off；论文主比较统一使用 AMP on。
- [ ] `[验收]` GPU 计时前后调用 CUDA synchronize，排除异步计时偏差。
- [ ] `[验收]` 纯模型推理至少 warm-up 20 次、正式计时 100 次，并报告均值、标准差和 P50/P95。
- [ ] `[验收]` whole-volume 计时至少重复 3 次，并同时报告含 I/O 与不含 I/O 的结果。
- [ ] `[验收]` 所有方法在同一 GPU、相同输入尺寸、相同生成切片集合和相同精度模式下比较。

### 3.2 必测 ECSI 配置

| 名称 | channels | blocks | batch 候选 | 当前代码状态 |
|---|---:|---:|---|---|
| ECSI-Tiny | 32 | 6 | 16/32/64 | 已有 `profile32_b6`，尚未完整扫 batch |
| ECSI-Base | 48 | 8 | 8/16/32 | 已有 `profile48_b8`，尚未完整扫 batch |
| ECSI-Plus | 64 | 10 | 4/8/16 | 尚无 profile |

- [ ] `[验收]` Tiny 完成全部 batch 候选测试。
- [ ] `[验收]` Base 完成全部 batch 候选测试。
- [ ] `[决策 D2]` 仅在 Tiny/Base 的质量不足且效率仍有余量时增加 Plus。
- [ ] `[阻断 B3]` 不允许为“表格完整”直接训练 Plus；必须先有 D2 的结果依据。

### 3.3 Profiling 产物

- [ ] `[证据]` `runs/profile/efficiency_profile.csv`
- [ ] `[证据]` `runs/profile/memory_profile.csv`
- [ ] `[证据]` `runs/profile/inference_profile.csv`
- [ ] `[证据]` `runs/profile/profile_environment.json`
- [ ] `[证据]` `reports/efficiency/profile_summary.md`

`profile_environment.json` 至少记录：GPU 型号、显存总量、驱动、CUDA、PyTorch、cuDNN、Python、AMP、TF32、输入尺寸、warm-up 次数、计时次数和 commit/代码快照标识。

- [ ] `[阻断 B4]` 缺少环境记录、同步计时或公平输入口径时，不得引用速度倍数。

## 4. Smoke 链路与健康度验收

Smoke 只验证链路，不用于性能结论。

- [ ] `[验收]` `smoke` 完成训练、验证、checkpoint、整卷推理、Linear/Cubic 和 metrics 全链路。
- [ ] `[验收]` 训练中无 NaN/Inf；`skipped_nonfinite = 0`。
- [ ] `[验收]` `training_history.csv/json`、best/final checkpoint、`run_manifest.json` 存在。
- [ ] `[验收]` ECSI、Linear、Cubic 的 `summary_metrics.csv` 记录完整。
- [ ] `[验收]` 输出 NIfTI 数量与 smoke test manifest 一致。
- [ ] `[验收]` 输出 shape、affine、header、动态范围和 generated-slice 位置正确。
- [ ] `[验收]` mask mean 不接近 0 或 1。
- [ ] `[验收]` mask 标准差 `>= 0.01`，避免近似常数图。
- [ ] `[验收]` correction 有限，且 P99 绝对值不出现明显爆炸。
- [ ] `[验收]` 任取至少 3 个 generated slices 检查 prediction、linear、GT、error、mask、residual 六联图。
- [ ] `[证据]` `reports/efficiency/smoke_acceptance.md`
- [ ] `[证据]` `reports/efficiency/smoke_visual_qc/`

- [ ] `[决策 D3]` smoke 全部通过后进入 mini。
- [ ] `[决策 D3]` 若只有 mask 退化，先调整 `mask_bias`、`lambda_mask`、`lambda_prior`，重复 smoke。
- [ ] `[决策 D3]` 若 residual 爆炸，先降低 `residual_scale`、检查归一化和 loss 权重，重复 smoke。
- [ ] `[阻断 B5]` smoke 未通过时禁止运行 mini/full。

## 5. IXI mini 质量验收

- [ ] `[验收]` `mini` 按固定 seed、固定 train/val/test case 完成。
- [ ] `[验收]` 记录 best epoch、early stopping、总训练时间、平均 sec/epoch 和 peak VRAM。
- [ ] `[验收]` ECSI 相对 Linear：PSNR/SSIM/NCC 更高，MAE/MSE 更低。
- [ ] `[验收]` ECSI 相对 Cubic：PSNR/SSIM/NCC 更高，MAE/MSE 更低。
- [ ] `[验收]` 每个 test case 均有 per-case metrics，不只看均值。
- [ ] `[验收]` 检查是否由单个容易 case 抬高均值。
- [ ] `[验收]` 至少保存 5 个代表 case：最好、最差、中位数、高变化、低变化。
- [ ] `[验收]` 可视化中无大面积伪影、强度漂移、边缘振铃或切片错位。
- [ ] `[证据]` `runs/mini/metrics/summary_metrics.csv`
- [ ] `[证据]` `runs/mini/metrics/paper_table.csv`
- [ ] `[证据]` `reports/efficiency/mini_quality_summary.md`
- [ ] `[证据]` `reports/efficiency/mini_visual_qc/`

- [ ] `[决策 D4]` 若全面优于 Linear/Cubic，进入 mask 解释性验收和 Pareto 初筛。
- [ ] `[决策 D4]` 若仅略输 Cubic但效率显著，允许进行一次容量/损失调整后重跑 mini。
- [ ] `[决策 D4]` 若明显输 Linear，优先检查 coarse/correction 公式和训练稳定性，不扩模型规模。
- [ ] `[阻断 B6]` mini 不能稳定优于 Linear 时，禁止运行 `full_test115`。

## 6. Change-aware mask 与 residual 验收

### 6.1 统计产物

- [ ] `[验收]` 保存 mask mean、std、P01、P50、P99。
- [ ] `[验收]` 保存 foreground/background mask mean。
- [ ] `[验收]` 保存 high-change/low-change region mask mean。
- [ ] `[验收]` 保存 residual 和 correction 的 mean、std、P95、P99、max absolute value。
- [ ] `[验收]` 按 case、slice、phase/offset 分层保存统计。
- [ ] `[证据]` `runs/mini/metrics/mask_statistics.csv`
- [ ] `[证据]` `runs/mini/metrics/residual_statistics.csv`
- [ ] `[证据]` `runs/mini/metrics/mask_correlation.csv`

### 6.2 关系与解释性

- [ ] `[验收]` 计算 `corr(mask, |target - linear|)`。
- [ ] `[验收]` 计算 `corr(mask, |prediction - linear|)`。
- [ ] `[验收]` 计算 `corr(mask, image gradient)`。
- [ ] `[验收]` high-change region 的 mask 均值高于 low-change region。
- [ ] `[验收]` foreground 的 mask 统计与 background 分开报告，避免背景比例影响结论。
- [ ] `[验收]` mask 在解剖边界和真实 linear error 高的区域有可解释响应。
- [ ] `[验收]` correction 集中在需要修正的区域，而非全图同幅度变化。
- [ ] `[证据]` `reports/efficiency/mask_interpretation.md`
- [ ] `[证据]` `reports/efficiency/mask_visual_qc/`

- [ ] `[决策 D5]` 如果 mask 非退化且与 `|target-linear|` 正相关，保留 change-aware 主张。
- [ ] `[决策 D5]` 如果 mask 非退化但相关性弱，只主张 gated residual，不主张“准确定位困难区域”。
- [ ] `[决策 D5]` 如果 mask 接近常数但重建有效，必须做 w/o mask 消融，判断 mask 是否仅为缩放因子。
- [ ] `[决策 D5]` 如果 mask 全 0/全 1 或修正区域无解释性，调整正则并回到 smoke/mini。
- [ ] `[阻断 B7]` 在 mask 退化问题未解释前，不得把 change-aware 作为论文核心贡献。

## 7. 第一版 Quality-Efficiency Pareto 验收

### 7.1 公平比较方法

- [ ] `[验收]` 至少纳入 Linear、Cubic、ResUNet、I3Net、SwinIR、HAT、SMamba、ECSI-Tiny、ECSI-Base。
- [ ] `[验收]` 参数量和 FLOPs 使用统一输入 `1 x 4 x 256 x 256` 和统一定义。
- [ ] `[验收]` learned 方法使用同一 GPU、AMP 和 batch=1 推理协议。
- [ ] `[验收]` 同时报告纯模型 `ms/slice` 和 whole-volume `sec/case`。
- [ ] `[验收]` 训练吞吐比较时同时给出 batch 和 samples/s，不能只比较 sec/epoch。
- [ ] `[验收]` 引用历史日志时标记 `historical log`，与本轮同机实测分栏。
- [ ] `[验收]` 至少对 I3Net、HAT、SwinIR 和 ECSI 做同机复测。

### 7.2 必须形成的表和图

- [ ] `[证据]` `reports/efficiency/efficiency_quality_table.csv`
- [ ] `[证据]` `reports/efficiency/efficiency_quality_table.md`
- [ ] `[证据]` `reports/efficiency/figures/pareto_psnr_vs_sec_case.png`
- [ ] `[证据]` `reports/efficiency/figures/pareto_psnr_vs_vram.png`
- [ ] `[证据]` `reports/efficiency/figures/pareto_psnr_vs_params.png`
- [ ] `[证据]` `reports/efficiency/figures/pareto_ssim_vs_sec_case.png`

- [ ] `[验收]` 每张图明确标出同一数据集、倍率、case 数、硬件和误差方向。
- [ ] `[验收]` Pareto frontier 由脚本计算，不凭目测选择。
- [ ] `[验收]` 对重复计时给出误差条或置信区间。

- [ ] `[决策 D6]` ECSI-Tiny/Base 至少一个位于 PSNR-vs-sec/case Pareto frontier，才进入 IXI full。
- [ ] `[决策 D6]` 如果 Tiny 更快但质量不足、Base 质量合格且仍在 frontier，Base 作为主模型，Tiny 作为部署变体。
- [ ] `[决策 D6]` 如果 Tiny/Base 都被 I3Net 严格支配，优先优化实现或模型结构，不扩 full。
- [ ] `[阻断 B8]` 没有 Pareto 图和公平计时证据时，不得使用“显著更高效”表述。

## 8. IXI full_test115 验收

- [ ] `[验收]` 仅在 B2-B8 全部解除后启动 `full_test115`。
- [ ] `[验收]` 训练、推理和评估覆盖 115 个测试 case。
- [ ] `[验收]` 记录实际训练 epoch、best epoch、early stopping、总 GPU 时间和 peak VRAM。
- [ ] `[验收]` 记录 115 case 总推理时间、平均/中位/P95 sec/case。
- [ ] `[验收]` ECSI 与 baseline 使用相同 GT、case manifest 和 generated-slice mask。
- [ ] `[验收]` 主指标包含 PSNR、SSIM、MAE、MSE、NCC。
- [ ] `[验收]` 报告 mean、std 和 bootstrap 95% CI。
- [ ] `[验收]` 与 I3Net/HAT/SwinIR 做 paired per-case comparison。
- [ ] `[验收]` 检查 offset 1/2/3 的 per-offset 指标，避免平均值掩盖特定 phase 失败。
- [ ] `[验收]` 检查最差 10 个 case 和最差 10 个 slice。
- [ ] `[验收]` 生成质量-效率联合表，而非将速度与质量拆成互不关联的表述。
- [ ] `[证据]` `reports/efficiency/full_test115/main_results.md`
- [ ] `[证据]` `reports/efficiency/full_test115/per_case_paired.csv`
- [ ] `[证据]` `reports/efficiency/full_test115/per_offset_metrics.csv`
- [ ] `[证据]` `reports/efficiency/full_test115/runtime_summary.csv`
- [ ] `[证据]` `reports/efficiency/full_test115/visual_qc/`

- [ ] `[决策 D7]` PSNR 差距 `<= 0.30 dB` 且至少两项效率强通过：进入跨数据集主线。
- [ ] `[决策 D7]` PSNR 差距 `(0.30, 0.50] dB` 且速度/显存优势很强：保留 efficient clinical model 定位，但收紧主张。
- [ ] `[决策 D7]` PSNR 差距 `> 0.50 dB`：先做容量和 mask 消融，不直接扩 fastMRI/NingXia。
- [ ] `[阻断 B9]` 115 case 未完整对齐或只完成部分 case 时，不能形成 full_test115 结论。

## 9. 消融实验验收

所有消融必须共享数据划分、训练 epoch/early stopping 规则、seed 和评估脚本。

| 消融 | 必做级别 | 要回答的问题 |
|---|---|---|
| Full ECSI-Net | 必做 | 主模型基准 |
| w/o mask branch | 必做 | mask 是否真正贡献质量或选择性修正 |
| w/o mask sparsity | 必做 | `lambda_mask` 是否必要 |
| w/o mask prior | 必做 | change prior 是否必要 |
| channels 32/48/64 | 必做 | 容量与效率权衡 |
| blocks 4/8/12 | 必做 | 深度与效率权衡 |
| kernel 3/5/7 | 建议 | 大核 depthwise 的收益 |
| mask bias on/off | 建议 | 保守初始化是否改善稳定性 |
| early-exit on/off | 条件触发 | 仅在静态 ECSI 已形成 Pareto 后启动 |

- [ ] `[验收]` 每个必做消融至少完成 mini；进入论文主表的消融需使用完整或预登记代表性数据。
- [ ] `[验收]` 同时报告质量、参数量、FLOPs、VRAM 和 sec/case。
- [ ] `[验收]` mask 相关消融同时报告 mask 健康度与可视化。
- [ ] `[验收]` 至少使用 3 个 seed，或对不能多 seed 的 full run 给出 paired bootstrap CI。
- [ ] `[证据]` `reports/efficiency/ablation_table.csv`
- [ ] `[证据]` `reports/efficiency/ablation_interpretation.md`

- [ ] `[决策 D8]` w/o mask 与 Full 几乎无差异时，弱化或移除 mask 核心贡献表述。
- [ ] `[决策 D8]` channels/blocks 增大带来小质量收益但破坏 Pareto 时，选择较小配置作为主模型。
- [ ] `[决策 D8]` 只有 Plus 达到质量阈值且效率优势消失时，ECSI 独立论文路线降级。
- [ ] `[决策 D8]` early-exit 仅在预计能带来 `>= 20%` 整卷推理降幅且质量损失 `<= 0.10 dB` 时进入正式实验。
- [ ] `[阻断 B10]` 不允许只报告有利消融；预登记的必做项必须完整呈现。

## 10. fastMRI-brain-T2 验收

- [ ] `[前置缺口]` 建立 ECSI fastMRI 包或通用数据适配入口。
- [ ] `[验收]` fastMRI 使用与其他方法一致的 processed 数据、划分和倍率。
- [ ] `[验收]` 先跑 fastMRI smoke，再跑 mini/代表性子集，最后才运行 full。
- [ ] `[验收]` 复测参数量、FLOPs、VRAM、ms/slice 和 sec/case，不能直接沿用 IXI 运行时间。
- [ ] `[验收]` 报告质量相对 I3Net/HAT/SwinIR 的差距和 paired CI。
- [ ] `[验收]` 检查高纹理、高变化和低 SNR case 的 visual QC。
- [ ] `[验收]` 检查 mask 在复杂结构下是否饱和或退化。
- [ ] `[证据]` `reports/efficiency/fastmri/main_results.md`
- [ ] `[证据]` `reports/efficiency/fastmri/runtime_summary.csv`
- [ ] `[证据]` `reports/efficiency/fastmri/mask_statistics.csv`
- [ ] `[证据]` `reports/efficiency/fastmri/visual_qc/`

- [ ] `[决策 D9]` fastMRI 保持 IXI 的 Pareto 优势：进入 NingXia CV，并允许主张跨数据集效率稳定。
- [ ] `[决策 D9]` fastMRI 速度优势保持但质量明显下降：增加容量或结构增强，只做一次预登记调整。
- [ ] `[决策 D9]` fastMRI 质量接近但速度优势消失：检查数据预处理、I/O 和 resize 是否主导端到端时间。
- [ ] `[阻断 B11]` fastMRI 未通过 smoke/mini 时禁止直接跑 full。

## 11. NingXia case-level CV 验收

- [ ] `[前置缺口]` 将 `ecsinet` 接入 `processing.run_ningxia_case_cv` 的 model choices 和 module mapping。
- [ ] `[验收]` 使用与 baseline 一致的 patient-level 8-fold CV，避免 slice 泄漏。
- [ ] `[验收]` 每 fold 独立训练、选择 checkpoint 和评估。
- [ ] `[验收]` 所有 fold 使用相同 profile、seed 规则和 early stopping 规则。
- [ ] `[验收]` 报告 fold mean/std、case-level bootstrap CI 和最差 fold。
- [ ] `[验收]` 报告每 fold 训练时间、peak VRAM、sec/case。
- [ ] `[验收]` 检查 mask 在外部临床数据中的分布漂移。
- [ ] `[验收]` 保存失败 case 和 sagittal/coronal visual QC。
- [ ] `[证据]` `reports/efficiency/ningxia_cv/fold_summary.csv`
- [ ] `[证据]` `reports/efficiency/ningxia_cv/runtime_summary.csv`
- [ ] `[证据]` `reports/efficiency/ningxia_cv/mask_shift_analysis.csv`
- [ ] `[证据]` `reports/efficiency/ningxia_cv/visual_qc/`

- [ ] `[决策 D10]` NingXia 各 fold 稳定且效率优势保持：允许使用“external clinical robustness”表述。
- [ ] `[决策 D10]` 均值尚可但 fold 方差大：只表述跨域可行性，不主张更稳健。
- [ ] `[决策 D10]` mask 明显饱和或质量崩溃：回到 mask prior/正则和归一化检查。
- [ ] `[阻断 B12]` 未完成全部 fold 时不得把 partial CV 当作 NingXia 完整结论。

## 12. x2/x4/x6 多倍率验收

- [ ] `[验收]` x4 主线通过后再运行 `full_test115_x2` 和 `full_test115_x6`。
- [ ] `[验收]` 三倍率分别训练或明确说明 checkpoint 是否共享。
- [ ] `[验收]` 三倍率均记录质量、参数量、FLOPs/generated slice、sec/case 和 peak VRAM。
- [ ] `[验收]` 端到端 sec/case 考虑不同倍率生成切片数量，不只比较单 slice 时间。
- [ ] `[验收]` x4 按 offset 1/2/3，x6 按 offset 1-5 分层报告。
- [ ] `[验收]` 检查倍率增大后 mask mean、std 和高低变化区差异。
- [ ] `[证据]` `reports/efficiency/multiscale_quality_efficiency.csv`
- [ ] `[证据]` `reports/efficiency/figures/pareto_multiscale.png`

- [ ] `[决策 D11]` 三倍率都在 Pareto frontier：可主张 scalable efficiency。
- [ ] `[决策 D11]` 仅 x4 成立：论文聚焦 x4，x2/x6 放附录并解释边界。
- [ ] `[决策 D11]` x6 质量明显下降：优先评估 phase/offset 建模，不盲目增加 blocks。
- [ ] `[阻断 B13]` 不同倍率使用不同 case 集或计时口径时，禁止横向画同一 Pareto 曲线。

## 13. 统计、QC 与可复现性验收

- [ ] `[验收]` 所有主表数值可由脚本从 CSV 重生成。
- [ ] `[验收]` 所有主图都有输入 CSV、绘图脚本和输出 PNG/PDF。
- [ ] `[验收]` 所有 case manifest 保存绝对来源路径和匿名 case id 的映射；投稿版移除本地绝对路径。
- [ ] `[验收]` 固定并记录 Python、NumPy、PyTorch 和 DataLoader seed。
- [ ] `[验收]` 记录数据预处理、归一化、target shape 和 generated-slice 规则。
- [ ] `[验收]` 对质量差异使用 paired test 或 paired bootstrap CI。
- [ ] `[验收]` 对速度重复测试报告波动，不只报告最好一次。
- [ ] `[验收]` 对 OOM、跳过 batch、锁文件和中断 run 留下日志。
- [ ] `[验收]` 检查 summary、paper table、Markdown 和 CSV 数值一致。
- [ ] `[验收]` 检查 smoke/mini 没有进入 full-results master table。
- [ ] `[验收]` 检查历史日志与本轮同机实测明确区分。
- [ ] `[验收]` 检查所有主张可追溯到 `reports/efficiency/` 下的证据文件。

- [ ] `[阻断 B14]` 不可重生成的手工表格不得进入论文主文。
- [ ] `[阻断 B14]` 未记录硬件和计时协议的速度结果不得跨方法比较。

## 14. 论文级主表、主图和表述验收

### 14.1 主表

- [ ] Table 1：IXI/fastMRI/NingXia 重建质量，包含 PSNR、SSIM、MAE、NCC。
- [ ] Table 2：效率主表，包含 Params、FLOPs、peak VRAM、batch max、samples/s、ms/slice、sec/case。
- [ ] Table 3：quality-efficiency 联合排名和 Pareto 状态。
- [ ] Table 4：mask/residual 消融。
- [ ] Table 5：Tiny/Base/Plus 或 channels/blocks 容量消融。
- [ ] Supplementary：per-case、per-offset、per-fold 和多倍率完整结果。

### 14.2 主图

- [ ] Figure 1：ECSI-Net 结构与 `C + M * R` 数据流。
- [ ] Figure 2：PSNR vs sec/case Pareto。
- [ ] Figure 3：PSNR vs peak VRAM Pareto。
- [ ] Figure 4：mask、linear error、residual、prediction visual panel。
- [ ] Figure 5：跨数据集/多倍率效率稳定性。
- [ ] Supplementary：完整 mask 分布、ablation 和 worst-case panels。

### 14.3 主张边界

- [ ] `[验收]` 仅当 D6/D7/D9/D10 有对应证据时使用“better quality-efficiency trade-off”。
- [ ] `[验收]` 仅当 ECSI 位于计算得到的 frontier 时使用“Pareto-optimal”或“on the Pareto frontier”。
- [ ] `[验收]` 仅当 NingXia 全部 fold 通过时使用“external clinical robustness”。
- [ ] `[验收]` 仅当 mask 分析通过时使用“avoids unnecessary correction in easy regions”。
- [ ] `[验收]` 不把 Params/FLOPs 低等同于真实 wall-clock 快；两者必须分别报告。
- [ ] `[验收]` 不把训练吞吐快等同于整卷部署快；必须报告 sec/case。
- [ ] `[验收]` 不宣称所有指标 SOTA，除非完整主表确实支持。

## 15. 总体验收决策矩阵

| 最终结果 | 质量 | 效率 | mask | 跨数据集 | 结论与动作 |
|---|---|---|---|---|---|
| A：独立论文强通过 | 距第一梯队 `<=0.30 dB` | 至少两项强通过且在 frontier | 非退化且有解释性 | fastMRI + NingXia 稳定 | 进入独立 ECSI 论文写作 |
| B：应用论文可通过 | 距第一梯队 `0.30-0.50 dB` | 推理/显存优势很强 | 非退化或经消融证明有效 | 至少一个外部数据集稳定 | 收紧质量主张，强调部署效率 |
| C：高效变体 | 质量差距较大 | 效率显著 | mask 证据一般 | 未完整通过 | 作为大论文 efficient variant，不单独投稿 |
| D：实现优化后复评 | 质量接近 | wall-clock 优势不足 | 可用 | 暂停 | 优化 kernel、I/O、batch、AMP，再复测 Pareto |
| E：结构调整后复评 | 明显输 Linear/Cubic 或差距 `>0.50 dB` | 有余量 | 退化或无贡献 | 不扩 | 调整容量、loss、mask，不跑 full |
| F：停止路线 | 质量和效率均无优势 | 被 I3Net/轻量 baseline 支配 | 无有效解释 | 无必要扩展 | 合并为负结果或停止投入 |

- [ ] `[决策 D12]` 根据完整证据选择且只选择 A-F 中一个状态。
- [ ] `[验收]` 在 `reports/efficiency/final_decision.md` 记录选择、依据、关键数字和未解决风险。
- [ ] `[阻断 B15]` 不允许跳过 D12 直接进入论文强主张或新增大规模训练。

## 16. 当前建议执行顺序

- [x] 第一步：补齐 profiling 代码、GPU 同步计时、环境记录和可恢复入口。
- [x] 第二步：完成静态验收并写 `static_validation.md/json`。
- [ ] 第三步：运行 ECSI-Tiny/Base smoke profile，生成三份 profile CSV；当前被 GPU 外部进程阻断。
- [ ] 第四步：运行 smoke 全链路，完成 mask/residual 健康度检查。
- [ ] 第五步：运行 IXI mini，生成质量、mask、residual 和 visual QC 产物。
- [ ] 第六步：同机复测 I3Net/HAT/SwinIR，形成第一版 Pareto 表和图。
- [ ] 第七步：执行 D6；只有通过才启动 IXI full_test115。
- [ ] 第八步：完成 full_test115、paired statistics 和 per-offset QC。
- [ ] 第九步：执行消融并锁定 Tiny/Base/Plus 主配置。
- [ ] 第十步：按 fastMRI -> NingXia CV -> x2/x6 的顺序扩展。
- [ ] 第十一步：生成论文主表、主图和 reviewer attack list。
- [ ] 第十二步：执行最终 D12，确定独立论文、efficient variant、复评或停止路线。

## 17. 命令归档

每次新 PowerShell 终端先执行：

```powershell
Set-Location D:\MRI
$py = "D:\conda\envs\MRI\python.exe"
$env:PYTHONPATH = "D:\MRI\pre;D:\MRI\baseline;D:\MRI\design;D:\MRI"
$env:IXI_DATA_ROOT = "D:\MRI\dataset\IXI"
```

静态导入检查：

```powershell
& $py -B -c "import ixi_ecsinet_2p5d.run_all; import ixi_ecsinet_2p5d.paper_table; print('ECSI imports OK')"
```

Smoke：

```powershell
& $py -u -B -m ixi_ecsinet_2p5d.run_all --profile smoke
& $py -u -B -m ixi_ecsinet_2p5d.paper_table --profile smoke
```

Mini：

```powershell
& $py -u -B -m ixi_ecsinet_2p5d.run_all --profile mini
& $py -u -B -m ixi_ecsinet_2p5d.paper_table --profile mini
```

现有 Tiny/Base profile：

```powershell
& $py -u -B -m ixi_ecsinet_2p5d.run_all --profile profile32_b6
& $py -u -B -m ixi_ecsinet_2p5d.paper_table --profile profile32_b6

& $py -u -B -m ixi_ecsinet_2p5d.run_all --profile profile48_b8
& $py -u -B -m ixi_ecsinet_2p5d.paper_table --profile profile48_b8
```

IXI x4 full_test115，仅在 B2-B8 全部解除后运行：

```powershell
& $py -u -B -m ixi_ecsinet_2p5d.run_all --profile full_test115
& $py -u -B -m ixi_ecsinet_2p5d.paper_table --profile full_test115
```

IXI x2/x6，仅在 x4 主线通过后运行：

```powershell
& $py -u -B -m ixi_ecsinet_2p5d.run_all --profile full_test115_x2
& $py -u -B -m ixi_ecsinet_2p5d.paper_table --profile full_test115_x2

& $py -u -B -m ixi_ecsinet_2p5d.run_all --profile full_test115_x6
& $py -u -B -m ixi_ecsinet_2p5d.paper_table --profile full_test115_x6
```

运行后检查：

```powershell
Get-ChildItem D:\MRI\design\ixi_ecsinet_2p5d\runs\<profile>\metrics
Get-Content D:\MRI\design\ixi_ecsinet_2p5d\runs\<profile>\training_history.json
Get-Content D:\MRI\design\ixi_ecsinet_2p5d\runs\<profile>\metrics\summary_metrics.csv
```

注意：`<profile>` 是人工替换位，例如 `smoke`、`mini` 或 `full_test115`；它不是可直接复制执行的 PowerShell 变量。

## 18. 每次阶段验收记录模板

每完成一个阶段，在对应 summary 文档末尾填写：

```text
阶段：
运行日期：
代码/配置快照：
数据集、倍率、case 数：
GPU 与软件环境：
验收项通过数 / 总数：
关键质量结果：
关键效率结果：
mask/residual 健康度：
异常与排除项：
对应证据文件：
解除的阻断节点：
触发的决策节点：
决策：继续 / 调参复跑 / 降级定位 / 停止
决策依据：
下一步：
```

最终原则：先解除阻断节点，再扩大实验；先形成质量-效率联合证据，再形成论文主张。任何 smoke、mini、部分 case 或跨硬件日志都只能作为筛查证据，不能替代 full、同机和完整 CV 的结论。
