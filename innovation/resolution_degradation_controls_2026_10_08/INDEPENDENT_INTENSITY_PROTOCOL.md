# 独立强度参考的执行前协议

已真实观察组合检查 session31866 的 ee6557 exit0，228 字段最大 post-intensity error 为 1.9073486328125e-6。此前两份分辨率结果经过同一个生产强度函数，不能冒充独立强度实现。

新增 independent_intensity.py 不导入或调用旧 augmentation.apply，单独实现 gamma 的 min/max 标准化和均值/标准差恢复、三轴指数 bias、固定 seeded noise。统计量采用 float64 累积作数值参考，各变换边界仍为 float32。两实现共享 NumPy PCG64 的 float32 正态抽样规范；不宣称随机数发生器也独立重写。单轴长度1的 bias 坐标按旧 linspace(-1,1,1) 为 -1，保持算法定义。

先执行不含患者数据的完整字段检查：5 个固定 fixture（常数、单体素、带纹理、完整64×128×128、有极端值及原padding的完整patch），全部8种 gamma/bias/noise 开关组合；另覆盖完整5984强度 primitives 的参数合法性。所有比较沿用3e-6，失败保存、不放宽、不修改生产函数。CPU1/低优先级/墙钟180秒/本目录总保存5MB/磁盘和RAM各8,000,000,000bytes储备；不初始化CUDA，无新依赖。

成功且真实 terminal exit0 后才开始完整真实 MRI 管线检查。独立数值实现通过不等于医学效果通过，也不认证padding对InstanceNorm的影响。11开发患者/19series可读取；4已见验证、8未见确认及lockedIXI均不在本检查内。
