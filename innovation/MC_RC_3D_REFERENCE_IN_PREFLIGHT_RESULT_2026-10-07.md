# PCHIP参照内部统计的实现准备结果

资格预检v3已实际exit0：两项非同输入synthetic primitive与float64 NumPy归一化定义的最大绝对误差5.72721e-7/4.63219e-7；两种synthetic shape及001首tile同输入自重放，三个head概率和0.5预测全部0差异。未进行参数更新，不打开GT/native隐藏MRI，不计算任何Dice或任务收益。

保留两个失败：首版手工中心化公式在batch2×16³产生2.2471e-5概率误差，未过原3e-6门槛；v2残差式数值通过，但ZIP屏蔽误挡了observed NPZ，退出失败。v3只允许解析后的这一份SHA已认证observed NPZ路径；原MR ZIP和NIfTI/GT load仍屏蔽。数学operator和原门槛没有放宽。

同observed生成PCHIP与linear，两者native lattice anchors逐值一致，z-score共享真实observed统计。无GT选择的首tile里，linear普通IN与PCHIP参照IN之间三个head最大概率差异为0.169379/0.182337/0.083286，预测差异428/53/0。全部14个IN的统计差异保留。这仅是弱checkpoint的输出敏感性，不是改善/损害、统计因果比例或可发表新方法。物理重采样会混合邻层，不能从anchors图像一致推断预测必须一致。

现在有可执行且核过自重放的模块，可用于未来合格任务网络的机制对照。仍需native/raw_PCHIP/同observed直接任务充分适配与能力验证；所有科学效果患者/域预先冻结后才正式实验。InstanceNorm/AdaIN/GN/RegionNorm等已有直接先例，新意未确认。

来源：[v3完整结果](experiments/mc_rc_3d_reference_in_preflight_v3_2026_10_07/attempt01.json)、[首版失败](experiments/mc_rc_3d_reference_in_preflight_2026_10_07/attempt01.json)、[v2失败](experiments/mc_rc_3d_reference_in_preflight_v2_2026_10_07/attempt01.json)、[数值修复定义](MC_RC_3D_REFERENCE_IN_NUMERICAL_ADDENDUM_V2_2026-10-07.md)、[三篇原文排重](literature/2026-10-07_feature_normalization_primary_reading.md)。
