# ReMIND 术前 2D T2：新患者来源的冻结 MIRA 对照协议

**冻结状态：在读取任何 ReMIND 图像像素、预测或目标误差前写入。** 既有 MSValid、IXI 和 fastMRI 结果已知，故这不是完全独立的方法发现；但 ReMIND 是新患者/机构来源，全部患者及终点先由 TCIA 公共元数据和 DICOM 头部确定。阴性、头部不合格和推理失败都将保留，不凭结果更换来源、序列或模型。

## 来源与样本

唯一来源为 TCIA ReMIND collection DOI `10.7937/3RAG-D070` 的官方 NBIA API。全部 63 条术前 `2D_AX_T2`（36 人）与 `2D_AX_T2_BLADE`（27 人）序列按[冻结清单](literature/remind_native_t2_inventory.json)纳入，清单 SHA-256 `19186dd24b92e7a4db48ff9ee9c9e6d9cbd217e1c6e7e9ab5d35095585856b8c5`；患者 ID 无交集。不得从 3D SPACE、FLAIR、术中、术后或其他 2D 方向补人。下载每条清单所列 UID 的官方 `getImage` ZIP，核原包 SHA-256 并保留其 `LICENSE`；下载重试只对同 UID，不能换序列。TCIA 文件附带 CC BY 4.0、来源署名和禁止重识别条款。

上述两种 2D 系列试跑头的物理层位规则，但 `ImageType=ORIGINAL/PRIMARY/MPR`，不能仅凭发布 DICOM 证明每个层图像是未经重建的独立采集；任何阳性只称“TCIA 发布的术前 2D T2 规则层网格”的同目标上下文审计，不声称纯原始 k-space 测量身份因果效应。

## 仅头部资格闸门

对每个 ZIP 仅用 `pydicom.dcmread(..., stop_before_pixels=True)`检查：全部文件属于清单 PatientID、SeriesInstanceUID 和一个 StudyInstanceUID；DICOM 数等于 TCIA ImageCount，SOPInstanceUID 唯一；`StudyDescription=Preop`、SeriesDescription 匹配清单、单通道 `MONOCHROME2`；每层 Rows/Columns/PixelSpacing 一致（spacing 相对容差 0.5%）；每层 ImageOrientationPatient 与首层逐元素差不超过 `1e-4`；沿首层行/列方向叉积定义的法向投影后，位置唯一，全部相邻层距为正且相对中位数偏差不超过 2%；有效层数至少 24。按物理投影从小到大排序，不按文件名或 InstanceNumber 排序。头部不合格者标记预结果资格失败，不替换患者。

令层序列长度为 `n`，phase-0 锚点索引 `0,4,8,...`，phase-2 为 `2,6,10,...`。目标仅取 `z mod 4 in {1,3}`，且每相位在该目标的两侧各至少有两张真层。每个 residue 的合格目标升序表长度 `m` 必须至少为 2；用零基下标 `floor((m-1)/3)` 和 `ceil(2(m-1)/3)` 各取一个。每人因此固定 4 目标（residue 1/3 各 2 个）；若不足则头部不合格。只解码两相位的全部偶数锚点层及预定四张奇数目标层，其他奇数层不解码、不筛选。方案设计基于层位而非像素。

## 冻结推理与评分

- 两个模型均为已存在的 IXI T2 训练实现：HAT `baseline/ixi_hat_2p5d/runs/full_test115/checkpoints/hat_epoch_best.pth` SHA-256 `2fae831ab933cf260972260ebec4349f3895106ac7b4d1af3ba368f407498eae`；SwinIR `baseline/ixi_swinir_2p5d/runs/full/checkpoints/swinir_epoch_best.pth` SHA-256 `6a819e47e65bd96c2d6e5b6d3adc212e1a46347080a0a661c602367be8a6f323`。不使用 GPU；CPU float32、两条 torch 线程，无 AMP/TF32。仅对预定锚点与目标的 DICOM `pixel_array` 按层解码为 float32，应用每层 `RescaleSlope`/`RescaleIntercept`（缺省 1/0）；非有限、异常形状或锚点全常数记推理失败。
- 两相位均使用其**全部**真实发布层锚点的 observed-only min/max；沿用 `experiments/msvalid_mira_confirmation.py` 的 `normalize_volume`、256x256 resize、HAT/SwinIR 原 `interpolate_volume` 条件四通道、残差与反归一化。HAT phase 0 为固定参考 `a`；SwinIR phase 0 为共享 `b0`，phase 2 为不相交 `b2`，均预测同一个原生发布层目标 `y`。参考只计算一次，同一预测同时配两个伙伴。
- 评分支撑仅由 phase-0 紧邻两真锚点的 `abs(x)>1% * max(abs(x))` 并集确定，不读目标，不在两条件间变动。若支撑空或端点分母非正，记录该患者失败。每目标 `T=(MSE(a,y)+MSE(b,y))/2`、`O=mean(((a-b)/2)^2)/T`。同时报告配对 MAE/MSE、参考与伙伴 MAE、层距和支撑像素比例。原始强度单位只适合同一患者配对解读。

## 聚合、区间和判据

患者内先对每个 residue 的两目标平均，再对 residue 1/3 等权；然后每位**完整**患者等权求 `Delta O=O_disjoint-O_shared`，保留全部失败及原因。主点估计为所有完整患者的均值。主 95% 区间用 5,000 次分层患者 bootstrap：分别在 `2D_AX_T2` 与 `2D_AX_T2_BLADE` 完整患者中有放回抽同等人数，再按完整患者原组人数占比合并；种子 `20261002`。同法分别报告两组点估计及区间，不把层或两个目标当独立样本。预定成功条件为：至少 50/63 人完整、普通 T2 至少 25/36、BLADE 至少 20/27；主区间下界严格大于 0，且两个 2D 协议层的点估计均大于 0。其余结论即使有正点估计也不记为方案成功。主结果之外的两组区间、伴随 MAE 和与 MSValid 权重对的数值比较均为描述，不用另一指标替换主判据。

结果目录固定为 `innovation/experiments/remind_native_t2_ixi_pair/`，首次运行拒绝覆盖。保存清单/协议/脚本/权重及全部 ZIP SHA-256、每人头部资格与失败原因、逐目标和逐患者 CSV、汇总 JSON，并由单独的只读脚本复核病例数、目标位置、患者等权与同种子区间。若下载、DICOM 解码、数据完整性或 CPU 推理不完整，可在不看主端点的前提下仅重试**同一 UID**；若仍失败，按预定失败规则报告。不得根据任何早期患者方向停算或换模型。

## 不可跨越的解释

同一目标上的上下文切换仍同时改变完整邻层内容、signed geometry 与 observed-only 归一化，不能孤立纯锚点身份。ReMIND 术前脑肿瘤 MRI 与 MSValid RRMS、IXI 健康 T2 存在疾病、对比度、厚度和发布处理差异；阳性可增强“所测试固定模型和发布层网格下共享依赖审计”的跨来源证据，不能证明病灶安全、薄层真实恢复、临床效益、可部署个例正确性评分或所有 MRI 域。跨库匿名患者身份无法绝对核实。TCIA 图像不得用于重识别，原始 DICOM 不进入稿件交付包。
