# 已下载XML的题名标点差异处理

原fetch session12809实际1de6d5 exit1：第二篇题名Unicode U+2010 hyphen与索引ASCII '-'不相等，严格title断言失败。c82468已实际读取本地两XML身份、字节和SHA；两DOI和PMCID精确匹配，第一篇只终止句点/空白差异，第二篇连字符排版差异。没有证据表明取得别篇论文。

不改原已执行fetch脚本或文件，不额外GET。新本地登记只将U+2010映射为ASCII '-'、空白折叠、忽略末句点及大小写；仍要求所有DOI/PMCID精确匹配。逐字原title与索引title都保留。新complete仅表示身份与本地提取资格，不把原fetch exit1改成exit0，不宣称原丢失的内层HTTP返回/耗时已恢复，不计全文阅读。
