# 作者实现的有界检索

实际 PDF URI 枚举 37f396：RD-ViT 无 URI 注释，HiFi 只有论文/参考链接。RD23 声称 companion GitHub 但未给地址；OpenMythos 是上游，不是该作者实现。

用 GitHub repositories API 做四次匿名正常 TLS GET，依次查询 RD-ViT、该版本 arXiv ID in:readme、HiFi-MambaV2、该版本 ID in:readme，各最多五条。读取所有返回 metadata；先按 README 的题名、作者、版本和实验说明核身份，再考虑下载单个源文件。最多3MB/响应、30秒、无自动重试、无仓库clone、无作者代码执行/安装。未命中不能证明没有公开实现。
