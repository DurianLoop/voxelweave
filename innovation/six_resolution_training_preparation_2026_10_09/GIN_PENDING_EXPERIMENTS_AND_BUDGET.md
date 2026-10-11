# 尚未运行的强对照与研究尝试

当前能确认的是算子准备、24组独立NumPy合成公式检查，以及当前Torch的KL梯度语义；未完成医学GIN训练、完整3D IPA场、GIN的19series优化器/显存资格或严格LOPO。原分辨率增强228更新资格不能改称GIN资格。

| 待尝试项 | 冻定设计 | 开始前还需要什么 |
|---|---|---|
| basic 与 GIN-only | 两种原输入分别比较；同母GT、患者/series/schedule/patch、基本增强、原binary segmentation loss，四层随机卷积+Frobenius scaling | 所有19series的实际batch前向/反向/两步AdamW、GT不变、GPU/CPU重放、成本与完整储存预算 |
| GIN+IPA | 两视图互补混合、不用GT生成mask；第三视图GIN | 完整3D低频权重场的具体物理尺度/边界/归一化及独立资格，不能把测试linear场当完成 |
| GIN+IPA+consistency | 对三视图最终head构造softmax([0,z])；KL(mean||each)、attached target、element mean | lambda先冻结；深监督保留原loss，当前环境实际梯度/内存检查，禁止静默detach或替换forward JS |
| 预算公平比较 | 同曝光和同完整计算预算各给一组；计全部augmentation/3视图forward/backward/checkpoint recomputation/保存/evaluation/selection费用 | 各臂实测完整19series成本；同预算普通臂允许更多有效训练或强普通增强，不浪费费用凑数 |
| 患者级动作选择 | 强task后，对真实SR/TTA/联合动作完整FOV比较净收益；同信息action-risk差/QC/defer/metadata/static/random | 实际动作余量、训练外患者交叉拟合、全费用；共同信息不删除，负收益和defer保留 |
| 独立确认 | 先冻结患者聚合端点、模型/动作集合/预算、阈值及统计检验，再一次开启未见确认 | 开发内通过原六医学gate；严格LOPO全部cold-init；4已见验证不当新确认 |

三视图不能无检查直接将GPU batch从2扩大到6。可先准备顺序视图forward与checkpoint保留图，在保持attached均值梯度的前提下测量真实峰值；若内存不够，另冻数学等价方案并核对全梯度，不按显存压力擅自detach或改变loss。本轮没有执行这个训练实现。

沿用CPU1/interop1/below-normal、RAM/disk各8GB、GPU启动free8192MiB/allocator10%/peak2.5GB/runtimefree4GB；FP32/TF32off/deterministic，强度/概率3e-6、坐标3e-12、二值零差。GIN的synthetic oracle max2.5630e-6不能证明医学大patch/全部schedule误差；后者要独立测量。完整3D IPA原理可以尝试，但方法若成功属于强对照实现，不因空间维数改变宣称首次。

本轮fresh v3只读预检 actual55714f：ready=false，完整family仍104156359bytes高于8GB保留量，当时还缺51444935bytes；同时缺35904实际终态/独立audit、完整38FOV/atomic/费用资格。GPU准入通过不能替代这些门槛。没删历史、没扩大压缩、没缩小患者/分支/FOV范围，没正式训练。磁盘状态会变化，未来开始前必须fresh重新检查。

医学六gate继续是患者先均值fullDice≥.70/missingDice≥.65/recall≥.70/absRVE≤.50，各患者full/missingDice正，无series零TP。八未见确认12series与lockedIXI保持关闭。当前创新仅是待证伪的研究假设，不能以准备成功或技术资格通过替代临床收益/新颖性/独立确认。
