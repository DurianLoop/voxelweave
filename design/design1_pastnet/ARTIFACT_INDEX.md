# Design1 文件与证据索引

Design1 文档已集中到本目录并按阶段整理。Python 包、日志、checkpoint 和 `runs` 保持原位，避免破坏模块导入、历史命令与 warm-start 路径。

## 1. 单一入口

| 用途 | 文件 |
|---|---|
| Design1 总结与状态 | [README.md](README.md) |
| 正式结果账本 | [results/experiment_ledger.md](results/experiment_ledger.md) |
| 下一代 SOTA 路线 | [handoff/next_sota_handoff.md](handoff/next_sota_handoff.md) |
| 代码目录说明 | [code/README.md](code/README.md) |
| 运行目录说明 | [runs/README.md](runs/README.md) |
| 本文件 | [ARTIFACT_INDEX.md](ARTIFACT_INDEX.md) |

## 2. 代码入口

| 范围 | 路径 | 说明 |
|---|---|---|
| fastMRI 包 | `../fastmri_brain_pastnet_2p5d/` | G01-G090 训练、评估与全部模型 |
| fastMRI profiles | `../fastmri_brain_pastnet_2p5d/settings.py` | 所有 smoke/full 配置的事实来源 |
| 多锚点主干 | `../fastmri_brain_pastnet_2p5d/model_ma.py` | rich input、adaptive fusion、wide MA3、context |
| latent interval | `../fastmri_brain_pastnet_2p5d/model_ma3latent.py` | G076-G080 的三 offset latent interaction |
| aggressive refiners | `../fastmri_brain_pastnet_2p5d/model_ma3aggressive.py` | Flow、INR、unrolled、dual-domain、3D U-Net |
| sparse-window | `../fastmri_brain_pastnet_2p5d/model_sparse_window.py` | G087-G090 负结果主干，保留作证据 |
| fastMRI 训练 | `../fastmri_brain_pastnet_2p5d/train.py` | AMP、梯度累积、loss、EMA、checkpoint |
| fastMRI 入口 | `../fastmri_brain_pastnet_2p5d/run_all.py` | profile 调度与评估 |
| IXI 包 | `../ixi_pastnet_2p5d/` | G07 与固定 G086 泛化实现 |
| IXI G086 profiles | `../ixi_pastnet_2p5d/settings.py` | smoke/full 与显存约束 |

## 3. 冻结 checkpoint 与原始指标

| 产物 | 路径 | 当前状态 |
|---|---|---|
| fastMRI G086 best | `../fastmri_brain_pastnet_2p5d/runs/full_pastnet_g086_dual_restart60/checkpoints/pastnet_epoch_best.pth` | 存在，冻结 |
| fastMRI G086 metrics | `../fastmri_brain_pastnet_2p5d/runs/full_pastnet_g086_dual_restart60/metrics/summary_metrics.csv` | 正式 test-24 |
| fastMRI G086 cases | `../fastmri_brain_pastnet_2p5d/runs/full_pastnet_g086_dual_restart60/metrics/per_case_metrics.csv` | 配对统计源 |
| IXI G07 best | `../ixi_pastnet_2p5d/runs/full_g07_ma3_wide200_test115/checkpoints/pastnet_epoch_best.pth` | 存在，G086 初始化源 |
| IXI G07 metrics | `../ixi_pastnet_2p5d/runs/full_g07_ma3_wide200_test115/metrics/summary_metrics.csv` | 正式 test-115 |
| IXI G086 smoke | `../ixi_pastnet_2p5d/runs/smoke_g086_dual_interval/` | 链路验证，不是研究结果 |
| IXI G086 full | `../ixi_pastnet_2p5d/runs/full_g086_dual_interval160_test115/` | 当前不存在正式 best checkpoint |

若某个表格与 CSV 冲突，以对应 run 下的 `summary_metrics.csv`、`per_case_metrics.csv`、`training_history.csv` 和 `run_manifest.json` 为准。

## 4. 已归档文档时间线

| 阶段 | 归档位置 |
|---|---|
| Design1 原始蓝图 | [reference/original_design_blueprint_20260706.md](reference/original_design_blueprint_20260706.md) |
| 初版 full 分析 | [experiments/01_initial/fastmri_v1_full_analysis_20260715.md](experiments/01_initial/fastmri_v1_full_analysis_20260715.md) |
| MA2 分析 | [experiments/01_initial/fastmri_ma2_full_analysis_20260716.md](experiments/01_initial/fastmri_ma2_full_analysis_20260716.md) |
| G01-G10 架构与命令 | [experiments/02_g01_g10/architecture_sweep_20260723.md](experiments/02_g01_g10/architecture_sweep_20260723.md) |
| G01-G10 正式结果 | [results/g01_g10_full200_results_20260806.md](results/g01_g10_full200_results_20260806.md) |
| G071-G075 | [experiments/03_g071_g075/optimization_context_20260806.md](experiments/03_g071_g075/optimization_context_20260806.md) |
| IXI G07 正式结果 | [results/ixi_g07_test115_results_20260811.md](results/ixi_g07_test115_results_20260811.md) |
| G076-G080 | [experiments/04_g076_g080/latent_interval_20260820.md](experiments/04_g076_g080/latent_interval_20260820.md) |
| G081-G085 | [experiments/05_g081_g085/aggressive_methods_20260829.md](experiments/05_g081_g085/aggressive_methods_20260829.md) |
| G086-G090 | [experiments/06_g086_g090/sparse_window_20260905.md](experiments/06_g086_g090/sparse_window_20260905.md) |
| IXI G086 预注册与命令 | [experiments/07_cross_dataset/ixi_g086_generalization_20260907.md](experiments/07_cross_dataset/ixi_g086_generalization_20260907.md) |
| 滚动研究时间线 | [results/research_timeline_20260722_20260907.md](results/research_timeline_20260722_20260907.md) |
| 三数据集 baseline 主表 | `../../docx/experiment/experiment_master_table.md` |

## 5. 目录维护规则

1. 新会话只在本目录更新 Design1 的交接结论；`experiments/` 与历史 `results/` 作为不可变实验记录。
2. 新模型若是根本性重构，建立 `design/pastnet_v2/`，不要继续把 G091+ 塞进 76k 行的旧 `settings.py`。
3. 旧 run 不覆盖、不改名；新 run 使用唯一 profile 名并生成 manifest。
4. smoke 与 full 分开；任何报告表只接受 full。
5. 训练中断时从明确 checkpoint 恢复，禁止静默覆盖 best。
6. 原始逐病例 CSV 永远保留；Markdown 只做摘要，不替代原始证据。
