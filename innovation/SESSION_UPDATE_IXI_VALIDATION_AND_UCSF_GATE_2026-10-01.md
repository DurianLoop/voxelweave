# 本轮续作记录：IXI validation 诊断与 UCSF-PDGM 来源资格

用户要求在 GPU 正被占用时，继续基于 `D:\MRI` 单 T2、x4 缺层重建项目批量读论文、找创新点；能验证的先探索，不能验证的留下记录和后续方案，并将本轮对话产物集中在 `D:\MRI\innovation`。本轮沿用已有 29 篇 PDF 与多批全文/摘要审计，不重复声称旧材料是新读的全文；没有占用 GPU、碰正在训练的进程、读取锁定 IXI test 或更改用户已有的 `.gitignore`。

## 已完成的可复核工作

- [IXI validation 同邻片诊断](IXI_VALIDATION_EQUAL_NEIGHBOR_DIAGNOSTIC_RESULT_2026-10-01.md)按冻结的 58 人、每人 4 层 CPU 方案完成 232/232 层，并由独立只读脚本复核。患者等权全前景 MSE：raw linear 6,868.34、pipeline linear 6,868.34、HAT 4,945.28、SwinIR 5,014.36；两网络各在 57/58 人优于 raw linear。bootstrap 区间仅为此开发性 validation 样本的不确定性描述；checkpoint 曾由该样本选择，不能作为新外部确认。
- 先前已完成的 [MSD 同邻片肿瘤 ROI 对照](MSD_PIPELINE_LINEAR_CONTROL_RESULT_2026-10-01.md)为 raw/pipeline/HAT/SwinIR MSE 805/1,068/1,597/1,403；[同病例全前景复算](MSD_FULL_SUPPORT_EQUAL_NEIGHBOR_POSTRESULT_RESULT_2026-10-01.md)表明不能把局部差异说成整图崩溃。IXI validation 结果排除了这条代码路径普遍输给线性，但不能区分病理、域移、目标选择或预处理的因果作用。
- 核读 [TCIA UCSF-PDGM 官方页](literature/source_cache/ucsf_pdgm_official_2026-10-01/index.json)、[PMC 数据描述及 v5 元数据](literature/source_cache/ucsf_pdgm_descriptor_2026-10-01/index.json)，形成[来源资格报告](UCSF_PDGM_INDEPENDENT_T2_LABEL_SOURCE_GATE_RESULT_2026-10-01.md)。TCIA 对论文 501 人说法的修正为 **495 人、501 次检查**；6 次是其他 ID 的随访。501 条 CSV 中，298 条有 BraTS21 ID（分割 Training 262、Validation 36）；去掉随访后 495 条基线，其中 293 条有映射、202 条无映射。官方明确说该映射用于避免与 BraTS21 的数据泄漏。无映射不是已证明与 MSD/BraTS 或项目训练数据独立。
- 文献表明有 3D T2 和专家修订的分区肿瘤标签，但公开 T2 是非线性配准到 T2-FLAIR 1 mm 网格、去颅骨的 NIfTI，原始 DICOM 不提供。版本 5 的原方向修正仅针对 `DTI_eddy_noreg`，不能推及 T2。[官方包只读目录及单病例清单](UCSF_PDGM_SINGLE_CASE_FILE_LIST_RESULT_2026-10-01.md)返回 501 个与 CSV 完全对应的检查目录；事前预选 `UCSF-PDGM-005` 的同目录 T2 和肿瘤分割符号链接分别声明 2,693,713 与 50,345 字节。仍未取得文件内容、NIfTI 头或仿射，故未做 UCSF 病灶指标或跨来源叠标签。先前 UPENN 两文件 Aspera 试验认证失败、零字节；本轮 IBM Connect 文档端点连接失败，因此停止在官方材料支持的边界，未继续猜 CLI 用法。

## 创新判断与下一步

目前最牢靠的是**已发布邻片上下文的回顾性测量审计**，包括相同目标的成对误差可见性；它并不构成新的重建算法。MSD 中“全前景指标可能掩盖局部标注肿瘤误差”是值得报告的负结果，但异常保真、线性插值、选择性恢复与任务级不确定性均有先例，不能当作未经占据的宽泛新意。候选方法是后续按训练数据冻结的 residual shrinkage/线性回退规则；目前缺独立同网格标签、严格等处理对照和未触碰确认来源，不能借当前 MSD 结果训练后再把同集称为验证。

下一步按[已冻结的双文件头部协议](UCSF_PDGM_TWO_FILE_HEADER_PROTOCOL_2026-10-01.md)，为这两个精确文件取得有文档支持的 Connect 传输流程，再做 T2/标签头部形状、方向、仿射核验；同时继续查与 MSD/BraTS 的身份交叉映射。官方 IBM 文档本轮未能读到：一次 PowerShell 连接失败，另一种 Windows `curl` 在本机 Schannel 凭据阶段失败，均不能当作服务端拒绝证据。通过后另写事前像素协议：固定目标层、肿瘤/局部阴性 ROI、患者分母、raw/pipeline linear、PCHIP 与失败计数。不能通过则记录负结果并停止。Kuestner 2024 方法全文、权重再分发权利、干净环境复现以及作者/投稿场合审查也仍未完成。**当前尚无通过先例与复现双重审查的可发表 claim。**
