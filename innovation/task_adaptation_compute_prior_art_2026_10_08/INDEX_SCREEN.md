# 本轮索引筛查范围

实际公开原始索引为[index_attempt03/receipt.json](index_attempt03/receipt.json)，三GET实际exit0，返回12条：arXiv1+3，Crossref8。此前attempt01 Windows schannel凭据错误、attempt02默认网络连接拒绝均保留；attempt03在批准的公开GET路径下成功，TLS未关闭。无自动审批拒绝。不是对全部MRI计算论文的穷尽搜索。

| 索引返回 | 本轮处理与依据 |
|---|---|
| Task adapted reconstruction for inverse problems, 1809.00948v1 | 原文入选：同观测下分步/直接/联合任务适配以及保留信息条件 |
| Tuning-free Plug-and-Play Proximal Algorithm for Inverse Imaging Problems, 2002.09611v2 | 原文入选：当前状态的相对收益、修正参数和停止策略，含CS-MRI |
| TFPnP: Tuning-free Plug-and-Play Proximal Algorithm with Applications to Inverse Imaging Problems, 2012.05703v3 | 题名/摘要筛查；同作者扩展，不在本轮独立原文统计；后续可核作者代码与完整成本 |
| Tuning-free Plug-and-Play Hyperspectral Image Deconvolution with Deep Priors, 2211.15307v2 | 题名/摘要筛查；HSI residual-whiteness调参/停止，非本项目直接MRI任务原文 |
| Adaptive keyhole methods for dynamic magnetic resonance image reconstruction, 10.1016/j.compmedimag.2007.04.005 | 仅题名/元数据；动态keyhole信息与固定CISS恢复合同不同 |
| Compressed sensing-adaptive regularization for reconstruction of magnetic resonance image, 10.3724/sp.j.1087.2012.00541 | 仅题名/元数据；未取得摘要/正文，不推定其完整动作策略 |
| Efficient adaptive weighted minimization for compressed sensing magnetic resonance image reconstruction, 10.1145/3009977.3009991 | 仅题名/元数据；自适应权重不自动证明早停/任务收益 |
| Adaptive channel-modulated personalized federated learning for magnetic resonance image reconstruction, 10.1016/j.compbiomed.2023.107330 | 仅题名/元数据；personalized federation不是此处预算内动作选择，正文未读 |
| Embedded magnetic resonance image reconstruction using, 10.1109/cibec.2012.6473327 | 仅题名/元数据；索引标题本身截短，身份细节/正文未核 |
| Fast Sparse Magnetic Resonance Image Reconstruction, 10.1109/ibcast54850.2022.9990511 | 仅题名/元数据；不能凭fast推定逐输入compute gate |
| Multi-contrast magnetic resonance image reconstruction, 10.1117/12.2082136 | 仅题名/元数据；新增contrast违反本项目当前同observed输入比较 |
| An investigation of an adaptive modeling algorithm for magnetic resonance image reconstruction, 10.1109/pacrim.1993.407293 | 仅题名/元数据；返回无published字段，不能据DOI猜正文内容 |

Crossref八条没有直接的现代early-exit命中，只说明这个有上限的query.title查询效用较低；既不把它记为八篇已读论文，也不以阴性建立新颖性。额外`rg`只查本地Markdown，找到未曾核读这两篇的记录，因此两篇可计新增；这仍不是所有历史正文/外部文献的完整排重。
