# 本轮续作：MRI 创新点文献碰撞复核

持续目标是研究和验证到足以支撑可发表 claim；本轮仍未达到这一门槛。沿用用户边界：不触碰终端正在运行的训练、不占 GPU、不读取锁定 IXI test 图像。本轮围绕现有 MIRA 公开来源稿的**同目标发布层上下文审计**做文献压力测试，而不是启动新模型。

1. [Kuestner 2024 全文访问审计](literature/2026-10-01_kuestner_fulltext_access_audit.md)：OpenAlex、Semantic Scholar 和 Crossref 均指向 Wiley；Wiley 正文/PDF 请求在当前环境为 403，Europe PMC 无全文，TUM 页只可见元数据，arXiv 有界题名检索无匹配。故仍只核正式摘要，不臆测其具体实验是否与 MIRA 相同。
2. [NPB-REC 2022 固定 arXiv 原文核读](literature/2026-10-01_npb_rec_fulltext_result.md)：PDF、哈希、提取文本与两页方法/结果图表已归档。其九组权重预测共用同一 fastMRI 多线圈欠采样 k-space，图像级平均标准差与 MSE Pearson 为 0.94（dropout 为 0.91），但没有切换真实发布层邻片。广义多预测分歧/误差估计非 MIRA 新意。
3. [Edupuganti 等 TMI 2021 开放全文核读](literature/2026-10-01_edupuganti_fulltext_result.md)：NCBI BioC XML 156 段，通过 DOI/结构检查并归档，PMC HTML 验证码响应已删除。19 位膝 MRI 患者的单线圈欠采样实验中，方差可漏掉主导偏差，SURE 在假设下估计无真值 MSE；因此“首次发现共同误差漏检/首次无真值 MRI 风险审计”不能写入 MIRA。其观测算子与 MIRA 发布层切换不同。

[创新点优先级](INNOVATION_DECISION_MEMO_2026-10-01.md)、[发表门槛](CLAIM_PUBLICATION_GATE_2026-09-30.md)和[公开来源英文内稿](PUBLIC_ONLY_MIRA_MANUSCRIPT_DRAFT_2026-10-01.md)已同步引用与边界。当前 PDF 仍是旧文字快照，不能当作最新稿。未解决：Kuestner 全文的合法可读副本、目标投稿场合的系统性前后向查新、独立可复现运行、IXI 衍生权重再分发与作者/场合审核。没有证据把当前窄审计升级成新重建方法、纯原始采集身份因果或部署风险评分。

验证：`D:\conda\envs\MRI\python.exe -B innovation\verify_archive.py --write` 更新清单后只读复跑，28 份 PDF、151 份来源/阅读证据、809 个本地链接，错误为 0；新 NPB-REC PDF 哈希与登记值一致。未触碰终端训练或 GPU。
