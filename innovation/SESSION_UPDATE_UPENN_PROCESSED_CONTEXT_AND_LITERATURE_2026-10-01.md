# 本轮会话归档：GPU 占用期间的论文、创新点与 CPU 验证

用户要求接着 MRI 项目批量读论文、从既有实验找创新点；能验证的先探索，不能验证的记录与准备后续尝试，所有本轮内容放进 `D:\MRI\innovation`。延续此前边界：不碰正在运行的 GPU 训练、不占 GPU、不读取锁定的 IXI test 图像。此前已经核读 NPB-REC、Edupuganti 等全文并形成[创新备忘录](INNOVATION_DECISION_MEMO_2026-10-01.md)；本次接续的是已启动的、CPU 两线程、冻结的 UPENN 全队列推理会话，**没有重启或覆盖运行**。

1. [UPENN 官方引文审计](literature/upenn_gbm_official_citation_audit_2026-10-01.md)：TCIA 原页面及 DataCite JSON 原始响应与 SHA-256 已入档。正式数据引文为 Bakas 等、2021、Version 2、TCIA、DOI `10.7937/TCIA.709X-DN49`、CC BY 4.0；不将官网 NIfTI 配准说明套到所选 DICOM 的具体处理步骤。
2. [有界 arXiv 定向刷新](literature/2026-10-01_mira_targeted_arxiv_refresh_result.md)：三条事前查询返回九个不同 arXiv ID，原始 Atom/XML、URL、哈希和摘要均保留。新增 [Savant 2026 全文核读](literature/2026-10-01_savant_formulation_fulltext_result.md)：其 6 mm/3 mm 输入间距重定义已有“邻片选择重要”先例，但没有同目标固定参考的等间隔发布层相位切换或配对误差 `O`。该预印本的切片计数口径与扩散比较不能不加核验地搬入本稿。Kuestner 2024 仍只有摘要，定向检索非系统综述。
3. [UPENN 完整结果](UPENN_GBM_PROCESSED_T2_CONTEXT_RESULT_2026-10-01.md)：374/374 人、1,496 目标、零失败、CPU float32、无 GPU。患者等权 `Delta O=+28.1156` 点、冻结 5,000 次患者 bootstrap 95% CI +27.9006 至 +28.3309 点，达到事前至少 300 完整人且区间下界正的主标准。374/374 人和结果后检查的 1,496/1,496 目标为正；共享/不相交 `O` 为 1.3933%/29.5089%。
4. [独立统计复核器](experiments/verify_upenn_gbm_processed_t2_context.py) `PASS`，复算每目标公式、固定 HAT 参考、四目标/两 residue、患者等权与同种子 CI。[独立来源复核器](experiments/verify_upenn_gbm_processed_t2_sources.py) `PASS`，全 374 ZIP 哈希/CRC 与 23,702 非像素头、UID、几何、PixelSpacing、排序和目标一致；所选 374 套全为派生/次级，367 套物理层距 3.0 mm、七套 4.8 mm，名义标签却全是 1 mm。[结果后代数分解](experiments/upenn_gbm_processed_t2_context/posthoc_decomposition.json)提示 `Delta O` 中伙伴误差量级贡献约 +0.1491 点、误差对齐项约 +27.9665 点；它只是同一预测的代数重述。UPENN 配对 MSE 不改善，不能宣传重建收益。
5. [创新点优先级](INNOVATION_DECISION_MEMO_2026-10-01.md)：最可审的候选是三来源、固定 IXI 模型对的**处理/发布层上下文回顾性审计**，但窄新意与正式投稿仍未闭环。最高机制潜力是同中心、同几何、经正式授权的原始独立重复采集身份试验；当前 MSValid/ReMIND/UPENN、fastMRI/QIN/TCGA 筛查都不能供给该反事实。指定目标 slice response 的查询任务需要可信薄层参考，当前小样本已知 profile 留出选核为负。部署风险评分、结果后适配 gate 和同预算新集成仍停在已有负证据，不借 UPENN 阳性重新包装。

本轮新旧成果均在 `innovation`，原始 UPENN ZIP 仅留本地 git 忽略目录，不进发布包。公开来源五页 PDF 仍是两来源旧快照；本次没有擅自把第三来源数字塞进未经版面/作者/许可复核的投稿稿。后续必要动作：Kuestner 2024 合法全文与投稿场合前后向查新、IXI 衍生权重分发条件、清洁环境复现、真正原始同中心重复采集来源及其事前方案。GPU 训练与锁定 IXI test 始终未触碰。

归档验证：`D:\conda\envs\MRI\python.exe -B innovation\verify_archive.py --write` 更新清单后，再只读运行同脚本，统计为 **29 份 PDF、160 份来源/阅读证据、863 个本地链接、0 错误**。主运行、两个独立复核器、结果后描述和代数脚本均以退出码 0 结束。工作区原有 `.gitignore` 修改未被改写。
