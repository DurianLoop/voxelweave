# 本轮入口：文献、冻结预测 ROI 和真实 MRI 输入成本

本轮是实质progress，尚未达成可发表claim。已完成两项新CPU探索并独立核验，补读两篇正式会议原文。GPU授权有效，最新查询剩余1394MiB、总24455MiB、利用率90%，未达新GPU8GB余量；原训练session99542持续推进，没有重启、迁移或操作用户终端进程。

- [冻结ROI成本结果](MC_RC_OBSERVED_ROI_CACHE_COST_RESULT_2026-10-07.md)：16系列/8患者、64支持、3456缺层记录。主joint_QDA条件forward省55.1371%，但旧前景覆盖5.3781%、旧ROI gates0/16；低覆盖是旧事实，新结果是当前窗口成本。
- [真实MRI输入探针结果](MC_RC_OBSERVED_ROI_REAL_INPUT_PROBE_RESULT_2026-10-07.md)：16系列/64候选、4156窗口逐位核验，实际k全部等于几何k，anchors/tail不变。包括1次失败后成功独立重放，共33次observed包数组读取、0新GT/完整native/模型forward。
- [两篇原文阅读](literature/2026-10-07_temporal_cache_primary_reading.md)：Skip-Convolutions2021与MotionDeltaCNN2023，20PDF页取得、17页文字核读、4页实际视觉核看。任务门控/预算/ROI/cache已有先例；明确作者的信息来源、部分计时、历史context及batch限制。
- [创新候选和后续验证](OBSERVED_ROI_TO_NET_BENEFIT_CLAIM_PREPARATION_2026-10-07.md)：优先强基线能力、合法定位、剩余净收益和完整费用，然后同预算控制与冻结确认。

所有失败原版本/JSON和真实tool exit保留；tuple/list断言问题及独立观测hash字段引用问题均新版本修复，没有调整科学配置。本轮完整账本、对话和冻结hash见同名前缀SESSION文件及[literature manifest](literature/observed_roi_stage_manifest_2026-10-07.json)。

最新已观察训练native11286、invocation02新增11187、累计25168.02466809994秒（tool8088b4）；该工具返回同一live session，没有terminal exit。PCHIP99是历史状态；两臂各19998/总39996正式预算、原56FOV、全部6能力gates、strict和真实19系列最终模型资格仍待执行。没有当前病灶线确认患者或新风险证书，旧MIRA/MSValid84确认保留。
