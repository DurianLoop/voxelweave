# ReMIND 共同缩放与反向相位：全量结果后敏感性

**判定：两项探索性对照在全队列维持正向；不是独立确认或纯身份因果检验。** 已看到[事前主结果](REMIND_NATIVE_T2_CONFIRMATION_RESULT_2026-10-01.md)后，按[结果后固定方案](REMIND_POSTRESULT_CONTROLS_PLAN_2026-10-01.md)对同一 63 人、原四目标、IXI HAT/SwinIR 权重完成 CPU float32 推理。仍为 62 人/248 目标完整，ReMIND-092 仍仅在头部阶段按原规则排除，无新像素或推理失败。

| 患者等权指标 | 原事前前向 | 两相位共同 min/max，前向 HAT0 | 同一共同 min/max，反向 HAT2 |
|---|---:|---:|---:|
| 共享 `O` | 1.1093% | 1.1130% | 1.1065% |
| 不相交 `O` | 27.5092% | 27.4366% | 27.4114% |
| 不相交减共享 `Delta O` | **+26.3999** 个百分点 | **+26.3236** | **+26.3049** |
| 5,000 次分层患者 bootstrap 95% 区间 | +25.6945 至 +27.1686 | +25.5927 至 +27.1091 | +25.6051 至 +27.0733 |
| 正向患者 / 目标 | 62/62；248/248 | 62/62；248/248 | 62/62；248/248 |
| 伙伴共享 / 不相交 MAE | 132.13 / 131.71 | 132.09 / 131.63 | 131.39 / 131.59 |

共同缩放前向相对原结果减少 **0.0763 个百分点**；逐患者有 51 人降低、10 人升高、1 人不变，变化范围约 -0.583 至 +0.099 点。普通 `2D_AX_T2` 前向/反向为 +26.4088/+26.4589 点（各 35/35 人正），BLADE 为 +26.2133/+26.1052 点（各 27/27 人正）；两组两方向的探索性区间下界均 >0。预先写下的“前向至少保留原效果一半、全体与两组区间下界均 >0”敏感性判据通过。反向使用 phase-2 真锚点建立支撑，不能与前向差值解释成相位随机化效应。

[汇总 JSON](experiments/remind_postresult_controls/summary.json)、[逐患者 CSV](experiments/remind_postresult_controls/per_patient.csv)、[逐目标 CSV](experiments/remind_postresult_controls/per_target.csv) SHA-256 分别为 `99b42d3bcd763e926deefa1bc18132f9ba81da17cc76e9d9417978ede316539c`、`c87115fdae0ff2413880e66eb2ce76591bd7a1de62e53e535d2e3ad8000e0af9`、`4c0c55e09715c9bd5b58119a08b1e4060197ad6b7dc135cc486bdccbc5d98414`。[CPU 脚本](experiments/remind_postresult_controls.py) SHA-256 `560cb7f8e239afb49b8a11daaa71b6982ed6e6b35c993701231fafb5bdcdde3f`；方案 SHA-256 `6e6f07b91228ac070c6f2d4e01d4d7db01e166fb6ca38cc19702e2d9ce2f9b3f`。[独立只读复核器](experiments/verify_remind_postresult_controls.py) SHA-256 `81d78969dea7c3cb2f43ec2e5e065e0c33d0feecf39206a736eb81ef0a67d1ac`，复核结果 `PASS: 62/63 patients, 248 targets; forward=0.263236, reverse=0.263049, normalization_sensitivity=True`。

共同缩放让共享条件利用了不相交锚点的两个极值，不代表真实部署输入。相位反转仍替换完整邻层、signed geometry 和图像内容。两项结果只削弱独立缩放差异和单一方向作为**唯一**解释，不能解决发布 DICOM 的 `MPR` 标志、采集层独立性、纯物理身份因果或临床应用问题。原事前 ReMIND `Delta O` 与区间保持不变；不能把这两个结果后区间当新的独立重复。
