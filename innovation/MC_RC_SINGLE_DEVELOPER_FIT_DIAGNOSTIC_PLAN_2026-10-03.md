# 单开发系列可拟合性诊断（新训练前登记）

先前10患者/18系列、122,609参数、4000步固定pilot未通过；012训练内full Dice .010724，013留人全漏检。独立计数、物理cKDTree surface和12个完整plane重放均通过；012冻结模型在50个前景训练patch的micro Dice也只有.030755，说明失败不只是全FOV推断覆盖。不能据此判断是哪一容量、曝光或优化因素造成。

新增受限诊断：**同一architecture和4000步、同一optimizer/loss/augmentation/seed/patch采样，仅从随机初始化在012的唯一系列上训练，再全FOV评012。** 目的为检查该实现能否拟合一个已知监督case；这是训练内可拟合性，不能作为泛化、任务适应效果、新方法或未见确认。013及4验证/8确认患者都不读取。此前坏模型结果不覆盖。

使用已核observed-only raw PCHIP/observed_shared、同五层通道、96patch和stride64全FOV推断。每batch两个前景中心/两个随机全FOV，最终固定.5阈值，无ROI后处理；预算4000updates，cosine .001→.0001、AdamW wd=.0001、BCE+Dice。无早停、无阈值/checkpoint挑选，不因loss曲线增加预算。一次固定训练，保存完整合同、初/终weights SHA、每100步loss及最后checkpoint/预测。CPU单线程below-normal，磁盘15GB/内存8GB底线，GPU lazy_init禁止。

诊断通过定义：012原生full Dice≥.90、supported missing≥.90、full recall≥.90且绝对相对体积误差≤.10；全覆盖/来源/有限值/独立预测计数和至少3个完整plane直接前向重放通过。通过只说明训练内能够拟合，不把阈值提升称临床能力；若失败则此配置仍无可拟合性证据。独立核验使用另一种surface算法/计数实现，直接重放仍引用同模型architecture，不称完全独立实现。

无论结果如何，后续整体训练必须使用开发/验证能力门槛和预写同预算矩阵；不能把012的训练内结果与013或最终确认合并当患者泛化证据。单患者全FOV可拟合而多患者失败只提示进一步查跨患者异质性/优化预算/上下文，不证明其因果归属。
