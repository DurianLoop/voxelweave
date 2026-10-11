# anchors/缺层相位梯度能量：45人解析结果

固定45已见CISS，855完整四层间隔、2,565缺层。producer session44318与verifier15909均实际exit0；90旧raw/post体积逐位SHA重放、四条件体积身份和全部梯度dot-product/四汇总复核errors=[]。GPU未用，0新神经前向，新科学确认患者0。

预写指标L=log(Eanchor/mean(Einserted))，E是在同一个observed-only ROI内的面内梯度能量，每患者先对间隔等权平均。它是所测纹理统计，不是解剖保真、病灶保真或任务Dice。

| 条件 | E0 | E1 | E2 | E3 | 患者平均L | exp(平均L) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| raw | 0.000594172892 | 0.000464111221 | 0.000354174292 | 0.000469733762 | +0.32422887 | 1.382964 |
| raw_anchor_roundtrip | 0.000226842287 | 0.000464111221 | 0.000354174292 | 0.000469733762 | -0.64241590 | 0.526020 |
| mixed_post | 0.000594172892 | 0.000180352655 | 0.000141652653 | 0.000183324137 | +1.26286697 | 3.535543 |
| slab_roundtrip | 0.000226842287 | 0.000180352655 | 0.000141652653 | 0.000183324137 | +0.29622220 | 1.344769 |

exp(平均L)是患者能量比的几何平均，不是上表患者平均能量的比，也不是个体增长百分比的算术平均。

| 预定配对差 | n | 平均ΔL | min | max | 正/负/零人数 |
| --- | ---: | ---: | ---: | ---: | --- |
| mixed_post-raw | 45 | +0.93863810 | +0.82815245 | +1.11144843 | 45/0/0 |
| slab_roundtrip-mixed_post | 45 | -0.96664477 | -1.16021788 | -0.84741017 | 0/45/0 |
| raw_anchor_roundtrip-raw | 45 | -0.96664477 | -1.16021788 | -0.84741017 | 0/45/0 |
| slab_roundtrip-raw_anchor_roundtrip | 45 | +0.93863810 | +0.82815245 | +1.11144843 | 45/0/0 |

mixed_post−raw的L全45升高，平均+.93863810；同时处理anchors后，slab_roundtrip−mixed_post全45降低，平均−.96664477，平均L从1.26286697回到.29622220（raw为.32422887）。这支持本合同中面内处理扩大了观测相位与插入相位的梯度能量差。

两个改变anchors的条件仅是解释性干预，不满足原observed-preserving SR合同。slab_roundtrip的缺层与mixed_post逐位相同；raw_anchor_roundtrip的缺层与raw逐位相同；四条件tail相同。把这些控制当SR性能改进会违反原任务定义。

该log ratio可分为log(Eanchor)−log(Einserted)，所以本2×2的两组配对差按构造相同到浮点容差。这是指标可分离性，不能把四行当四个独立机制发现或任务无交互证据。原raw已有PCHIP带来的phase差，真实解剖也随z变化，common ROI不是组织跟踪mask；本结果不证明所有周期纹理为伪影。

没有网络前向就没有本干预的Dice或activation结论。将来只改anchors的任务对照还需固定paired baseline的全volume归一化，见[三个患者预检](ANCHOR_NORMALIZATION_CONTROL_CPU_RESULT_2026-10-03.md)。共享decoder/resize/NumPy，独立复算不是新科学队列。

数据：[45人CSV](experiments/anchor_bandwidth_diagnostic_cpu/all45_phase_energies.csv)、[预写方案](ANCHOR_BANDWIDTH_DIAGNOSTIC_CPU_PLAN_2026-10-03.md)、[独立复核](experiments/anchor_bandwidth_diagnostic_cpu/independent_gradient_and_identities.json)。
