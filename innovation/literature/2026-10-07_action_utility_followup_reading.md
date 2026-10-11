# 动作收益候选的增量查新记录

按 [事前查询](2026-10-07_action_utility_followup_search_protocol.md) 执行三条 Europe PMC 查询，响应及 SHA 位于 `source_cache/action_utility_followup_2026-10-07/attempt01.json`。hit_count 分别 1116、57、53，每条仅取 8 行，共 24 行、22 个唯一 source/id；没有穷尽全部命中，不是系统综述。第一/第二查询没有发布日期硬过滤，第三截止 2026-10-07；索引记录不等于已核全文或临床证据。

以下为实际重点摘要阅读，本阶段新增摘要 3 篇。Hsu 的各向同性异常检测摘要已在前阶段读过，本次再次查看，计重复 1 篇，不能算新增。HCC 已取得正文，本阶段新增完整阅读 1 篇，另见 [HCC 核读](2026-10-07_hcc_sr_task_primary_reading.md)。其余返回项只作题名/索引筛选，不算摘要/全文读完。

| 论文 | 核读程度 | 与本项目的直接关系 | 尚未核实 |
|---|---|---|---|
| Yang 等，Agentic Image Restoration Links Closed-Loop Controllers with Protocol-Aware Evaluation，DOI 10.20944/preprints202609.1256.v1 | 仅完整摘要，预印本；公开 PDF 路由 HTTP 403 | 闭环恢复已有 perception/decision/action/reflection 的分类，明确工具池、反馈和预算混淆，不能以 agentic/control 改名主张首创 | 无全文；不能用综述摘要证明具体机制/基线覆盖或性能 |
| Jiang 等，3D segmentation framework for whole-brain segmentation from thick-slice brain MRI，DOI 10.1016/j.jneumeth.2026.110834 | 仅完整摘要，索引注明 subscription | BSR 补缺层后用薄层训练 nnU-Net 分割，IBSR18/LPBA40/OASIS；直接排除“补层辅助 3D 分割”的宽创新表述 | 3.6%/1.2% 的准确端点、相对/绝对定义、完整患者隔离、降采样算子、PCHIP、预算匹配和所有退化结果缺正文 |
| Gou 等，LRD-ESR-Net，DOI 10.1109/tmi.2026.3662706 | 仅完整摘要，索引注明 subscription | 低分辨率残差解耦、edge-prior residual-shifting diffusion 的伪健康图像，再评病灶分割/术前后配准；不是病灶保真恢复目标 | 无完整架构、训练合同、任务网适配或具体收益预测机制，不能由题名认定本候选已被覆盖 |
| Hsu 等，Self-supervised isotropic reconstruction for abnormality detection in anisotropic MRI，DOI 10.1016/j.compmedimag.2026.102786 | 此前读过摘要，本次重复核看 | 各向同性 SR、健康 counterfactual、异常图和分割体积已有先例；不算新增 | 缺正文，不复述其宣传性摘要为已独立验证事实 |

Agentic 失败记录是出版社 HTTP 403，不是自动审批拒绝。此次没有绕过访问控制、不联系作者；未取得全文不能记作已读正文。保留失败原 JSON，暂不重复同路由请求。

## 候选如何进一步收窄

此前已读 SafeRestore/MoEDiff 和 task-aware/UQ 先例，故“学习何时恢复”“让恢复帮助任务”“用风险选择动作”本身都不新。尚可检验的问题为：在充分适配的任务网络之上，部署只看真实 observed，预测固定缺层修正动作的**配对病灶任务增益**，是否优于同预算/同观测的普通误差头、风险头、直接任务与强 PCHIP。

本次 HCC 原文要求保留混合端点和不显著差异；Jiang 摘要要求加入 SR + 强 3D 分割的直接基线。Agentic 摘要提醒训练/动作评估/推理预算需一起报告。LRD-ESR 摘要表明“恢复原病灶”和“生成无病灶 counterfactual”的目标必须精确区分，不能把两者的任务结果混作正证据。

本项目旧线性/QDA/addback 失败、风险排序反例和 45 CISS 负结果不能因新名称删掉。当前单 series 拟合仍待低 LR 两臂评分；正式 19 series 强适配、已见验证能力、收益残余和固定信息合同这些条件完成后才值得训练收益预测器。八确认继续关闭。本报告不证明领域首次，也不证明候选可发表。
