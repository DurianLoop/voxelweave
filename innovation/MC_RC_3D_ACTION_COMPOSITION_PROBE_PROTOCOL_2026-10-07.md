# 无GT的局部动作组合诊断：执行前协议

目标：为后续真实修正收益实验核实输出响应是否可相加、窗口/原batch成本是否可相加。当前不测病灶收益，不以概率变化替代Dice，不读取正在训练的19series中间权重或效果。

输入仅开发001/UID末尾369177的已认证observed-only PCHIP，模型仅已独立核验的旧PCHIP最后1024步，非本次正式19series中间模型。沿用原observed统计、physical lattice、16tile、原batch2、IN、Gaussian blending、native回映、阈值.5，CPU float32、4 intra-op/1interop、自身below-normal、无CUDA，不操作其他进程。完整native MRI和GT数组读取0；四已见验证/八保留确认/locked IXI均不打开。

三个动作在结果前固定：同missing层z14，7×7正方形，各加归一化float32 .25。
- A：r125:132、c125:132，沿用前次中心支持。
- B：r141:148、c125:132，与A原输入支持不相交，距离16像素。
- C：r16:23、c16:23，远离中心，与前两者不相交。

执行所有8个子集，固定序0/A/B/AB/C/AC/BC/ABC；联合输入由原PCHIP副本同时加所有动作，不作串行的概率叠加。每次通过真实physical_mr差分确认输入支持、受影响tile和保持原配对所需batch；缓存用同baseline概率，按实际变化重算原batch，聚合顺序/float64 numerator不变。全部7非空子集另做全16tile推断并与缓存逐tile、physical、native、阈值逐位比较。baseline再全量重复一次识别运行非确定性；ABC用原production infer_full_fov作独立聚合参考。

诊断记录：三对AB/AC/BC的mixed response `p_pair-p_a-p_b+p_empty`，以及三阶 `p_ABC-p_AB-p_AC-p_BC+p_A+p_B+p_C-p_empty`，全部float64计算并报告full/anchors/missing/tail的全分母count、max、RMS、L1；保存每子集概率SHA、响应幅度和预测变化计数。概率非加性只证实这个固定合成干预/旧模型的数值响应，不能证明病灶收益非子模，更不能排除sigmoid/卷积/ReLU/IN/重采样等其它原因。重复baseline若非逐位相同，不据微小残差声称非加性，保留失败。

成本：固定几何上令R_a为动作影响的原batch集合；保守成本为 `|union R_a|`，与 `sum |R_a|`及面积 `49*|S|`对照。真实联合输入另测R_S，若因float32重采样使R_S与支持并集不同，则两者都记录，使用实际R_S执行，不隐瞒差异。缓存初始化8forward必记，总wall time仅单次诊断计时，不能当优化benchmark。输出响应norm不是优化端点。

资源：最多900秒，RAM/磁盘余量各8,000,000,000 bytes，本阶段此实验保存<=10MB，只保存JSON，概率缓存仅RAM。每forward前查资源，无训练更新。完整forwards预算baseline8+repeat8+7*8 full+所有真实cache子集（各<=8）+production8，最坏136forward/272tile。模型状态、源包与协议SHA绑定，原文件SHA不变。错误与actual tool exit都保留，不覆盖首次结果。

后续任务效益必须等session99542真实terminal exit0、两最后19998权重冻结和原能力gates后，固定真实observed生成候选、完整FOV GT仅评分、联合收益及端到端成本。若没有剩余收益，停止正向策略claim；不由本诊断挑病灶ROI或策略超参。
