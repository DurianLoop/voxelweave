# 只改anchors时的全volume归一化：三个固定已见患者技术预检

固定原名单最前3人：VS-SEG-202、203、204；不使用运行中post任务的Dice决定名单。只构造已认证raw/post解析输入及anchors roundtrip对照，0神经前向、0GPU。CPU自身低优先级与既有15GB/8GB门槛。科学独立确认0。

原运行时对RAS contiguous数组执行MONAI 0.4 NormalizeIntensity()，默认整volume/nonzero=False，均值和std从全部像素计算。四种解析控制改变anchors但原缺层数组不变，不能直接称任务网络缺层输入不变。

预检分别对raw及mixed_post两个基线：

1. 基线按其own全volume均值/std归一化。
2. anchors roundtrip的新输入按其own均值/std归一化。
3. 相同新输入，使用对应基线的均值/std归一化。

从已认证MONAI wheel验证vendor文件逐字节一致，隔离执行文件中的NormalizeIntensity类源码（仅Transform基类替换为object，不导入MONAI/torch/模型，不改环境）。记录这一限制；这不是完整MONAI运行栈复现。使用与既有runtime相同RAS orientation、float32、复制和通道维度；固定stats用原np.float32 scalar，不改精度。

先重放旧raw/post全体积SHA；另证明干预只改变anchors、missing/tail数组相同。测missing/tail在own与固定stats下的逐位变化像素数、最大绝对差及RMS，保存两baseline×三人全部结果，不挑患者或改阈值。固定stats应使missing/tail逐位等于baseline；若失败保留失败并先处理实际兼容问题。ownstats不变也如实保留，不预设必定非零。

此预检只能确认送入网络前的控制是否成立，不能得到Dice、神经激活或因果任务结论；不把三个已见患者当新方法确认。
