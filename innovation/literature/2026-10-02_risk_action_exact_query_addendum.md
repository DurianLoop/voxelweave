# 精确标题补查：原有界查询保留

四个原Europe PMC查询已执行，38条响应记录（15+0+15+8），不是38篇相关论文或全文。其中SURE被当作普通词，Stein亦匹配不相干内容，前两类风险方法召回不足；零条ensemble结果不能解释为无先例。原方案、代码与attempt_01响应不修改。

补充三个Crossref精确题名查询，每条最多3结果：

- Ensemble Stein's Unbiased Risk Estimator for Unsupervised Learning。
- Extending Stein's Unbiased Risk Estimator to Train Deep Denoisers with Correlated Pairs of Noisy Images。
- Generalized Stein's Unbiased Risk Estimator for Training Deep Neural Networks。

另用Europe PMC查询TITLE_ABS:"unbiased risk" AND (MRI OR "magnetic resonance")，最多15条。身份须核准确题名/DOI，不能把Crossref第一排序自动当匹配。符合原最多三篇正文优先上限。日期截断2026-10-02，保留所有失败与排名。
