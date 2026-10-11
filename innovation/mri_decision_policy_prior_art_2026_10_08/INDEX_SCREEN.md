# 索引筛查及阅读范围

实际执行的三条查询见 [原始 receipt](index_attempt01/receipt.json)。每条返回 8 行，共 24 行；排序更正见 [说明](INDEX_ORDER_CLARIFICATION.md)。这是受限候选检索，没有进行完整系统综述，不支持“无人做过”的结论。

本接续先读取全部 24 个标题，再按组完整读取 24 条摘要：mri_RL_state 的 8 条见工具 33ee7a，downstream_selection 的 8 条见 f96f3f，mri_task_decision 的 8 条见 2b43c8。前一整份输出截断不计完整摘要阅读。以下表述都只是摘要筛查，只有明确选中的两篇计原文阅读。

| 索引 ID | 标题／摘要筛查决定 |
|---|---|
| 2212.02190v3 | L2SR，采样／恢复交替优化、终端收益、策略费用；选原文 |
| 2305.13979v1 | 模拟 MRI scanner 控制／phantom 识别；非固定临床观测，对本轮次要 |
| 2508.04727v2 | 心脏径向采样 RL／解剖 reward；记录待读全文，不认定真实病灶收益 |
| 2602.00348v1 | MASC，metal 模拟 paired data／PPO／U-Net joint vs frozen；记录待读原文，不将模拟伪影当真实植入物患者 |
| 2007.10469v2 | Active MR k-space Sampling，旧采样先例候选；本轮不新增核读 |
| 2312.04327v1 | Cartesian MRI thesis，摘要指出 RL 相比 stochastic LBCS 提升有限；强静态控制线索，原文未读 |
| 2406.16754v1 | The MRI Scanner as a Diagnostic: Image-less Active Sampling，直接诊断收益策略；选原文 |
| 2308.14946v1 | temporal medical sampling／fixed autoencoder，摘要 proof of concept；原文未读 |
| 2609.18368v2 | semantic CSI／beam selection，非 MRI，不能外推医学效果 |
| 2408.08736v2 | TADT，按图像／放大尺度预测计算路径；“task”是 SR 推断条件，非病灶标签；待原文核费用 |
| 2601.10192v1 | OPIR，degradation operator／uncertainty two-stage restoration；原文未读 |
| 2605.00310v2 | GeoSR-Bench，下游任务与 fidelity 不一致，遥感领域；非 MRI 新证据 |
| 2604.10904v1 | medical reconstruction downstream fairness／classification／segmentation；值得后续读，不据摘要提出公平性新 claim |
| 2511.04920v1 | IMDNet，多退化表征驱动路径；原文未读 |
| 2205.14526v1 | tabular feature space reconstruction，不是医学图像恢复 |
| 2411.05742v1 | graph feature space reconstruction，不是医学图像恢复 |
| 2106.06742v3 | T²Net，MRI 重建与 SR 多任务，不等于病灶下游任务；原文未读 |
| 2512.17137v2 | SDUM，多协议／cascade conditioning／DC；与固定 CISS 的策略收益不同，原文未读 |
| 2105.07495v2 | Capsule GAN prostate SR，下游 cancer classifier 评价；不是本轮新核读 |
| 2304.12507v3 | TACKLE 已有原文阅读，本轮仅返回摘要，不重计 |
| 2505.09565v1 | fetal meta-SVR，motion／多片重建；“480 reconstructions”不换算成患者，原文未读 |
| 2512.24674v1 | 多维 MRI disentangled representation／zero-shot adaptation；原文未读 |
| 2610.08109v1 | foundation cardiac MRI；receipt published=2026-10-06，不由编号猜日期，原文未读 |
| 2506.23701v1 | MDPG，latent/image priors／DC；原文未读 |

两篇选中文献在本次旧 Markdown 与 READING_PROVENANCE 的 ID／标题查重中未找到既有阅读记录，新增原文核读分别是 L2SR 的 24 个完整文字页、Diagnostic 的 9 个完整文字页。详见 [原文笔记](PRIMARY_READING.md) 和 READING_PROVENANCE.json。摘要条数不是新增全文篇数。

待读顺序优先 MASC 的 joint/frozen 与模拟分母，其次 thesis 的强静态策略、TADT 的控制器费用、medical fairness 的任务端点；本轮未下载这四篇，不添造实验细节，也不重试既有受限全文路由。
