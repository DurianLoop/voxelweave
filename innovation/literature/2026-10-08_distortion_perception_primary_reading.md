# 失真、感知和码率：两篇原文对 MRI claim 的边界

本阶段新增核读2篇原始作者稿的选定范围：各物理文字页1–5，共10页；各视觉页3、5，共4页。取得39页不等于全部读完。第一篇6–18、第二篇6–21未逐页读，补充证明、完整实验结果和参考文献不计核读；没有作者训练复现。[事前选择](2026-10-08_distortion_perception_primary_protocol.md)、[获取缓存](source_cache/distortion_perception_primary_2026-10-08/acquisition_attempt01.json)、[阅读范围与SHA](distortion_perception_reading_provenance_2026-10-08.json)。

## The Perception-Distortion Tradeoff

Yochai Blau、Tomer Michaeli；实际缓存是 [arXiv1711.06077v4](https://arxiv.org/abs/1711.06077)，2020-10-25，首页明确为2018 CVPR论文的extended version，18物理页，不能冒充2018会议版逐页复现。[原文](source_cache/distortion_perception_primary_2026-10-08/perception_distortion.pdf)。

| 已读物理页 | 原文定义／结果 | 对本项目的限制 |
|---|---|---|
| 2，式1 | 最优real-vs-fake判别成功概率=1/2+1/2·TV(pX,pXhat)；讨论输出集合分布而非单图likelihood | 边缘分布看起来真实不能证明患者病灶保持，也不是本项目ensemble方差 |
| 3，式3/4 | distortion为E[Delta(X,Xhat)]；perception为d(pX,pXhat)，允许随机p(Xhat\|Y)，非可逆指给定Y的后验support非单点 | 总体输出分布与具体患者配对误差不同，不能把同样合理的恢复解释当同样临床正确 |
| 3/4，MMSE和MAP示例 | MMSE后验均值可产生非先验支持内的值；MAP也可遗漏某些先验类别。MNIST/blank示例演示两个输出分布都可偏离先验 | 这不是PCHIP与direct的MRI任务实验，也不证明生成式恢复一定坏或一定好 |
| 4，Definition2；5，Theorem1 | non-invertible degradation下，不存在在TV邻域内stably distribution-preserving的distortion | 不能省掉non-invertible、stable和邻域限定，或写成任何恢复场景绝无同时改善 |
| 5，式10/Theorem2 | P(D)=min d(pX,pXhat)，约束E[Delta]≤D；非增，若d对第二参数凸则P(D)凸 | 这是最优可达边界的性质，不能由任意两个未达边界的算法推出必然此消彼长，更不是MRI病灶Dice定理 |

图5只是一维Gaussian、linear estimator Xhat=aY、MSE与KL的例子，视觉已核；没有将曲线读成真实MRI效应量。P(D)非增本身可包含平坦区，实际算法也可能在未达到边界时同时改进多个端点。正文未读后的proof或GAN/SR比较不作额外结论。

## Rethinking Lossy Compression: The Rate-Distortion-Perception Tradeoff

同作者，ICML2019/PMLR97；实际 [arXiv1901.07821v4](https://arxiv.org/abs/1901.07821)，2019-07-30，21物理页。事前选择使用subtitle，实际首页完整题名如上，作者/ID一致。[原文](source_cache/distortion_perception_primary_2026-10-08/rate_distortion_perception.pdf)。

| 已读物理页 | 原文定义／结果 | 对本项目的限制 |
|---|---|---|
| 2，式2 | iid source的information rate-distortion R(D)=min I(X;Xhat)，受期望失真约束 | matrix rank、数组元素数、GPU秒、ROI面积均不等于此互信息或bits/sample |
| 3，式4与脚注3 | R(D,P)=min I(X;Xhat)，约束失真与边缘分布距离；作者明确一般achievability不证明 | 不能把information lower bound改写为本机可达算法、实测成本预算或患者风险证书 |
| 3/4，Bernoulli示例 | Hamming distortion、TV、p≤1/2；P约束松时可与传统R(D)重合；图3为p=.1 | 无普遍严格tradeoff，更没有MRI数据的熵/噪声/解剖分布估计 |
| 4，A1/A2、Theorem1 | 对D/P非增；A1（divergence对第二参数凸）给凸性；A2（k(z)不能在整个source support处均最小）使R(·,0)与R(·,∞)不同 | 条件和“存在某些D差异”都要保留，不写为所有D必然严格分离 |
| 5，Theorem2、式8 | MSE下R(D,0)≤R(D/2,∞)，完美perception可通过至多2倍失真、相同rate获得；界一般不紧 | 不是任意MRI网络有2倍MSE界，不保证任何病灶任务/安全端点 |
| 5，实验开头 | MNIST toy，encoder latent uniform quantization；R≤dim·log2 L；作者不主张SOTA compression | dimension仅在已声明量化层数等设置下给rate上界，不等于上轮线性秩比例；本阶段未读后续完整训练及性能 |

视觉页3核三个对象的区分，页5核曲线轴、式8的1/2方向；没有反转不等式。论文的rate是编码bits，当前动作成本需要继续实测读取、预处理、动作生成、推理、transfer和后处理，不能借同名替代。

## 更新后的创新判断

两篇理论为“不要用单一图像代理指标替代目标端点”提供定义依据，不能证明本候选首次或任务收益。新输入控制已经把共享source落实到真实19系列，但ambient rank损失只说明理想线性变换有零空间；它没有实际MRI源分布、互信息、解剖signal落入零空间或病灶损失百分比。

可继续检验的候选保持为：在充分适配任务基线上，部署只用合法observed，选择固定修正动作的**患者配对病灶任务净增益**，并在完整同成本下优于普通误差/风险头、固定最佳动作及cost/defer控制。Noise2Self/SSDU的heldout平方风险、这里的perception、rank以及输入MSE都可作为开发特征或诊断，均不能发MRI效益证书。

此刻没有新增MRI任务收益，未开8确认/已见验证/lockedIXI。补层、PCHIP、mask输入、confidence convolution、自监督留出、感知与失真区分均为已知；应以强控制下的患者实际净收益和冻结确认支持具体claim。
