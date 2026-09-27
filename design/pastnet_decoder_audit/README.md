# 冻结control解码诊断

已完成train全量只读审计与smoke，未训练新候选。LACV E1增益+.014654 dB，未达+.10 dB，已按预登记停止。

本诊断结果：饱和位置仅承载1.45%平方误差，固定confidence幅度包络oracle MSE仅占当前MSE的.0965%，不支持通过放宽bounded residual继续full。低中频承载91.22%误差，但不是可预测信号或可实现收益的证明。

- [中文报告及下一假设边界](REPORT_ZH.md)
- [计算前协议](PROTOCOL_ZH.md)
- [全量结果](results/v1/summary.json)
- [smoke结果](results/smoke/summary.json)
- [LACV正式full复核](../pastnet_v2_crossview/results/crossview_full_review.md)

当前没有新full命令，旧源码与checkpoint保持不变。

后续[成熟latent分频读出对照](../pastnet_latent_readout/REPORT_ZH.md)也已完成：相对共享读出仅+.001613 dB，MAE不退guard失败，未进入validation/full。
