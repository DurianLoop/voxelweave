# 已知局部归一化算子的 float32 数值对照（执行前冻结）

原 Eq5 的矩差/输出差原型已完成合成资格，但 float32 的 constant_two 与 offset_1000 严格门槛失败。原源码、JSON 和 3e-6 门槛均保留。本补充只诊断实现精度，不改变论文算子、不声称新归一化方法或 MRI 收益。

新增显式窗口原型：每个卷积窗口及全部输入通道构成一个统计单元；先减该窗口一个固定元素，再计算残差均值，直接中心化、计算均方和归一化后的点积。输入、权重、所有中间计算、输出都维持原 dtype；float32 分支不得隐式升级到 float64。外部零 padding 纳入统计；bias 在归一化和点积之后加；dropout=0、无 dilation/groups。原矩差实现作为失败对照。

预定种子20261007，原4例（random、constant_two、zero、offset_1000）及 offset_1e6、near_constant_2 两个扩展压力例。float64 输出逐窗口 NumPy 显式参考误差 <=1e-7；float32 与同一**量化后输入/权重**的 float64 参考误差 <=3e-6，全部有限。另核 stride2、padding0 的随机边界/输出形状；原资格只支持 stride1/padding1，扩展不回写原结果。

float64 input/weight/bias 梯度核对独立 NumPy 有限差分，误差 <=1e-7；float32 梯度与同一量化数值的 float64 显式窗口 autograd 对照 <=3e-6。核同位置 interior 的 full/crop 等价和远处扰动无影响；float64 <=1e-12、float32 <=3e-6。任一失败单独保留，不能仅据 finite/exit0 判资格通过。

仅合成 CPU、1 intra-op/1 interop、自身 below-normal，CUDA 不初始化，不加载 MRI/GT、不更新任务网络。窗口元素硬上限10,000,000；新输出<1MB、墙钟<=120秒、RAM/磁盘各留8GB。显式窗口内存/速度未做真实网络资格，合成成功也不得直接启动19series KNConv网络。
