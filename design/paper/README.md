# MRI 层间插值双论文项目

当前 CVPR 科学版本为 **Plan 17（2026-09-11）**：共享测量影响框架、条件协方差命题、Algorithm 1、真实误差图和完整证据审计。TMI 保持 Plan 15 科学证据与 Plan 16 图稿版本。

| 文档 | 当前 PDF | 内容 |
|---|---|---|
| CVPR 正文 | [main.pdf](CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.pdf) | 8 页；技术内容止于第 7 页；4 张核心图、2 张主表 |
| CVPR 补充 | [supplement.pdf](CVPR/CVPR_ARCH_GENERALIZED/PAPER/supplement.pdf) | 20 页；审计、推导、失败评分、完整 baseline 和预算分析 |
| TMI 正文 | [main.pdf](TMI/TMI_ARCH_GENERALIZED/main.pdf) | 11 页；本轮未改动 |
| TMI baseline 补充 | [baseline_supplement.pdf](TMI/TMI_ARCH_GENERALIZED/baseline_supplement.pdf) | 5 页；本轮未改动 |

Plan 17 修正历史影响量公式描述、前瞻性措辞及排序估计对象，新增去自比较敏感性。唯一 acquired-only guard 未证实优越性；0 阳性内部评价与每配对仅 2 阳性的 IXI 结果完整保留，不声称真正未触及确认。没有新增训练或外部投稿。

## 当前入口

- [详细中文报告](PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/FINAL_REPORT_ZH.md)
- [三位严格审稿人、自评和最高价值后续实验](PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/HOSTILE_REVIEW_ZH.md)
- [证据审计](PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/research_audit.md)、[研究台账](PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/research_ledger.json)、[实验登记](PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/experiment_registry.csv)
- [主张证据矩阵](PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/claim_evidence_matrix.md)、[运行说明](PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/RUN_COMMANDS_ZH.md)
- [保护和构建验证](PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/outputs/final_verification.json)
- [本地审阅包](PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/delivery/CVPR_PLAN17_REVIEW_PACKAGE.zip)

## 既有 baseline 和历史版本

13 模型、111 配置、555 指标值、3,735 行病例结果继续全部使用；CVPR 完整主表和 20 项预算分析现在位于补充材料，TMI 保持原位置。15 项预算 MAE 同时区间支持改善、5 项跨零；13 个重建 baseline 不等于 13 架构物理干预验证。原生全平面指标与共同支撑 QA 不混算。

- [Plan 15 完整 baseline 整合报告](PLAN15_BASELINE_INTEGRATION/FINAL_REPORT_ZH.md)、[逐方法使用情况](PLAN15_BASELINE_INTEGRATION/BASELINE_USE_MAP_ZH.md)
- [Plan 16 历史图稿报告](PLAN16_RESEARCH_DIAGRAMS/FINAL_REPORT_ZH.md)
- [Plan 14 报告](PLAN14_SCIENTIFIC_STRENGTHENING/FINAL_REPORT_ZH.md)、[Plan 13 报告](PLAN13_EVIDENCE_UPGRADE/FINAL_REPORT_ZH.md)
- [Plan 12 报告](ARCHIVE/PLANS/PLAN12_STRICT_REVIEW_ITERATION/STRICT_REVIEW_ITERATION_REPORT_ZH.md)

所有新产物保存在 paper 内。Plan 17 改稿前的 162 个文件由快照保护，根 README、原始数据和 TMI 未改动。A 类提交资料由用户处理；当前仍是研究候选稿，不能给出可校准的录用概率。
