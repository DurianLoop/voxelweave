# Plan 14 声明与证据映射

所有路径相对于本目录。Plan 13 原始结论保持历史身份；其模型库 mask／成员解释由本轮 SOURCE_CORRECTIONS_ZH.md 更正。

| 声明 | 可复算输入与结果 | 稿件位置 |
|---|---|---|
| 模型库预测掩膜及成员来源 | [原预测复算](outputs/bank_mask_raw_reproduction.csv)、[manifest](outputs/bank_mask_manifest.json)、[原始脚本](scripts/bank_mask_audit.py) | 两稿支持定义；CVPR 补充 Section 15 |
| 三种评分支持的受益关联 | [全部模型相关](outputs/bank_mask_correlations.csv)、[预算](outputs/bank_mask_budgets.csv)、[配对差异](outputs/bank_mask_paired_differences.csv) | TMI retrospective consequence；CVPR 补充 |
| fastMRI 患者划分与 DICOM | [划分](outputs/fastmri_split_audit.json)、[几何](outputs/fastmri_test24_geometry.json) | 两稿方法／限制 |
| IXI 评分／端点单位交叉 | [相关](outputs/ixi_scale_contract_correlations.csv)、[预算](outputs/ixi_scale_contract_budgets.csv)、[源哈希](outputs/ixi_scale_contract_manifest.json) | TMI 受益结果；CVPR 补充四格图 |
| TopCoW 局部增益与血管负边界 | [逐平面](outputs/topcow_per_plane.csv)、[病例](outputs/topcow_per_case.csv)、[效应](outputs/topcow_effects.csv)、[排名](outputs/topcow_rankings.csv)、[风险](outputs/topcow_risk_coverage.csv) | 两稿外部实验；补充完整协议 |
| 固定估计器倍率对照 | [病例受益](outputs/topcow_benefit_per_case.csv)、[预算](outputs/topcow_benefit_budgets.csv) | TMI 外部结果；CVPR 补充 |
| TopCoW 探索性亮区规则 | [排名](outputs/bright_anchor_rankings.csv)、[覆盖](outputs/bright_anchor_coverage.csv)、[执行来源](outputs/bright_anchor_manifest.json) | TMI 解剖段落；CVPR 补充八行表 |
| CAS2023 固定规则迁移 | [逐平面](outputs/cas_transfer_per_plane.csv)、[病例](outputs/cas_transfer_per_case.csv)、[排名及风险](outputs/cas_transfer_rankings.csv)、[源哈希](outputs/cas_transfer_manifest.json) | TMI 摘要／主图／结果；CVPR 补充 |
| 历史五架构及条件相关 | [Plan 13 映射](../PLAN13_EVIDENCE_UPGRADE/CLAIM_EVIDENCE_MAP.md)，来源解释以上述更正为准 | 原主结果保持；未当作新增试验 |
| 文件保护与构建 | [原始快照清单](original_manifest.json)、[数值验证](outputs/verification.json)、[编译](build_logs/build_audit.json) | 本轮交付审计 |

L/C 是固定解析估计器，不是新神经架构。disjoint 的分歧值需要互补 phase-2 测量；亮区 mask 本身只需 phase-0 锚点。不能把该结果描述为无需额外测量的普遍获益。
