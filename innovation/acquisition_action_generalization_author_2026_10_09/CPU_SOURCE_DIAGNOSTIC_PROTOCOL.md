# 四项新的定向 CPU 诊断

只用 synthetic arrays 和自己写的短公式，既不 import/exec 作者 repo，也不加载病例或权重。目标是本批次读到的具体假设，不计医学效果：

1. AMDU pinned source 的正 KL(uniform || prediction) 公式与梯度步：核实际最小化朝 uniform；另用一层 encoder/head toy 验证 classifier 步 detach 与 encoder confusion 步的梯度隔离。不是执行完整作者 trainer，也不认证 adaptive schedule。
2. UAF-AIMM 式9：learnable alpha 未给正约束时，正/零/负 alpha 对 variance gate 的单调方向；不推断作者训练得到负 alpha。
3. DG-TTA d=2 consistency Dice：两个相同概率场可达到零 consistency loss，同时病灶漏检；与 d=1 比较。说明该自监督端点不能独立证明真实病灶动作收益，不否定作者真实实验。
4. PEIL MRI 的复数 scale-phase gauge：改变 sensitivity/image 但观测保持；验证物理参数误差和 observation consistency 不是独立 task gain。此玩具不复现作者 CG/辅助正则/fastMRI结果。

CPU1/below-normal、wall120秒、目录累计2MB、磁盘/RAM8GB与其他allowance保持；新计4项source-directed diagnostics，既有5项不重复计数。全部结果、失败与来源记录入 innovation。
