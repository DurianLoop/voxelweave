# Plan 15：既有 baseline 的完整整合与结果复核

完成日期：2026-09-10。起因是用户指出实验主表里的大量模型没有充分进入两篇论文。本轮不新增无关数据集，重点把已有训练和评价投入转化为正文比较、可复算证据和影响结论的分析。

## 1. 对此前工作的更正

**此前确实没有充分利用这批结果。** 13 类 baseline 曾部分用于重建背景、模型库关联和加密受益分析，但论文主线主要围绕五个干预架构。旧表仅覆盖可恢复的 masked 共同支撑输出，因此多个已在原生评价中完成的 IXI 结果仍显为缺失；20 项 60/90 epoch 结果没有系统进入论证。只说“模型已经列在某张表里”不能解决这个问题。

用户所指旧路径 `docx/experiment/experiment/_master/_table.md` 在当前工作区不存在。已找到现行唯一维护表 [experiment_master_table.md](../../../docx/experiment/experiment_master_table.md)，并完整读取、保存 [原表快照](master_table_original.md)。原表和 baseline 目录均未修改。

现在已完成：

- **两稿正文加入完整 13 方法 × 3 数据集的 ×4 比较**，展示 PSNR、SSIM、MAE。
- 全部 **111 个配置、555 个五指标数值**完成来源核验：39 行 ×4、52 行 ×2/×6、20 行延长训练。
- 从 **3,735 行病例指标**独立复算汇总，NingXia 按八患者 fold 等权；没有把 22 序列当 22 独立患者。
- 对全部 20 项已有延长训练实验做配对重分析，主 MAE 区间同时覆盖全部 20 项：15 项改善，5 项跨零。
- 把三队列的病例难度相关扩展到全部 13 方法，共 **234 个模型对**，不再只依靠少量架构讨论模型多样性。
- 追回被 ResUNet 指标覆盖的 SAINT ×2/×6：从保留的 48 份预测重新计算五指标，与原表一致。

## 2. 现在从哪里能看到这些模型

| 位置 | 实际内容 |
|---|---|
| [CVPR 主文](../CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.pdf)，第 8 页 Table 4 | 13 方法、三队列 ×4 的 PSNR/SSIM/MAE；第 6 页正文解释完整模型库和预算敏感性 |
| [TMI 主文](../TMI/TMI_ARCH_GENERALIZED/main.pdf)，第 7 页 Table VI | 同一完整主表；第 6 页 Section V-G 是 baseline 和训练预算分析 |
| [CVPR 补充](../CVPR/CVPR_ARCH_GENERALIZED/PAPER/supplement.pdf)，第 11–15 页 | 完整评价协议、111 配置的五指标表、全部 20 项预算图及负边界 |
| [TMI baseline 补充](../TMI/TMI_ARCH_GENERALIZED/baseline_supplement.pdf)，5 页 | 同一完整 baseline 证据，可独立阅读和构建 |
| [逐方法使用说明](BASELINE_USE_MAP_ZH.md) | 每类方法用于哪些比较，哪些物理干预证据仍然没有 |
| [逐行来源表](outputs/baseline_all_verified.csv) | 每行原指标、原始 summary 路径、完整精度值、四位小数误差与恢复状态 |

13 类为 Linear、Cubic、ACVTT、Res-SRDiff、ArSSR、CycleINR、ResUNet、Pix2Pix-GAN、SwinIR、SAINT、I3Net、HAT、SMamba-UNet。局部适配／内部实现仍如实标记，不能自动称为全部官方论文的严格复现。

PAST-Net 的 G079–G090 等轨迹是 fastMRI 开发过程，原表也明确尚未进入三队列主表；它们没有被冒充为独立验证。具体已在使用说明中解释。

## 3. 为什么不能直接把旧数字互填

原主表的指标来自全平面 evaluator：逐个非采集层评价整幅图像，再病例内平均；PSNR 使用该目标平面的动态范围。NingXia 先平均患者 fold 内序列，再对八个 fold 等权。旧论文中的重建背景和 QA 机制分析使用的是 **1% 掩膜／共同支撑**，有不同像素支持及汇总规则。

例如 IXI I3Net ×4 的原表 MAE 是 **17.5276**，旧 masked 背景表是 **39.26**；两者不能直接当成数字冲突，也不能填入同一列。此次新增独立、明示口径的原生评价表，保留旧共同支撑实验与负结果。新表出现完整 IXI 13 方法，不表示新增了 13 方法的物理扰动实验。

检查发现每个队列／倍率内，13 方法的病例身份和生成层数量相符：IXI ×4 为 115 例，fastMRI 每倍率 24 例，NingXia 22 序列／8 患者，未发现模型间生成层计数不一致。这个检查不等于重新认证全部历史预处理、训练和物理坐标；后者仍受 Plan 14 的边界约束。见 [支撑审计](outputs/target_support_audit.csv)。自动阈值 mask 的 Dice/HD95 没有被当成真实解剖分割成绩。

## 4. 原始结果追回与表述纠错

### 4.1 IXI 的两个模型在 pre 中

SAINT／ResUNet 的 n=115 原指标实际位于 `pre/ixi_diffusion/runs/saint_full_t2_test115` 与 `resunet_full_t2_test115`，不是统一放在 baseline 下。已追溯原 summary 和 per_case_metrics，全部五指标匹配；其他 IXI 模型的完整评价亦已收回。源文件扫描共检查 463 份合格 full summary，并保留所有数值匹配候选来源，不按新结果挑更好的运行。

### 4.2 SAINT 的 summary 被同目录运行覆盖，预测仍在

fastMRI SAINT 的 `full_x2`／`full_x6` 目录中同时保存 saint_outputs 和 resunet_outputs，而现有 `metrics/summary_metrics.csv` 只剩 ResUNet。仅依靠 summary 会误判 SAINT 缺失。

已对两个倍率各 24 例读取原 GT 和 saint_outputs，按原 `_generated_indices`、动态范围、PSNR、SSIM、MAE、MSE、NCC 定义复算，并核对形状和 affine。结果如下，五指标全部符合原表的四位小数精度。

| 配置 | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|
| SAINT fastMRI ×2 | 24.4308 | .7809 | 39.6861 | 6749.7212 | .9373 |
| SAINT fastMRI ×6 | 22.3172 | .7466 | 52.5303 | 11683.3596 | .8979 |

见 [恢复的逐例结果](outputs/saint_recovered_per_case.csv)、[原图像／预测哈希](outputs/saint_recovery_manifest.json)。没有重训练，也未把新指标写回原 baseline。

### 4.3 ACVTT 延长训练的原文字方向相反

原表最后一句说 fastMRI ACVTT ×6 的 60-epoch “低于标准预算、没有获益”，但同表原数字为：

| 指标 | 原标准配置 | 60 epoch | 实际方向 |
|---|---:|---:|---|
| PSNR | 19.8309 | 20.0269 | 改善 |
| SSIM | .6601 | .6677 | 改善 |
| MAE | 72.4367 | 70.9050 | 改善 |
| MSE | 20031.3896 | 19173.6891 | 改善 |
| NCC | .8120 | .8211 | 改善 |

本轮病例配对的 MAE 改善是 **1.5317 [0.2694, 2.7940]**，区间同时覆盖全部 20 项预算比较。原主表文字保留以保护既有记录，纠正在当前论文补充及本报告公开说明。

## 5. 这些 baseline 如何改变科学结论

### 5.1 强方法随队列变化

I3Net 在 IXI 和 fastMRI 的原生 ×4 五指标上都领先；NingXia 则由 SwinIR 领先 PSNR/SSIM/MAE/MSE，HAT 的 NCC 最高。SMamba、SAINT、ACVTT、INR 和 diffusion 的结果全部参与比较，不因未成为最优而删除。

这些是当前本地记录配置的描述性排名。主表保留不同训练预算、early stopping 和适配方式，fastMRI HAT 明确使用 full_extend60；因此不能称为严格等算力排行榜，也不能用最优单次结果宣称统计优越性。

### 5.2 扩展到 13 方法后的共享难度

以原生 MAE 计算每队列全部 78 个模型对，得到：

| 队列 | 独立汇总单位 | 模型对 | 相关中位数 | 最小／最大 |
|---|---:|---:|---:|---:|
| IXI | 115 检查 | 78 | .9970 | .9820／1.0000 |
| fastMRI | 24 检查 | 78 | .8987 | .7296／.9983 |
| NingXia | 8 患者 fold | 78 | 1.0000 | .6190／1.0000 |

现在“不同模型仍可能共享困难病例”的证据来自完整基线集合。与此同时，fastMRI 的 .899 明显低于旧 masked 分析的相关，**没有为保持强结论而隐藏这一较弱结果**。这些模型对互相依赖，且 NingXia 只有八个秩次；未把 234 个模型对当成 234 次独立重复。

见 [全部模型对](outputs/all13_error_dependence_pairs.csv)、[汇总](outputs/all13_error_dependence_summary.csv)。这不是新不确定性分数或因果机制验证。

### 5.3 训练预算改变了扩散失败的解释

对原表全部 20 项延长预算运行和各自标准行配对，10,000 次 bootstrap，种子 20260910；fastMRI 的单位为检查，NingXia 为患者 fold。主要 MAE 的同时区间覆盖全部 20 项，其他指标的逐项区间完整保留在 CSV。

结果为 **15 项同时区间支持改善，5 项跨零**。最显著的解释变化是宁夏 Res-SRDiff ×2：

| 记录预算 | 全平面 MAE | 相对 30 epoch 的改善（同时 95% CI） |
|---|---:|---:|
| 30 epoch | 440.6059 | 参照 |
| 60 epoch | 140.4503 | 300.1555 [153.1733, 447.1377] |
| 90 epoch | 118.2457 | 322.3602 [166.0125, 478.7079] |

90 epoch 仍落后于 Linear ×2 的 78.5349；更长训练没有使它变成最强方法。但短预算严重退化不能直接升级为“扩散模型天然失败”。这些是不同训练运行，不能解释为严格控制随机种子和其他条件的单 checkpoint 续训因果效应，也没有用高预算替代标准表。

五项未排除零的比较全部保留：NingXia SAINT ×4、CycleINR ×2、ArSSR ×6、Res-SRDiff ×6、ResUNet ×6。CycleINR ×2 的平均 MAE 改善约 0.000006，接近数值不变，不能因为点估计为正就叫有效提升。

见 [全部配对预算结果](outputs/training_budget_paired.csv)、[预算图](figures/p15_training_budget.pdf)。原 ×4→×2 QA 受益实验仍使用原本固定的模型与预算，历史退化和非显著结果没有被新训练预算结果替换。

## 6. 稿件、构建与文件保护

CVPR 将 13 模型主表放入主文，保留机制与外部 MRA 主线；TMI 用完整原生评价表替换正文里稀疏的 masked 背景表，并增加专门预算分析。旧 masked 数值在原稿快照及既有补充中继续保留。五指标、多尺度、全部延长预算以完整表格交付，而不是只写“见数值记录”。

最终构建：CVPR **9 页，技术内容止于第 8 页**；CVPR 补充 **15 页**；TMI **10 页**；TMI baseline 补充 **5 页**。四份文档均无未定义引用、LaTeX 错误或 overfull 警告。全部 **39 页**渲染后查看，另单独检查 CVPR 第 8 页、TMI 第 7 页的主表及预算图，未见遮挡或越界。见 [构建审计](build_logs/build_audit.json)、[页面图](final_page_renders/)。

渲染曾因自动审批额度耗尽被拒绝；用户要求继续后，重新核对脚本只读 PDF、仅向本目录写图，并重试同一操作，已获准并完成。该项现已解除，没有绕过拒绝执行。

本轮修改前保护 **149 个文件**；Plan 13 的 135 文件快照、Plan 14 的 140 文件快照同时验证。原主表、463 份 full summary、相关 per-case 文件和 SAINT 图像／预测哈希均不变。555 个主表数字的最大四位小数舍入差为 0.0000499483，全部在预设舍入容差内；逐病例汇总的复现误差小于 10⁻⁸。见 [验证记录](outputs/verification.json)、[源文件索引](outputs/source_manifest.json)、[完整分析记录](outputs/analysis_manifest.json)。没有改动正在训练的项目，也没有发送或提交论文。

## 7. 仍未解除的科学风险

- **13 个重建 baseline 不等于 13 个架构干预实验。** 完整的共享／不相交物理干预仍只覆盖已有五架构、两个脑队列；预算分析和重建表不能冒充这部分证据。
- 不同训练预算和本地适配影响公平性。当前完整呈现配置与敏感性，不宣称统一算力；SAINT/CycleINR 等名称仍需理解为当前本地实现。
- 历史 fastMRI train/val 患者重叠、长期开发测试集、目标支持与倍率专用权重限制没有因主表补齐而消失。
- 111 个配置不等于 111 个独立试验，病例、模型、倍率和预算之间存在依赖；NingXia 仍只有八患者。
- baseline 重建指标和预算敏感性有助于收紧结论，但没有自动解决 CVPR 方法创新性、神经模型的 acquired-only 完整验证、临床筛选价值或诊断端点。

这轮解决了“已有 baseline 投入没有充分进入论文”的具体问题。后续若继续补实验，应优先让尚未覆盖的模型进入同一物理干预／QA 协议，而非再添加一张没有新判断价值的重建排行榜。A 类提交资料仍由用户处理。

## 8. 交付与复现入口

- [运行指令](RUN_COMMANDS_ZH.md)：审计、SAINT 重算、配对分析、绘图、构建和验证的完整顺序。
- [源码与派生证据包](packages/PLAN15_BASELINES_PAPERS_AND_EVIDENCE.zip)：含当前两稿、两份补充、图表、CSV 和脚本，不含原始医学图像或权重。
- [文件哈希清单](delivery_manifest.json)、[交付核验](delivery_verification.json)：ZIP 内文件与当前交付逐一核对。

原始医学资料、完整历史快照和 baseline 运行记录仍保留在本机既有位置；ZIP 不是脱离这些依赖即可重跑全部实验的数据包。
