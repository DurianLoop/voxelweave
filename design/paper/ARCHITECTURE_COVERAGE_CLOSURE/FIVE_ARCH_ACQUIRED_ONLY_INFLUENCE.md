# 五核心架构 acquired-only 影响复核

同一 acquired-only 信息合同下，实际可运行 HAT、SwinIR、SAINT；I3Net/CycleINR 保留接口不合格 NA。技术适用性、数值稳定性和 beyond-count 支持是三个不同判断。

| 队列 | 模型 | 最低稳定性 / 门槛 | beyond count [同时95%CI] | 固定count [同时95%CI] | 判定 |
|---|---|---|---|---|---|
| fastmri | hat | 0.964290 / 0.85 | 0.103320 [0.088609,0.118030] | 0.474106 [0.320855,0.627356] | SUPPORTED |
| fastmri | swinir | 0.942054 / 0.85 | 0.093322 [0.080496,0.106149] | 0.365012 [0.215608,0.514415] | SUPPORTED |
| fastmri | saint | 0.950686 / 0.90 | 0.032751 [0.015435,0.050067] | 0.379778 [0.253344,0.506212] | SUPPORTED |
| fastmri | i3net | NA / .90 | NA | NA | INELIGIBLE |
| fastmri | cycleinr | NA / .90 | NA | NA | INELIGIBLE |
| ixi | hat | 0.929824 / 0.85 | 0.097822 [0.089505,0.106138] | 0.269526 [0.193923,0.345128] | SUPPORTED |
| ixi | swinir | 0.880314 / 0.85 | 0.093251 [0.083625,0.102876] | 0.264861 [0.195426,0.334297] | SUPPORTED |
| ixi | saint | 0.996341 / 0.90 | 0.132790 [0.125627,0.139953] | 0.417380 [0.379176,0.455584] | SUPPORTED |
| ixi | i3net | NA / .90 | NA | NA | INELIGIBLE |
| ixi | cycleinr | NA / .90 | NA | NA | INELIGIBLE |

HAT/SwinIR 原每队列两模型同时家族原样保留。新增 SAINT 复制检验按每端点覆盖两个队列，仍使用原5000检查bootstrap及18003/18004种子；不是把它加入原家族，也不声称五模型全局同时覆盖。该扩展家族在新数值计算前写入 PROTOCOL.md。
SAINT 每个队列的 .005/.02/−.01 三次排名稳定性均须≥.90；HAT/SwinIR 的 .85 门槛不变。三者均数值 PASS 且对应 beyond-count 同时区间为正。原六-stratum 总体门槛仍为NA，未补造 acquired-only NingXia。
历史 SAINT beyond-count .014 [−.002,.029] 和 fixed-count .063 [−.021,.149] 仍是有效负/不确定结果。其全检查强度范围、目标掩膜和混合精度合同不同，不能与新 acquired-only 数值互填，也不能解释为旧空结果被证伪。
历史 I3Net (.859,.737,.939) 和 CycleINR (.779,.857,.876) 的 .90 门槛失败照常保留。这些数字属于历史 IXI 四锚实验，不是 fastMRI/IXI 本轮双锚 acquired-only 稳定性。
全部48个次要端点×幅度/队列组合保存在 outputs/saint_secondary_signs.csv，并在补充材料列全。较弱的直接disagreement优势（fastMRI primary .002943）不替换更有利alignment主端点；paired/reference error 关联较弱，不能泛化成可靠误差预测器。
所有417目标的原始响应数组和13344上下文/幅度观察保留；响应写盘并绑定哈希后才读取独立目标。输入掩膜、Q1偏移、Q99-Q1范围、物理锚点、四个Rademacher种子与九上下文记录均已核验。