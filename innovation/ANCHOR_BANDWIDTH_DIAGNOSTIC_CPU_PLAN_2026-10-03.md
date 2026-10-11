# 观测锚点与缺层的面内带宽差：仅解析CPU诊断

写于post任务全45尚未完成时。此实验不读动态post Dice，不做新的神经前向，固定原45已见CISS；科学独立确认0。CPU单线程、只降低自身优先级、磁盘15GB/可用内存8GB门槛。GPU/用户训练/locked IXI test/根环境不操作。

新问题：在缺层down/up而anchors保留的混合体积中，沿z的面内梯度能量是否出现更大的观测相位/插入相位差。只用observed anchors构造；共享decoder会载入已见原网格MR/标签，但特征及干预不使用隐藏层或标签。

固定四个条件，形成2×2解析对照：

| 条件 | 缺层 | anchors | tail |
| --- | --- | --- | --- |
| raw | 原raw PCHIP | 原观测 | 原raw尾部约定 |
| raw_anchor_roundtrip | 与raw逐位相同 | observed-only归一化、256 down/up | 与raw逐位相同 |
| mixed_post | 原post_resize_pchip | 原观测 | 与raw逐位相同 |
| slab_roundtrip | 与mixed_post逐位相同 | 与raw_anchor_roundtrip逐位相同 | 与raw逐位相同 |

后两种改变anchors的条件仅为解释性干预，**不满足observed-preserving SR合同，不是可部署的新SR方法**。tail不纳入相位指标。

每个完整4层间隔，以左右观测anchor支持域并集固定共同ROI（绝对信号>各anchor最大绝对信号1%，既有阈值），所有四相位用同一ROI。面内相邻两个像素都在ROI才计梯度边。归一化梯度能量为dx/dy平方和除以边数再除以observed span平方；不使用病灶真值。每患者先对每相位所有间隔等权平均E0,E1,E2,E3，固定指标L=log(E0/mean(E1,E2,E3))；若能量非正保留undefined，不填零。L衡量相位间相对面内梯度能量，不能单独解释为解剖信息或临床质量。

报告四条件各相位能量与L，四个固定配对差：mixed_post−raw、slab_roundtrip−mixed_post、raw_anchor_roundtrip−raw、slab_roundtrip−raw_anchor_roundtrip。全45均值/中位数/min/max/正负人数仅描述，不做显著性成功门槛、不挑患者或调整参数。共同ROI并非跟随解剖的精确mask，不同phase本来具有真实解剖变化；raw相同患者对照用于区别额外处理效应，不能消除所有混杂。

复核需完整45旧raw/post数组SHA重放，逐位证明干预只改变anchors、缺层/tail保持；另一gradient表达（差分dot-product）重算每间隔/相位能量及全部患者标量与汇总。共享解码器/resize为限制，数值复核不是科学独立确认。

本解析结果只能支持或反驳所测相位能量解释。任务影响仍需post全45完整结果，随后另冻结只改anchors的CPU任务合同与2×2条件对照，保持输入归一化机制明示；全volume NormalizeIntensity也可能改变缺层送入网络的值，不能把raw数组不变等同于网络激活不变。没有任务前向即不写Dice结论。
