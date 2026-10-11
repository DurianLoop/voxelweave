# 本地TADT实际来源和数学字形编码

587000 / exit1的网络部分HTTP200/curl0，完整PDF10,036,939bytes与明确Content-Length相同，pypdf解析16页。实际字节SHA为d5aab3d1dba2a68aee7981641f0ab450c0241f3ba7066166c7b70ec006373cd8，与ETag c75737c8c8d20511dfe4a50711d679178e80e0426a50bc4654e04d944104bd97不同；不声称ETag验证通过。

已完整读取本地第1页：题名为Task-Aware Dynamic Transformer for Efficient Arbitrary-Scale Image Super-Resolution，作者Tianyi Xu / Yijie Zhou / Xiaotao Hu / Kai Zhang / Anran Zhang / Xingye Qiu / Jun Xu，页脚arXiv:2408.08736v2 / 25 Aug 2024，与索引版本身份相符。以实际PDF字节SHA绑定此版本阅读来源；不重复下载。

提取阶段遇UnicodeEncodeError，是pypdf返回UTF-16数学字形的surrogate代码单元，不能直接写utf8。另存本地提取attempt04：原始提取字符串完整保存为ensure_ascii=true JSON，保留所有代码单元；若代码单元严格解码为成对UTF-16，则输出合法Unicode文字，验证归一化前后UTF-16字节完全相同；不替换/删除数学字符、不猜补符号。旧失败source/receipt/partial text保持，不把39页或16页提取等同全部读完。
