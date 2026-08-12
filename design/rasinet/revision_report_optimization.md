# 优化阶段修订报告

| 修改前问题 | 实际修改 | 文件/结果 | 状态 | 投稿影响 |
|---|---|---|---|---|
| 模型库范围不清 | 审计 11 个通用神经模型、2 个解析模型及 factor-4 扩展模型；检查 identity、shape、affine、finite、OOF fold | `outputs/optimization/MODEL_BANK_AUDIT.md` | 完成 | 提高复现性 |
| 候选选择可能接触测试集 | 固定 IXI/fastMRI development 与 NingXia validation，验证前序列化四个 finalist 及 hash | `configs/selection_protocol.yaml`, `frozen_finalists.yaml` | 完成 | 消除主要泄漏疑虑 |
| 方法仅是 median difference | 评价 132 个原子候选、40 个 score–committee 候选、shared/target decomposition | `candidate_registry.csv` 等 | 完成 | 技术质量提高；算法新颖性仍有限 |
| 委员会扩充缺乏迁移证据 | 宁夏 ×2/×4/×6 一次性冻结验证，2,000 次 bootstrap | `finalist_validation_*.csv` | 完成 | 揭示开发选择不迁移，避免夸大 |
| target-specific 解释过强 | 计算 matched/mismatched attribution matrix；验证优势 −0.008 至 0.014 | `target_attribution_results.csv` | 完成 | 收紧为 target-conditioned ranking |
| 跨倍率一致性未验证 | 检查 138 个 same-case 比较，全部因 shape/support 不兼容判定不可直接计算 | `cross_scale_consistency_feasibility.csv` | 完成检查 | 限制相应主张 |
| 表格可能手抄 | 新表格、汇总、Pareto 和 transfer 图由 CSV 自动生成 | `generate_optimization_assets.py` | 完成 | 降低数值漂移 |
| regular 叙事暗示普遍提升 | 重写为 selection/transfer/failure-boundary 故事，保留预设 baseline | `paper_icassp_regular_optimized.tex` | 完成 | 可信度提高，正向 SOTA 叙事减弱 |
| 扩展稿缺少完整筛选链 | 加入候选漏斗、冻结表、宁夏验证与负迁移解释 | `paper_extended_optimized.tex` | 完成 | 完整性提高 |
| PDF 合规风险 | 编译 5 页 regular 和 9 页 extended；修复新图 Type 3 字体；检查引用与溢出 | PDF/log/preflight | 完成 | 满足格式硬要求 |

## 真实运行结果变化

开发集 universal mean nAURC 从 baseline 的 0.089 改善至 0.040，但宁夏验证从 0.070 恶化到 0.116。low-cost 验证为 0.080，未建立优越性。最终推荐因此保持预设 baseline，而不是开发集最优方案。

