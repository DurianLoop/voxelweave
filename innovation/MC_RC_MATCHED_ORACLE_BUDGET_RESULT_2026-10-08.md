# 匹配支持的两种费用流程与未执行重打包

[事前协议](MC_RC_MATCHED_ANCHOR_ORACLE_PROTOCOL_2026-10-08.md) 固定 m∈{1,2,5,10} 和两个不同真实流程的计费语义。这里的 N 是一次整系列固定窗口 forward 调用数，k 是该支持在原 batch2 布局中要重算的 batch 数；相同支持重复 m 次仅是计数场景，不外推连续编辑。

- A：cached 需要一次初始化，dense 候选无需额外 baseline；比较 N+m·k 与 m·N。
- B：两个实际流程确实都需要同一 baseline；比较 N+m·k 与 N+m·N。

B 的共同初始化计费此前已有说明，本轮新增的是当前 19 系列预测的匹配数字。必须按实际实现事先选定流程，不能选择更有利的分母。两边费用未包含定位、生成、探索、transfer、后处理，也未按不同形状/批次实测延迟；所有数值均是 forward 次数比，低于 1 仅表示此口径的条件空间。

[生产费用 JSON](experiments/mc_rc_matched_oracle_budget_scenarios_2026_10_08/attempt01.json) 真正退出 `106be7=0`。新增 [独立整数有理数核验 v2](experiments/mc_rc_matched_oracle_budget_scenarios_2026_10_08/independent_integer_rational_v2_attempt01.json) 真正退出 `c66c47=0`：从 geometry 元数据重建 batch 集合、核 76 个 series-support、608 个逐序列费用比、96 个汇总费用比、44 个患者工作量及成分汇总；不 import 生产代码、Fraction 或医学库，不读取新医学数组。

核验 v1 真实退出 `08b74d=1`，原冻结预测 schema 没有新 oracle 的 `repacking_execution_equivalence_verified` 字段，触发 KeyError。v1 源码和失败 JSON 保留；v2 仅兼容字段缺省，不更改数值、设置或输出资格，整体计数场景仍明确未执行重打包。缺省字段不构成等价证据。

主费用口径为**每患者全部 series 的 N/k 先相加，再计算费用比，最后患者等权**。原 patient/series 两层等权、全队列 pooled 全部保留，避免按有利口径选结果。

| 支持 | m=5，A，完整患者等权 | m=5，B，完整患者等权 | 全部 N/k | 假设重打包 k |
|---|---:|---:|---:|---:|
| 理想 observed anchor | 0.617952615 | 0.514960512 | 572/181 | 142 |
| empirical QDA | 0.577788186 | 0.481490155 | 572/175 | 144 |
| balanced QDA | 1.028456773 | 0.857047311 | 572/447 | 413 |
| balanced ExtraTrees | 1.019887691 | 0.849906409 | 572/417 | 404 |

empirical QDA 的低费用伴随前景覆盖仅 0.8820%，不属于有用修正证据。balanced QDA 的 A5 pooled 比为 0.981468531，患者等权却为 1.028456773；pooled 不能替换患者结果。B5 为 0.857047311，只支持该流程的条件计数空间，尚不能宣称实际加速或净任务收益。

附加重打包只用 affected tile 数 T 计算每 series `ceil(T/2)`，再求和；原窗口及 batch 合同未替换。balanced QDA 从 k447 到 413，对原 conditional calls 最多减少 7.6063%；ExtraTrees 417 到 404，最多 3.1175%。两者的支持广泛触及窗口，重打包不能解决主要定位成本。

没有执行重打包，没有检查输出、浮点差异、硬预测或 latency 等价，也没有改变原 cache 资格。若执行新布局，需要最终冻结模型上的整 FOV full/cached/重打包核验；小 ROI 和共享集合公式均不能代替这一资格。可验证的下一步见 [动作价值准备](MATCHED_ANCHOR_TO_ACTION_VALUE_PREPARATION_2026-10-08.md)。
