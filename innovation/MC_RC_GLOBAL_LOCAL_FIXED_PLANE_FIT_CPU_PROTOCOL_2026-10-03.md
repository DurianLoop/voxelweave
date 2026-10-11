# 单012固定切面、全视野tile覆盖最小拟合诊断

两臂各4000步已结束并独立核4000draw/6plane：BCE+Dice full .865312、Unified配方 .823786，均未过原fit gate。后者recall .917088→.955726，但FP39186→70526、absRVE .119669→.320328，不能只以召回增大判成功。本轮另作最小优化链条检查，不修改这两臂或20k结果。

固定唯一开发患者012/原唯一系列，仅根据开发GT有前景的原生z唯一集合取排序后的中位元素（len//2），在训练前输出z/label SHA。GT用于确定训练例/监督，不提供部署定位；无验证/确认/隐藏MR。输入仍已核observed-only PCHIP/shared与原physical上下文，随机初981,602参数GlobalLocalUNet/seed20261004，不读已有权重。

固定该完整plane，不作augmentation；生成与全FOV推断相同的全部128tile/stride96位置，将列表按row-major排列，每update循环连续两个位置。1000updates保证完整tile列表被反复覆盖；不是仅取GT附近训练patch。该细化取代下一准备中“两固定patch位置”的概括，避免未监督远处干扰最小拟合检查。改变采样/曝光/augmentation是整体诊断，不能把与旧分数之差归于一个因子。

每update同BCE+跨两patch前景Dice+.5global辅助，AdamW wd=.0001，cosine .001→.0001（分母999），无早停/阈值或checkpoint选择。前10真实updates平均耗时≤2秒才继续，仅资源守卫；不依效果调整1000步。每100步记曲线，非有限梯度停止保留。

只保存最后checkpoint，然后按原infer_native仅重放该完整原生plane、同probability回原生/.5。拟合gate：2D native plane Dice≥.95、recall≥.95、绝对相对面积误差≤.05。面积误差采用counts相同分子/分母的ratio，明确不是完整3D体积。独立label轴、plane bincount及另套完整plane重放通过才能解释。单已见切面成功不叫完整患者/缺层/泛化能力，不作重建评价器。

不并行第二重训练；CPU单线程、自身below-normal，磁盘≥15GB/内存≥8GB，新增<50MB/exist_ok=False。GPU/用户训练/locked IXI test不操作，科学确认0，goal active。原来8确认人仍关闭。
