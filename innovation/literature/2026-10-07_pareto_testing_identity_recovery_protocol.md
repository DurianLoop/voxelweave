# Pareto Testing 身份恢复协议

attempt01 实际 exit1，两个猜测 URL 失败：PMLR 路径 404；arXiv2210.07998 的官方题名为 Lambda-DARTS，与候选论文不符。未下载错误论文 PDF，reading=false 保留，不能引用错误 ID。

恢复 attempt02 先读取官方 PMLR v206 卷索引（30秒/2MB），从题名所在 paper 区块提取 abs 链接，再逐一核精确 citation_title。无命中则保存失败。使用原 acquisition 帮助函数，但独立目录与源码 SHA；身份确认后 PDF<=32MB/60页。原失败目录不改。
