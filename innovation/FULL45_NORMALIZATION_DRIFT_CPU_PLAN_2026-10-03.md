# 完整45人归一化漂移：CPU审计方案

本方案写在三人统计互换实验和完整45人原任务结果已知之后，属于事后开发分析。使用原固定45 CISS名单，不挑患者、不筛掉反例。目的仅是量化输入统计改变了多少，并检查三人技术预检与全队列的代表性；不是估计归一化的因果贡献，也不训练或验证新SR方法。

逐人重放原 raw PCHIP 和 post-resize PCHIP 数组，用原记录SHA核对。按任务链相同RAS朝向与NumPy float32计算整volume mean/std。图像相同的observed anchors与unsupported tail，在各自统计归一化后满足实数关系 `Y_post = a*Y_raw+b`，其中 `a=std_raw/std_post`，`b=(mean_raw-mean_post)/std_post`。记录a、b、std变化和归一化后的anchors/tail RMS；实际float32逐体素结果与解析式只允许浮点误差，不声称逐位相等。

全部三个采集域分别保存count/sum/sum-square、均值及方差；用float64矩分解复核全体积统计与归一化误差。原生held-out missing像素仅经既有解码器读取，但不用于选择统计、阈值、方法或患者。raw/post重建只依赖observed anchors。此审计不新增神经前向，不能据小RMS推断网络不敏感，也不能用关联排除机制。

在完整45人全部完成后统一汇总以下三个预列指标：`a-1`、`b`、`observed_normalized_rms`。与既有两标签full `post-poststats minus raw-rawstats` Dice作6个Pearson和6个Spearman描述关联，保存所有关联，无显著性检验、bootstrap、风险排序部署或归因百分比。保留固定202/203/204三人的值和全45范围/均值，另保留该三人与其余42人原任务均值。三人原任务方向为正、全队列为负是已知事实，不能包装成新的发现或独立确认。

执行使用 D:\conda\envs\MRI\python.exe，CPU单线程、进程自身低优先级；每人前检查磁盘至少15GB、可用内存至少8GB。禁止CUDA初始化，不改用户训练、根环境或locked IXI test。首失败保留并停止；不因等待重启。

后续决策：仅当完整审计发现足够明确、可区分的输入漂移问题，才考虑另立控制方案；不能因关联最大而挑患者或重跑旧失败干预。优先准备在相同输入曝光预算下的任务模型训练矩阵与真正新患者资格。所有科学确认患者仍为0。
