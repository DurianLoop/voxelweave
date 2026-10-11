# 公开来源线性伙伴负对照：两来源全量 CPU 结果

**性质：看到两来源主结果后设计的探索性负对照，不是独立确认。** [运行前方案](PUBLIC_LINEAR_PARTNER_CONTROL_PLAN_2026-10-01.md)固定了原 IXI 权重 HAT phase-0 参考、目标、acquired-only 支撑、患者权重和 bootstrap；仅把 SwinIR phase-0/phase-2 伙伴替换为两张对应真实发布层之间的原生强度线性插值。[CPU 脚本](experiments/public_linear_partner_control.py)重放每个目标的 HAT 预测，并以原逐目标参考 MAE 和支撑像素数为闸门；未用 GPU，未改原结果。线性权重按头部验证的近规则层网格与原模型相同的索引相位 `1/4` 或 `3/4` 计算，ReMIND 未逐层改用实际微小 z 距离偏差。

| 患者等权指标 | MSValid RRMS | TCIA ReMIND 术前 T2 |
|---|---:|---:|
| 固定清单/完成患者；目标 | 84/84；479/479 | 62/63；248/248 |
| 线性伙伴共享 `O` | 5.8641% | 5.6629% |
| 线性伙伴不相交 `O` | 26.4085% | 28.6015% |
| **线性伙伴 `Delta O`** | **+20.5445 个百分点** | **+22.9386 个百分点** |
| 95% 患者 bootstrap 区间 | +20.1283 至 +20.9729 | +22.3772 至 +23.5257，按普通 T2/BLADE 分层 |
| 正向患者 | 84/84 | 62/62；普通 T2 35/35、BLADE 27/27 |
| 线性伙伴共享/不相交 MAE，扫描内原始强度单位 | 145.72 / 145.33 | 150.11 / 149.43 |
| 原 SwinIR 伙伴主 `Delta O`，仅并列描述 | +24.1856 | +26.3999 |

ReMIND 线性对照的普通 `2D_AX_T2` 患者均值为 +22.9994 点，BLADE 为 +22.8597 点。ReMIND-092 仍按原头部 24 层门槛排除；没有新增像素/推理失败。所有 727 个固定目标的 HAT 参考 MAE 与原始主实验逐目标核对，容差 `1e-5`，支撑像素数完全相同。[独立只读复核器](experiments/verify_public_linear_partner_control.py)核查精确目标集合、患者内 residue 等权、5000 次相同种子 patient bootstrap、ReMIND 35/27 分层和全部汇总，输出两来源 `PASS`。

MSValid [汇总](experiments/public_linear_partner_control/msvalid/summary.json)、[逐患者](experiments/public_linear_partner_control/msvalid/per_patient.csv)、[逐目标](experiments/public_linear_partner_control/msvalid/per_target.csv) SHA-256 依次为 `63c262cf9a02e4eb64ab9ded6f9b3be4d73806324e0d5cc0fc630eee16bf17b5`、`da2f85e1d26fdfc633992f216939694148165880095ace6bd53971c5ea756eaa`、`7c50260886e4564e9be2583985379692101e447ba03b8c964518bf8e12402d96`。ReMIND [汇总](experiments/public_linear_partner_control/remind/summary.json)、[逐患者](experiments/public_linear_partner_control/remind/per_patient.csv)、[逐目标](experiments/public_linear_partner_control/remind/per_target.csv) SHA-256 依次为 `e4f1dbc3b1443d683da0e90eaab8a48bb5dfa1d9c04350d8392e7a1bd21fea6e`、`18f9539419ca8adc5acb3b283eceda3722924562b4e73d27bed29267db794e45`、`368197fbd3a5a1dece41546cfed0bdea9c480c36ecb49d0acd1ef74b08af77b6`。方案 SHA-256 `3cb3af5bac317f31d17ddcd432aa1f507f21b41c8e1c4b01f4c218f00f1f73c4`；CPU 脚本 `f4703eed96825815e50172b38dfc266d6c5eee7dac3500084e563388c9f55fb1`；复核器 `6985beb0eedf667513a485a703ee3ee5b515b046231dd2feb04f2ebc94336d0f`。IXI HAT 权重哈希与主分析相同。

**对科学主张的影响：** 正向效应并非双学习模型或跨架构配对独有；原稿若暗示“只有深度网络因共享观测而一起犯错”应删除。线性伙伴与 SwinIR 的 `O` 有各自不同的 MSE 分母，且伙伴误差水平不同；两组 `Delta O` 的数值差不是可识别的网络特有贡献。此结果增加了对“固定参考下，发布层上下文复用能压低输出分歧”的一般性说明，同时使新意更依赖**定量审计合同、患者级透明报告与两个来源的限制**，而非模型机制。它仍不能证明原始采集层身份因果、消除完整邻层内容/几何共变、提供无需真值的病例分数或修复 ReMIND `MPR` 限制。线性对照是结果后设计，区间不等于另一次独立证实。
