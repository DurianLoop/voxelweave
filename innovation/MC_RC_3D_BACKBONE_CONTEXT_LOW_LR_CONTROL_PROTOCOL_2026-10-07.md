# 相同初始checkpoint/流的低学习率骨干对照（训练前冻结）

当前1024更新接续诊断已结束并独立核验：native主head在全部16tile二值输出为空；前景概率最大1.07209e-7，三个head均无TP。固定pair4/5的native主headsoft-Dice encoder L2梯度从初始13.8400降至最终2.39979e-7；BCE梯度仍非零。最后64步含前景53batch平均loss1.010795，空GT11batch平均.010529。PCHIP相同流则full Dice=.973981，通过原gate，但原背景增强crop有278 FP。饱和/优化失败观察真实，不能据此断言学习率是唯一原因，也不能解释成SR收益。

下一新阶段进行**单一配置因素**对照：从与原lr=.001两臂完全相同的各自初始全tile head checkpoint重新开始，不从native崩塌后权重继续。唯一训练改动为AdamW恒定lr=.0001（原.001的十分之一）；weight_decay=.0001、全部参数、原三尺度BCE+Dice、无增强、同一seed20261007事前128轮完整16tile permutation/batch2流、含空tile、各1024更新、最后checkpoint、threshold=.5不变。两臂均执行、不只救native；不选择最佳checkpoint、不改gate、不修改旧结果。原LR.001已完成模型作为开发对照，不能因低LR成功而删掉它。

理由：初始head已在冻结骨干上优化，其较大权重及native初始soft-Dice骨干梯度提示接续优化可能敏感。低LR是标准优化对照，不是新方法；只有单一factor实际结果才能评价这个具体配置干预。每臂各自继承的模型此前已经使用不同图像训练，所以它仍不是MRI重建收益的科学比较。

执行前绑定原训练/独立核验/全16tile无更新诊断SHA，并确认全部实际exit0。当前19series CPU资格准备要求两臂原gate均通过，故**当前不能启动该资格**。低LR结果无论成功或失败都保留同一原门槛：foreground crop Dice≥.9、完整native-grid Dice≥.9、recall≥.9、absRVE≤.25、TP>0，所有full/anchors/missing/tail与两个原增强crop分母/空值保持。

资源：已实际观察原两臂2048更新/主评价3314.34秒；新阶段CPU4 intra-op/1 interop、自身below-normal，两臂总墙钟<=5400秒，新保存<=120MB、RAM/磁盘各留8GB。前32步仍按原真实时间投影guard，不依据loss停训/改预算。GPU原fresh free≥8,000,000,000bytes/4GB运行余量/2.5GB peak保持；本阶段没有CUDA初始化。

两臂最后checkpoint均冻结后才评分；再独立核全部1024行history、共享tile/GT流、权重SHA、module/functional三个head与生产/float64坐标，各原门槛和四域端点。浮点门槛3e-6/0二值差异保持，不通过仍保留。全部写入新low_lr目录，不能覆盖本次已冻结的lr=.001阶段。四验证/八确认仍关闭，发表claim0；此训练不属于正式11患者/19series充分适配。
