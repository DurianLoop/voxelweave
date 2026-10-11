# 全视野/局部基线的冻结后验证与复核协议

本文件在训练仍运行、验证模型效果尚未读取时写入。沿用训练前协议，不调预算、模型、输入、阈值或能力门槛。20,000 次更新的最后 checkpoint 才能用于验证；必须核对训练协议、源码、输入证明、初始和最终权重、患者身份与 checkpoint SHA。最终科学确认集合仍关闭。

仅评价固定 020/022/024/025 四验证患者的全部九个合格系列，两条件为 raw PCHIP/observed_shared 和 raw linear/observed_shared，共 18 项。只读已证明的 observed-only 包；不解码 native 隐藏 MR。不用标签定位、裁剪、挑层、后处理或改变阈值。标签在完整预测生成之后用于评分。先建立绑定最终 checkpoint 的诊断 split 回执，四验证患者不因效果改变角色。

每项完整 FOV 与全部原生 z 推断；记录覆盖计数、物理网格、z spacing、输入 SHA、模型调用数和完整原生 bool 预测。报告 full、anchors、supported missing、tail 的 TP/FP/FN、Dice、precision、recall、相对体积误差以及 full 物理 ASSD/HD95。空间距离采用六邻接 voxel surface、双向距离合并后取均值和线性 95 分位；不和论文不同定义的 AVD 数值直接比较。空预测、空 GT、undefined 不删除。

先在患者内平均其全部系列，再平均四患者。仅主 PCHIP 使用已有门槛：full Dice≥.70、missing Dice≥.65、full recall≥.70、full absRVE≤.50；4/4 患者 full/missing Dice>0，任何系列不能完全漏检。两个条件都完整公开，linear 未作匹配训练，不能根据微小差距得出 SR 收益。门槛通过仅说明该基线值得进一步能力和公平矩阵检查，不能称创新成功。

训练等待期间只做没有网络前向的几何证明：物理 z 取样、RCZ/ZRC 顺序、全 FOV→local feature 的像素中心及边缘、全 FOV tile 覆盖、概率回原生的 align_corners=False 映射。先合成非方形、不同 spacing 与边界反例，再在九个验证包的固定 z=0/n//2/n−1 重采样切面复核。记录全部容差与最大差值。这不读取分割效果。

复核从原始 NIfTI 标签做独立 signed permutation，以逐层二元编码 bincount 核计数，用显式六邻接与物理坐标 cKDTree 核表面距离。每个验证条件固定重放 z=0/n//2/n−1，共 54 个完整原生切面；独立实现 z context、tile 坐标、grid bilinear 和概率映回，调用同一冻结 architecture。共享 architecture 的重放不是第二个独立训练模型。若生产/独立边界或预测不一致，保存失败并排查，不选择性删除。

旧小基线的 counts/surface 和独立 bincount/cKDTree 函数将按 AST 提取到新纯 NumPy/SciPy 模块；保存原文件和提取内容 SHA。不导入旧 Torch support，避免重复设置 interop threads；正在运行的训练 support 和协议一律不修改。

所有数值过程 CPU 单线程、只降低自身优先级，磁盘≥15 GB、可用内存≥8 GB。预测与 checkpoint 的本批新增文件总量须核对训练前约束；不操作用户终端训练。失败保留，重试新增 attempt，不覆盖旧结果。
