# S-CVaR full 复核：停止

2026-09-17，seed 3407，64 轮早停；best epoch 49。仅 clean validation 23 患者，未使用 test。

- PSNR 25.564924 dB，对照 25.562011 dB；配对增益 **+0.002913 dB**，95% CI [0.001949, 0.003706]，22/23 患者为正。
- 预设门槛 +0.10 dB 未达到；MAE 平均增加 0.000001134，Dice intensity-proxy 平均减少 0.000000130，质量方向 guard 也未通过。这两个变化的 CI 均跨零，不能称为显著退化。
- SSIM +0.00005703；tail10 MSE -0.00002545；困难四分位 PSNR +0.003698 dB。
- 耗时 10.609 h；峰值 19.631 GiB allocated / 20.322 GiB reserved；forward 47.797 ms/缺失层，992,179 参数。
- 结论：停止；不补 seeds，不调 tau，不继续训练挽救门槛。局部梯度稳定性没有转化成足够大的泛化收益。

当前下一步为独立官方 I3Net 同输入、同 validation 指标参照，以确定可信的差距。它从随机初始化开始，和继承 G086 的 control 不构成同初始化/累计预算架构消融。不得把本结果写入旧 test 主表或据此声称 SOTA。

完整配对统计见 [gate](gate_soft_tail_seed3407.json)；权重 SHA：`71a94df466ce1b758fef6c0db6f1f866ad910556ea286554d15c927ae96da912`。原代码、协议、full.ps1 和权重保留。
