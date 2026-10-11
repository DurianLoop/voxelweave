# hard标签往返：保留生产float32，独立核对float64坐标

首版在第6个开发系列因原生产float32插值与NumPy float64坐标实现的最大概率差超过3e-6而失败；原数值、计数和失败保留。sharp hard GT的插值不等同于平滑网络概率，不能凭此改写先前已通过的网络概率重放，也不能把差异静默消掉。

新版本完整报告全部19series的两条原路径：生产PyTorch float32与NumPy float64坐标后cast float32，各自四域、患者内均值后患者均值，以及逐例原3e-6/阈值0差异是否通过。原float32失败不改判。

新增独立坐标资格：对同一physical hard GT另执行PyTorch float64 trilinear，再cast float32，与NumPy路径比较，仍要求最大误差<=3e-6、0.5预测0差异。只有这个新增float64坐标核对通过才称coordinate verification完成；不是生产float32已通过。目标是分清hard标签网格误差与浮点坐标误差，不能将本项标签参照冒充模型性能上界或更改原任务评分实现。

仅开发GT，原180秒/3MB/RAM磁盘8GB/CPU单线程/无MR与CUDA/验证和确认关闭不变。保留两种原端点，不选更好链作科学结果。
