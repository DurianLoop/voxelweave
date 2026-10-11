# 已核原文与本项目创新判断

本阶段共核读三篇原文、45 个完整文字页，其中 4 个纯参考文献页；26 个不同原文页实际看图。交接前 SADFN 的 16 文字/12 视觉页按交接来源记录，本次新增 SERANet 13 页、ITFS/DRLC 16 页；SADFN 第13/14页均另行放大重看，不增加不同页计数。下载、提取和渲染均不单独算阅读。三篇作者代码未读，未复现论文训练。索引元数据筛选没有完成系统综述。

## SADFN：语义指导重建的早期明确先例

Fan 等，*A Segmentation-aware Deep Fusion Network for Compressed Sensing MRI*，arXiv 1804.01210v1，16 页。原文 SHA `fc01a83a218d4f699c39a96b94a4080523b5bf548f07207f6b8d8aad580aa903`。全部文字已读；实际视觉页1/2/6/7/8/9/10/11/12/13/14/15。

MRBrainS 仅5次 scan，随机4训练（192 slices）、1测试（48 slices）；只用T1。48个切片不能当48个独立患者，正文不能核具体患者ID。主要输入30% Cartesian k-space，另展示20% random，不是本项目 CISS through-plane 缺层。终点是GM/WM/CSF组织。

Pre-RecNet 用完整MRI作 target，32000 updates/batch4；Pre-SegNet 用完整MRI和人工组织标签，32000 updates/batch16、128²裁块。推理先重建，再由固定Pre-SegNet提取10层特征、MLFA聚合，然后另一个fusion重建路径。fine-tune 12000 updates/batch4，固定两个预训练网，训练fusion/1×1聚合，以完整MRI L2监督。WOS对照匹配fusion构件，但不具同等分割预训练监督，不能把全部pipeline监督/费用都说成完全配平。

Table5用同一个固定Pre-SegNet处理全部重建结果，没有逐输入分别充分适配任务网。CPU视觉转录及Decimal差值完成：对WOS，三组织Dice各增加1.91/5.45/0.83个百分点，描述性等组织均值+2.73；对Pre-RecNet均值+3.1166667。缺患者级数据，不能重算置信区间/p值。SADFN不是所有9端点最优：GBRWT的CSF HD=1.647，SADFN=1.649。全采样相对SADFN的三组织Dice差距1.54/5.60/0.68个百分点。

Table4打印Pre-RecNet=.03s、SADFN=.06s、WOS=.07s，未核完整特征生成、预训练、warmup/同步/整FOV计费范围。只能称打印runtime，不能以此证明本项目完整成本更低。

## SERANet：身份补查成功，循环任务反馈已有先例

Huang、Chen、Metaxas、Nadar，*Brain Segmentation from k-space with End-to-end Recurrent Attention Network*，下载首页面明确 **1812.02068v2，21 Jul 2019**。13页原文SHA `f3b317aa7523663d33d4b38146af7c47acee155b977eaa9dca06bc5ef9ca8129`。13页文字全读（第13页纯参考），视觉1/2/4/5/6/7/8。第3页和Algorithm1明确模型全名Segmentation with End-to-end Recurrent Attention Network，确认它就是此前未找到的SERANet，不是Acar 2022章节。

输入真实结构的模拟k-space及已知mask，经Reg/DC初始化，预测4组织概率，再以每组织概率乘两通道复数图像特征，拼成8通道进入AttReg/DC；共享U-Net/ConvLSTM反复预测。第5页Algorithm1明确每轮使用初始化的倒数第二个重建块特征与上一轮分割图，不宜简化为每轮必然对上一轮完整重建图再重建。最终仅以分割cross-entropy优化，没有本模型的全采样重建target；输出的“重建”实为任务特征，不要求临床图像逼真。

20个健康数字BrainWeb体积，MRiLab spin-echo模拟；17训练/969 slices、3测试/171 slices，180×216，1mm，30% phase-encoding lines含16中心线，10%/20%额外白噪声。不存在真实病灶患者泛化验证。所有网最多50epochs、batch12、Adam、LR1e-4，每20epochs×.5；经验选T=2，未见独立验证集和公开可核模型/完整训练费。

比较Two-step（独立重建+任务）、Joint（最终分割loss）、不同Reg类型和2–7块，以及有全采样pretraining的LI/Syn/SegNetMRI。共享结构不等于total参数、全部曝光和推理次数配平；SERANet循环次数增加任务网调用，不是免费attention。Figure2不能从小图曲线精确读数当新数值证据。

Table1组织顺序CSF/GM/WM，Table2为CSF/WM/GM，分别保留，不能跨表默认同列语义。Table2 SERANet-7打印平均Dice .8876/.8459，高于SegNetMRI .8563/.8006（都是合成组织任务）。Table1 final_lce/20%三值 .8083/.8762/.8415 等权平均 .8420，打印 .8423；CPU v1因为全均值一致假设 exit1，v2明确保留这一差异后 exit0。其余17个打印均值在四位小数半单位容差内；差异原因未核，不能擅改原论文或称复现。

对创新的直接限制：中间任务概率引导图像域特征、循环分割反馈、共享任务网络、任务loss优于重建loss，在2019原文中均已明确提出。更换attention、加入ConvLSTM、把分割结果喂回不能单独作为本项目新claim。

## ITFS/DRLC：病灶任务与训练曝光亦有先例

Qi 等，*Multi-task MR Imaging with Iterative Teacher Forcing and Re-weighted Deep Learning*，首页面明确 **2011.13614v1，27 Nov 2020**，16页SHA `ee08c6ab061e2ca652f3f6718dc430e6ff70b316ff634895cdd5c0a2df2272eb`。文字全读（15/16纯参考，14结论/参考混合），视觉1/4/5/6/7/10/13。

D5C5重建+U-Net分割；训练时交替让分割网看完整图与实际重建图（ITFS），另用epoch依赖的α/β调重建/任务loss（DRLC）。完整图是训练期额外监督/曝光，不能给提出方法独有而称模块公平增益，也不能把teacher输入延伸到部署。

ATLAS 229 T1标准空间subjects，120训练/40验证/69测试，189 slices每subject、裁224×192；50epochs/batch16/LR1e-6，每10epochs×.2。BrainWeb 20体积17/3，batch4/LR1e-4、3000epochs、翻转/旋转/仿射；40个in-house FLAIR病例20训练/20测试，485 slices（247/238），厚6–7mm、间隔7.8–9.1mm，50epochs/batch16/LR1e-4。原文报告retrospective k-space R4、中心8%，每体积同mask；不能因FLAIR厚层就把实验称through-plane重建，也未取得可核原始复数多线圈数据来源。

Table1从无两模块到两者都有，Dice .494→.518，precision .636→.688，recall .462→.479，PSNR28.78→28.87；ITFS单独Dice+.005而PSNR−1.58/SSIM−.014，DRLC单独Dice+.016。CPU只做打印均值算术，不重算患者显著性或凭交互差值推因果。Table3相对全采样U-Net：Dice+.006、precision+.056，**recall−.032**；说明不能用一个Dice优势称所有病灶端点改善。全采样模型是有限训练经验参照，不是所有有限模型性能必然不能超过的数学上界。

复现前须解决的原文差异（不推断作者实现）：第4页称cross-entropy但Eq4是soft overlap形式；第5页文字说α升β降，而Fig2/Eq5相反；按文字t=epoch字面Eq5在t≥ln4≈1.386已达到α=.05底值，t是否归一化未知。BrainWeb段落WM/GM/SSIM .9285/.9354/.993与Table4 .958/.960/.997不同；in-house段落SSIM .983与Table5 .986不同；Table1/2的固定权重基线离散量及Table1/2与Table3的最终SSIM也不同，可能不同run但没有核实。保留原文，不选择方便值称忠实复现。

病灶联合重建分割、动态loss权重、交替完整图训练都不能直接称新。原文末段主动把training cost留作未来问题，未给本项目所需完整action净效用比较。

## 尚未完整读到的身份

Acar/Çukur/Öksüz 2022官方章节DOI 10.1007/978-3-031-17247-2_6：只核官方摘要。摘要有分割proxy误差反传形成pseudo-attention、全采样逐渐增加undersampling、OCMR cardiac。Publisher PDF多次失败且最后HTTP200仍是HTML，不能称章节全文已读。OpenAlex/S2按精确DOI均为closed、无公开PDFURL，机构landing位置保留给后续，不证明作者稿不存在。

Xu/Öksüz 2024 *Segmentation-aware MRI subsampling for efficient cardiac MRI reconstruction with reinforcement learning*，DOI10.1016/j.imavis.2024.105200：目前仅题名/作者，未读原文。其它索引筛选也不能算全文排重。

[阅读来源](READING_PROVENANCE.json)、[SADFN算术](table_audit_attempt01/receipt.json)、[循环论文算术](recurrent_audit_attempt02/receipt.json)、[后续准备](INNOVATION_AND_MATCHED_CONTROLS.md)。这里没有本项目新MRI效应、科学确认或可发表claim。
