# Noise2Same附录局部推理核查：只审查一个条件方差推断

实际文字与视觉核读官方Supplemental第1页Eq(16)→(17)及解释，原文从Var(Xj)=1说明Var(Xj|Y)≤1。标准全方差公式给的是平均条件方差上界，不能一般推出每个Y上的点态上界。另立这个固定有限概率例子，核验推理边界；不是新定理、完整Theorem1的反例或MRI风险结果。

预固定Y=0概率19/20、Y=1概率1/20；噪声ε|Y=0为0，ε|Y=1对称±sqrt(381/20)，条件均值0。X=Y−1/20+ε，标准化的是总体边际均值／方差，非样本mean/std。Fraction从条件矩及全方差两路径求：EX=0，VarX=1，EVar(X|Y)=381/400，Var(E[X|Y])=19/400，Var(X|Y=1)=381/20>1。固定这些值后执行，不为失败调整。

只需标准库，CPU1、自身below-normal、8GB RAM／disk余量、60s、输出≤1MB，读已有原文／protocol字节绑定，无MRI／模型数组、神经／GPUforward／训练更新。不关闭任何用户进程；原训练99542继续。

通过只否定“边际variance1一般蕴含点态conditionalvariance≤1”这一推断。本例没有完整核验论文所有函数／mask／normalization假设，也不证明Theorem1最终上界错误；总体Cauchy-Schwarz可能提供另外的证明。Theorem2的常方差独立additive noise另有更强条件。MRI中sample-derived归一化和magnitude噪声适用性仍未证明。本例不充当可发表MRIclaim。
