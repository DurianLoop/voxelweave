# 接续native二值空预测的无更新诊断（执行前固定）

两组最后模型已冻结、主训练和独立核验实际exit0。native full/crop Dice均0；PCHIP full Dice=.973981并过原gate，但原背景增强crop有278 FP。核验两个生产坐标及独立float64坐标均通过原严格门槛。不能将此差异解释为重建收益或SR损害。

只读单开发001同一series，对两臂各自**初始全tile head checkpoint与最后骨干checkpoint**作无更新诊断；不读取中途/最佳模型、不保存新权重。固定全部16tile、batch2、原tile顺序、包含空tile。所有3个deep-supervision head逐tile测对应分辨率GT、二值contingency table、BCE/soft Dice项、正负GT上的logit/probability均值/范围。重叠tile统计分母是tile voxel instances，不能当唯一完整体积指标。原最后主head full-FOV端点保持。

从完整1024行history按batch是否含FG分别报告first32/last64的loss分布；不把空batch低loss混成能力成功。固定tile对4/5（此前线程资格的相同pair），分别反向BCE与soft Dice部分，量主head/encoder/decoder的梯度范数；每次重新zero_grad，不optimizer.step。保留初始与最后两模型，不据最有利head选科学端点。诊断可以揭示当前饱和/优化现象，不能仅凭梯度或logits归因某个唯一机制。

CPU4 intra-op/1 interop、自身below-normal、float32、无CUDA；墙钟<=300秒、新输出<5MB、RAM/磁盘各留8GB；四验证和八确认不打开；正式训练更新0。完成后才另立已知优化配置或从共同初始化训练的下一对照协议；原失败不回写。
