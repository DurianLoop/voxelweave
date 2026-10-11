# 原始 2D T2 重复来源补充检索结果

[事前计划](2026-10-01_native_2d_t2_retest_targeted_search_plan.md)取消了先前 2015 年起始限制，使用三条精确 OpenAlex 查询，每条只取默认相关性的前 50 条。[原始响应和去重索引](search_snapshots/native_2d_t2_retest_targeted_2026-10-01/index.json)共 150 条、145 个不同 work ID。逐条筛看标题，针对性核读显式重复/数据集条目的摘要；**不是 145 篇全文核读，也不是完整查新**。

最强的新命中是 [ON-Harmony 2025](../ON_HARMONY_REPEAT_T2_SOURCE_GATE_RESULT_2026-10-01.md)：全文确认存在 2D T2w FLAIR 与九人的同机重复，但官方非影像表证明两组交集为零。其他摘要级排除或保留：

| 条目 | 当前判断 |
|---|---|
| [Connectivity-based test-retest dataset, 2015](https://doi.org/10.1038/sdata.2015.56) | [全文协议核读](../CONNECTIVITY_TEST_RETEST_T2_SOURCE_GATE_RESULT_2026-10-01.md)：第一次 session 有 T2w，第二次未列；两次共有的 S-MRI 是 T1w 3D MP-RAGE。论文级排除重复 T2w 候选，包内未下载核对。 |
| [YOUth MRI protocol/test-retest, 2020](https://doi.org/10.1016/j.dcn.2020.100816) | 17 位成人相隔一周复扫；摘要列的是结构 T1w、DWI 和 fMRI，没有 T2w 证据，当前优先级低。 |
| [EPAD open-access MRI, 2022](https://doi.org/10.1016/j.nicl.2022.103106) | 摘要列核心结构序列为 3D T1w 与 3D FLAIR；不构成项目 2D T2w 同机重复来源。 |
| [Open relaxation-diffusion neurosurgical MRI, 2024](https://doi.org/10.1038/s41597-024-03013-9) | 摘要中的多 TE 是同一扩散协议的不同回波时间，不是两次独立 T2w 结构像采集。 |

此次补充命中不能证明世界上不存在合格队列。2015 年 57 人全文采集表现已核读为 T2w 不对称；任何新来源需先给出**同人、同机、同协议、原始 2D T2w、可核层位和使用权**，再做非像素头审计。发表候选的原始采集机制门槛仍未通过；已验证的窄发布层审计及其先例、复现和权利缺口保持原判。
