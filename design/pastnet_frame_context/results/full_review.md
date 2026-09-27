# frame-context full 复核：停止，2026-09-23

63轮早停，best第48轮。PSNR25.562437 dB，对原control仅 **+0.000426 dB**，95%CI **[-0.000113,0.000982]**；14/23患者改善。未达到+0.10，CI下界未大于0，困难四分位-0.000075dB，三个守卫失败。其余质量与效率守卫通过，但不能据此晋级。

推理50.195ms/缺失层，延迟比1.05245，参数1,006,163；训练耗时11.418h，峰值19.787/20.502GiB allocated/reserved。

结论：按预登记停止，不运行plain full，不补seeds，不改变共享分支宽度或系数。非零分支的等变性成立、可学习性检查通过，没有转化为足够的validation收益。原有模型与checkpoint保留。

下一轮先修复已确认的训练监督错误：病例113452254821_ax_t2的32层来自两个不同UID的16层序列，旧转换按同名标签合并、按InstanceNumber交错排列，造成错误phase和跨采集输入/target。`design/pastnet_series_integrity`保留原数据，仅生成独立修复版本；不是新架构，也不把数据修复收益归于frame-context。

完整配对：[gate_shared_seed3407.json](gate_shared_seed3407.json)；独立全validation复算：[full_reverification.json](full_reverification.json)。不修改旧test表或论文结论。
