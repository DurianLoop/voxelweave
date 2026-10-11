# 原sampling-mask与条件插补先例：本项目的新意进一步收窄

[Medical Image Imputation from Image Collections](https://doi.org/10.1109/TMI.2018.2866692)，[PMC6393212](https://pmc.ncbi.nlm.nih.gov/articles/PMC6393212/)，Dalca等。原SynthSR2021的bib0030明确引用该文，不能把引用代作全文阅读。本批四段实际连续读流完整覆盖158blocks，包含主文和AppendixA；25HTML table节点全是公式布局，没有结果数据表。图注文本读过，图像像素和外链supp/final PDF未读。

公开PMC头部明确Author manuscript，available in PMC2020-02-22；在线日期2018-08-22，DOI含2018。作者仓库README与citations.bib把最终卷期写作IEEE TMI38(2),504–514,2019。本批保持在线年/卷期年之别，没有独立核publisher final PDF。它扩展IPMI2017 preliminary版；本批没有读该被引版本，不另计一篇。

## 直接碰撞的新意

观察mask不是附带概念：block33 graphical model明确O_i提取实测patch子集，41–45对观测子集构造likelihood；conditional GMM/低维embedding由稀疏数据学习。block53/54给条件低维均值/协方差，70–74给近似hard-cluster MAP/conditional-mean reconstruction，73/118明确支持posterior sampling并讨论下游噪声估计。因而“给mask条件生成模型加不确定性”已存在直接先例，不能当新的独立方法。

block118把noisy manifestation与noiseless observed ground truth两种恢复区分；默认重建整patch（包括观测体素），原观测可根据下游任务保留。更早的论文已经指出观测保留/去噪存在任务与噪声取舍。当前项目既有point x4输入的anchor保持合同合法，但既不是该取舍首次提出，也不自动保证具体病灶收益。

block46明确不显式建模未知/不同scanner层厚，把原采集近似高分辨率薄平面；104另用blur压力实验探索层厚变化，并非forward-model严格保持。不能把“未精确建模”写成完全忽略thickness，也不能把作者近似当真实scanner校准。block120假定观测与voxel intensity独立；block122承认小型TBI/tumor集合可能缺少足够共享解剖covariation。这些是适用条件和对照设计依据，不是本项目已取得的病例结果。

## 实验分母与证据强度

| 原文实验 | 实际支持 | 不能扩展的结论 |
| --- | --- | --- |
| ADNI826 T1，从1mm下采样到6mm spacing | 原HR图像仅作比较真值，集合稀疏图像用于学习，MSE/PSNR重建证据 | 没有明确独立held-out患者训练/测试划分，不能把它说成完全未见测试；图5统计实际50随机扫描，不是826张独立最终评分。 |
| 4个subvolume的k=[1,2,5,10,15]、d=[10,20,30,40,50]分析 | 作者选k5/d30，比较equal observed-count的三种mask：axial、随机方向、随机mask | mask方向/coverage效应已有先例；不能把region参数分析推广为病灶因果收益。 |
| blur模拟层厚 | 原文承认更厚时误差上升，报告视觉近似稳健 | 没有病灶保持、scanner profile识别或测量残差保证。 |
| 766真实卒中T2FLAIR，0.85×0.85mm/6mm间隔 | 配准/强度归一化后代表性结构展示 | 没有人工病灶GT或定量损害；不能拿766当766例病灶收益确认。 |
| skull stripping Fig9 | 一个failure→success例子，作者称illustration | 不足以证明全cohort任务收益、排除失败或成本优势。 |

93的MSE统计p值/PSNR改善照原文记录，本批没有图像像素或raw paired统计量来独立重算。Eq18扁平MathML的PSNR写法不能据扁平文本作忠实数值复现；posterior covariance记号也未以final PDF/作者完整estep实现独立确认，本批不宣称修正论文公式。

学习在共同atlas，mask由affine interpolation weights阈值化且高梯度用更高阈值；21³ subvolume内聚合11³ overlapping patches，中心步长11。native恢复通过把模型统计反变换到subject space减少插值。这意味着注册、mask构造、cohort模型训练、patch重叠拼接都是完整费用，不能只算最终conditional mean。

## 固定作者实现的实际读取

[adalca/papago](https://github.com/adalca/papago/tree/92bba2322944b1f84a3dcf7d494fd1b5502e7777)的commit固定为92bba2322944b1f84a3dcf7d494fd1b5502e7777；repo/ref/tree3个GET加5文件GET，逐文件核Git blob SHA1与长度、另存SHA256。当前commit未证明就是论文release。只有5文件全文计阅读：README44行、citations19行、recon575行、sigmarecon206行、sampleSigmaRecon70行，共914行，7段actual读流。tree输出截断只是目录观察，不能计完整仓库阅读。

recon.m的latentMissing分支从Y拷贝，只更新missing；latentMissingR显式把原downsample mask体素写回。latentSubspaceR则把所有体素更新，observed copy语句为comment，最后使用mu+WXhat。前者与后者呼应论文noiseless/noisy取舍，不能说该代码全部硬保留观测。

sigmarecon.m是补covariance矩阵低weight entries的辅助算法，不是每病灶voxel posterior UQ；sampleSigmaRecon.m是沿x1→x2→x3的Gaussian采样机制，不能凭文件名把它当全图像posterior sampling pipeline。已读recon.m没有输出动作gain/cost策略；本文提及posterior sampling也没有量化其病灶校准或动作收益。没读estep/全部pipeline，没执行作者代码或权重，不能宣称完整复现/认证没有其他路径。

README说明subvolume columns准备可能耗很长时间/内存，cluster训练和reconstruction存储另需费用，还把volume重组合记为unfinished。固定tree无root LICENSE，GitHub license metadata为null；第三方ext许可证不作为主项目许可证。本批只阅读，不作安装/再分发主代码的许可证推定。

## 可发表候选与下一控制

采集mask、mask条件的生成/UQ、观测保留、不同mask方向的重建收益、下游目的取舍均更早存在。将它们组合或更换网络名字，不能单独承担新意。当前核心假设只保留：充分任务与常规增强之后，合法可见采集信息对固定动作的paired病灶损害差是否有超过强QC/absolute error及cost-sensitive控制的增量，并且该增量在未见patient和完整费用下成立。

条件不确定性需要列强对照：模型/先例同信息的posterior risk、任务不确定性、QC/absolute error，加动作条件和成本后的合法risk差决策，不只比较“高uncertainty就调用”。已经有本项目精确risk-vs-gain/LTT反例，不能再重跑相同toy当新的医学进展。最终仍要真实paired完整FOV action损害差。

原全11GT的19998parent只能开发能力，不能作严格LOPO外折初始化；所有训练/定位/QC/gain/校准和patient group都必须折内。原四臂医学评价尚待全部36FOV和真正terminal，强数值/六医学门槛不降。8确认patient/12series、lockedIXI继续关闭。本批无独立确认医学claim，goal保持active。

原urllib默认代理拒绝两个GET，真实c44fea失败；direct构建意外替换了已有引用源路径，真实f553ed在GET前失败。两失败和来源均保留；仅精确恢复已冻结refsrc后，132b9f真实exit0下载/提取成功。下载仍不计阅读，独立注册核实际连续读流才放行。
