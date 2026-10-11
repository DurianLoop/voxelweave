# SSC 原文阅读与已有结构对照的准备

Heinrich等，Towards Realtime Multimodal Fusion for Image-Guided Interventions Using Self-similarities，MICCAI2013/LNCS8149 pp187–194，DOI10.1007/978-3-642-40811-3_24。公开publisher PDF实际取得249477bytes，SHA058e96f9d877abeea15a1caeb57a04a0f8ea2189bf71d6b565886cd3eee8367d；8页正文/参考列表和8页render实际全部读/检查，4图，3条编号公式，无独立实验数据表。未取得或执行作者实现。

原文§3.1/图1：对六邻域patch之间12条非对向pair，计算SSD；SSC不以中心patch作为所有距离的共同端点。σ²为patch distances均值，exp(-SSD/σ²)再归一化max(S)=1。实验patch3×3×3，邻域中心distance2vox，0.5mm isotropic grid。变换中心、有效support与边界处理须明确；论文未给退化常量区域数值规则，准备代码的constant→ones是显式约定，不冒称作者源码精确复现。

图2/§3.1：12个descriptor元素各5bit的一元编码，总60bit可装uint64；每元素只支持0/5至5/5六级，不能用普通二进制32级替代。XOR后popcount/(12×5)精确等于**量化后**descriptor的平均SAD，不能当未量化descriptor任意实数SAD完全同。准备代码固定nearest/ties-up到六级；论文未给所有tie规则，不声称作者quantizer逐位同。核量化误差、36种标量级配对以及12通道完整随机向量的精确恒等式。

§3.2/式3用原独立forward/backward displacement同时更新保证inverse consistency；不是图像简单左右取平均。原优化器是tree belief propagation、blockwise parametric、stochastic similarity sampling/regularisation，不在本轮复现完整registration。特征加速不能隐去descriptor提取、量化和selection预算。

实验是BITE 13对preoperative MRI/pre-resection3D US，每对约27专家landmarks，非本项目CISS病灶Dice。SSC TRE2.12±1.29mm，MIND2.45±1.44，MI3.07±1.74；图3报p7×10^-4/<10^-6，本文未明示具体检验及其统计单位，不照搬到本项目。作者优化lambda/Mi bins等参数；独立外部确认协议未报告。初始TRE6.76±2.20，与引用SeSaMI文4.12不同，因为后者使用额外US-tracking信息；比较不可忽略信息差。time约20s SSC/Hamming、55s MI；图3stack包括descriptor/regularisation/similarity，120min alpha-MI来自引用、异优化器，不把跨论文time比当本项目增益。lambda×4/÷4仅该实验TRE约+0.1mm。

对本项目的意义：结构自相似/局部noise robustness/bitpacked Hamming均已有先例，作为SSC-only/QC强对照或信息相同的action-risk输入准备。不能把它们命名为本轮新方法。合成 affine invariance 或抑制中心异常值不证明对真实病灶、采集分辨率或SR hallucination有益；可能同时忽略需要发现的局部异常。必须用合法observed/reconstructed输入，不能在部署特征里计算native_reference/未观测真值SSC。母GT/native_reference仅允许作开发训练/结果参考，原无泄漏协议继续有效。

本轮独立NumPy实现及Torch double/CPU oracle只作数学准备：shifted patch3和offset2，replicate边界显式冻定，constant→ones，归一化公式以exp(-(SSD-minSSD)/meanSSD)稳定实现；输出float32。输入/统计float64是准备算子选择，不是GPU FP32部署资格。CPU1/interop1/below-normal，CUDA/MRI/GT/model/训练0，wall180s，preparation7MB/FOV20MB/other22.8MB与RAM/disk8GB完整保留。没有SSC医学训练/实际患者QC评分。
