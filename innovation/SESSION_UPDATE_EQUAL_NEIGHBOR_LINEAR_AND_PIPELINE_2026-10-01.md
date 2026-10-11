# 本轮对话与研究归档：同邻片线性基线、预处理反解释

用户本轮要求：“接着基于我的MRI项目读论文找创新点”；进一步说明 GPU 正被占用，要批量读论文、结合以前工作探索创新点，能验证的先验证，不能验证的记录并准备后续尝试，且“把这轮对话所有的内容放进 `D:\MRI\innovation`”。IDE 显示 `.gitignore` 和 `environment.yml` 打开。工作遵循既有单 T2、x4 缺层重建合同，只在本目录新增研究协议、脚本、数据汇总和报告；没有触碰用户修改的 `.gitignore`、正在运行的 GPU 训练或锁定 IXI test。

## 本轮实际完成

1. 复核原始 IXI HAT/SwinIR MSD 推理路径：每次预测用两张相邻 phase-0 锚点及其线性粗插值、位置通道；归一化 min/max 来自病例所有 phase-0 锚点，输入 240→256，输出裁剪并 256→240。因此“同两张邻片”不是“严格同全部信息/同预处理”。
2. 在看全量联结结果前写下[事后探索规则](MSD_EQUAL_NEIGHBOR_LINEAR_AUDIT_PROTOCOL_2026-10-01.md)，只联结既有神经/解析两套 484 个病例 JSON，不运行模型。完整同源、同目标、同 ROI 的 483 人/1,932 层上，[两邻片原始线性对照结果](MSD_EQUAL_NEIGHBOR_LINEAR_AUDIT_RESULT_2026-10-01.md)：病灶 MSE raw linear 805.23，HAT 1,597.15，SwinIR 1,403.28；HAT/SwinIR 高于 linear 的患者分别 453/483、435/483。局部阴性区差距较小。PowerShell 独立重算 CSV 均值/阳性人数及 1,932 行、逐目标 ROI 面积，结果一致。
3. 因 resize 可能构成反解释，先固定并运行 `BRATS_001` 四层 CPU 像素预检：原始 linear 误差逐 ROI 与解析档案一致；病灶 raw/pipeline linear MSE 为 468.49/915.93。默认 base Python 缺 `nibabel`，随后使用已有 `D:\conda\envs\MRI\python.exe`，未安装或更改环境。
4. 在首例结果已知的情况下，另行冻结[全量预处理线性方案](MSD_PIPELINE_LINEAR_CONTROL_PROTOCOL_2026-10-01.md)并在本地精确官方 MSD 压缩文件上完成 [483 人全量 CPU 重放](MSD_PIPELINE_LINEAR_CONTROL_RESULT_2026-10-01.md)。每层原始线性 MSE 容差 `1e-6` 重现；病灶 MSE raw/pipeline/HAT/SwinIR = 805.23/1,068.26/1,597.15/1,403.28，网络对 pipeline linear 仍高 +528.89/+335.02（95% 病人 bootstrap 区间 +468.72 至 +594.38 / +298.81 至 +376.16；451/483、417/483 人为正）。同层局部阴性区 HAT 对 pipeline linear +33.72（区间跨零），SwinIR -111.39（区间全负）。这是一项结果后、首例后解释性控制，不是新确认队列。
5. 定向重读已有可得全文/抽取文本：Radmanesh 2022 临床脑 MRI 异常退化与跨器官评估、SliceBridge 2026 的明示两边界线性基线及 T1 结果、Verschuur 2022 新生儿 T2 插值/分割、SafeRestore 2026 的 raw/恢复动作与认证，并结合 Fischer 2023、Morshuis 2025 既有全文审计及 Kuestner 2024 访问记录，形成[碰撞矩阵](literature/2026-10-01_msd_linear_failure_prior_art.md)。本轮没有把旧检索索引误称为新读全文，也没有得到 Kuestner 方法正文。
6. 在看到 MSD 病灶结果后，预写并完成[MSValid/ReMIND 两来源全前景 CSV 联结](TWO_SOURCE_EQUAL_NEIGHBOR_PERFORMANCE_CHECK_RESULT_2026-10-01.md)：模型在 MSValid 84/84、ReMIND 62/62 人均优于 raw linear。由于与 MSD 病灶 ROI 口径不同，再事后冻结[MSD 全前景方案](MSD_FULL_SUPPORT_EQUAL_NEIGHBOR_POSTRESULT_PLAN_2026-10-01.md)并完成 483 人、1,932 层 CPU 像素重放：[全前景结果](MSD_FULL_SUPPORT_EQUAL_NEIGHBOR_POSTRESULT_RESULT_2026-10-01.md)是 HAT 相对 raw linear -20.12 MSE（区间跨零），SwinIR -221.40（区间全负，但仅 244/483 人更好）。同病例病灶更差、全前景更好的符号反转为 HAT 195 人、SwinIR 197 人。PowerShell 独立逐人联结计数已复核。

## 当前科学判断与未完成事项

目前最可靠的新增信息是**固定 IXI→MSD 发布层合同下，已有 HAT/SwinIR 在标注肿瘤区域明显落后于简单同邻片线性插值，而全前景的 HAT 接近线性、SwinIR 均值较优**。预处理产生一部分病灶误差，但两网络相对同款预处理线性仍有剩余劣势；这不能单独证明肿瘤特异的学习先验损害、域移因果或临床漏诊。不能把本轮误写成 MSD 整幅图像上模型失效。原 MIRA `Delta O` 三来源测量仍是回顾性事实，但纯解析 phase 切换已能重现大效应，模型性能/新方法叙事进一步减弱。参考[创新决策备忘录](INNOVATION_DECISION_MEMO_2026-10-01.md)与[发表门槛](CLAIM_PUBLICATION_GATE_2026-09-30.md)。

[后续实验队列](MSD_EQUAL_NEIGHBOR_FAILURE_FOLLOWUP_2026-10-01.md)已将预处理对照标记完成：下一步先用 IXI **validation-only** 检查模型是否在原域也总输给线性，再寻找同空间独立 T2 病理标签来源。UPENN 现有 DICOM 与专家修订 atlas NIfTI 按设计不对齐，不能把标签贴到旧目标。只有 GPU 空闲且上述对照及先例门槛通过后，才考虑冻结小型 residual-shrinkage/fallback 方法试验。Kuestner 2024 方法全文、真正独立来源、IXI 派生权重权利、干净环境复现、作者/场合审查均未关闭；不能宣称当前已是可投稿创新。

本轮可复核数据与脚本都在 `innovation/experiments/`：`msd_equal_neighbor_linear_audit.py`、`msd_equal_neighbor_linear_audit/`、`msd_pipeline_linear_preflight.py`、`msd_pipeline_linear_preflight_brats001.json`、`msd_pipeline_linear_full_control.py`、`msd_pipeline_linear_full_control/`、`two_source_equal_neighbor_performance_check.py`、`two_source_equal_neighbor_performance_check/`、`msd_full_support_equal_neighbor_postresult.py`、`msd_full_support_equal_neighbor_postresult/`。各项生成统计保留逐目标或逐人表和完整汇总，所有研究判断可从上述协议与输出追溯。
