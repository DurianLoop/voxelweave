# 温度校准与FOV融合顺序：执行前合成检查

不读MRI、不用神经网络、不训练、无GPU。固定两个重叠tile对同一voxel的binary logits为(2,-10)，归一化blend weights=(.6,.4)，T=(.5,1,2,4)。先sigmoid再blend是当前FOV生产执行器的数学顺序；仅使用合成一个voxel，非完整FOV复现。

对比A：tile logits分别除正T，sigmoid后blend；B：原T1融合概率先转logit，再除正T，sigmoid；C：logits先按权重blend再除T/sigmoid。核A的每tile.5预测不变，但T1/T2融合预测改变；B对所有T保持原融合.5预测；C是另一推理定义，不混成原生产路径。

NumPyfloat64与独立Decimal80位exp/log解释器逐数核atol1e-12，所有binary threshold逐位一致。阈值固定.5，保存原全部数值，不只保存改变项；使用稳定sigmoid，无拟合T、无MRI校准证据。耗时<=60秒，single-thread/below-normal，8GB磁盘/RAM余量，保存<=1MB。科学解释仅限校准施加位置必须冻结，不能把Guo单预测argmax不变结论无条件搬到当前融合流程。

