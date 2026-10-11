# 低LR等待期间的动作收益查新

此前已读SafeRestore/MoEDiff、Morshuis七方法benchmark、task guidance/UQ及SynthSeg等，不重复计新增。新一批Europe PMC三个固定查询，各最多8条；返回重复/不相关项仍保留，不称系统综述。只有实际取得并读正文才计新增完整阅读，metadata/摘要分别登记。截止2026-10-07；不重试此前被拒的Kuestner全文路径。

1. `(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND (TITLE_ABS:reconstruction OR TITLE_ABS:"super-resolution") AND (TITLE_ABS:"decision" OR TITLE_ABS:"utility" OR TITLE_ABS:"selective")`
2. `TITLE_ABS:"image restoration" AND (TITLE_ABS:"downstream" OR TITLE_ABS:"task-aware" OR TITLE_ABS:"risk")`
3. `TITLE_ABS:"super-resolution" AND TITLE_ABS:segmentation AND (TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND FIRST_PDATE:[2024-01-01 TO 2026-10-07]`

目的：核动作特定效用/风险与强适配任务先例，不因MRI/缺层改名就称首创。每请求<=25秒、返回<=5MB；无GPU/训练/影像下载，原查询及原响应/SHA保留。正文选择按直接机制/信息合同相关性与可核原文决定，不按有利结果挑选。
