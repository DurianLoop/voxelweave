# 动态路由与重建后下游任务：实际核读

新增两篇原文。完整读出34个不同物理页的文字，实际查看15个不同物理页的渲染图。34页包括20页主文、7页有关附录和7页参考文献/视觉例子的附带文字，不能写成34页全部是方法正文。PDF下载/提取页数不计阅读；范围和SHA见READING_PROVENANCE.json。未读作者代码，不声称已复现网络。

## TADT：任务是输入图像和倍率

Tianyi Xu等，*Task-Aware Dynamic Transformer for Efficient Arbitrary-Scale Image Super-Resolution*，[arXiv2408.08736v2](https://arxiv.org/abs/2408.08736v2)，2024-08-25。该PDF16页，文字1–16完整，视觉1/3/4/5/6/7/9/10。第8页引用、第11–16页主要是视觉例子图注，不冒充新方法章节；未查看这些末尾例子的全部图像。

3–5页明确：ASSR task=(LR图像, SR倍率s)，不是病灶分割/临床任务。控制器图像分支输出32个概率、倍率分支输出β；8个MSTG，每组两个MSTB共享4分支路由，不是64个独立路由。按p做Bernoulli采样并用STE训练，跳过局部/全局attention及对应线性projection；Eq(5–7)为L1+λβM、λ=.0002，M取决于β≥.25+.25√s。这是已有输入/倍率条件动态选择与质量-计算权衡，不把“按可观测输入选择计算路径”泛称成我们的新机制。正文没有从模型名称推出下游病灶优化。

5页用DIV2K自然图像、s~U(1,4)、bicubic生成48×48 LR和48s×48s HR，采样48×48个对应输出像素算L1。TADT是在预训练Baseline上继续训练，Baseline只用L1。核读版本没有给出两者总optimizer更新/训练时间相同的证明；不能把表中路由收益全部当同总训练曝光的因果效应。项目任何selector新增训练/标签生成费用均须计入，静态继续训练对照也应获得等量曝光。代码链接只是原文来源，未取代码确认sampling在部署时的seed/实现。

6–7页的CPU表复核实际358e08=0：LIIF×2，TADT相对SwinIR FLOPs下降20.893%，相对自己的无路由Baseline下降6.274%；两者是不同分母。SwinIR→Baseline本身已有架构/容量变化，不全部归功动态控制。LIIF表1相对自身Baseline的PSNR增量各倍率为+.02至+.04dB；表4中×2固定β=.5得到33.66，TARC33.65，严格低.01dB，不能称所有倍率都优于静态。表5无penalty时×2多388.75GFLOPs/+.02dB。表3和表5×2 TADT FLOPs分别6986.92与6986.91，保留原值、不拼接改写。

表3是FLOPs和参数，不是完整患者实测秒、能耗或内存节省。5页正文交叉引用Table6、Figure8/9与当前版表号/图号部分错位，视觉核对后按物理页和实际表头记录。固定β控制、无controller backbone、权重和路径共同适配的比较均已有先例；我们仍需完整任务适配+真实费用下的MRI效应，不能靠换成CISS给宽泛动态机制首创背书。

## 医疗重建与下游表现/公平性

Matteo Wohlrapp、Niklas Bubeck、Daniel Rueckert、William Lotter，*Evaluating the Impact of Medical Image Reconstruction on Downstream AI Fairness and Performance*，[arXiv2604.10904v1](https://arxiv.org/abs/2604.10904v1)，2026-04-13，MIDL2026。PDF39页；完整文字1–13、21–23、28–29共18页；视觉5/7/10/11/21/23/28。14–20参考文献、24–27和30–39的其他图/理论附录未完整核读；引用的BCE/公平性证明不算已读证明。

4–6页MRI是UCSF-PDGM的501个preoperative glioma exams，T2-FLAIR；CheXpert是224,316radiographs/65,240patients。70/10/20按患者分层切分，CheXpert训练再分重建70%/分类30%，MRI两任务共用训练患者。不是501测试MRI或按slice分train/test。三种重建U-Net/Pix2Pix/SDE从头训练；下游ResNet50/DenseNet/U-Net均只在原始未退化图像训练。公平性缓解仅微调重建，诊断网冻结；因此它回答固定诊断模型受到重建输出影响，不是充分匹配输入训练的分割模型是否仍有剩余可修正病灶损失。

21–23页说明MRI无原始多coil/复杂k-space；从已重建single-channel图像DFT、假定零phase、radial mask acceleration4/8/16、IFFT生成synthetic zero-filled图，再image-to-image学习。与本项目固定z抽层/missing-plane操作不同，不能借“加速MRI”的词汇认为是同物理逆问题。分割2D、min-max/256×256，训练全slice但评估只用60–130层；先每slice Dice，再每patient平均，再patient平均。分类同范围取median概率，patient AUROC。不是完整3D voxel Dice，不是整FOV缺层病灶检出。原文明确这些slice包含较多GT，不应据此替换我们冻结的全FOV主要端点或把阳性范围平均当全病例安全性。

22–23页U-Net20epochs、GAN200epochs、SDE MRI300epochs/CheX40epochs，各按validation选权重；不是同训练预算或容量的比较。SDE训练最多48h不是部署推理费用。不能把其表格生成方法排名当我们同容量/同充分适配/总费用控制下的因果效应。

7–13页图文在研究条件下显示PSNR变化与任务表现不一致，MRI Dice随噪声变化约≤3%；这属于该方法、任务和选择范围，不能推出我们的病灶任务必然对插值稳健。泛称“PSNR不能代表下游性能”“联合重建/诊断评价”已经存在。EODD通过validation balanced threshold，SER=max(1−Dice)/min(1−Dice)，相对偏差变化会受原始偏差分母影响。表3 sex24.1%→7.56%是reported median百分数差16.54个百分点；不是16.54点Dice、不是median患者配对收益，不能相加原mean EODD替代patient data。原文1,000bootstrap但所核正文未明确完整重采样单位与多重比较校正，故不重算p值。

28页人口表实际视觉核对发现字面不一致：Table6年龄≤58的cells155+92=247，printed row total为147；另一行254、sex列299/202、grand total501均保留。打印行总计401，而四个cells合计501。CPU已复核差100；不猜修复为作者实际实验人数，不据此宣称原论文结论失效。Table5的4×6cells/列/行总计56810全部一致，但与dataset65,240patients的范围关系不在所核文本中明确，不当作独立test人数。

## 对本项目的实质变化

1. 路由收益必须以同backbone、同额外训练曝光的静态继续训练作为对照；PSNR/FLOPs与完整病灶/费用不能混用。
2. 固定任务模型的重建输入失配，和各输入充分适配后的任务效应分开估计。三臂主比较仍是各自充分训练后的同角色、完整FOV、相同病灶端点；交叉模型/输入只作失配诊断，不能替代部署action gain。
3. 范围/汇总要绑定真实label：全FOV/观测层/缺层按原协议，每series→patient聚合；不按GT再选slice或重新挑主要端点。
4. MRI原始单通道抽层不是零相位synthetic radial k-space。论文的模拟前提、数据分母和未读材料独立记录，不能将其稳定性结果外推成我们的能力或将人口学公平性包装成本项目创新。

目前新增证据改进对照设计，未确认MRI方法收益。窄候选仍是固定CISS观测，在强且充分适配的任务路径与完整费用下是否保留可部署动作的真实病灶余量。动态routing、task adaptation、matched-static control这些单独机制不能宽称首创。
