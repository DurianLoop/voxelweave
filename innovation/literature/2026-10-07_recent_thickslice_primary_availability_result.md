# 已知三篇厚层/伪健康恢复论文的原文取得状态

本次只核精确DOI公开索引，没有新增原文或摘要阅读。三篇皆一条精确Europe PMC MED记录，`isOpenAccess=N`、无pmcid，fullTextUrlList只列“Subscription required” DOI。这个结果限于本次索引路径，不能证明所有作者预印本渠道不存在，也不能称已核正文/图表。

| 已知论文 | DOI | PMID | 本次取得程度 |
|---|---|---|---|
| Jiang等，3D segmentation framework for whole-brain segmentation from thick-slice brain MRI | 10.1016/j.jneumeth.2026.110834 | 42314995 | 只核元数据；此前摘要阅读保持 |
| Gou等，LRD-ESR-Net | 10.1109/tmi.2026.3662706 | 41662552 | 只核元数据；此前摘要阅读保持 |
| Hsu等，Self-supervised isotropic reconstruction for abnormality detection in anisotropic MRI | 10.1016/j.compmedimag.2026.102786 | 42378935 | 只核元数据；此前重复摘要不增计 |

初次脚本采用环境代理127.0.0.1:9，连接WinError10061拒绝；随后`sha(__file__)`未转Path导致记录写出前AttributeError，实际tool exit1。失败源码/失败receipt保留。v2只对本次公开GET禁用该不可用本地代理，没有更改系统代理或访问订阅内容，修复Path参数后实际exit0，保存3响应及SHA。没有自动审批拒绝、没有作者联系、没有绕过访问控制，Agentic旧403路由不重试。

Jiang摘要仍只支持“补层后强3D分割已有直接先例”的有限判断；不能据此认定其PCHIP/预算/患者隔离已核。Gou/Hsu伪健康或counterfactual目标也不能混成病灶保真正证据。本次未取得正文，候选的defer/cost-sensitive降级判断仍来自前两篇真正已读原文，不把题名检索升级为方法排重完成。

[原摘要记录](2026-10-07_action_utility_followup_reading.md) · [原始失败](source_cache/recent_thickslice_primary_availability_2026-10-07/attempt01_failure_receipt.json) · [实际取得与SHA](source_cache/recent_thickslice_primary_availability_attempt02_2026-10-07/attempt01.json)。
