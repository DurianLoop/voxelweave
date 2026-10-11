# 精确滑窗、TIN、KIN 原文核读与创新边界

本阶段新增实际核读 3 篇原文：Exact Tile-Based Segmentation 的公开完整 XML 共176提取块（含重复摘要/题名/表格及引用块，不能当176独立段落）；TIN 固定 arXiv v3 的10个物理PDF页；KIN 固定 arXiv v1 的24个物理PDF页，后8页为同一PDF内补充材料。两份PDF共34物理页的可提取文本已读，包括主文/图注/表/引用/补充文字。TIN 页4，KIN 页7、12、18四页实际渲染并 view_image 核读。其余示例图/曲线像素没有完整视觉核读；未复现作者网络和实验。

Kernel Normalized Convolutional Networks（arXiv2205.10089v4，TMLR 02/2024）已获取21页原文，只查看题名/作者/首页摘要，不计为完整新增阅读；保留后续待阅。2013 Patch Based Intensity Normalization of Brain MR Images 仅检索到 metadata，全文路线失败，不作正文结论。

## Exact Tile-Based Segmentation Inference for Images Larger than GPU Memory

Possolo、Bajcsy，J. Res. NIST126，2021，DOI [10.6028/jres.126.009](https://doi.org/10.6028/jres.126.009)，[原始公开XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10914126/fullTextXML)。作者信息姓 Possolo；同稿Biography写 Majurski，保留这一原文差异，不据此合并为别篇。

块11–16、28–32说明 ZoR 为输出责任区、输入含两侧 halo，stride=ZoR；不能把任意Gaussian重叠平均说成精确整图推断。块23–24明确依赖局部有限感受野，不适用于 self-attention、SE、deformable/non-local 等可变或全局依赖层。块45–50的 BN 在推断中使用训练后冻结统计，**不是本项目的 eval InstanceNorm**。

块54–68、90说明网络最粗特征网格要求所有窗口偏移保持在同一格点上；论文 U-Net 的因子是16，halo92向上对齐为96。不能照搬16/96到本项目：本项目四级/三次pool，因子8，而且14个IN仍使用当前tile空间统计。大halo和起点对齐都不能单独保证该网络与整图一致。

块78–88的20个3584²区域来自phase-contrast microscopy，单GPU24GB。Table1的512输入、halo96得到RMSE4.17e-10/ME0、相对运行2.58；它证明特定网络的分块数值等价，不证明临床分割准确或本项目MRI任务收益。AppendixC DenseNet的较小halo192也可使阈值ME为0，但概率RMSE仍2.44e-7；“分类一致”与“概率严格相同”须区分。本文GPU/速度数字不能直接用作本机资格。

本项目已执行元数据审计：19开发series/11患者、1139推断tile，11series的341tile起点非8倍数；001的16tile中7个受此条件影响。独立原tile_plan重放和对齐准备的覆盖全部核验通过，没有MRI前向或效果评分。只是待控制的格点差异，不是其危害大小或失败原因的实验证明。

另一个纯合成数值反例表明：保持4³crop输入完全不变，仅改变8³体积外部一个点，crop IN输出不变，但整图IN probe改变0.0222506；float64 NumPy/Torch最大差4.44e-16，远程导数与有限差分差1.23e-12。这是IN非局部性质核验，不是新定理、MRI性能证据或新方法收益。

## Towards Ultra-Resolution Neural Style Transfer via Thumbnail Instance Normalization

Chen、Wang、Xie、Lu、Luo，[arXiv2103.11784v3](https://arxiv.org/abs/2103.11784v3)，PDF标2022-03-16，AAAI2022引用由KIN参考文献给出。本项读固定v3，不冒充2021首稿。

PDF页3–4、Figure3–4和Eq2：

`TIN(x,t) = gamma * (x - mu(t)) / sigma(t) + beta`

先让thumbnail流经共享网络取得各层统计，再用这些统计规范patch。这个算子形式与本项目的reference-IN直接相近：当前实现同样用参照流统计标准化candidate，仅增加数值epsilon且参照来自同observed的PCHIP。同输入残差等价实现和source屏蔽仍是必要工程证明；**选择不同参照并不赋予“外部参照统计归一化”算子首创性**。上一阶段仅与AdaIN比较不同还不充分，本项补上更直接先例。旧文件不修改，新候选边界由本报告追加。

页5–6：1064²窗口、stride1000、thumbnail短边1024；style短边1024，训练COCO/WikiArt约80k各，batch8、VGG19 relu4_1 perceptual loss。页3明确thumbnail target分支detach；不是本项目完整3D标签监督、病灶分割或同预算MRI结果。页6的统计随thumbnail大小稳定是作者展示的VGG/natural-image经验，不是所有MR、所有层的保证。

页9 Appendix Eq6还扩展为thumbnail whitening，并用官方预训练CycleGAN替换全部IN，不需重新训练；因此“预训练网络上替换统计”“外部参考二階统计”也有直接先例。其不适用无IN/IW的优化式网络。GPU<5GB、线性patch耗时为作者具体自然图实验，不能替代本机fresh totals。

获取与页码问题完整保留：第一次15MB响应上限不满足，v2取得27,844,402byte原PDF；原整份pdftotext按formfeed切分显示12段，pdfinfo证明实际10页。原因是图表字体中含额外formfeed码点。新脚本按 -f/-l 物理页提取，旧12段JSON保留，绝不把12说成实际页数。

## Ultra-high-resolution unpaired stain transformation via Kernelized Instance Normalization

Ho、Wu、Wu，[arXiv2208.10730v1](https://arxiv.org/abs/2208.10730v1)，PDF标2022-08-23。不将未核对的后续发表版与本次v1合并。

页5–7 Figure3/Eq3–7：缓存每个patch、每层IN的均值和标准差，再对邻域patch统计表做constant/Gaussian kernel平滑，以平滑统计规范对应patch；标准差表的平均不是合并总体的精确方差，不能改写成MRI population moment计算。模块只在测试替换原IN，CycleGAN/CUT/LSeSim按原设置训练（512²patch，50/100/100epochs）。KIN是已有空间参考统计方案。

页7–8：ANHIR训练图像不足而在训练集推断，作者明确这一限制；private glioma 105患者的55train/50test；Kyoto17summer/20autumn train、4summer test。Glioma指病理染色图像，不是MR glioma。因此不能当本项目独立MRI队列或任务证据。

页9人工评估只选CUT，因为另外两框架图像差；5 specialists的30秒质量/10秒真假选择与Dice等患者端点不同。页12 Table2（实际视觉核读）有明确反例：glioma test CUT的FID105.66→100.90更好，但PIQE24.02→31.94更差、histogram correlation .85→.80更差；不能宣称KIN所有指标全面获益。

页18补充0.2（实际视觉核读）：真实IHC patch训练ResNet50、生成patch测试，并刻意裁接缝处；patch-wise IN/TIN/KIN accuracy98.8%/88.4%/99.2%。未给此段明确的独立患者patch分配或不确定性，且ANHIR生成推断原就是训练WSI，不能将0.4百分点写作独立临床收益确认。它足以排除“改归一化统计后评估下游任务”这一宽首创。页19的SSIM .94/.90/.93和FSIM .79/.74/.78，KIN反而略低于IN；作者认为这些指标难评接缝。页19–20保留缺少特定场景时KIN劣于TIN的失败。固定PCHIP统计的有效性不能默认成立。

## 对项目的具体决定

1. 完整16tile的骨干接续拟合仍是基线能力诊断。本轮两臂都在最后checkpoint冻结后再评分，当前loss不能当拟合成功。
2. “增加halo/对齐滑窗/共享IN统计/邻域统计平滑/换参照/加任务指标”均已有明确先例。参考IN仅保留为有source限制、同输入可重放的机制对照，不单独包装为新模块论文。
3. 剩余候选仍须落在本项目真实部署信息限制下，**预测具体缺层修正动作对任务的paired收益**，与充分适配的同observed直接任务、强PCHIP及已有风险/路由方法比较。现有addback、线性、QDA和弱任务失败全部保留；当前没有该候选有效性或独立新颖性确认。

原文：[KIN PDF](source_cache/kernel_normalization_primary_2026-10-07/kin.pdf)、[TIN PDF](source_cache/thumbnail_instance_normalization_v2_2026-10-07/thumbnail_instance_norm.pdf)、[Exact tile XML/文字块](source_cache/tile_context_alternates_2026-10-07/)。[正确物理页提取和四张原页](source_cache/tile_context_visual_review_2026-10-07/)。[窗口元数据结果](../experiments/mc_rc_3d_tile_lattice_audit_2026_10_07/attempt01.json)、[独立格点核验与IN反例](../experiments/mc_rc_3d_tile_lattice_audit_2026_10_07/independent_and_in_locality_attempt01.json)。
