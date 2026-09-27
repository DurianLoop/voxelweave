# 13 模型 continuous-influence 大表

实际测试 8 个模型、16 个模型/队列；其中 14 个模型/队列通过数值稳定性，14 个同时满足稳定性与 beyond-count 区间为正。其余模型仍逐行保留。

本表使用新的每队列/每端点八模型同时置信区间。旧三模型点估计保持不变，原推断家族区间保存在 CSV 的 legacy 列及上一轮交付；两种区间不混称同一家族。

| 模型 | 队列 | 技术资格 | 稳定性 .005 / .02 / −.01 | 门槛 / 判定 | beyond count [同时95%CI] | fixed count [同时95%CI] | beyond-count 支持判定 |
|---|---|---|---|---|---|---|---|
| Linear | fastmri | ELIGIBLE | 0.981955 / 0.996626 / 0.999749 | 0.90 / PASS | 0.077 [0.061, 0.092] | 0.371 [0.067, 0.675] | SUPPORTED |
| Linear | ixi | ELIGIBLE | 0.991735 / 0.989113 / 0.998750 | 0.90 / PASS | 0.083 [0.077, 0.088] | -0.076 [-0.126, -0.026] | SUPPORTED |
| Cubic | fastmri | INELIGIBLE | NA / NA / NA | NA | NA | NA | INELIGIBLE |
| Cubic | ixi | INELIGIBLE | NA / NA / NA | NA | NA | NA | INELIGIBLE |
| ACVTT | fastmri | ELIGIBLE | 0.789229 / 0.958875 / 0.998067 | 0.90 / FAIL | 0.092 [0.078, 0.105] | 0.223 [-0.044, 0.491] | NUMERICAL FAIL |
| ACVTT | ixi | ELIGIBLE | 0.897623 / 0.968612 / 0.997814 | 0.90 / FAIL | 0.082 [0.071, 0.092] | 0.194 [0.129, 0.259] | NUMERICAL FAIL |
| Res-SRDiff | fastmri | INELIGIBLE | NA / NA / NA | NA | NA | NA | INELIGIBLE |
| Res-SRDiff | ixi | INELIGIBLE | NA / NA / NA | NA | NA | NA | INELIGIBLE |
| ArSSR | fastmri | ELIGIBLE | 0.994519 / 0.963778 / 0.999756 | 0.90 / PASS | 0.082 [0.069, 0.094] | 0.430 [0.237, 0.622] | SUPPORTED |
| ArSSR | ixi | ELIGIBLE | 0.999716 / 0.998991 / 0.999903 | 0.90 / PASS | 0.123 [0.118, 0.128] | 0.562 [0.508, 0.617] | SUPPORTED |
| CycleINR-style | fastmri | INELIGIBLE | NA / NA / NA | NA | NA | NA | INELIGIBLE |
| CycleINR-style | ixi | INELIGIBLE | NA / NA / NA | NA | NA | NA | INELIGIBLE |
| ResUNet | fastmri | ELIGIBLE | 0.989373 / 0.991655 / 0.994260 | 0.90 / PASS | 0.094 [0.078, 0.110] | -0.103 [-0.260, 0.054] | SUPPORTED |
| ResUNet | ixi | ELIGIBLE | 0.998505 / 0.997747 / 0.998715 | 0.90 / PASS | 0.127 [0.120, 0.134] | 0.400 [0.325, 0.475] | SUPPORTED |
| Pix2Pix-GAN | fastmri | INELIGIBLE | NA / NA / NA | NA | NA | NA | INELIGIBLE |
| Pix2Pix-GAN | ixi | INELIGIBLE | NA / NA / NA | NA | NA | NA | INELIGIBLE |
| SwinIR | fastmri | ELIGIBLE | 0.978903 / 0.942054 / 0.977629 | 0.85 / PASS | 0.093 [0.078, 0.109] | 0.365 [0.181, 0.549] | SUPPORTED |
| SwinIR | ixi | ELIGIBLE | 0.880314 / 0.950539 / 0.911329 | 0.85 / PASS | 0.093 [0.081, 0.105] | 0.265 [0.180, 0.350] | SUPPORTED |
| SAINT-style | fastmri | ELIGIBLE | 0.950686 / 0.983707 / 0.996964 | 0.90 / PASS | 0.033 [0.012, 0.054] | 0.380 [0.226, 0.534] | SUPPORTED |
| SAINT-style | ixi | ELIGIBLE | 0.996704 / 0.996341 / 0.997466 | 0.90 / PASS | 0.133 [0.124, 0.141] | 0.417 [0.372, 0.463] | SUPPORTED |
| I3Net | fastmri | INELIGIBLE | NA / NA / NA | NA | NA | NA | INELIGIBLE |
| I3Net | ixi | INELIGIBLE | NA / NA / NA | NA | NA | NA | INELIGIBLE |
| HAT | fastmri | ELIGIBLE | 0.985533 / 0.964290 / 0.972553 | 0.85 / PASS | 0.103 [0.085, 0.121] | 0.474 [0.285, 0.663] | SUPPORTED |
| HAT | ixi | ELIGIBLE | 0.929824 / 0.957558 / 0.934796 | 0.85 / PASS | 0.098 [0.088, 0.108] | 0.270 [0.177, 0.362] | SUPPORTED |
| SMamba-UNet | fastmri | ELIGIBLE | 0.926954 / 0.917539 / 0.993569 | 0.90 / PASS | 0.078 [0.060, 0.097] | 0.202 [-0.011, 0.415] | SUPPORTED |
| SMamba-UNet | ixi | ELIGIBLE | 0.992994 / 0.968170 / 0.993162 | 0.90 / PASS | 0.096 [0.083, 0.109] | 0.304 [0.215, 0.393] | SUPPORTED |

Linear 是物理双锚插值控制，不是新增神经架构。ArSSR 的线性稠密初始化只作为内部特征，不计作额外采集锚。结构兼容、稳定性和 beyond-count 支持是不同结论。

## 接口不合格原因
- Cubic：Native two-anchor fallback becomes linear。
- CycleINR-style：Frozen four-anchor x4 context contract。
- Pix2Pix-GAN：Fixed x4 channels cannot express every target fraction。
- I3Net：Frozen four-slice stride4 input window。
- Res-SRDiff：Additional stochastic sampler noise outside frozen response contract。

旧 SAINT 的目标知情空结果、I3Net/CycleINR 历史稳定性失败和所有旧负结果保留。本轮没有新增协方差验证，Claim D 仍仅覆盖 HAT/SwinIR/SAINT 的原 IXI 试验。
