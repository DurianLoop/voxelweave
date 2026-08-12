# RASI 可信性论文发表执行清单

总目标：把 Design 3 从当前 post-hoc reliability 证据推进到一篇可投稿论文。当前已经完成的 post-hoc 分析只是第一阶段证据，不是终点；后续不再以“低算力”为边界，而是按论文价值继续补充 TTA、learned uncertainty、跨数据集统计、消融、可视化、写作和返修材料。

当前论文定位暂定为：

> 面向医学层间插值的 post-hoc reliability / failure-awareness 框架：不替换已有强重建模型，而是在 I3Net、HAT、SwinIR、ACSI 等模型输出之上构建低成本 uncertainty proxy，用于错误定位、风险覆盖和失败 case 检测。

当前阶段方向决策：

- 主 proxy：`baseline_disagreement`。它在三数据集的 pixel/nonzero correlation、risk-coverage 和 failure detection 上最适合作为主线。
- 辅助 proxy：`residual_linear`、`residual_cubic`、`TTA variance`。它们进入 proxy ablation / supplementary，不替代主 proxy。
- TTA 结论：三数据集 SwinIR TTA variance 的 slice-level correlation 明显更强，但 pixel-level correlation 和 risk-coverage 不稳定优于 `baseline_disagreement`。
- learned uncertainty head：暂不启动 full training；只作为 reviewer 追问时的备用 ablation 或后续工作。
- 接下来优先级：先生成论文主表、主图、paper outline 和 reviewer response notes，再决定是否需要新增训练型实验。

文档与代码统一放在 `D:\MRI\rasinet`：

- 代码：`rasinet/posthoc_uncertainty.py`
- QC 代码：`rasinet/posthoc_qc.py`
- 报告代码：`rasinet/posthoc_report.py`
- 运行输出：`rasinet/runs/posthoc_uncertainty/`
- 分析报告：`rasinet/reports/posthoc_uncertainty/`

## 0. 论文方向锁定

- [x] 重新核对 `docx/design/design3_rasinet_reliability.md`。
- [x] 重新核对 `docx/design/design_overview_table.md`。
- [x] 重新核对 `docx/design/design3_rasinet_next_guide.md`。
- [x] 确认当前路线是 post-hoc uncertainty analysis，不是 full RASI-Net training。
- [x] 确认 linear/cubic 不是主比较对象，只作为 coarse/reference 信号参与 proxy 构造。
- [x] 确认后续文档和代码都集中放在 `rasinet/` 专门目录下。
- [x] 明确论文题目候选。
  - 候选：`Post-hoc Reliability-Aware Slice Interpolation for Medical MRI`
  - 候选：`Failure-Aware Uncertainty Proxies for MRI Through-Plane Interpolation`
- [ ] 明确目标投稿层级。
  - 备选：MICCAI workshop / ISBI / IEEE JBHI / Medical Image Analysis 短线预研。
  - 需要根据完整实验强度再定。
- [x] 明确论文核心贡献数量。
  - 建议 3 个贡献：post-hoc uncertainty proxy、risk/failure evaluation protocol、三数据集验证。

## 1. 代码与运行产物

- [x] 新增 post-hoc 分析入口：`rasinet/posthoc_uncertainty.py`。
- [x] 使用已有 full_test115 预测：I3Net、HAT、SwinIR、ACSI。
- [x] 增加逐 case 进度输出，避免 full run 看起来无反应。
- [x] 跑通 smoke。
  - 输出：`rasinet/runs/posthoc_uncertainty/smoke/metrics/`
- [x] 跑通 mini。
  - 输出：`rasinet/runs/posthoc_uncertainty/mini/metrics/`
- [x] 跑通 full_test115。
  - 输出：`rasinet/runs/posthoc_uncertainty/full_test115/metrics/`
- [x] 确认 full_test115 输出文件齐全：
  - `paper_table_posthoc.md`
  - `summary_posthoc_reliability.csv`
  - `per_case_posthoc_reliability.csv`
  - `risk_coverage_posthoc.csv`
  - `calibration_bins_posthoc.csv`
  - `failure_detection_posthoc.csv`

## 2. full_test115 当前结果快照

- [x] full profile 完成 115 个 IXI case。
- [x] 方法包括：`i3net`、`hat`、`swinir`、`acsinet`。
- [x] proxy 包括：
  - `baseline_disagreement`
  - `residual_linear`
  - `residual_cubic`
- [x] 首轮结论记录：
  - `swinir__baseline_disagreement`：pixel corr `0.6153`，slice corr `0.4572`，failure AUROC `0.9871`。
  - `hat__baseline_disagreement`：pixel corr `0.6090`，slice corr `0.4578`，failure AUROC `0.9871`。
  - `acsinet__baseline_disagreement`：pixel corr `0.5667`，slice corr `0.4178`，failure AUROC `0.9871`。
  - `i3net__baseline_disagreement`：pixel corr `0.5018`，slice corr `0.3567`，failure AUROC `0.9822`。

## 3. QC 检查

- [x] 确认 115 个 case 在 GT、linear、cubic、I3Net、HAT、SwinIR、ACSI 之间全部对齐。
  - 结果：`115/115` shape aligned。
  - 文件：`rasinet/reports/posthoc_uncertainty/full_test115/qc_alignment_summary.csv`
- [x] 生成 per-case manifest，记录每个 case 使用的输入路径。
  - 文件：`rasinet/reports/posthoc_uncertainty/full_test115/qc_manifest.csv`
- [x] 检查 proxy 是否只在 x4 generated slices 上评价。
  - 结果：所有 method/case 行 `mismatched_rows = 0`。
  - 文件：`rasinet/reports/posthoc_uncertainty/full_test115/qc_generated_slice_summary.csv`
- [x] 检查背景区域是否支撑了 pixel-level correlation。
  - 结果：背景比例均值约 `0.5894`，全像素 corr 确实高于非零区域 corr。
  - 文件：`rasinet/reports/posthoc_uncertainty/full_test115/qc_mask_background_summary.csv`
- [x] 增加非零脑区 / masked 版本评价。
  - `swinir__baseline_disagreement`：all pixel corr `0.6153`，nonzero corr `0.4711`。
  - `hat__baseline_disagreement`：all pixel corr `0.6090`，nonzero corr `0.4628`。
  - `acsinet__baseline_disagreement`：all pixel corr `0.5667`，nonzero corr `0.4037`。
  - `i3net__baseline_disagreement`：all pixel corr `0.5018`，nonzero corr `0.3068`。
  - 结论：非零区域仍保持正相关，但应优先报告 masked/nonzero 版本，避免被质疑背景抬高结果。
- [x] 比较 pixel-level 与 slice-level 结论，标出分歧 case。
  - 文件：`rasinet/reports/posthoc_uncertainty/full_test115/qc_pixel_slice_disagreement.csv`
  - 摘要：`baseline_disagreement` 的 large-gap case 约 `24-25` 个；residual proxy 分歧更多。
- [x] 检查 failure case 排名。
  - 文件：`rasinet/reports/posthoc_uncertainty/full_test115/qc_failure_case_review.csv`
  - 高误差 case 示例：`IXI014-HH-1236-T2.nii.gz` 在多个方法中同时位于 error rank 1 和 uncertainty rank 1。
- [x] 写出第三步 QC 总结。
  - 文件：`rasinet/reports/posthoc_uncertainty/full_test115/qc_step3_summary.md`

## 4. 表格整理

- [x] 生成干净的 full_test115 reliability 中文总结表。
  - 源：`rasinet/runs/posthoc_uncertainty/full_test115/metrics/summary_posthoc_reliability.csv`
  - 目标：`rasinet/reports/posthoc_uncertainty/full_test115/full_test115_summary.md`
- [x] 生成 proxy 对比表：
  - `baseline_disagreement` vs `residual_linear` vs `residual_cubic`
- [x] 生成方法对比表：
  - I3Net vs HAT vs SwinIR vs ACSI，在同一个 proxy 下比较。
- [x] 生成 failure detection 表：
  - AUROC、AUPRC、top-k recall。
- [x] 生成 masked/nonzero 版本主表。
- [x] 暂不写入 `docx/experiment/experiment_master_table.md`，等结果更适合论文主表后再迁移。

## 5. 图表

- [x] 画 `baseline_disagreement` 的 risk-coverage 曲线。
  - 文件：`risk_coverage_baseline_disagreement.png`
- [x] 画所有 method/proxy 的 correlation bar chart。
  - 文件：`correlation_all_method_proxy.png`
- [x] 画 masked vs all-pixel correlation 对比图。
  - 文件：`masked_vs_all_correlation.png`
- [x] 画 failure ranking / top-k recall 图。
  - 文件：`failure_detection_baseline_disagreement.png`
- [x] 图全部输出到：
  - `rasinet/reports/posthoc_uncertainty/full_test115/figures/`

## 6. 可视化 case review

- [x] 选择 top 5 high-risk/high-error case。
  - 文件：`rasinet/reports/posthoc_uncertainty/full_test115/visual_qc_case_selection.csv`
- [x] 选择 top 5 low-risk/low-error case。
  - 文件：`rasinet/reports/posthoc_uncertainty/full_test115/visual_qc_case_selection.csv`
- [x] 选择 3 类 mismatch case：
  - high uncertainty but low error。
  - low uncertainty but high error。
  - pixel corr 与 slice corr 分歧明显。
- [x] 保存 prediction、absolute error、uncertainty proxy 三联图。
  - 文件夹：`rasinet/reports/posthoc_uncertainty/full_test115/figures/visual_qc/`
- [x] 写一份视觉 QC 说明，判断 uncertainty 是否集中在解剖边界、结构变化或失败区域。
  - 文件：`rasinet/reports/posthoc_uncertainty/full_test115/visual_qc_case_review.md`

## 7. 解释与论文表述

- [x] 判断 `baseline_disagreement` 是否作为主 proxy。
  - 结论：作为当前 IXI full_test115 主 proxy。
- [x] 判断 residual proxy 是否只作为 sanity / ablation。
  - 结论：只作为 sanity / ablation，不作为主故事。
- [x] 写保守主张：
  - 现有强插值方法可以外挂 post-hoc reliability signal。
  - baseline disagreement 与重建误差、失败 case 有稳定关系。
  - 这是 reliability layer，不是一个新的 SOTA reconstruction model。
- [x] 写限制：
  - proxy 不是严格校准的概率不确定性。
  - 多模型同时犯错时 disagreement 可能失效。
  - 背景区域会抬高 pixel-level corr，所以需要报告 nonzero/masked 版本。
  - fastMRI / NingXia 还需要跨数据集验证。
  - 文件：`rasinet/reports/posthoc_uncertainty/full_test115/interpretation_notes.md`

## 8. 已完成的跨数据集补强实验

- [x] 如果能增强论文贡献，为一个强模型增加 TTA variance proxy。
  - 状态：已完成 fastMRI SwinIR 24-case、IXI SwinIR full_test115、NingXia SwinIR CV 三套实验。
  - 结论：TTA variance 的 slice-level correlation 明显强于 baseline disagreement，但 pixel-level correlation 和 risk-coverage 不稳定优于主 proxy，因此定位为 proxy ablation / supplementary analysis。
  - 说明：`rasinet/reports/posthoc_uncertainty/tta_variance_feasibility_note.md`
  - 汇总：`rasinet/reports/posthoc_uncertainty/tta_variance_cross_dataset_summary.md`
- [x] 在 fastMRI-brain T2 输出上重复 post-hoc 分析。
  - 输出：`rasinet/reports/posthoc_uncertainty/fastmri_full/`
  - 结果：baseline disagreement nonzero corr `0.2347-0.3500`，failure AUROC `1.0000`。
- [x] 在 NingXia CV 输出上重复 post-hoc 分析。
  - 输出：`rasinet/reports/posthoc_uncertainty/ningxia_cv/`
  - 结果：baseline disagreement nonzero corr `0.2886-0.3137`，failure AUROC `0.9474`。
- [x] learned RASI-Net uncertainty 只作为辅助 ablation，不作为当前主路线。
  - 文件：`rasinet/reports/posthoc_uncertainty/learned_rasi_ablation_note.md`
  - 结论：只保留 IXI mini 5-case 可行性说明，不启动 full RASI-Net training，不进入主表。

## 9. 论文级补强实验

- [x] 决定是否补 TTA variance proxy。
  - 最小版本：只选 I3Net 或 SwinIR，在 fastMRI 24 cases 上跑 4-view flip TTA。
  - 完整版本：IXI full_test115 + fastMRI + NingXia 全部补 TTA。
  - 当前策略：不再因为算力限制搁置；先检查现有推理脚本和 checkpoint，若可复用则启动代表性 TTA 实验。
  - 完成标准：输出与 `baseline_disagreement` 可直接对比的 corr、risk-coverage、failure detection 表。
  - 已完成：fastMRI SwinIR 24 cases，IXI SwinIR full_test115，NingXia SwinIR CV。
  - 当前定位：proxy ablation，不替代 `baseline_disagreement` 主 proxy。
  - 输出：`rasinet/runs/posthoc_uncertainty/fastmri_swinir_tta/metrics/`
  - 输出：`rasinet/runs/posthoc_uncertainty/ixi_swinir_tta/metrics/`
  - 输出：`rasinet/runs/posthoc_uncertainty/ningxia_swinir_tta/metrics/`
  - 输出：`rasinet/reports/posthoc_uncertainty/tta_variance_cross_dataset_summary.md`
- [x] 决定是否补 learned uncertainty head。
  - 当前决策：暂不启动 full learned uncertainty training，不进入主线。
  - 理由：已有 `baseline_disagreement`、residual proxy、TTA variance、bootstrap CI、failure definition ablation 和三数据集验证，已经足够支撑 post-hoc reliability 论文主张；继续开 learned head 会把论文重心拉回训练模型。
  - 保留用途：reviewer 如果追问“为什么不用 learned uncertainty”，再做 IXI mini/full_test115 learned-head rebuttal ablation。
  - 现有说明：`rasinet/reports/posthoc_uncertainty/learned_rasi_ablation_note.md`
- [x] 增加 calibration 指标。
  - ECE-like binning：uncertainty 分桶后比较 mean uncertainty 与 mean error 单调性。
  - Spearman rank correlation：比 Pearson 更适合 monotonic reliability claim。
  - 完成标准：三数据集都有 calibration table / plot。
  - 输出：`rasinet/reports/posthoc_uncertainty/paper_experiments/calibration_monotonicity_summary.csv`
- [x] 增加 statistical confidence。
  - bootstrap 95% CI for pixel corr / nonzero corr / AUROC / AUPRC / top-k recall。
  - paired comparison：baseline disagreement vs residual proxy。
  - 完成标准：主表不只给 mean，还给 CI 或 std。
  - 输出：`rasinet/reports/posthoc_uncertainty/paper_experiments/bootstrap_ci_by_method_proxy.csv`
  - 输出：`rasinet/reports/posthoc_uncertainty/paper_experiments/masked_bootstrap_ci_by_method_proxy.csv`
  - 输出：`rasinet/reports/posthoc_uncertainty/paper_experiments/paired_proxy_comparison_ci.csv`
- [x] 增加 failure definition ablation。
  - MAE top-k failure。
  - SSIM bottom-k failure。
  - 3D consistency worst-k failure。
  - 完成标准：failure detection 不依赖单一 MAE 定义。
  - 当前已完成：MAE top-k、risk-AURC top-k、MAE@50% low-U top-k、SSIM bottom-k、masked-SSIM bottom-k、z-error、3D inter-slice consistency failure。
  - 输出：`rasinet/reports/posthoc_uncertainty/paper_experiments/failure_definition_ablation.csv`
- [x] 增加 domain shift 分析。
  - IXI vs fastMRI vs NingXia 的 proxy 强弱差异。
  - 背景比例 / nonzero mask 对结果的影响。
  - 完成标准：写入 Discussion 或 Experiments。
  - 输出：`rasinet/reports/posthoc_uncertainty/paper_experiments/domain_shift_masked_summary.csv`
- [x] 增加 runtime / storage cost 表。
  - post-hoc disagreement 只需读取已有预测。
  - TTA variance 若补做，需要报告额外推理成本。
  - 完成标准：证明 reliability layer 成本低于重新训练模型。
  - 结果：IXI / fastMRI / NingXia 的新增 post-hoc metrics/report 产物为 MB 级；读取的已有预测目录为 GB 级；当前 post-hoc 不需要训练和 GPU。
  - 输出：`rasinet/reports/posthoc_uncertainty/paper_experiments/runtime_storage_cost.csv`
  - 输出：`rasinet/reports/posthoc_uncertainty/paper_experiments/runtime_storage_cost.md`

## 10. 论文主表与图

- [x] 生成 paper-ready table 脚本。
  - 目标：把当前散落在 `runs/posthoc_uncertainty/*/metrics/` 和 `reports/posthoc_uncertainty/paper_experiments/` 的 CSV 合并成论文主表。
  - 脚本：`rasinet/paper_tables.py`
  - 输出：`rasinet/paper/tables/table_main_reliability.md`
  - 输出：`rasinet/paper/tables/table_failure_detection.md`
  - 输出：`rasinet/paper/tables/table_proxy_ablation.md`
  - 输出：`rasinet/paper/tables/table_runtime_cost.md`
- [x] Table 1：三数据集重建质量背景表。
  - 方法：linear、cubic、I3Net、HAT、SwinIR、ACSI if available。
  - 指标：PSNR、SSIM、MAE、NCC。
  - 目的：说明 reliability 不是和 linear/cubic 比主性能，而是在强模型上做风险估计。
  - 输出：`rasinet/paper/tables/table_reconstruction_context.md`
- [x] Table 2：主 reliability 表。
  - 指标：nonzero corr、slice corr、risk-AURC、MAE@50% low-U。
  - 数据集：IXI、fastMRI、NingXia。
  - 主 proxy：baseline disagreement。
  - 输出：`rasinet/paper/tables/table_main_reliability.md`
- [x] Table 3：failure detection 表。
  - AUROC、AUPRC、top-k recall。
  - 至少包含三数据集。
  - 输出：`rasinet/paper/tables/table_failure_detection.md`
- [x] Table 4：proxy ablation 表。
  - baseline disagreement vs residual-linear vs residual-cubic vs TTA variance。
  - 当前结论应写清楚：TTA variance 的 slice-level signal 强，但不替代 `baseline_disagreement` 主 proxy。
  - 输出：`rasinet/paper/tables/table_proxy_ablation.md`
- [x] Table 5：runtime / storage cost 表。
  - 目的：说明 post-hoc reliability layer 只读取已有预测，不需要重新训练模型。
  - 输出：`rasinet/paper/tables/table_runtime_cost.md`
- [x] Figure 1：方法框架图。
  - 输入：已有多模型 prediction / coarse interpolation / target only for evaluation。
  - 输出：uncertainty proxy、risk-coverage、failure ranking。
  - 输出：`rasinet/paper/figures/figure1_framework.png`
- [x] Figure 2：risk-coverage 曲线。
  - 三数据集各一组，或主文放 IXI + appendix 放全部。
  - 输出：`rasinet/paper/figures/figure2_risk_coverage.png`
- [x] Figure 3：masked vs all-pixel correlation。
  - 用来主动回应背景区域抬高 correlation 的质疑。
  - 输出：`rasinet/paper/figures/figure3_masked_vs_all.png`
- [x] Figure 4：proxy ablation 图。
  - 用来说明 baseline disagreement 与 TTA variance 的互补关系。
  - 输出：`rasinet/paper/figures/figure4_proxy_ablation.png`
- [x] Figure 5：visual QC case panels。
  - high-risk/high-error。
  - low-risk/low-error。
  - mismatch/failure cases。
  - 输出：`rasinet/paper/figures/figure5_visual_qc.png`
- [x] Supplementary Figure：calibration bins。
  - 输出：`rasinet/paper/figures/supp_calibration_bins.png`
- [x] Supplementary Table：per-case failure ranking。
  - 输出：`rasinet/paper/tables/supp_table_failure_ranking.csv`
- [x] Supplementary Table：TTA variance cross-dataset ablation。
  - 来源：`rasinet/reports/posthoc_uncertainty/tta_variance_cross_dataset_summary.md`
  - 输出：`rasinet/paper/tables/supp_table_tta_ablation.md`

## 11. 论文写作

- [x] 写 paper outline。
  - `rasinet/paper/outline.md`
- [x] 写 Introduction。
  - 问题：MRI through-plane interpolation 平均指标不足以提示失败风险。
  - 缺口：现有方法很少报告 post-hoc reliability / failure awareness。
  - 贡献：proxy、protocol、三数据集验证。
- [x] 写 Related Work。
  - MRI slice interpolation。
  - uncertainty estimation。
  - post-hoc confidence / failure detection。
  - risk-coverage / selective prediction。
- [x] 写 Method。
  - baseline disagreement proxy。
  - residual proxy。
  - optional TTA proxy。
  - risk-coverage and failure detection protocol。
- [x] 写 Experiments。
  - datasets。
  - baselines。
  - metrics。
  - implementation details。
  - main results。
- [x] 写 Discussion。
  - 背景区域影响。
  - proxy 非概率校准。
  - 多模型同错风险。
  - 临床使用边界。
- [x] 写 Conclusion。
- [x] 写 Abstract。
- [x] 写 Contributions bullet。
- [x] 写 Limitations paragraph。
- [x] 写 Reproducibility paragraph。
  - 主文：`rasinet/paper/main.tex`
  - 引用：`rasinet/paper/references.bib`
  - Overleaf 说明：`rasinet/paper/README_overleaf.md`

## 12. 投稿前质量控制

- [ ] 所有表格数值可由脚本重生成。
- [ ] 所有图都有脚本、输入 CSV 和输出 PNG。
- [x] 所有主文 claim 都能追溯到 `rasinet/reports/posthoc_uncertainty/` 下的文件。
- [x] 检查没有把 smoke/mini screening 当 full conclusion。
- [x] 检查没有宣称 RASI-Net reconstruction SOTA。
- [x] 检查 linear/cubic 只作为 coarse/reference 或 sanity baseline。
- [x] 检查三数据集 case 数、fold 数、方法数写清楚。
- [x] 检查 mask/nonzero 设置写清楚。
- [x] 检查所有缩写第一次出现有定义。
- [x] 检查图中文字在双栏尺寸下可读。
- [ ] 检查 LaTeX / Word / Markdown 表格和 CSV 数字一致。

## 13. 投稿材料

- [x] 建立论文目录。
  - 建议：`rasinet/paper/`
- [x] 建立 `rasinet/paper/main.tex` 或 `main.md`。
- [x] 建立 `rasinet/paper/figures/`。
- [x] 建立 `rasinet/paper/tables/`。
- [x] 建立 `rasinet/paper/references.bib`。
- [x] 建立 reproducibility README。
  - `rasinet/paper/README_overleaf.md`
- [ ] 建立匿名版 checklist。
  - 删除本地绝对路径。
  - 删除可能暴露身份的目录名。
- [ ] 选择投稿模板。
  - conference: LaTeX。
  - journal: Word/LaTeX 视目标而定。
- [x] 编译 PDF 并做视觉检查。
  - 本地输出：`rasinet/paper/main.pdf`
  - 编译顺序：`pdflatex main.tex` -> `bibtex main` -> `pdflatex main.tex` -> `pdflatex main.tex`
  - 日志检查：无 undefined citation/reference，无 fatal error；仅有正常浮动位置提示。

## 14. 内部审稿与返修准备

- [ ] 自查 reviewer attack list。
  - “这是不是只是模型 ensemble disagreement？”
  - “为什么不是 probabilistic uncertainty？”
  - “背景区域是不是抬高相关性？”
  - “case 数是否足够？”
  - “为什么不用 learned uncertainty？”
- [ ] 为每个 attack 写 response note。
- [ ] 准备 appendix。
  - per-case ranking。
  - all risk-coverage curves。
  - calibration bins。
  - visual QC 全部 case。
- [ ] 准备 rebuttal 备用实验。
  - TTA variance。
  - alternate failure definition。
  - bootstrap CI。

## 15. 命令归档

Post-hoc full：

```powershell
cd D:\MRI
$env:PYTHONPATH=(Resolve-Path .\pre).Path
D:\conda\envs\MRI\python.exe -u -B -m rasinet.posthoc_uncertainty --profile full_test115 --source-set ixi --progress-every 1
```

第三步 QC：

```powershell
cd D:\MRI
$env:PYTHONPATH=(Resolve-Path .\pre).Path
D:\conda\envs\MRI\python.exe -u -B -m rasinet.posthoc_qc --profile full_test115 --source-set ixi --factor 4 --top-k 12 --progress-every 10
```

## 16. 当前下一步执行顺序

- [x] 第一步：生成论文主表。
  - 合并 IXI / fastMRI / NingXia 的主 proxy、masked/nonzero CI、failure detection、TTA ablation 和 runtime/storage cost。
  - 不再新增训练实验，除非主表暴露明显证据缺口。
  - 脚本：`rasinet/paper_tables.py`
  - 输出目录：`rasinet/paper/tables/`
- [x] 第二步：生成论文主图。
  - 三数据集 risk-coverage 曲线。
  - masked vs all-pixel correlation 图。
  - proxy ablation 图，突出 baseline disagreement 与 TTA variance 的互补关系。
  - visual QC case panels。
  - 脚本：`rasinet/paper_figures.py`
  - 输出目录：`rasinet/paper/figures/`
- [x] 第三步：写 paper outline。
  - 先写 `rasinet/paper/outline.md`，锁定题目、贡献、实验结构和主结论。
  - outline 完成后再进入 Introduction / Method / Experiments 正文。
- [ ] 第四步：写 reviewer attack list 和 response notes。
  - 重点回应 ensemble disagreement、probabilistic uncertainty、背景区域抬高 correlation、case 数、learned uncertainty 这五类问题。
- [ ] 第五步：根据主表和 reviewer notes 决定是否还需要补实验。
  - 可能补：learned uncertainty head 小规模 ablation。
  - 可能补：更多 model-level TTA，比如 I3Net TTA。
  - 不建议优先补：重新训练一个完整 RASI-Net reconstruction model。

## 17. 2026-07-15 紧凑论文升级（本轮已完成）

- [x] 修正主方法定义为目标特异委员会分歧，并在代码中强制排除目标模型自身。
  - 代码：`design/rasinet/committee_reliability.py`
  - 公式：`design/rasinet/paper/main.tex`
- [x] 完成三个 full profile，不使用 smoke/mini 支撑论文结论。
  - IXI：115 例，4 个神经目标，2760 条逐例代理记录。
  - fastMRI-brain：24 例，3 个神经目标，432 条逐例代理记录。
  - NingXia held-out CV：22 例，3 个神经目标，396 条逐例代理记录。
- [x] 完成 2000 次病例级 bootstrap、固定覆盖率风险、委员会组成和留一成员分析。
  - 报告：`design/rasinet/reports/committee_reliability/`
- [x] 生成主表、置信区间表、risk-coverage 图、委员会组成图和定性失败案例图。
  - 表格：`design/rasinet/paper/tables/`
  - 图片：`design/rasinet/paper/figures/`
- [x] 完成紧凑双栏英文主文和独立补充材料。
  - 主文：`design/rasinet/paper/main.tex`
  - 补充材料：`design/rasinet/paper/supplement.tex`
- [x] 完成审稿攻击清单，明确 disagreement、概率不确定性、委员会成本和共同失败边界。
  - 文档：`design/rasinet/paper/reviewer_attack_notes.md`
- [x] 完成自动验证和 PDF 逐页视觉检查。
  - 单元测试：23/23 通过。
  - 主文：6 页；补充材料：2 页。
  - 一致性报告：`design/rasinet/paper/consistency_report.md`
- [x] 建立并独立解压验证 Overleaf 最小上传包。
  - 压缩包：`design/rasinet/paper/overleaf_upload_rasinet_compact.zip`

## 18. 投稿与发表剩余事项

- [ ] 根据篇幅、医学影像契合度和截稿日期确定目标会议或期刊。
- [ ] 替换为目标 venue 官方 LaTeX 模板，并再次检查页数和匿名要求。
- [ ] 补全作者、单位、伦理审批、数据可用性和代码可用性声明。
- [ ] 请至少一位未参与实验的人进行内部审稿，并关闭 reviewer attack list 中的剩余问题。
- [ ] 生成最终匿名投稿包并完成投稿系统元数据。
- [ ] 投稿后记录编辑决定、审稿意见、rebuttal 和返修实验。
- [ ] 接收后生成 camera-ready、公开代码版本和可复现实验归档。
