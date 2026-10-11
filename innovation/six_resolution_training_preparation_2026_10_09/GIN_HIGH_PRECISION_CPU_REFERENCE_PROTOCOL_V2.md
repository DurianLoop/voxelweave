# 独立高精度归约 CPU reference v2

目的为检验原FP32 CPU norm反向的数值敏感性，旧v1/production/GPU/失败全部保持；不为拟合GPU舍入而改公式。参数、输入、卷积/反卷积/池化/激活、head和optimizer均沿原FP32。只把每样本每channel的norm均值、population variance、affine计算及其autograd归约显式置于float64，eps1e-5，输出cast回FP32。没有running statistics，原模型54参数名/shape不变。该数学参考与原FP32设备算子存在精度版本区别，不能把它冒称逐位等价。

先验验证：合成shape(2,3,4,5,6) seed50002的输入、affine和上游梯度，用独立NumPy float64公式检查output/dx/dgamma/dbeta；三组全部参数directional有限差分，h=1e-3/1e-4/1e-5，明确二阶收敛检查及小步长误差标准。导数检查在纯float64输出上进行，FP32输出的舍入不被解释为可微操作本身。梯度/输出数值gate3e-6保持，不改变上一轮实际有限差分失败。

再完整沿旧人工16³/3view/两step/54参数162state比较CPU production与v2 reference，使用原seed、原GIN及母target。全部实际更新记录；失败就停止，不能从norm解析正确推断完整CPU/GPU资格。若人工通过，则另版本完整19series GPU runner仍逐病例、两输入两步、全部head/梯度/参数/moments/二值判断，首失败停止、全scope保留；任何假设与真实结果分开。

CPU1/interop1/below-normal、RAM/disk8GB，prep7MB/FOV20MB/other22.8MB/paper6MB cap均保持，free扣未花余量避免双重计占用；人工wall180秒、receipt160KB，无MRI/GT/parent/CUDA。后续GPU沿启动8192MiB/allocator min(10%,2.4GB/total)/peak2.5GB/runtimefree4GB/FP32/TF32off/deterministic。既有医学gate、坐标3e-12、二值0不降低，正式医学训练仍未ready。
