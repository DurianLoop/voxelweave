# 全FOV tile特征上的主head覆盖诊断

在四个固定crop输出层分支最终结果和独立核验后提出：两臂full-head训练crop Dice通过0.9，但完整训练FOV仍失败。此新协议在新全tile训练前冻结，目的检查同一骨干是否能通过覆盖实际推断contexts的线性输出层优化拟合完整训练系列；不作为重建新方法或独立确认。

只使用开发001同一series、原native/raw_PCHIP最后512checkpoint。按原完整FOV tile_plan（16个64×128×128 tile、half overlap、无GT选框）逐tile获取最后decoder的16通道固定特征。模型eval、全部骨干参数冻结；same original observed statistics、physical grid及hard中心标签。特征只保存在RAM，禁止写入患者特征/标签/MR cache。

每臂从其原最后主head17参数重新开始，固定1024次AdamW更新、lr0.01、weight_decay0.0001，主headBCE+Dice乘4/7。每次更新使用全部16个tile体素，保留全部背景/空tile；没有foreground筛选。aux heads全部冻结，其常数loss不参与优化。全部tile的重叠体素重复计入训练目标，记录此分母；这不是Gaussian coverage-weighted完整FOV loss，不能把它当独立patient或等价临床风险。

相对于原两个crop，这项改变了训练空间/context覆盖和loss聚合域，不能将差异只归因某个单独因素。特征内容未重训、head参数/优化器/LR/更新数与上一full-head诊断相同，避免用更多主head更新作为解释。

每臂1024条history、原/最后SHA、16tile位置/label数量、固定骨干52项断言、最后head参数及最后checkpoint保存；两个最后checkpoint全部冻结后再评原两个训练crop、全部tile硬计数及原完整FOV四域。推断采用独立functional+NumPy native mapping、不读取GT用于tile/混合/阈值选择。保持0.5阈值和原训练gate（foreground crop Dice>=.9、full Dice>=.9、recall>=.9、absRVE<=.25、TP>0）。任何诊断通过也不打开四验证或八确认。

CPU单线程、自身below-normal，不初始化CUDA。RAM/磁盘各保留8GB，新输出<=60MB，不写特征缓存。总墙钟<=3600秒，首32更新投影两臂总更新>3600秒则失败保留、不扩大预算；每32步检查资源/时间。只有相同协议最后权重，无early stopping或最好checkpoint。

若两臂全FOV都无法达到gate，优先充分骨干训练/采样、context或已知normalization配置，不将native-PCHIP差值解释为恢复损害病灶。若达到，仅说明这个已见开发系列的拟合能力，需要19series充分适配及固定四验证能力门槛，最终独立确认仍未进行。
