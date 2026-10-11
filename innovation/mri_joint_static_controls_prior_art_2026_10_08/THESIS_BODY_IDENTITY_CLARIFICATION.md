# 实际PDF与ETag不一致：来源资格范围

单次扩大上限的公开GET实际HTTP200/curl0，实际12,377,385bytes与两个响应Content-Length完全相同；但实际PDF SHA256是`f318edd5dd559c1282a4f935a443fdbaa519aaaf9f1326d695ef3ca9292ed3bb`，不等于header的ETag sha256。于是下载程序aa837c实际exit1，receipt complete=false，已保留；不能写成预期SHA检查通过。没有再次联网下载，没有解释或猜测服务方ETag为何不同。

本地身份检查444c08=0成功解析189页；第1页清楚包含标题Learning to sample in Cartesian MRI、作者Thomas Sanchez、thesis n9981和arXiv:2312.04327v1／7 Dec2023。它们与原索引、具体版本URL及Content-Disposition文件名相符。封面答辩日期3 juin2022与arXiv提交日期2023不同，按各自含义记录，不假装同一日期。

据此另建本地阅读来源记录，以**实际PDF字节SHA**绑定，记录TLS公开GET、完整长度、可解析PDF、封面身份及明确未通过ETag的一项。可以核读这个公开获取版本；不会声称验证了ETag期望内容、传输cryptographic equality或旧下载attempt全部成功。本地提取入口必须再次核实际SHA、封面身份、页数；旧失败源码／receipt不改。

原大小修订要求ETag相等未达成，故不把它冒充成功路径。本说明明确新增较窄的“已获取正文身份／实际字节来源”阅读资格；不改医学样本、训练、能力／资源门槛或论文成功标准，也不把这种文献获取核验作为MRI效果。若论文身份有新的反证，应暂停使用对应阅读结论并保留记录。
