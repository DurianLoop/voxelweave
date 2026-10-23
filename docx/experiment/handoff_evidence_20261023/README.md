# 交接证据快照

整理日期：2026-10-23。原始影像、预测体积、权重和优化器状态不在此目录。

本目录复制文档引用而原Git忽略的轻量汇总CSV/JSON/表格，保留原字节并在[source_availability.csv](source_availability.csv)记录原路径、大小、SHA-256和新路径。已跟踪的源码与报告沿仓库原路径阅读。超过2MB、逐患者/切片明细、manifest和目录资产不自动复制，文档中的相关链接指向索引以说明本地取回位置。它们不因此变成可公开下载的完整复现数据。

`copied aggregate evidence`表示已随本次提交带入；`tracked source`表示来源原已在研究代码快照中；`local asset only`表示接手者需另行取得本地资产。相同实验的重复导出不是独立验证。旧记录内部的live/待运行描述保留原文，当前结论以交接和实际completion/gate为准。

快照目录用`.gitattributes`保留证据原字节，避免Git自动换行影响哈希。已跟踪源码的SHA记录交接时本地字节；跨系统checkout可能转换换行。主表核验同时使用统一LF内容哈希，区分换行变化与数值/文本变化。

可用根目录命令 `python processing/verify_research_handoff.py` 核验快照哈希、文档链接、表格及比较数值。权重位置与真实文件哈希另见[checkpoint_inventory.csv](checkpoint_inventory.csv)；该表仅为库存，不包含权重文件。

本次交付的核验结果见[validation_report.json](validation_report.json)，其中本地权重哈希在原工作区核验；新机器默认不要求权重已存在。

本次来源状态计数：

- copied aggregate evidence: 157
- local asset only: 5
- new handoff document: 4
- tracked source: 291
