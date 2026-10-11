# 两篇原始正文与项目创新判断

本轮完成 BigAug 主文22–115块及相关脚注/选定参考文献，完成 SynthSeg+ 主文18–120块及数据可用性/选定参考文献。块号来自本目录标准库解析的原始PMC HTML；下载、提取、实际核读分别保存，未读取图片像素、PDF、独立补充材料，未执行作者代码或下载权重。下述为原文任务结果，不是本项目新患者效果。

## BigAug：必要增强控制已经有直接先例

[Generalizing Deep Learning for Medical Image Segmentation to Unseen Domains via Deep Stacked Transformation](https://doi.org/10.1109/TMI.2020.2973595)，TMI 2020，PMC7393676。原始来源：[PMC HTML](https://pmc.ncbi.nlm.nih.gov/articles/PMC7393676/)。精确DOI Crossref与HTML元标签的题名/DOI匹配。前次NCBI BioC429、EuropePMC XML500保留；本次HTML取得200，实际78f44b=0，不能将前次失败改写成成功。

方法42–56、实施74–75：九种stacked变换覆盖quality/appearance/spatial，各概率.5；blur sigma[.25,1.5]、unsharp强度[10,30]、noise std[.1,1.0]、brightness shift[-.1,.1]、gamma[.5,1]或[1,4.5]，空间rotation±20°、scale[.4,1.6]和elastic。图像和GT空间变换同步，foreground/background随机crop，Dice loss，AH-Net且encoder采用ImageNet ResNet50预训练。训练source分别26/6、16/4、8/2，300epochs×3次，再按source validation选择；当前本项目2992步一次配对续训和last state不是复现该配方。正文同时写ADAM与“all using SGD”，优化器歧义保留。

结果78–113：prostate MRI、left atrial MRI、left ventricle US，非VS病灶/SR。表II报告unseen平均baseline49.8、Top4 74.9、CycleGAN63.5、BigAug80.0 Dice点；这些汇总既不是当前患者先均值，也不是七domain简单等权。按三任务先平均再等权得到BigAug79.9611，接近原80.0。原baseline定义是random crop only；已有预训练骨干和300epoch预算，不能挪成当前弱模型预期。作者只评Dice，明确未评Hausdorff；无肿瘤recall/体积保持或缺层净收益证据。

本轮标准库提取每个原始table cell并用Fraction独立复算：[算术结果](robust_qc_extraction_attempt01/bigaug_table_arithmetic.json)。Perturb行原unseen Average55.7，而按三任务等权为62.2556，按七domain等权63.5714；其余可计算行与三任务等权差异均<=.2 Dice点。不能自动修正原表，也不能凭此宣称全篇结果无效；用于避免直接复制不一致汇总。原表保存于[结构化cells](robust_qc_extraction_attempt01/bigaug_tables.json)。

归一化范围必须分实验：小样本实验74–75为固定[0,2048]或[0,255]映到[0,1]且增强后不再归一化；465例MultiCenter实验105改用zero mean/unit std并增大ROI至128×128×32。后者报告unseen87.5→89.6，仅2.1 Dice点增益，不能把小样本30.2点差异当所有异质数据效果。CETUS vendor由视觉外观启发式分组，作者承认可能误分；ProstateX排除术后异常解剖病例是原文限制，不授权本项目删除困难患者。

项目决定：普通空间/强度增强用于建立强任务基线。当前四分支完全独立冻结，主要比较为同输入、同起始权重、同2992步的spatial-minus-intensity；不能用99步旧control归因。开发方向最大倾斜81.73°、验证最大14.07°的既有元数据审计也不支持“验证更倾斜所以失败”的简单解释。空间增强资格通过仅证明坐标/标签处理正确，不证明医学泛化。

## SynthSeg+：纠错、无真值质量预测、拒绝和体积分析都不是宽泛新意

[Robust machine learning segmentation for large-scale analysis of heterogeneous clinical brain MRI datasets](https://doi.org/10.1073/pnas.2216399120)，PNAS 2023，PMC9992854。原始来源：[PMC HTML](https://pmc.ncbi.nlm.nih.gov/articles/PMC9992854/)。精确DOI索引与HTML题名/DOI匹配；本地定向Markdown查重未找到SynthSeg+/该DOI记录，不将此前已读SynthSeg或TumorSynth重复计新论文。

方法38、85、91–108：S1分四种coarse tissues，D纠错，S2根据图像+D输出分31结构，S3分68cortical regions；R根据S2分割本身预测10区域Dice。segmenters以随机label-map合成图训练，Gaussian blur+subsampling+返回1mm网格已经覆盖任意层厚直接分割路线。采用1020结构map（OASIS20、ADNI500、HCP500），部分为FreeSurfer自动标签，非VS人工病灶。85总述称仅synthetic/no real images；96/98更具体地写D/R用降质real images经冻结S1/S2生成输入，不能把后两模块也概括成全程不使用真实图。其实际影像来源/患者划分细节在未读补充材料与代码中尚未核实，不推断泄漏。

98明确R回归的是若有GT时的Dice，用validation选择阈值.65。它不是本项目具体动作a的paired净收益标签；但不能据一篇文献推断全领域没有增量收益策略，此前已读defer/cost-sensitive/SafeRestore/MoEDiff继续构成直接先例。选择/训练一个收益头本身仍不足作创新。

53–58评594例（500+94几乎不可用影像）pass/fail，总体rejection18.2%，去掉94例后4.9%；table1 R为Sensitivity .999、Specificity .906、Accuracy .981、AUC .998，DeLong对Liu p=.081不显著。正类方向需澄清：以18.2%作failure prevalence复算accuracy为.922926，以pass prevalence复算为.982074，后者更接近原.981；精确confusion matrix及positive class未取得，不把.999写成失败检出率99.9%。[CPU核验](robust_qc_metric_audit_attempt01/receipt.json)保存两种方向与全部原cells。

42–49与87：500例临床标签来自同session的1mm T1 FreeSurfer结果刚体映射，再视觉剔除138标签/注册错误及94低质例，520划分20validation/500test；是清理后的silver references，不等于500原生人工真值。人工降质contrast/resolution实验为20T1、18T2、18DBS、8PD，合计64 scans，而88又写66，计数不一致保留。61图注与60正文把62例/500例ICV相关.910/.906对调，原文不确定。不能把这些数据流程直接视作本项目新确认病灶合同。

70–81：14752scans来自1367patients，按区域QC>.65筛选后留12954–13357例，以年龄B-spline、gender和resolution校正复现群体atrophy；不是1367独立成对治疗患者，更不是个体纵向肿瘤增长检测。论文99–108列出每segmenter约300000step（RTX6000七天）、R50000step（一天），完整推断12–16秒。QC对照要计五个模块和训练标签生成等完整费用，不能称推断免费或只报R头。

项目决定：后续强控制补充“分割输出→绝对Dice/失败概率→拒绝”与raw、直接observed任务和两路径成本defer同预算比较。保留所有被拒患者的分母、失败率、费用和覆盖率；不能只在accepted子集报告Dice后宣称医学能力达标。解剖纠错的平滑先验不直接迁移小VS病灶，先验证实际病灶保持，不能下载现成模型直接宣布有效。

## 下一科学分支和停止条件

当前native/raw原19998步、99步配对pilot均未通过原六医学门槛；原四已见验证患者/9series不能称独立确认。正在运行四2992步匹配空间增强是普通基线能力实验，尚未取得结果，本轮不评分任何中间checkpoint。

任务能力合格后才有资格检验具体缺层动作：只用同observed预测动作的真实病灶增量收益，并对完整全FOV效应、体积/召回守卫、全部算力费用负责。现有先例已覆盖error regression、defer和一般gain gating；潜在新结果必须提供这些强基线尚不能解释的实际机制/增益。例如具体局部动作组合在IN/上下文中产生非加性的真实任务变化，需实际联合输入评分和同预算联合动作对照；这只是待证假说，不能称首创。

若四新分支未过医学门槛，继续普通充分适配/来源合格的同架构预训练准备；不开放8未见确认患者/12series或locked IXI来选模型。若强raw与直接任务消除动作余量，停止正向收益策略并保留反证。六门槛、全患者分母、强控制和确认边界保持原定义。
