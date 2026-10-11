# 有限差分用独立60位十进制目标计算

V1 actual71b301 exit1；已完成的random/constant输出和VJP误差<=2.2737367544323206e-13。constant-input的float64有限差分h1e-5误差6.181664705118273e-8，未满足1e-8 gate，不能提前认证后续case或整网。

Windows NumPy longdouble的eps与float64相同，不能据此提高验证精度。V2保留原case/RNG/direction scaling/步长/1e-8 gate与模型源码；只将独立目标及输入扰动计算改为stdlib Decimal，prec60，通过Decimal.from_float绑定真实FP64点和方向。保存plus/minus/derivative的完整十进制字符串，使后续audit无需依赖已舍入的float记录。旧失败与源文件不改；本版本不启动GPU/MRI/GT/optimizer。
