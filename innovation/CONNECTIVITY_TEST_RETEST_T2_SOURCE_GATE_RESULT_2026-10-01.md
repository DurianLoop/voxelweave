# 2015 年 57 人多模态 test-retest 数据的 T2 来源门槛

**论文协议级排除：T2-weighted 结构像只列在第一次 session，第二次没有列出 T2w；两次都采的 S-MRI 是 T1w 3D MP-RAGE。** 因此不能把摘要的“57 人两次多模态扫描”解释为 57 对重复 T2w，更不能据此开启本项目原始 2D T2w 身份实验。

[Zuo et al. 2015, *Scientific Data*, DOI 10.1038/sdata.2015.56 的全文 HTML 快照](literature/source_cache/connectivity_test_retest_article_2026-10-01/article.html)在 Study design 中写 57 名健康青年两次 session，间隔约 40.94 +/- 4.51 天。第一次 session 包含各一套 S-MRI、T2-weighted structural imaging、D-MRI 和两套 R-fMRI；第二次 session 包含 S-MRI、D-MRI 和 R-fMRI，未列 T2w。MRI acquisition 下的 S-MRI 段明确是 T1-weighted sagittal 3D MP-RAGE。Data Records 说共享于 CoRR/INDI 的三个 `.tar.gz` 文件；本次未下载也未核包内目录，所以结论限于**论文所定义的重复扫描协议**，不声称已经逐文件证明公开包绝无额外 T2w。

文章作者以 T2w 对参与者作异常筛查的陈述不改变上述 session 不对称。该来源不满足[事前 T2 门槛计划](CONNECTIVITY_TEST_RETEST_T2_SOURCE_GATE_PLAN_2026-10-01.md)；无影像像素、GPU、当前训练或锁定 IXI test 访问。
