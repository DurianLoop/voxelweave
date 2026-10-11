# 本轮续作：原始重复 T2 来源补充检索

在前次 Kirby21 3D 来源门槛之后，本轮冻结并运行三查询 OpenAlex 补充检索，得到 150 条/145 个去重 work ID，随后核读 ON-Harmony 2025 开放 HTML 全文及 OpenNeuro 官方非影像发布材料。最重要的新证据是 ON-Harmony 的 **2D T2w FLAIR 仅在 GE MR750，九位同机重复者的重复扫描仪中 GE MR750 为零**；见[来源门槛报告](ON_HARMONY_REPEAT_T2_SOURCE_GATE_RESULT_2026-10-01.md)。这排除了一个表面上同时有 2D 和复扫的来源，避免将跨扫描仪/跨协议差异误称采集身份效应。[145 条索引筛查](literature/2026-10-01_native_2d_t2_targeted_search_result.md)记录了其他摘要级线索。

另核读[2015 年 57 人数据论文全文](CONNECTIVITY_TEST_RETEST_T2_SOURCE_GATE_RESULT_2026-10-01.md)：第一次 session 有额外 T2w，第二次未列；每次的 S-MRI 则是 T1w 3D MP-RAGE。故该线索也在论文协议级被排除，未读取三个共享 tar 包。

公开数据集说明标 CC0；本轮只取得论文 HTML、目录页、README、描述 JSON 和 `scan_delays.csv`，没有下载 NIfTI 或读取像素。GPU、用户终端训练和锁定 IXI test 均未触碰。原始 2D 身份机制仍无合格来源，Kuestner 2024 方法全文、IXI 衍生权重发布、干净环境复现和作者/场合审查仍是发表门槛。当前不标记 claim 为可发表完成。
