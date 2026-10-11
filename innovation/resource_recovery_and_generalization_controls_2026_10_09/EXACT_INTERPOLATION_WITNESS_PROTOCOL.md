# 单位置精确有理数插值核验

56d85e已真实复现v2 shared/full3.814697265625e-6；完整float64 gamma仍同超限，不选其作修复。固定该最大post witness [15,37,110]，只对throughplane两级线性插值用Fraction计算：fine/coarse坐标均为整数端点的有理比，r/c为未改变的精确整数位置；把cache float32值转换成exact rational，再计算coarse两邻点及恢复值。精确nearest-float32使用相邻三个浮点的有理距离和ties-to-even，不以float64中转认作精确舍入。

对比原Torch interpolate+normalized grid_sample、独立SciPy和精确两级值；分别记录float32 cast前及原scale/shift后的结果。仅证明一个开发位置的舍入与真实值关系，不外推所有35904字段，不改原oracle/算子或门槛，不将throughplane witness用于删难样本。CPU1/interop1/below-normal，单MRI输入、不读GT/model/验证，wall120秒、保存<=30kB及原stage2MB/8GB守卫。
