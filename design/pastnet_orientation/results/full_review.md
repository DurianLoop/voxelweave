# 方向增强 full 复核：停止，2026-09-22

32轮按原规则早停，best为第17轮。PSNR **25.656399 dB**，相对control +0.094388 dB，95%CI [0.043520,0.149981]，17/23患者改善。原+0.10dB门槛未达到。

质量守卫同样失败：SSIM均值-0.000411807（CI跨零），Dice intensity-proxy均值-0.000000304（CI跨零），HD95 intensity-proxy **+0.158420**，95%CI **[0.061572,0.264209]**，19/23患者没有改善。最后一项是有配对证据的退化，不能以PSNR接近门槛忽略它。代理指标不是解剖分割结论。

MAE -0.000022213、MSE -0.000074161、NCC +0.001286、tail10 MSE -0.000814304；control困难四分位PSNR +0.152472 dB。这些正证据保留，但候选仍不晋级。

耗时 5.232 h；峰值 19.654/20.322 GiB allocated/reserved。forward47.623ms/缺失层，参数992179，推理显存0.858745GiB，与control基本相同。

已重算配对报告并与原报告一致；最佳权重独立全validation重算记录见 `full_reverification_20260922.json`。旧代码、协议、checkpoint、test表保留。

停止该增强分支：不继续训练、不调整动作集合或概率、不补三seeds。不把0.094四舍五入为达到0.10。下一项是独立的frame-context结构：原方向样本、原G086初始化，主干保留解剖坐标先验，新局部分支共享D4方向；若先通过full筛选，必须再做同参数plain分支消融，方可归因方向共享。

完整配对统计：[gate_orientation_seed3407.json](gate_orientation_seed3407.json)。best SHA：`37aba16ede23cd923b73afdfd90a073a9830ce48dfd5d5488305e6f8f07fdf8c`。
