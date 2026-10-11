# ReMIND 独立患者来源：术前 2D T2 冻结确认结果

**判定：预定主门槛通过；仅在 TCIA 发布的规则层网格和这一固定 IXI 权重对上成立。** 在读取任何 ReMIND 像素前，已冻结[协议](REMIND_NATIVE_T2_CONFIRMATION_PROTOCOL_2026-10-01.md)、[63 人清单](literature/remind_native_t2_inventory.json)、[头部资格与目标层](literature/remind_native_t2_qualification.json)、IXI-T2 HAT/SwinIR 权重、患者分层 bootstrap 及失败规则。ReMIND 来自 TCIA DOI `10.7937/3RAG-D070`，与既有 MSValid RRMS 来源不同；跨库匿名患者身份不能绝对核实。

## 全量结果

63 人中 62 人完成、每人预定 4 目标，共 248 目标；唯一排除为头部阶段 ReMIND-092（21 层，低于预定 24 层门槛）。没有像素解码或模型推理失败，没有换序列、患者、模型或终点。HAT phase 0 参考保持固定，SwinIR phase 0 为共享伙伴、phase 2 为不相交伙伴，评分支撑只来自 phase-0 真锚点。

| 患者等权统计 | 全队列 | 普通 `2D_AX_T2` | `2D_AX_T2_BLADE` |
|---|---:|---:|---:|
| 完整患者 | 62/63 | 35/36 | 27/27 |
| `Delta O`，不相交减共享 | **+26.3999 个百分点** | +26.5156 | +26.2500 |
| 5,000 次分层患者 bootstrap 95% 区间 | **+25.6945 至 +27.1686** | +25.6603 至 +27.3785 | +24.9766 至 +27.6079 |
| 正向患者 | 62/62 | 35/35 | 27/27 |

全队列共享 `O` 为 1.1093%，不相交为 27.5092%；residue 1/3 的患者等权 `Delta O` 分别为 +26.3434/+26.4565 个百分点。逐患者范围 +20.3327 至 +33.8934 个百分点。SwinIR 伙伴患者等权 MAE 共享/不相交为 132.13/131.71 原始强度单位，31/62 人的不相交 MAE 较低；原始强度不可跨扫描直接比。预定门槛要求至少 50/63、普通 ≥25/36、BLADE ≥20/27，主区间下界 >0 且两组点估计 >0，本次全部满足。不能把目标层或两组当成额外独立复制。

## 完整性与复核

- [CPU 推理脚本](experiments/remind_native_t2_ixi_pair.py) SHA-256 `f3beec0d45ec03f5d15cd3a1e85c1ab0b29c8f146ce0e22425c44771191d92ab`；冻结协议 SHA-256 `1d5f761ae68500cd4ffea15ff0b30e955715ba5135c9664053fa5ccfc2f32534`；头部资格快照 SHA-256 `2f93f2849968a07b800ffca8c66ee21c9cdaea9e7152aac9c900d48099991b49`。两权重哈希见协议。CPU float32、两条 torch 线程，未访问 GPU。
- [结果汇总](experiments/remind_native_t2_ixi_pair/summary.json)、[逐患者 CSV](experiments/remind_native_t2_ixi_pair/per_patient.csv)、[逐目标 CSV](experiments/remind_native_t2_ixi_pair/per_target.csv) SHA-256 分别为 `e755ef75d3a20daf4db560426145d56f8356c69b2c8c7108c9b9e2ec9abaf071`、`1227664c0b2fb4a96092300d61daea67855161f6c00d4ccccc9d05bcb42eceb2`、`450def82f8f03261b55c36ffaed952ee865e7c3be83c0c5b77df1f6a8e441e1c`。
- [独立只读复核器](experiments/verify_remind_native_t2_ixi_pair.py)最终 SHA-256 `acf8776e65b05827db77b06f41543e320e398e88562d4b96900ffee791e27b53`；按官方下载清单重算全部 63 个 ZIP 和两权重哈希，核对固定目标精确位置、逐目标 `O` 与配对 MSE、固定参考、逐患者 residue 等权、失败集合及种子 `20261002` 的分层区间。结果 `PASS: 62/63 patients, 248 targets; delta O=0.263999, CI=(0.256945, 0.271686), primary_success=True`。首遍复核器误以为不合格者在资格快照中也有 ZIP 哈希，报 `KeyError`；仅修正复核器去读取全量下载清单后通过，主推理输出和冻结脚本未改。

## 科学边界与下一步

这给出继 MSValid 之外的**另一个患者来源**上的预定单对照正结果，但实验是在见到既有 MSValid/IXI 结果后设计，不能抹去研究历史选择。ReMIND 的 `ImageType` 均含 `MPR`，DICOM 头无法证明发布层是独立原始采集；因此这里只支持发布的术前 2D T2 规则层网格上的上下文/依赖现象。切换 phase 也同时改变完整邻层内容、相位几何和 observed-only 归一化，不隔离纯锚点身份因果效应。`O` 需回顾性目标真值，不是临床可用的逐例正确性分数；肿瘤病灶安全、真实薄层恢复和临床效益均未验证。

论文可把 MSValid 与 ReMIND 写成疾病/来源不同、各有预定方案的**两项单权重对照**，并把同 MSValid 的 IXI 权重次级重复单列为探索性。不可声称“全架构矩阵跨两个外部队列重复”，也不可把两队列数值差解释为疾病效应。尚需原稿 fastMRI 刊图权利、NingXia 来源/伦理及完整补充材料同步；若重构仅用 IXI/MSValid/ReMIND 公共许可的稿件，也需单独完成全套图表、引用和复核。
