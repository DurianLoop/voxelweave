# raw/post图像 × raw/post全volume统计：固定三人CPU机制预检

此方案写于全部既有45post/三人anchors结果已核读之后，属于新开发机制实验。原post带宽恢复解释已经失败；本实验不改变anchors，不扩展原失败干预，不验证新SR方法。仅用固定VS-SEG-202/203/204，不能作科学独立确认。

每人四格：raw图像/raw统计、raw图像/post统计、post图像/raw统计、post图像/post统计。两个对角格已由完整旧队列生成并复核，不重跑。只新增两个交叉格，共6次官方冻结分割CPU前向；图像数组与已有对应baseline逐位同一，均值/std精确用原MONAI float32全volume统计约定。其余checkpoint、RAS、tuple/Gaussian滑窗、阈值和两标签保持同一。

互换统计量是解释性干预，会改变完整网络输入的仿射强度，不是物理图像修改，也不是可部署SR收益。raw/post自己的统计都可从候选重建取得，不使用hidden参考MR或label选择，但对官方checkpoint更改归一化仍是输入分布变化；不能将其改善直接称形态恢复。

全部6交叉格完成及保存预测/真实物理grid指标核验后才做统一效果分析，不读取动态子集Dice。保留两标签×full/slab/去1mm带，另直接保留supported missing与observed anchors confusion，unsupported tail也保留undefined。以下固定五个contrasts覆盖原三域，共30端点：

- post_rawstats−post_poststats：主要关注JSON full，固定raw统计后是否收窄post损失。
- raw_poststats−raw_rawstats：原raw图像仅受统计互换的影响。
- post_rawstats−raw_rawstats：固定raw统计下的图像变化。
- post_poststats−raw_poststats：固定post统计下的图像变化。
- interaction=(post_poststats−post_rawstats)−(raw_poststats−raw_rawstats)：归一化效应对图像的条件依赖。

保留逐人和三人描述均值，不bootstrap或多重显著性声明。用四格路径可作精确代数分解，但两个路径若不同是交互，不存在自然唯一“归一化导致损失百分比”。不得用有利路径或域来挽救原恢复解释。即使六格均改善，也需要跨输入训练、适配/独立任务网络和真正未见患者，不完成可发表claim。

CPU单线程、自身低优先级；每forward前磁盘15GB/可用内存8GBgate，CUDA_VISIBLE_DEVICES=-1且惰性初始化禁用。GPU/用户训练/locked IXI test/根环境/.gitignore未操作；仅写innovation。首失败原样保存并停队列，禁止因超时重启；所有旧已完成队列保持结束。
