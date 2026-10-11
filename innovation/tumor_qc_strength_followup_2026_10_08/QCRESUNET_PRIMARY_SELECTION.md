# QCResUNet 原始来源选择

两个固定Europe PMC query实际1e0fb6 exit0，分别125/109总命中但只取各8条。首次输出被截断，621399已完整重读16题名/DOI/日期与QCResUNet摘要；不称16篇原文已读。与本项目最直接的新候选是QCResUNet: Joint subject-level and voxel-level segmentation quality prediction，DOI10.1016/j.media.2025.103718，PMID40945175，索引firstPublicationDate2025-08-27/pubYear2026。索引摘要明确脑肿瘤患者级metric+体素错误图与BraTS2021/SSA/WUSM评价，细节尚未核原文。

本地排除tools/data的Markdown确切题名/DOI查重无旧记录，尚不是全球穷尽查新。原16条中reviews/标准化dataset/其他模态/普通分割并非本轮直接QC主文，全部原响应保留；LesionLab只属摘要级合成训练样本质量/难度筛选，不凭其摘要推断VS补层收益。

追加两个不同来源的公开GET：精确DOI Crossref元数据，以及arXiv export标题QCResUNet检索最多3条。确认题名与作者身份后再取得一个原始HTML正文版本。无publisher登录、无自动retry，原端点失败保留。方法/数据/标签生成/结果/费用未核读前不登记原文完成，不把预测error map当实际纠错或修正动作收益。
