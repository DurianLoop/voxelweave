# MSValid 次级复制：IXI 训练 HAT/SwinIR 权重

**判定：冻结的次级单配对对照为正；不是第二个独立患者队列。** 这项实验在看过 fastMRI 训练权重的 MSValid 主结果后提出，并在运行 IXI 权重之前固定了[协议](MSVALID_IXI_WEIGHTS_SECONDARY_PROTOCOL_2026-10-01.md)。它检验的是现象是否仅依赖那一对 fastMRI 权重，不估计纯训练来源效应，也不增加原主结果的事前检验次数。

## 结果

采用相同的 84 名 RRMS T2 患者、479 个 residue-1/3 目标、acquired-only 支撑和相位合同：IXI-T2 训练的 HAT phase 0 始终固定，IXI-T2 训练的 SwinIR 由 phase 0 共享锚点切换为 phase 2 不相交锚点。全部患者/目标完成，无失败；全部 84 名患者的 `Delta O` 为正。

| 患者等权统计 | IXI 权重次级结果 | 原 fastMRI 权重预设结果，仅供描述 |
|---|---:|---:|
| 共享 `O` | 1.0420% | 2.8428% |
| 不相交 `O` | 25.2276% | 22.5993% |
| 不相交减共享 `Delta O` | **+24.1856 个百分点** | +19.7565 个百分点 |
| 5,000 次患者 bootstrap 95% 区间 | **+23.7150 至 +24.6726 个百分点** | +19.3276 至 +20.1605 个百分点 |
| 正 / 负患者 | 84 / 0 | 84 / 0 |
| SwinIR 共享 / 不相交 MAE | 130.33 / 129.46 原始强度单位 | 141.68 / 139.06 原始强度单位 |

IXI 权重下逐患者 `Delta O` 范围为 +19.05 至 +30.31 个百分点，residue 1/3 的患者等权结果分别为 +23.8635/+24.5077 个百分点。53/84 人的不相交 SwinIR MAE 比共享时低。两个权重对在相同患者上的 `Delta O` 均值相差 +4.4291 个百分点（IXI 减 fastMRI），这是结果后描述，不是随机化训练来源比较。原始强度单位跨扫描不具有绝对可比性。

## 完整性与独立复核

- 协议 SHA-256 `18b99551b6cf71cb485c7ac31027a298904bf9d656151b7434962e29220e1f03`；[CPU 脚本](experiments/msvalid_ixi_weights_secondary.py) SHA-256 `6e8fc904784c66642a076a341043bf12d6e615e6c3a7d09ff2fa097db2ac79f2`。脚本运行前逐一校验 84 份源 NIfTI 的提取清单 SHA-256 和两个权重 SHA-256。
- IXI HAT 权重 SHA-256 `2fae831ab933cf260972260ebec4349f3895106ac7b4d1af3ba368f407498eae`；IXI SwinIR 权重 SHA-256 `6a819e47e65bd96c2d6e5b6d3adc212e1a46347080a0a661c602367be8a6f323`。模型类是仓库已有的 IXI 2.5D HAT/SwinIR 实现；CPU FP32、两条 torch 线程，未触碰 GPU 训练。
- [结果目录](experiments/msvalid_ixi_weights_secondary/summary.json)含汇总、逐患者和逐目标 CSV；[独立只读复核器](experiments/verify_msvalid_ixi_weights_secondary.py)核对协议/脚本/资格/源清单/权重哈希、479 个目标精确名单、固定参考 MAE、逐患者 residue 等权均值和同种子 bootstrap，运行结果 `verified=true`。
- 结果文件 SHA-256：`summary.json` `d36cde42258600c71fb48f5eff0a8cf8424a414ae5fbbbb69c3bae81e97e1023`；`per_patient.csv` `c70ae51db2e212a353ef651bf1a581104db4dc70c4d467035357260f68711659`；`per_target.csv` `ad2871338d1e4288913327eb5935d9056acd70bb447640d1f288a36533830ba4`。

## 科学解释与投稿边界

这个结果说明同一 RRMS 队列的共享测量依赖现象不限于之前一组 fastMRI 训练权重，并为仅使用 IXI/MSValid 公开来源重新构稿提供技术可能。它**不能**替代独立患者来源验证：84 人在上一预设试验中已被评分；此次 pair 选择也受先前结果启发。两对权重同时改变训练来源和具体 checkpoint，不是训练来源的受控因果对照。phase 2 仍改变完整邻层内容、signed geometry 和每相位归一化，非纯锚点 ID 随机化。`O` 需回顾性真值；未验证病灶、安全、真实薄层恢复或临床使用。IXI/MSValid 的公开许可也不自动解决原稿中 fastMRI 刊图和 NingXia 伦理材料的问题；若走公开来源路线，必须重新生成仅含可分享材料的完整主文、图表和补充材料。
