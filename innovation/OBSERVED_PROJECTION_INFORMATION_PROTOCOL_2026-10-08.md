# 观测投影信息范围：新诊断的事前协议

只验证未来直接任务/PCHIP强对照的输入解释，不改变原live99542、旧两通道模块/资格、19series/2mm诊断或任何冻结输出。原共同初始化训练真实exit0且两臂最终冻结后，才运行原56FOV/6gates/strict；本轮不读取中间模型任务效果。GPU授权有效，新任务仍遵守既有8GB启动余量。

## 全19系列元数据线性秩

仅读取已冻结两通道资格的attempt01.json及其独立核验JSON；使用19开发series/11患者的native shape、observed_indices、grid unpadded形状。参数仅由metadata确定；不读任何MRI/GT/NPZ/checkpoint或验证/确认病例。

按原 `align_corners=False` 的像素中心映射定义一维线性插值矩阵R(n→m)，坐标 `((2*j+1)*n-m)/(2*m)`，越界clamp最近边界。z轴仅保留实际观测索引0,4,...，r/c全部native索引。padding为固定零嵌入，不改变理想实数秩。normalized sparse numerator到physical field的线性映射为 `Rz_observed ⊗ Rr ⊗ Rc`，在归一化统计已固定的条件下，其秩为各轴秩的积；availability只由固定mask决定，不增加未知强度自由度。metadata mean/std等如果单独传递，需按其真实语义另分析；本诊断不声称raw强度的统计无条件可逆。

生产用Fraction稀疏消元计算精确有理数秩，缓存相同axis mapping。报告全部19原观测强度维数、projection秩、nullity、各轴source/target/rank/zero columns及complete患者统计；不挑series，不用浮点SVD阈值。独立核验用另一个整数坐标公式生成矩阵，在两个固定素数1000003、1000033下做modular rank；若达到每axis `min(rows, columns)`，该结果在denominator不被素数整除的条件下给出有理数rank的独立证书。若达不到，不能只靠一致较低modular rank证明精确rank，记录未资格而不更换prime来救结论。

实际float32算子既有数值核验保留；精确实数rank不证明float32逐位可逆或良好条件数，也不证明实际MRI信号位于丢失子空间。PCHIP非线性，不能套同一线性rank公式或声称其总保留信息更多。

## 固定合成非等价见证

仅合成native r=4、c=1、z=16，观测z=[0,4,8,12]；physical r=2、c=1、z=12，原trilinear/pixel-center，最后观测后的tail复制。不运行神经网。两个observed数组A/C行定义为：

- A：[[0,0,2,2],[0,2,0,2],[0,1,1,2],[0,1,1,2]]。
- C：[[0,0,0,2],[0,2,2,2],[0,1,1,2],[0,1,1,2]]。

先核两者observed mean/std/元素数相同、并按各自同observed统计做归一化。比较三条固定路径：(1) sparse numerator+availability原physical map；(2) native逐pixel PCHIP后physical map；(3)先将observed anchors面内投影到共同physical平面，再PCHIP并z投影。A/C是否在(1)输入完全相同，而(2)可不同；(3)应只依赖共同投影后的anchors。只测输入数值，不能声称实际任务增益、解剖差异或临床效果。

生产SciPy PchipInterpolator+Torch CPU float32 trilinear；独立用有理数Fritsch-Butland/PCHIP斜率、Hermite及显式像素中心插值，最后以共同sqrt(3/4)归一化比较。固定atol1e-5/rtol1e-5，所有差异/失败保留，无实际MRI任务分数。不事后换见证，不用差异当PCHIP更优。

## 资源与输出

所有新文件仅D:\MRI\innovation，新stage<=20MB；每生产/独立<=600s、CPU1/interop1、BLAS1、below-normal、CUDA不可见、RAM/disk各8GB余量。新医学数组、神经/GPU forward、训练更新均0，不操作/枚举其他PID，无新代理。修改已执行源用新版本，失败保留。确认/验证/lockedIXI不打开。
