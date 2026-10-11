# ReMIND 主结果的误差对齐代数分解

**结果后描述，不是独立实验。** 仅从[事前主结果的 248 行逐目标 CSV](experiments/remind_native_t2_ixi_pair/per_target.csv)读取 MSE 与 `O`，按[固定分解方案](REMIND_ERROR_ALIGNMENT_DECOMPOSITION_PLAN_2026-10-01.md)代数重写。未重新解码 DICOM、重新推理或选择患者。62 位患者两 residue 等权，普通 T2 与 BLADE 分层患者 bootstrap 仅为探索性描述，不替换原事前区间。

| 患者等权量 | 全队列 | 普通 T2 | BLADE |
|---|---:|---:|---:|
| 原 `Delta O` | +26.3999 个百分点 | +26.5156 | +26.2500 |
| 伙伴 MSE 失衡贡献 | **+0.0779** 个百分点 | +0.0710 | +0.0868 |
| 误差余弦/对齐贡献 | **+26.3220** 个百分点 | +26.4446 | +26.1632 |
| 共享 / 不相交误差余弦 | 0.9780 / 0.4508 | 0.9796 / 0.4500 | 0.9759 / 0.4519 |

两贡献在每个目标精确相加为 `Delta O`，最大绝对闭合误差 `2.22e-16`。伙伴 MSE 比在 `1/1.05` 至 `1.05` 的 81 个目标（49 人）中，目标等权 `Delta O` 仍为 +26.47 个百分点，81/81 目标为正；这只是结果后筛选的描述，不作患者独立推断。`1/1.10` 至 `1.10` 为 146 目标/57 人、+26.20 点；`1/1.20` 至 `1.20` 为 201 目标/59 人、+26.37 点。

[结果 JSON](experiments/remind_error_alignment_decomposition/summary.json)、[逐目标表](experiments/remind_error_alignment_decomposition/per_target.csv)、[逐患者表](experiments/remind_error_alignment_decomposition/per_patient.csv) SHA-256 分别为 `d2470873096c4e4affbaa0a30e0b5b2ee53b06d4aafe9b0bcbf966ba0e2211bdb`、`cf6d01cace9b7def59e027e26672460a66d59ba57537fa274c5e7ed589914c98`、`b159d8848eb5a403bcc30d53717c06196aca476439501b5d0ffd00da1fa20de0`。[计算脚本](experiments/remind_error_alignment_decomposition.py) SHA-256 `cb7856579fd87d7b9ea9b471bd1fb43f54c3f8e6b4f1fe1cbd3a3f25bac8f2a4`；[独立只读复核器](experiments/verify_remind_error_alignment_decomposition.py) SHA-256 `fa4281846ce72e746efdbf1c86f55ee822bb0f6f4876f4f12c739ffcfc8990ce`，复算输入行、恒等式、患者/分层聚合及同种子 bootstrap，结果为 `PASS: 62 patients, 248 targets; quality=0.000779, alignment=0.263220`。

该分解只表明按固定 `O` 定义，伙伴 MSE 分母失衡不是主差的主要代数来源。误差余弦降低仍可由完整邻层内容、signed geometry、归一化、MPR 发布处理及模型响应共同造成；没有从这组数值识别纯物理身份效应。
