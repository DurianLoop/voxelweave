# 四倍抽层病灶覆盖的定向文献补查

先保留SafeRestore、MoEDiff-SR、分割引导和GSURE已读先例，再查病灶厚度/部分容积/观测覆盖是否已有直接实验。新增三条Europe PMC题名摘要查询：

1. `(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND TITLE_ABS:lesion AND (TITLE_ABS:"slice thickness" OR TITLE_ABS:"partial volume")`
2. `(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND (TITLE_ABS:"adaptive sampling" OR TITLE_ABS:"active acquisition") AND (TITLE_ABS:lesion OR TITLE_ABS:diagnostic)`
3. `(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND (TITLE_ABS:"slice interpolation" OR TITLE_ABS:"through-plane") AND TITLE_ABS:lesion`

日期截止2026-10-03，每条最多15个core索引记录，顺序单连接、每请求一次、socket30秒、响应上限5MB；错误及原响应保留，不自动重试。它是有界定向筛查，不是系统综述；结果数量/排序/无命中不证明首创。人工核结果后另写正文选择范围，再获取公开正文，付费/认证来源保留未读状态。不读取患者影像或使用GPU。
