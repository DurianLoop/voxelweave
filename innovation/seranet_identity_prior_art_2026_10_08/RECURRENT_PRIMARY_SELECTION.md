# 按 OpenAlex 实际返回位置选择原文

location_attempt01 三条请求均 HTTP 200。OpenAlex `search=SERANet` 是跨元数据检索，不是严格题名匹配；返回五个题名已完整筛读（没有新的五个摘要），其中三个非 MRI 相关，两个相关。

选择完整读取：

- Qiaoying Huang 等，Brain Segmentation from k-space with End-to-end Recurrent Attention Network，OpenAlex W2963749200，实际 PDF 地址 https://arxiv.org/pdf/1812.02068 。它是 SERANet 的候选身份；必须以 PDF 正文核实缩写，尚不直接宣称身份已确认。
- Kehan Qi 等，Multi-task MR Imaging with Iterative Teacher Forcing and Re-weighted Deep Learning，OpenAlex W3108772721，实际 PDF 地址 https://arxiv.org/pdf/2011.13614 。用于核对额外监督、重建/任务交互和训练曝光。

下载沿用已执行标准库 HTTPS 客户端，每 PDF 10 MB，阶段全部文件不超过 30 MB。两个实际链接没有版本号；用 HTTP 最终 URL、PDF 首页面标记及 SHA 记录实际版本，不能补称 v1。不把下载/提取计成阅读，读后再记录。

Acar 章节的两条精确 DOI 索引都未提供公开 PDF，OpenAlex 为 closed 且两个机构位置 pdf_url=null；S2 openAccessPdf.url 为空。摘要已核，但全文未得。这不等于不存在作者稿，后续可循实际机构 landing page 查找；当前不重复出版社失败路径。
