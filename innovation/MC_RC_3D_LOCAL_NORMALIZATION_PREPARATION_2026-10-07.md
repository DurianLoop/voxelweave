# 有限局部统计的已知算子：仅作为后续基线准备

在已核读3篇全文之后，追加定向核读已获取的 Kernel Normalized Convolutional Networks（arXiv2205.10089v4，TMLR02/2024）方法/对照/资源部分，以确认一个不使用全tile统计的已知候选。本项不修改已运行的接续拟合，也不声称新归一化发明。

准备 KernelNorm/KNConv Eq5 的3D、dropout=0局部算子，均值/方差在一个3D卷积窗口的全部输入channels取，bias在标准化后加；当前版本不实现论文训练的随机dropout规则、专门KNResNet架构或其训练配方。与普通Conv3d+IN的参数集合/功能不同，不能直接替换旧checkpoint当公平MRI方法比较。

只进行合成CPU核验：独立显式NumPy逐窗口标准化和dot product；float64/float32输出；input和weight梯度有限差分；局部crop interior与整图的同坐标比较、远处扰动控制；常量/零padding边界检查。全部MRI像素、GT、任务网络效果0，CUDA不初始化。CPU1线程、自身below-normal；新输出<1MB。该准备是实现资格，不是MRI改善、新颖性或充分任务能力。

若后续旧网络能力仍不足，局部统计可与固定/运行统计、已知优化配置一起事前设计从头训练对照；全部病例、相同监督、分母、预算、最后checkpoint和原gate保持。局部算子理论上仍须足够卷积halo、正确外边界和下采样格点，不能把3³统计窗口当整个U-Net的halo半径。
