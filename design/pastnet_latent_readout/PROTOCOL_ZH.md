# 成熟latent分频读出：计算前登记（2026-09-15）

LACV、STC、旧线性图像残差和MAE约束探针均维持既定停止结论。本实验检验新的信息表征：control实际混合MA3 latent 中能否读出跨训练患者可预测的剩余误差。不是重新训练旧结构，不读validation/test，不改变旧checkpoint。

## 数据与唯一主要变量

冻结 `pastnet_v2/runs/full_control_seed3407_vram20/best.pth`。使用同一观测归一化、256²、train全部z%4=0完整区间。捕获原 `base.single.decoder` 第二次调用的输入，即实际mixed latent，64通道。复用旧残差探针的56名fit、55名check患者名单。它们均见过历史网络训练，check名单及结果也曾参与其他开发，故不是独立holdout。

两臂同一latent、相同target−control残差、相同MSE拟合目标和ridge λ=.001，不改其他输入，不增加图像级预测/锚点特征。以slice→series→patient等权，三个phase共享系数。常数项加64通道latent共65维。

- shared：单组65维仿射读出，所有空间频率共享系数。
- frequency：低、中、高频各自读出系数，正交频带 r<.10、.10≤r<.28、r≥.28 cycles/pixel。中高频常数列严格为0，故有效自由度65+64+64=193。

唯一主要变量是是否解除频带间的系数绑定。这也增加有效自由度，不能将其包装成相同容量的机制消融；若以后做神经网络full，仍需单独的容量对照。这里只有诊断性线性读出，不是已提交的输出refiner，也不证明分频解码的神经网络形式有效。

## 求解与保护

按fit患者统计逐频带XX/XY，标准化ridge以每列中心方差为惩罚尺度，截距不惩罚；非零频带不含截距。每列方差下限1e-8。shared使用三个正交频带XX/XY之和。GPU关闭TF32，以float32得到矩阵乘积，CPU float64累计/求解；记录方程相对残差和矩阵条件数，必须有限且相对残差≤1e-6。首个fit区间用CPU float64直接矩阵乘法复核充分统计量相对误差≤1e-5。

检查时，shared在latent上仿射读出；frequency先各自仿射读出再投影到对应频带并相加。修正最后统一clip至±.05，两臂一致；不clamp最终图像。该clip是注册的部署保护，所以ridge解不宣称最小化clip后目标。固定系数，不按check选步数、频率边界、clip或ridge。

合同：初始化/零系数与control一致；读出函数不接触target；FFT重建与Parseval；频率相同系数退化到shared；带偏置的频带充分统计量等于原特征统计量；实际混合latent捕获恰好两次；来源哈希；fit/check患者无重叠。smoke使用各组前两名患者（按字符串排序）的z=0区间，两臂走完整拟合和评估；smoke绝不准入下一阶段。

## 固定检查门槛与停止

仅frequency可进入下一阶段，要求同时满足：

1. 对未修正control的patient等权PSNR增益≥.05 dB；对shared增益≥.03 dB。
2. 两项配对比较均做10,000次患者bootstrap，Bonferroni两比较97.5% CI下界>0，分别≥60%患者改善。
3. 对control的MAE、MSE均值不退（MAE数值容差1e-8），control最差四分位PSNR不退。
4. 数值求解、数据和输入合同全部通过；结果完整。

任一失败即停止该固定线性latent分频假设，不改参数或追加更复杂读出救援。通过只允许另行登记一次冻结系数validation诊断，不直接授权full、三seeds或外部测试。即使失败，也只排除当前读出函数族，不能宣布所有频率解码没有价值。本轮用户无需运行full。
