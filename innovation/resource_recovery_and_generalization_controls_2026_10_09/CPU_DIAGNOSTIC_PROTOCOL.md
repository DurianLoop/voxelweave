# 五项独立CPU准备诊断（非病例实验）

原文核读后事前限定以下toy/exact算术检验：

1. 按AMDU式9及正文96/98/128的解读，检验低absRVE是否足以推出小FP；用完整二值集合独立计TP/FP/FN和Fraction复算。
2. 按Borges正文82的逐体素分位数再求和，与每个完整MC样本先求总体积再取分位数比较。两组同边际、不同跨体素依赖的合法soft概率，NumPy线性分位数与Fraction独立重算。只证明二者estimand不同，不否定其另行校准后的覆盖率。
3. 按Bézier式2，用合法单调、端点固定、偏离identity<=0.5的两条固定曲线，在常数3D toy上计算训练mask相关的边界信号；Bernstein和展开多项式双计算，GT不变，global同曲线作为控制。不冒充作者随机sampler/可选seam smoothing/预训练网络复现，也不称使用训练GT本身是泄漏。
4. Borges当前PMC XML式1/2的负pair-L2，在普通最小化时是否与拉近feature的文字意图一致。只限当前公开XML字面式，未核publisher PDF或源码。
5. AMDU当前PMC式4的负KL，在普通最小化时是否以uniform为最优。其正文另提gradient reversal，故不从字面符号推出作者实际实现错误；运行源码与梯度路径仍待核。

CPU1/低优先级、wall120秒、stage2MB，磁盘/RAM各8GB及原预留。只加载toy数值与公开XML/提取块，不载MRI/GT/model数组或CUDA，不读取验证/确认集，不安装、不查控其他PID。保存完整反例和版本来源，不把这些诊断当病灶改善或发表确认。
