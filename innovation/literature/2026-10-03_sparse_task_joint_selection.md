# 新正文选择与去重

四个PMC查询返回5+12+12+2=31题名行（含重复），总命中5/52/15/2。本次选三项尚无本地阅读登记的直接方法：

- JOINT DEEP LEARNING FOR IMPROVED MYOCARDIAL SCAR DETECTION FROM CARDIAC MRI，PMC10959501，DOI10.1109/isbi53787.2023.10230541：联合SR/分割与病灶检测是否已有直接训练对照。
- Towards contrast-agnostic soft segmentation of the spinal cord，PMC13110827，DOI10.1016/j.media.2025.103473：软标签、低分辨率/partial volume与体积任务的先例和控制。
- DRIPS: Domain Randomisation for Image-based Perivascular spaces Segmentation，PMC12633610，DOI10.1101/2025.10.22.25337423：细小结构直接分割/分辨率随机化，小病灶鲁棒性的边界；明确其检索版本为预印本。

精确DOI检索既有literature Markdown与reading_provenance未命中这三项。仍需对正文来源及引用关系实际核对；不把获取算阅读。SynthSR、SynthSeg以及过去的任务/分辨率文献命中不当新发现。选择不影响患者角色或模型效果阈值。

正文核读后的追加修正：joint_scar实际联合的是心肌分割与瘢痕分割，原条目的“联合SR/分割”是检索意图，不能当论文内容。为覆盖直接SR近邻，另追加PMC10206514（DOI10.1117/1.JMI.10.5.051808）；其efetch front-only失败保留，公开HTML正文成功。四篇实际阅读与限制见 [报告](2026-10-03_sparse_task_joint_fulltext_reading.md)。
