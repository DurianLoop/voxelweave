# ReMIND 原生术前脑 T2：独立队列来源资格审计

目的：寻找尚未参与本项目 MIRA 方法开发且允许公开研究使用的第二患者来源。本文件记录**像素读取前**的公开元数据和头部资格审计；后续冻结方案的全量 CPU 结果见[正式结果](REMIND_NATIVE_T2_CONFIRMATION_RESULT_2026-10-01.md)。发布 DICOM 含 `MPR`，不能据此确认各层为独立原始采集。不能把已有 MSValid 两对权重当成两个独立队列。

## 官方来源与候选合同

2026-10-01 从 TCIA 官方 NBIA API `https://services.cancerimagingarchive.net/nbia-api/services/v1/getPatient?Collection=ReMIND` 与 `getSeries?Collection=ReMIND&Modality=MR` 直接读取：集合为 114 名患者、670 个 MR 序列。每条序列元数据记录 `LicenseName=Creative Commons Attribution 4.0 International License`、`LicenseURI=https://creativecommons.org/licenses/by/4.0/`、`CollectionURI=https://doi.org/10.7937/3RAG-D070`。术前 `3D_AX_T2_SPACE` 有 66 序列 / 66 患者，TCIA `FileSize` 总计约 1.7 GB，通常约 192 幅；术前 `2D_AX_T2_BLADE` 为 27/27、约 0.5 GB，`2D_AX_T2` 为 36/36、约 1.02 GB。先限制在一种原生 3D axial T2 SPACE 协议，避免事后混合扫描合同。

元数据固定试跑的首条记录按 `PatientID, SeriesInstanceUID` 字典序选择：`ReMIND-002`，UID `1.3.6.1.4.1.14519.5.2.1.251095052855047573579916052732313639478`，`ImageCount=192`、`FileSize=25591156`。[仅头部结果](literature/remind_native_header_pilot.json)显示 192 个唯一层、约 1.0 mm 规则间距、方向完全一致，未解码像素。但 `ImageType=ORIGINAL/PRIMARY/MPR` 对应 3D SPACE 体积重建，层间物理采集独立性与原 2D 层插值合同不同；**不把这个 3D 序列用于主要独立确认**。

进一步从相同官方接口核得术前 `2D_AX_T2_BLADE` 为 27 名患者、`2D_AX_T2` 为 36 名患者，患者 ID **没有交集**。两组固定试跑头部结果分别为[70 层、2.5 mm BLADE](literature/remind_blade_header_pilot.json)和[28 层、6 mm 普通 T2](literature/remind_plain_header_pilot.json)，均有唯一层位置和稳定方向，未解码像素；两者 `ImageType` 都带 `MPR`。因此可把它们称为 TCIA 发布的术前 2D T2 规则层网格，**不能仅凭 DICOM 头证明每层独立原始采集**，此限制必须随任何后续正结果报告。两序列协议不同，需分别报告，正式队列资格不能按结果挑换。

拟正式使用 IXI T2 训练的冻结 HAT→SwinIR 对照，以 TCIA 发布的术前 2D DICOM 规则层作为输入；若全部头部资格通过，这将是与 MSValid、IXI 开发患者不同的脑肿瘤队列。资格通过前不能写成已具备验证集。正式分析必须先固定患者/序列样本、目标层、预测及 mask 合同、权重/源码哈希、患者 bootstrap 和失败规则，再读取任何目标像素。若使用 TCIA 图像刊图，按官方 CC BY 4.0 给出准确来源与归属，并遵守随下载包的禁止重识别和来源署名条款。

## 排除的捷径

- Zenodo `19541844` 的 BraTS 2021 二次上传虽标 CC BY 4.0，但上传者不是官方 BraTS 发布方，也未给出原始授权链；标准 BraTS 图像已统一重采样，不能直接作为真实物理采集层身份干预的独立确认。
- Zenodo `12700312` 的 ReMIND2Reg 虽明确引用官方 TCIA ReMIND 且标 CC BY 4.0，但把 MRI 裁剪并重采样到 `0.5 mm` 等距网格；不用于主锚点身份实验。
- Zenodo `15381866` NeuriPhy 描述含 T2，却暂无公开文件；Zenodo `20485285` OSI2ONE 是幻影而非患者。`dataset/OAI-ZIB-prepared` 的本地样例是标签样灰度图，不是 T2 图像真值。
