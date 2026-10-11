# 本轮 MRI 创新研究交接：UPENN-GBM 来源门槛

用户本轮要求：GPU 被既有训练占用时，批量读论文、结合已有 MRI 工作寻找创新点；能先验证的用 CPU/只读证据探索，不能验证的记录并准备后续实验；本轮资料归档至 `D:\MRI\innovation`。继续遵守既有边界：不操作运行中的训练，不占 GPU，不读取锁定 IXI test 图像。

现阶段最稳妥的创新候选是固定 IXI 训练 HAT/SwinIR 对的**同目标发布层上下文切换审计**。MSValid 84 人/479 目标 `Delta O=+24.1856` 点；ReMIND 62 人/248 目标 `+26.3999` 点。线性伙伴在两来源也有大效应，故不主张双深度网络特有机制；ReMIND 含 `MPR`，也不主张原始采集身份、部署风险评分或真实薄层恢复。同预算 PCHIP 控制令新集成方法路线停止。157 标题定向查新及 2022 年 Radmanesh 全文、2024 年 Kuestner 摘要继续压缩新意边界，后者全文仍需取得。

本次按[事前元数据筛查](UPENN_GBM_T2_SOURCE_SCREEN_PLAN_2026-10-01.md)和[冻结首例头部方案](UPENN_GBM_T2_HEADER_PILOT_PLAN_2026-10-01.md)检查 TCIA UPENN-GBM。官方清单为 3,680 MR 套/630 人，所有行报告 CC BY 4.0，DOI `10.7937/TCIA.709X-DN49`；最大字面轴位 T2 描述为 `Axial T2 tse: Processed_CaPTk`，402 套/374 人。唯一冻结首例的约 3 MB 官方 ZIP 经独立只读复核，64/64 非像素 DICOM 头为 `DERIVED/SECONDARY/OTHER`，虽然标 2D；投影位置间隔约 3 mm，而 `SpacingBetweenSlices=1 mm`。因此停止把该首例/此已选分层当作原始采集层的扩展，不下载剩余 401 套、不解码像素；不把首例外推为所有 402 套。证据、哈希和复核命令见[完整结果](UPENN_GBM_T2_SOURCE_AND_HEADER_RESULT_2026-10-01.md)。

后续优先级：取得能证明独立原始层、同几何和合法使用的**新患者来源**，再事前冻结患者、目标、模型和失败规则；或将当前稿明确定位于回顾性发布层测量审计，并在目标投稿场合做前后向查新、取得 Kuestner 2024 全文、完成全新环境复现及许可/作者审核。所有这些仍是门槛，不是本轮已验证的新方法或投稿资格。

追加的[TCGA-GBM 事前元数据筛查](TCGA_GBM_T2_SOURCE_SCREEN_RESULT_2026-10-01.md)发现官方集合网页可访问，但 NBIA `getSeries` 在带/不带 MR 筛选时均返回 HTTP 200 空体，官方集合枚举未列该精确标识。故患者数、T2 分层和精确文件许可均为未知；没有下载 DICOM。已归档空响应、集合枚举、哈希与脚本，不把接口空体解释为没有 T2。[创新点决策备忘录](INNOVATION_DECISION_MEMO_2026-10-01.md)汇总论文碰撞、正负证据及下一门槛。

验证：`D:\conda\envs\MRI\python.exe -B innovation\experiments\verify_upenn_gbm_t2_header_pilot.py` 返回 `PASS`，64/64 派生头、ZIP 哈希与物理层距一致；`innovation\verify_archive.py --write` 后再次只读运行，27 份 PDF、146 份来源/阅读文件、785 个本地链接，错误数为 0。没有启动 GPU 工作或读取锁定 IXI test 图像。
