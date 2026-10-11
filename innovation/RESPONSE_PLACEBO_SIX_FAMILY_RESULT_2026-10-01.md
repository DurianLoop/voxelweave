# 六个 HAT/SwinIR 锚点响应错配对照的同时区间

按[已写方案](RESPONSE_PLACEBO_SIX_FAMILY_PLAN_2026-10-01.md)，同队列 HAT、SwinIR 与 HAT→SwinIR 三个对照按相同检查对象索引联合重抽，fastMRI/IXI 各自独立重抽；2,000 次、六项最大绝对标准化偏差的 95% 分位数为 `2.6226`。输入仅为已经核过原始 NPZ/目标哈希的逐上下文 CSV，[完整 bootstrap 与汇总](experiments/response_placebo_six_family/summary.json)保留输入、方案和脚本哈希。此 family 是**看过单项结果后定义**，不能控制此前全部研究选择。

| 队列 | 配置 | 正确配对偏相关减两错配均值 | 六项同时 95% 区间 |
|---|---|---:|---:|
| fastMRI | HAT | +0.1846 | `[+0.0488,+0.3203]` |
| fastMRI | SwinIR | +0.2340 | `[+0.0391,+0.4289]` |
| fastMRI | HAT→SwinIR | +0.2124 | `[+0.0009,+0.4238]` |
| IXI | HAT | +0.3036 | `[+0.2256,+0.3815]` |
| IXI | SwinIR | +0.2842 | `[+0.2064,+0.3619]` |
| IXI | HAT→SwinIR | +0.1139 | `[+0.0403,+0.1875]` |

这组六个结果在本次**同时**敏感性下仍同向，但 fastMRI 跨架构下界几乎贴零，说明该层最脆弱。SAINT 的[两种错配拆解](SAINT_EXACT_CONTEXT_AUDIT_2026-09-30.md)有明确非优势/跨零，**不属于这组六项，也不能被六项结论背书**。本结果不改变 MSValid 的外部连续影响严格基线负结果、历史选择偏差、真实物理采集未随机化与部署 guard 失败。
