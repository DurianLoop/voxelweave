# 两篇直接先例与本项目的创新边界

本批完整文本阅读PSACNN2019与原SynthSR2021，覆盖主文、图注、内嵌表和页尾；新增两篇不同主文。下载/解析成功没有计作阅读，实际12段连续且未截断的读流另注册。PSACNN是PMC accepted manuscript，页尾说明尚未copyedit；SynthSR为PMC journal HTML。两篇final PDF、图像像素、外链supp和作者代码/权重没有读或运行，不能把这些计作完成。

| 论文 | 原文 | 对当前候选最直接的影响 |
| --- | --- | --- |
| PSACNN: Pulse Sequence Adaptive Fast Whole Brain Segmentation (2019) | [DOI](https://doi.org/10.1016/j.neuroimage.2019.05.033)，[PMC6688920](https://pmc.ncbi.nlm.nih.gov/articles/PMC6688920/) | 已用单幅影像估计序列的三参数近似并生成训练增强；“采集参数/成像模型自适应”不能单独承担新意。 |
| Joint super-resolution and synthesis of 1 mm isotropic MP-RAGE volumes from clinical MRI exams with scans of different orientation, resolution and contrast (2021) | [DOI](https://doi.org/10.1016/j.neuroimage.2021.118206)，[PMC8354427](https://pmc.ncbi.nlm.nih.gov/articles/PMC8354427/) | 已使用采集可靠性地图作为训练和推断输入，同时建模spacing、thickness和注册误差；“加入观测层mask”已存在直接先例。 |

## 原SynthSR2021：需要新增的强对照

§2.1.4（block78）、§2.2.1（81）及§2.3（96）明确区分原始实测和插值体素，输入reliability map；非整数尺度或注册会生成0–1软值。文章引用Dalca2018 sampling mask，但本批没有阅读该被引用论文。后续2023文章没在相同位置强调该地图，不能据此忽略2021的先例。

成像模拟分别用厚度控制Gaussian blur、spacing控制subsampling，blur因子随机0.8–1.2；这是近似slice profile，作者没有证明复现全部scanner物理。多对比、多方向、配准误差、任务目的差异也已有先例。超参表与公式含MathML分数/根号，扁平文本会丢布局，不据此声称逐公式忠实数值复现。

训练39主体，192³ patch、200000固定iteration、lr1e-4、P10016GB约12天。约3秒是神经推断，注册和后续FreeSurfer另计。SR-only用合成HR目标，joint SR/synthesis用真实MPRAGE目标；2021每输入组合需训练，不能混同2023泛化版本的结果或主动病灶填补行为。

ADNI100（50AD/50control）从原MPRAGE模拟3/5/7mm spacing，三组thickness固定3mm；参考FreeSurfer是silver labels，不能当人工病灶GT。Table3的7mm SynthSR体积error3.0%、Dice0.875；正文block121对7mm fully supervised写2.7%，表为2.8%，本批核验保留这0.1个百分点差异，不修原文。Table2的3/5/7mm SynthSR比cubic的PSNR高3.9/3.8/3.7dB，SSIM高0.136/0.166/0.176；比fully supervised低，不能据此普遍声称最好。

真实5mm FLAIR海马error8.4%、correlation0.76，但cortical thickness不可用；相同生成影像跨任务效用不同已被观察。MGH50先排除大肿瘤/切除腔，分析时再排除3个baseline FreeSurfer失败，最后47；没有人工GT/HR参照，只间接aging。block155说明不替代个体肿瘤检查，161承认大tumor/stroke不能建模，并把UQ传播列为future work。这支持我们关注病灶任务，但不自动证明新意或任务收益。

## PSACNN：自适应信息边界和全费用

三参数近似来自单幅影像CSF/GM/WM的GMM均值，不能声称从影像精确辨识真实TR/TE。参数grid利用各类test acquisition的无label强度覆盖目标域；应明确使用未标注目标采集信息，不能擅称label leakage，也不能把它描述成完全没见test acquisition。

主分割训练16、validation3、Buckner test20，41结构、96³、Adam lr0.001、每epoch600K pairs，validation停止约10epochs。预备阶段另需8个relaxometry主体，并给每个训练主体训练3个NMR synthesis UNet；16主体意味着48额外UNet，不能只算最终segmentation head。

同scanner native ALLDice0.9396；GE14 SPGR上PSACNN0.7636、SAMSEG0.7708、MALF0.7804，未处处最好。三个volume coefficient-of-variation表是重复采集的一致性；Table4 T2SPACE10人的Dice是两个自动分割之间的一致性，均不能替代人工病灶准确率。原HTML逐cell独立重析后，4表PSACNN严格最优计数分别5/9、5/9、6/9、6/9；Table2的CA与CNN并列最低，Table4的TH与SAMSEG并列最高。作者Table2的6/9包括tie。

GPU45秒只主segmentation，preprocessing10–15分钟，CPU约5分钟；模型准备、预处理和失败都必须算入成本。作者明确当前没建模resolution、局部B1和病理；1.5→3T转换的强体素线性假设未有理论保证，只健康成人经验支持。这些限制可指向实验条件，不能把填补每个限制都算新理论。

## 已执行的非医疗机制探索

当前项目observed indices由 `range(0,native_shape[2],4)` 定义，是既有native voxel的phase-0点抽层。当前训练与评价继续采用其原合同。层厚积分属于另一个forward model，不能把点anchor保持外推成scanner measurement保持。

Fraction精确反例：center0/thickness4的box测量，只有z1=1时y=1/4；把y写进z0，点anchor完全保留，但box重测只有1/16，残差3/16。

全部预定90几何×12固定轮廓=1080案例真实完成；全部点anchor逐位一致。thickness1的180例box残差均0；thickness>1的900例中810例非零，最大0.24。标准最小范数测量投影后独立重测最大1.11e-16，但809/900厚层例出现超出[0,1]范围的值，最大中心改变量约0.482。记录全部失败方向和零残差案例，没有选择性删除。

连续球体384组/1036非零积分用解析原函数与SciPy quad交叉核验，最大误差2.84e-14。它与前面的分段常数体素实验不同，没有混合结果。以上不是患者证据、scanner校准或新重建算法，只给合同与后续实验设计依据。

实际机制runner首次47e55a因Windows HANDLE ctypes默认类型失败，尚未创建输出目录；原代码和失败保存。独立wrapper只修WinAPI签名，新真实c2b9cb exit0。原HTML39节点独立流式重析真实066bf8 exit0：31公式布局、1超参表、7结果表。表格节点数不是数据表数。

## 本批后的候选排序

| 候选表述 | 本批判断 | 必须补的对照 |
| --- | --- | --- |
| 添加mask/reliability、spacing或pulse参数 | 已有直接先例，不能作独立创新 | 2021 reliability map、PSACNN序列近似适配、同容量地图输入 |
| 更真实地模拟厚层/使用data consistency | 物理模拟和标准测量约束已有广泛先例；toy只澄清合同 | ordinary resolution augmentation、正确forward model、profile误设压力实验 |
| 用可见采集证据预测具体动作的paired病灶收益 | 仍是待验证核心假设，未确认可发表新意 | 同信息/同容量QC、绝对error-cost/defer、去采集特征收益头、仅metadata收益头 |
| 在完整费用约束下选择保留raw、修正或defer | 必须证明超过强任务基线后仍有真实动作余量 | static、random、always-action、联合动作输入/优化、所有失败与fallback费用 |

主候选应写成：在充分常规任务能力之外，可见采集证据是否为固定动作a的病灶损害差提供额外预测信息，并在未见patient层面改善包括定位、配准、QC、动作、后续任务与失败fallback的完整费用结果。训练目标是同患者同输入baseline-minus-action损害差，不能用单次风险或漂亮图像分数替代。不能把QC不够强导致的收益称采集因果效应。

当前尚未取得独立确认的医学claim。原四臂last2992医学评价优先；任务六门槛不足时继续补普通基线。原全11GT训练的19998父模型仅用于开发能力，不合法充当严格LOPO初始化。8未见确认患者/12series及lockedIXI继续关闭；资源/数值资格与文本阅读均不等于科研目标完成。
