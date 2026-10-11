# 本轮续作：近年全文碰撞审计与下一步门槛

用户要求继续批量读论文、结合 MRI 项目寻找创新点，GPU 被占用期间先做可验证的探索，并把本轮材料留在 `D:\MRI\innovation`。本次没有触碰训练终端、GPU、锁定 IXI test 图像或用户修改的 `.gitignore`。此前三来源的固定 IXI HAT/SwinIR 发布层结果保持原状：MSValid 84 人/479 目标 `Delta O=+24.1856` 点，ReMIND 62 人/248 目标 `+26.3999` 点，UPENN 处理后 DICOM 374 人/1,496 目标 `+28.1156` 点。UPENN 全部选中系列为派生/次级，配对 MSE 没有改善；这仍只是回顾性误差可见性审计。

本轮预先写下[四式近年检索计划](literature/2026-10-01_targeted_recent_mri_screen_plan.md)，保存 4 份 OpenAlex 原始响应、URL、哈希和去重索引：200 条返回、163 个不同 work ID。按最新排序的每式 50 条样本噪声较大，不能作为系统综述或全局新意证明。两篇高相关开放论文通过完整 PDF/EOF、Content-Length、`pdfinfo` 和关键表格渲染核验，来源及 SHA-256 在[源索引](literature/source_cache/targeted_recent_fulltexts_2026-10-01/index.json)，精读结论在[全文碰撞审计](literature/2026-10-01_targeted_recent_fulltext_result.md)。

1. Li 等 *SliceBridge*（arXiv:2609.01827，13 页）已实现 T1 连续切片修复，581 个 IXI T1 外部病例上使用相同上下文的配对独立生成对照，跨切片梯度误差下降 32.9%-41.3%。其受影响区域体积 APE 在控制损坏实验中由 1.95% 降至 1.05%，但与同上下文独立生成模型同为 1.05%，调整后 `p=0.370`；不能把跨切片一致性改善自动解释为额外下游收益。它不做本项目的固定参考、切换另一估计器发布层伙伴上下文、比较成对误差可见性。
2. Mosquera Rojas 等（MELBA 2026，27 页，DOI `10.59275/j.melba.2026-456d`）已经评估胶质瘤分割/分型任务的不确定性、错误检测和选择性预测；其分割错误检测在 DSC <=0.7 定义下，MCD 预测不确定性的 U-AUC 为 0.95、AP 为 0.82。它不是 MRI 重建实验，但阻止本项目把 `Delta O` 宣称为首个可用的任务风险指标。

[三来源英文内稿](PUBLIC_ONLY_MIRA_MANUSCRIPT_DRAFT_2026-10-01.md)和[创新决策备忘录](INNOVATION_DECISION_MEMO_2026-10-01.md)已补充这两篇的可核对表述。最强的候选创新仍限于**同目标、固定参考、切换伙伴发布层邻片上下文的成对误差可见性实证审计**；不是新的插值器、原始采集身份因果、可部署告警或临床安全证明。Kuestner 2024 的 OpenAlex 内容 XML 新路线返回 401，仍只能作摘要级对照，见[访问审计](literature/2026-10-01_kuestner_fulltext_access_audit.md)。

UPENN 的专家修订肿瘤标签与 atlas NIfTI 对齐，和现有 DICOM 按设计不对齐。官方约 69 GB Aspera 包的文件级清单依然没有取得，本次也未启动包下载。因此任务级实验仍必须先通过[独立 NIfTI 空间门槛](UPENN_GBM_NIFTI_LABEL_FEASIBILITY_RESULT_2026-10-01.md)：核对同一扫描 ID、T2/标签文件存在性及 shape/affine，再冻结目标面、肿瘤/非肿瘤 ROI、等信息基线和失败统计。没有这一步不得把标签回填现有 1,496 个 DICOM 目标。另需通过 Kuestner 方法级排重、权重分发权限、干净环境复现及作者/场合审查；当前[发表门槛](CLAIM_PUBLICATION_GATE_2026-09-30.md)仍未通过。

本轮另外冻结并执行了[UPENN 固定分母敏感性分析](UPENN_FIXED_DENOMINATOR_RESULT_2026-10-01.md)，只读取此前 1,496 行逐目标指标：共同条件成对 MSE 固定为两种条件的分母后，患者等权差值 +28.4961 点，5,000 次患者 bootstrap 结果后区间 +28.2633 至 +28.7296；374/374 人和 1,496/1,496 目标均正。独立 pandas 分组核算复现了均值和符号数。它排除分母变化是原 +28.1156 点的唯一算术原因，不增加独立病人证据，也不改变 DICOM 派生身份和临床标签门槛。

本次所有新检索响应、两篇 PDF、提取文本、关键表格渲染、源哈希、脚本和判断均在本目录；最后以[归档清单](literature/archive_manifest.json)和 `python innovation/verify_archive.py` 的只读检查为准。旧五页 PDF 仍是两来源快照，未更新为当前三来源稿。

最终归档验证：29 份 PDF、199 个证据文件、1,005 个本地链接、零错误；两篇 PDF 与四份检索原始响应的 SHA-256 均复核一致，UPENN 三份输入文件哈希未变化。工作区 `.gitignore` 的既有用户修改保持原状。
