# 任务输入归一化与跨域评估：追加阅读选择

这次选文发生在完整三人 pilot 及全部36端点已核读后，属于事后机制探索。停止 post anchors 带宽恢复解释，不选择论文来挽救该解释。新增文献不等于新颖性证明。

Europe PMC 首四查询均 HTTP503，失败保留于 `source_cache/task_normalization_context_search_2026-10-03/attempt_01.json`。Crossref 备用查询成功但题名相关性较弱；NCBI 首个宽检索的自动词扩展过宽，不能据其数量声称相关研究。随后使用限定 Title/Abstract 的三个查询及截止日期，保留全部原响应与摘要目录：`source_cache/task_normalization_context_ncbi_2026-10-03/attempt_01.json`。返回26条题名记录，有重复、会议摘要及一个标称2026年12月的期刊条目；它们均不是26篇已读全文，未选择未来标称日期条目。

固定选择三个公开正文：

| key | PMC | DOI | 选择原因 |
| --- | --- | --- | --- |
| multisite_normalization | PMC7457546 | 10.1109/isbi.2019.8759295 | 直接检查归一化方法在多中心训练/测试的作用及可迁移条件 |
| segmentation_harmonization | PMC8294062 | 10.1109/TMI.2021.3059726 | 检查分割约束的图像 harmonization 与任务评价是否构成方法先例 |
| feta2024 | PMC13338501 | 10.1016/j.media.2026.103941 | 新的多中心任务评测，检查SR处理链、domain shift与评估范围 |

只获取有 DOI 身份匹配及 body 的公开 JATS 正文。取得之后再逐段读方法、实际对照、结果与局限；读取正文不包括作者实验复现、视觉图检查或补充材料核读。无新增PDF，无GPU任务。
