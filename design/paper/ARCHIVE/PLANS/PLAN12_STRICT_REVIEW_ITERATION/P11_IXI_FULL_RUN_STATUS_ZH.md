# P11 IXI 五架构正式实验最终状态

启动：2026-09-06 08:27（Asia/Shanghai）  
完成：2026-09-06 10:38  
状态：**正式队列与 identity-swap 均完成**  
冻结后缀：`full`  
病例数：115；每病例目标平面数：5；Bootstrap：5,000

## 1. Clean shared/disjoint 正式结果

| 模型 | 病例 | Wrapper max-abs | Observable gain 中位数 [95% CI] | Ranking Δρ [95% CI] | 病例正方向 |
|---|---:|---:|---:|---:|---:|
| HAT | 115 | 0 | 0.2903 [0.2862, 0.2963] | 0.0305 [0.0157, 0.0531] | 115/115 |
| SwinIR | 115 | 0 | 0.3021 [0.2946, 0.3069] | 0.0355 [0.0192, 0.0592] | 115/115 |
| I3Net | 115 | 0 | 0.2520 [0.2442, 0.2602] | 0.0254 [0.0085, 0.0528] | 115/115 |
| SAINT-style | 115 | 0 | 0.2981 [0.2917, 0.3048] | 0.0316 [0.0167, 0.0551] | 115/115 |
| CycleINR-style | 115 | 0 | 0.2961 [0.2915, 0.3004] | 0.1345 [0.0577, 0.2576] | 115/115 |

五模型等权 family observable gain 为 0.2856；leave-one-family-out 范围为 0.2814--0.2968。CycleINR 是仓库中的 internal CycleINR-style/implicit-coordinate checkpoint 与 wrapper，不是官方权重的精确复现。

## 2. Matched-geometry identity-swap

identity-swap 固定最近锚点距离多重集 `{1,3}`，分别汇总 residue 1/3 后等权，以检测左右反射方向是否改变结论。

| 模型 | Reflection-balanced gain [95% CI] | Mirror difference [95% CI] | Orientation warning |
|---|---:|---:|---:|
| HAT | 0.2920 [0.2856, 0.2973] | 0.0000 [-0.0052, 0.0068] | 否 |
| SwinIR | 0.3004 [0.2950, 0.3082] | 0.0007 [-0.0030, 0.0064] | 否 |
| I3Net | 0.2509 [0.2442, 0.2573] | 0.0025 [-0.0044, 0.0125] | 否 |
| SAINT-style | 0.2972 [0.2884, 0.3019] | -0.0003 [-0.0057, 0.0058] | 否 |
| CycleINR-style | 0.2947 [0.2904, 0.2994] | 0.0014 [-0.0004, 0.0040] | 否 |

结论边界：结果排除了可检测的 residue 左右方向差异，但只实现“反射等价”的几何匹配，不是 signed geometry 完全相同。

## 3. 完整性检查

- clean per-plane：5,750 行 = 5 模型 × 115 病例 × 5 目标 × 2 条件；
- identity-swap per-plane：2,875 行 = 5 × 115 × 5；
- identity-swap balanced：575 行 = 5 × 115；
- duplicate key：0；非有限值：0；
- shared/disjoint 各 2,875 行，每例每条件均为 5 个目标；
- 五个 phase-0 wrapper 的 MAE 和 max-abs reproduction error 均为 0；
- stderr 日志为空，stdout 末尾存在 `QUEUE_DONE`。

## 4. 产物与复现

- 队列脚本：`scripts/run_p11_ixi_full_queue.ps1`
- stdout：`runtime/p11_ixi_full_queue_20260906_082711.out.log`
- stderr：`runtime/p11_ixi_full_queue_20260906_082711.err.log`
- 正式结果：`../PLAN11_CLAIM_STRENGTHENING/outputs/p11_ixi_clean_*_full.*`
- identity-swap：`../PLAN11_CLAIM_STRENGTHENING/outputs/p11_identity_swap_*_full.*`

论文使用规则：完整五模型结果全部保留。clean、reflection-balanced 与 ranking 是不同估计量；fastMRI 使用均值、IXI 使用中位数，数值不得直接跨队列合并。
