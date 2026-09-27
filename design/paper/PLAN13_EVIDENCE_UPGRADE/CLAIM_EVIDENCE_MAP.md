# Plan 13 主张—证据映射

路径均相对于 `design/paper`；历史结果与本轮探索性结果明确分开。

| 主张/审计 | 精确数据或脚本 | 推断单位 | 边界 |
|---|---|---|---|
| 三队列原始 clean 排名对照 | `CVPR/archive/CVPR_UPGRADE/outputs/clean_max_overlap_summary.json`、`clean_max_overlap_ixi_summary.json` | examination / NingXia patient | 与 reversal、Plan 9/11 的采样/掩膜协议不能混用 |
| fastMRI 五架构原始 gain | `ARCHIVE/PLANS/PLAN9_ARCH_GENERALIZATION/outputs/p9_architecture_forest.csv`；两份 `p9_disjoint_shared_per_plane*.csv`（主文件和 transformer_reference） | 24 examinations | 局部 gain 用 mean/mean；ranking 使用病例内 median |
| IXI 五架构原始 gain | `ARCHIVE/PLANS/PLAN11_CLAIM_STRENGTHENING/outputs/p11_ixi_clean_per_plane_full.csv`、`p11_ixi_clean_model_summary_full.csv` | 115 examinations | 5,750 行不是 5,750 独立样本 |
| reflection-balanced identity-swap | `ARCHIVE/PLANS/PLAN11_CLAIM_STRENGTHENING/outputs/p11_identity_swap_balanced_per_case_full.csv` | 115 examinations | reflection-equivalent，不是完全相同 signed geometry |
| 40 种局部敏感性与排名同时区间 | `PLAN13_EVIDENCE_UPGRADE/outputs/architecture_sensitivity.csv` | 两队列分别 examination bootstrap | 每端点五模型同时覆盖；不覆盖全部历史比较 |
| 598 行原始受益关联 | `ARCHIVE/PLANS/PLAN11_CLAIM_STRENGTHENING/outputs/p11_same_model_benefit_per_case.csv`、`p11_same_model_benefit_correlations.csv` | fastMRI examination / NingXia patient cluster | same-label，不保证同权重 |
| 当前误差条件关联 | `PLAN13_EVIDENCE_UPGRADE/outputs/benefit_coupling.csv` | 同上 | 真值控制变量，回顾性诊断，不是部署分数 |
| NingXia 患者删除与等权 | `PLAN13_EVIDENCE_UPGRADE/outputs/benefit_leave_one_cluster_out.csv`、`benefit_patient_equal.csv` | 八患者 | 后者改变 estimand，非替换原点估计 |
| 29,296 行代数与 MAE 定义核验 | `TMI/archive/TMI_MANUSCRIPT_MASTER/scripts/plan6_consensus_distributions.py`、`experiments/p6_e02_consensus_per_plane.csv`；`PLAN13_EVIDENCE_UPGRADE/outputs/algebra_audit.json` | 描述性逐平面恒等式检查 | κ 不可省略；非独立经验机制证据 |
| 新 IXI I3Net ×2/×4 | `PLAN13_EVIDENCE_UPGRADE/outputs/ixi_i3net_benefit_per_plane.csv`、`ixi_i3net_benefit_per_case.csv` | 115 examinations | 7,334 common odd planes；factor-specific checkpoints |
| IXI 尺度反转与预算负结果 | `PLAN13_EVIDENCE_UPGRADE/outputs/ixi_i3net_benefit_correlations.csv`、`ixi_i3net_benefit_budgets.csv` | examination bootstrap | score normalized，endpoint raw；不能推广所有归一化方案 |
| 全指标重建语境 | `ARCHIVE/PLANS/PLAN9_ARCH_GENERALIZATION/outputs/p9_three_cohort_reconstruction_benchmark.csv` | 24/115 examinations，22 OOF series | 不同支持于新 IXI odd-plane 实验，不补 missing cells |
| HAT/SwinIR fixed-count、有限响应负边界 | CVPR supplement 原有 tables；`CVPR/archive/CVPR_UPGRADE/outputs/plan6_neural_shared_influence_confirm3*`；`ARCHIVE/PLANS/PLAN9_ARCH_GENERALIZATION/outputs/p9_new_arch_influence_stability.csv` | examination/patient cluster | 不支持新架构普适 influence stability |
| 完整负结果保留 | CVPR supplement `Material Negative and Boundary Results`；Plan 13 两稿结果/限制 | 各实验声明单位 | Res-SRDiff、SSIM、归一化、fixed-count、selector 等均未按方向筛除 |

统计脚本为 `scripts/analyze.py`、`scripts/ixi_benefit.py`；图表为 `scripts/figures_tables.py`；独立公式校验为 `scripts/verify.py`。这些脚本均在本阶段目录下。
