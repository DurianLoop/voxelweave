# 作者稿补充渠道：三次固定arXiv标题检索

OpenAlex v2实际ccc872 exit1：Jiang/Hsu exact DOI返回200且closed、各位置仅DOI/PubMed无pdf；Gou429明确共享IP免费日额度不足，原响应保留，不重试/增加key。该索引不能证明作者稿在所有渠道不存在。补充仅arXiv export官方API三个固定标题查询，每条max_results=3，time order descending，不作自动翻页/扩大查询/重试；每HTTP timeout30秒，整体wall180秒。标题和作者/DOI须实际核对，检索候选不直接下载或登记全文。

目标题名：Jiang “3D segmentation framework for whole-brain segmentation from thick-slice brain MRI”；Gou “LRD-ESR-Net”（完整题名已由旧exact DOI响应再次核：Pseudo-Healthy Image Synthesis Based on Low-Resolution Residual Decoupling and Edge-Prior-Guided Super-Resolution Reconstruction Module）；Hsu “Self-supervised isotropic reconstruction for abnormality detection in anisotropic MRI”。查询字符串、原XML/错误响应gzip、SHA、HTTP status及Atom题名/作者/日期保存。maintext和医学证据计数0，标题检索也非系统穷尽检索。

标准库HTTP仅本opener禁用旧不可用环境代理，TLS/系统代理不改，不安装依赖或联系作者。响应单份max500KB，压缩三份合计80KB；本检查输出max100KB，并保留完整管线日志到1.5MB、审计150KB和后附100KB的5MB总容量。磁盘/RAM8GB储备、CPU1/低优先级保持，无MRI/GT/模型读取，对外仅公开论文标题。不干预两个真实live任务，也不改变其frozen sources。
