# MC-RC 九系列来源预检：原生头、标签可用性与网格

本轮取得真实来源证据，尚未取得新患者重建或分割性能。固定 VS-MC-RC-001/002/003 的全部九条 T2 描述系列，完成 473 个 DICOM 对象头部检查；独立复核后，六条通过原生头部条件，四条、两名患者同时通过标签网格预检。该结果属于来源/开发预检，不能称四名患者、完整新来源合格或新方法独立确认。

依据：[执行前头部方案](MC_RC_THREE_PATIENT_NATIVE_HEADER_PLAN_2026-10-02.md)、[标签方案](MC_RC_THREE_PATIENT_LABEL_GRID_PLAN_2026-10-02.md)、[追加方案](MC_RC_GEOMETRY_AND_LABEL_AVAILABILITY_FOLLOWUP_PLAN_2026-10-02.md)。原始下载/头部记录在 [attempt01](literature/source_cache/mc_rc_three_patient_headers_2026-10-02/attempt_01.json)，原标签失败在 [label_grid_attempt01](experiments/mc_rc_native_t2_label_gate/label_grid_attempt_01.json)，追加结果在 [geometry_availability_attempt01](experiments/mc_rc_native_t2_label_gate/geometry_availability_attempt_01.json)。

## 实际读取范围

下载九个 MR 系列 ZIP 和一个官方标签 ZIP，合计 79,554,134 bytes，低于原 300MB 合同上限。MR ZIP 传输包含像素字节，但全部 DICOM 均用 `stop_before_pixels=True` 读取；未解码任何 MR `pixel_array`，未运行新 MR 重建/分割性能实验。另提取并读取预选九系列中实际存在的六个标签数组，其余三条明确缺文件。

官方 pathname 表实际为 CSV，非 XLSX。使用此前已读取的 Spreadsheets 技能，以 bundled artifact-tool 只读导入虚拟 `Official pathnames!A1:O488`；487 条记录、15 列，所有单元格与独立 Python CSV 解析精确吻合，UID 保持字符串，没有编辑或导出工作簿。忽略 `__MACOSX/._…csv` AppleDouble 伪表。见 [读取证据](experiments/mc_rc_native_t2_label_gate/official_pathnames_artifact_read.json)。源 CSV SHA256：`f9d8d2b2ecab74824d02c95fdccd42f60c82f5e17746b830e3c67f73f9a372eb`。

## 标签包没有覆盖全部现行目录

官方现行 API/CSV 均有 487 系列，但发布的 2023 标签 ZIP 实际只有 301 个非 MacOS NIfTI、124 名患者。联结失败不等于全部路径拼错：

| 类别 | 系列数 | 可作出的判断 |
| --- | ---: | --- |
| 指定路径有真实标签文件 | 301 | 文件存在；仍需逐扫描核 native geometry 和 grid |
| SegmentationPath 为空 | 60 | 既有 T1 53 条、2026 新增 T1 7 条；不能借同 study 的 T2 标签补上 |
| 指定 T2 路径在包内不存在 | 126 | 全部为 2026 新增 T2；开放 MR 影像不等于标签同步开放 |

按官方 ID 规则排除全部 58 名共享 VS-SEG 患者后，**71 名候选患者、159 条 T2 系列有实际标签文件**。这是目录资格数，尚非 71 名原生薄层或独立确认患者。此前 102 候选、100 有 T2 描述患者的统计仍是历史目录结果，不能作为当前带标签可用人数。旧八行 crosswalk 的 legacy UID 联结缺口继续保留。

VS-MC-RC-003 三条系列的标签均缺失；其中两条头部条件通过，也不能放行标签/任务实验。没有猜测新的标签下载地址或用其他时间点标签替代。

## 几何估计器修正的事后属性

首跑以逐分量中位相邻 IPP 差估计步长，在 002 第二时间点 144 切片上产生 0.0300mm 累计位置误差，触发原 0.02mm 阈值。沿法向 gap 的变化仅约 5.2e-7mm，不能据此称真实采集不规则。

在追加方案保存后，用全部 IPP 的中心化线性回归拟合 affine，最大位置残差为 0.000482mm；独立完整设计矩阵 `np.linalg.lstsq` 和首末位置法核验一致。**0.02mm 位置阈值、0.05mm 标签角点阈值未改变**，没有阈值搜索、配准、缩放或形变修复。原首跑五条头资格、三条标签预检和完整标签 gate `exit1 / complete=false` 均保留；追加结果明确为事后几何估计器修正。

| 患者/时间点 | DICOM r,c,z 间距 mm | 名义层厚 mm | 标签前景体素 | 拟合后最大网格角点误差 mm |
| --- | --- | ---: | ---: | ---: |
| 001 t1 | 0.527344, 0.527344, 0.7000 | 1.4 | 1,011 | 0.000401 |
| 001 t3 | 0.527344, 0.527344, 0.7000 | 1.4 | 750 | 0.001537 |
| 002 t1 | 0.507812, 0.507810, 0.8000 | 0.8 | 1,192 | 0.008307 |
| 002 t2 | 0.507812, 0.507813, 0.4000 | 0.8 | 7,046 | 0.045605 |

只允许整数轴置换/翻转来联结网格。002 t2 的 0.045605mm 接近预定 0.05mm 边界，报告实值，不能描述为数值精确重合。001 t2 缺 `MRAcquisitionType`，保持 pending，不能说已经确认 2D。002 的 reformatted 与 003 的 MPR/派生系列即使网格吻合仍不放行。

**间距与物理分辨率分别解释。** 0.4mm/0.7mm 发布网格间距不证明对应物理分辨率；名义层厚分别为 0.8mm/1.4mm，层面 oversampling、采集 k-space 和实际 PSF 尚未认证。`ORIGINAL` 与 3D tags 支持本轮头部条件，但不是物理分辨率的完整证明。单患者跨时间点的体素数差不能直接解释成病灶进展、重建损害或重复观测噪声。

## 独立复核与后续门槛

[独立脚本](experiments/verify_mc_rc_native_t2_label_preflight.py)从原九个 ZIP 重读 473 头，并重查六标签数组；用完整最小二乘和 `inv(DICOM affine) @ label affine` 的整数变换核验，避免复制主实现的 48 置换穷举。实际 `exit0 / errors=[]`，见 [独立证据](experiments/mc_rc_native_t2_label_gate/independent_raw_geometry_grid_verification.json)。其通过的是来源算术/几何复核，不清除全库标签覆盖失败，也不增加科学独立性能确认患者。

接下来优先核有实际标签的 71 人/159 系列；预选/下载及患者整体分组见 [后续准备](MC_RC_LABELLED_NATIVE_EXPANSION_PREPARATION_2026-10-02.md)。当前四系列开始 MR 数组或模型实验前，还需要另写观测、预处理、动作、预算与评价合同。多时间点不得当独立患者；已做来源/开发预检的患者不作新方法未见确认。任务模型训练患者独立性、病灶评价和真实低分辨采集的外推边界仍待验证。
