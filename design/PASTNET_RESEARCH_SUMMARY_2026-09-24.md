# PAST-Net 研究尝试汇总（2026-09-24）

范围：接手后的 v2 研究，不把原有 G0xx 历史实验当成本轮新增。依据实际 completion.json、efficiency.json、配对 gate 与诊断报告；没有把 smoke 算 full。

## 数量与比较口径

完成13个full配置：1个PAST control、10个PAST结构/训练变体（STC两臂分别计数）、1个数据修复对照、1个官方I3Net参照。另完成5组重点低成本诊断/筛选，及初始证据、误差分布和信息探针审计。新的修复数据版I3Net尚无完成结果。

PAST full均为seed3407开发筛选，目前没有通过完整晋级条件的最终候选，未开展最终三seed确认及锁定后的IXI/NingXia正式复评。

旧G086的24.446977 dB来自多轮参与开发的fastMRI test-24。下文是256²、observed-only归一化、23患者validation、missing slices逐series再逐patient等权的分数；不可将两者相减当作提升。此前隔离了1名train/val交叉患者，并移除了归一化对隐藏target极值的依赖。

共同底座：四真实锚点rich conditioning、64通道/10块wide MA3、linear coarse+bounded residual、多尺度latent、dual-domain residual，992,179参数；PAST各分支继承同一G086，采用原AdamW/warmup cosine/EMA配方。多数是单变量增量，不能描述为13种从零设计的新架构。

## 旧训练数据下的PAST full

共同control=25.562011 dB，增益列均相对此control。STC扩展臂还必须对其local容量对照比较。

| 配置 | 方法 | PSNR dB | 对control增益 | 结论 |
|---|---|---:|---:|---|
| control | 原G086结构，统一新评价合同后固定预算训练 |25.562011|—|共同基点；冻结G086同合同为25.515590 |
| geometry | DICOM恢复的物理间距/方向，经FiLM调制特征 |25.564138|+.002126|未达+.08门槛，CI跨零，13/23胜 |
| correspondence-only | coarse作query，在真实锚点1/4、1/2特征上作3×3局部对应；去掉geometry |25.564482|+.002471|未达+.10门槛 |
| STC local | 原局部四槽的多尺度潜特征轨迹值/斜率/曲率，容量对照 |25.566130|+.004119|容量对照健康；不代表机制晋级 |
| STC extended | 六槽真实稀疏上下文、valid mask及查询条件轨迹拟合 |25.567219|+.005208|对local仅+.001089，CI跨零；分支停止 |
| LACV crossview | 保留真实锚点轴，在(anchor,x)/(anchor,y)平面交互后融合 |25.576666|+.014654|22/23胜、其它守卫通过，未达+.10 |
| QGCR global | coarse query读取每张真实锚点的整幅1/8特征图 |25.571022|+.009011|未达+.10 |
| soft-tail | 同架构，将hard top10%平方误差项替换为平滑CVaR |25.564924|+.002913|效应不足，MAE/Dice均值守卫也失败 |
| orientation | 同架构，训练时随机D4旋转/翻转；推理单方向，无TTA |25.656399|+.094388|最高validation PSNR，但未达+.10且质量退化 |
| frame-context | 原方向主干加低分辨率D4方向共享局部特征分支 |25.562437|+.000426|CI跨零，未晋级 |

方向增强的HD95 intensity proxy退化+.158420，95%CI[+.061572,+.264209]；SSIM均值亦略降。不能因PSNR接近门槛而将其升为最终候选。Dice/HD95均为强度阈值代理，不等同解剖分割质量。

来源：[v2](pastnet_v2/README.md)、[独立对应](pastnet_v2_independent/README.md)、[STC](pastnet_v2_context/README.md)、[LACV](pastnet_v2_crossview/README.md)、[QGCR](pastnet_v2_globalmatch/README.md)、[soft-tail](pastnet_softtail/README.md)、[方向增强](pastnet_orientation/results/full_review.md)、[frame-context](pastnet_frame_context/results/full_review.md)。

## 修复训练数据后的full

发现一个32层训练volume混合了两个不同DICOM SeriesInstanceUID，存在物理位置重复与错误target phase。按UID分成两个16层volume，逐像素验证、无重采样；train由1360变1356区间，患者仍111名，validation23患者/69区间完全不变。

| 配置 | 方法 | PSNR dB | 合法比较 | 结论 |
|---|---|---:|---|---|
| repair control | 原架构/配方，仅修复训练序列 |25.567453|对旧数据control +.005442|修复本身有效，保留为共同数据基线；不是架构收益 |
| wavelet3 | 十个主干depthwise卷积引入共享原卷积核的三级Haar多尺度算子，640个新增gate参数 |25.585002|对repair control +.017549|23/23胜，全部其它守卫通过；效应不足+.10，停止 |

小波主干PSNR差95%CI[+.012126,+.024497]，SSIM/MAE/MSE/NCC/Dice/HD95/tail10方向均改善。推理52.963ms/缺失层，对repair control的47.841ms增加约10.7%；训练20.72GiB allocated。属于小幅正证据，不是显著性能突破或跨seed稳定性证明。未运行J1 full。

来源：[修复复核](pastnet_series_integrity/results/full_review.md)、[小波复核](pastnet_wavelet_trunk/results/full_review.md)。

## 五组低成本诊断与筛选

这些结果不能混入上面的validation表；训练内检查患者曾被历史网络见过，也参与过开发。

| 尝试 | 方法及结果 | 决策 |
|---|---|---|
| 剩余误差可预测性 | 冻结control，self/local/extended特征的低分辨率ridge残差读出；检查组总增益+.024857/+.027663/+.028215 dB，MAE退化；远端相对local仅+.000552 | 不支持直接重启长上下文full |
| MAE不退约束 | 相同预测自身特征，比较无约束与MAE不增约束拟合；+.025205降至+.002331 dB | 保住MAE后效应不足，停止 |
| 解码器饱和诊断 | 冻结模型，测tanh/confidence幅度和频带梯度；饱和位置仅承载约1.45%误差，低中频承载91.22%误差 | 不支持放宽bounded residual；误差能量不等于可学习收益 |
| 成熟latent分频读出 | 同一冻结64通道latent，shared与低/中/高频独立ridge；frequency对control+.024048、对shared仅+.001613 dB，MAE+2.0841% | 不进入神经网络frequency full |
| 双锚点bilateral transport | 两尺度25候选位移，比较L(x−td)/R(x+(1−t)d)，保留对应分布；机制检查通过；冻结旧网络96步MSE只降.9208%，stationary对照.9056% | 低于注册5%容量门槛，停止，无validation/full |

来源：[残差](pastnet_residual_audit/REPORT_ZH.md)、[MAE约束](pastnet_mae_constraint/README.md)、[解码器](pastnet_decoder_audit/REPORT_ZH.md)、[latent读出](pastnet_latent_readout/REPORT_ZH.md)、[双锚点](pastnet_bilateral_transport/README.md)。

初始审计还比较了线性插值、target辅助配准、四/六槽强度包络、近邻真实层、oracle低频替换等。它们帮助定位困难区域与信息限制；涉及target的结果不得进入模型输入，也不是可部署模型或Bayes信息上限。见[初始审计](pastnet_v2/docs/01_证据与信息审计.md)。

## 官方基线与当前状态

已完成官方I3Net完整64通道、16 I2Block、3 CrossViewBlock本地参照，23.205M参数，4锚点→13位置、中央三缺失层监督。validation25.172132 dB，低于旧PAST control约.389879 dB。但I3Net随机初始化，PAST继承G086，loss与累计预算不同；I3Net第100轮早停时cosine尚未走完，不能据此宣布SOTA。

新的 `i3net_repaired_reference` 使用修复数据、随机初始化，完整300轮、不早停；实现、两轮smoke、实际断点续训状态等价与指标复算均通过。本次汇总时尚无completed full结果，不能给它填写预期PSNR。

总体事实：已排除多条当前预算下效应很小或质量有代价的路线，也修复了评价与训练数据问题；**尚未找到达到预设实用增益且通过全部质量守卫的核心v2候选，尚无三seed或跨域SOTA证据。** 多数尝试仍围绕G086做局部结构/训练增量，其负结果不能外推成“稀疏MRI信息已到上限”。
