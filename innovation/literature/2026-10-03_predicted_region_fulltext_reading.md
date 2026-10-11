# 预测区域失败后的三篇新增正文核读

四条预写 Europe PMC 查询返回41条索引记录，不是41篇相关或全文读过的论文。[原响应/摘要](source_cache/predicted_region_search_2026-10-03/attempt_01.json)。本轮按直接相关性取得三篇 JATS 正文，DOI逐篇认证：[取得记录](source_cache/predicted_region_fulltexts_2026-10-03/attempt_01.json)。下面依据实际核读的正文、表格和图注文本；没有取得补充文件或视觉审阅新文章的图，没有复现训练。已有PRETTIER、spinal-SR、crossMoDA不计新增。主要相关摘要另读，其他条目仅标题筛查，不能称整个结果列表都读过。

## SynthSeg：尺度和对比度稳健分割早已有具体方法

*SynthSeg: Segmentation of brain MRI scans of any contrast and resolution without retraining*，2023，DOI [10.1016/j.media.2023.102789](https://doi.org/10.1016/j.media.2023.102789)。[正文](source_cache/predicted_region_fulltexts_2026-10-03/synthseg_2023_maintext.txt)，实际核读段落0–139、141–156；140仅为未读补充材料入口。

方法20–70不靠更复杂骨干：从label map采样，仿射/非刚性形变，随机组织GMM、bias、gamma、噪声，独立采样方向、slice spacing与thickness（后者受spacing约束），Gaussian profile blur后降采样，再回到1mm生成输入。训练为同一3D U-Net，30万step，两次训练，用validation选权重。测试先trilinear到1mm、1/99百分位强度归一化，原/左右翻转概率平均，每个结构保留最大连通成分。这些是已有操作，不能把「尺度条件」「独立厚度/spacing」「合成label训练」「区域mask」「多视图一致」本身当首创。

数据72–94/Table1：训练标签为20手工T1-39、500 HCP、500 ADNI；只用label并不意味着没有解剖先验。评估宣称5000 scans、六模态/十分辨率，不能改写为5000独立患者。多数评价label是对应T1上FreeSurfer产生的silver standard，经人工QC；T1-39/MSp和心脏部分有手工标签。2393真实5mm FLAIR是实质真实低分辨率证据；另外3/5/7mm人工降采样并未采用真实slice profile。其比较先验、数据、预处理与当前native x4抽层不同，不直接换算优劣。

结果111–124/Table2–3：T1-39 Dice .88，监督T1/nnUNet .91；真实FLAIR .78，对SAMSEG .64。1→7mm spacing平均降低3.8 Dice points，皮层等薄结构仍退化。5000扫描的结构分割不证明小病灶完整保留。分辨率/对比度分布收窄的变体反而下降；额外自动标签提升形态泛化。作者138明确各种lesion/tumour的定量性能仍待研究。WM lesion模拟主要让正常结构分割对病灶稳健，不应把发布brain模型称为已认证VS检测器。

对项目的改变：若native对照也失败，下一步可研究「符合物理尺度/协议的任务表征」，但域随机化本身已被占位。不能直接用SynthSeg替换失败VS checkpoint，再按有利任务救原主比较；解剖结构任务与VS人工label不是同一端点。新模型需独立合同、来源/语义审计和完整未见患者确认。

## 轴位T2脊髓MS病灶：更多3D上下文和预处理未必改善任务

*Automatic segmentation of spinal cord lesions in MS: A robust tool for axial T2-weighted MRI scans*，2025，DOI [10.1162/imag.a.45](https://doi.org/10.1162/imag.a.45)。[正文](source_cache/predicted_region_fulltexts_2026-10-03/axial_ms_2025_maintext.txt)，0–120全部提取正文/表格/图注实际核读。模型公开集成SCT，但原私人队列不公开，不能称已复现训练。

数据11–22/43–51：四中心582患者；TUM317人、每人两个时点和三脊段，另NYU153、BWH80、UCSF32。TUM按患者80/20划分，254开发/63测试；126是测试时点扫描，不是126独立患者，正文49的「126 patients」与43/51不一致，报告按明确患者划分处理。两个时点不能算独立研究样本。NYU加入训练，BWH/UCSF保持未见。TUM预分割后人工修正，外中心病灶人工标注；标注机制不完全同质。

方法25–35：比较raw chunks、stitching、straightening及两者结合。Stitching在scanner世界坐标对齐并resample/blend，未使用额外registration；straightening使用cord mask和warp，label线性插值后.5阈值。nnUNet v2 region-based联合预测cord∪lesion和lesion，Dice+BCE；2D对自动配置的2D/3D混合kernel，1000epoch、3fold。骨干/patch会随数据版本自动变化，作者118承认不能把各差异全归因单一预处理。全脊髓更大patch没有显著改善。

结果72–96/Table2：2D raw chunk多数不劣于3D/stitched；straightening反而较差。两中心模型TUM Dice .62、BWH .51、UCSF .53；single-site对应.60/.45/.52。外中心two-site相对single-site改善没有显著性，不应把所有均值提升都称显著泛化。小于10mm³病灶仍难，10–50mm³约60%检出，更大病灶约90%；这些是该病种/评价匹配准则下的数据，不能预测VS表现。

评价53–61/111–112保留无病灶病例，GT/pred都空时Dice=1；逐chunk等权与整patient堆叠计数得到不同estimand。图4混称Recall/F1，按明确展示的Recall计数理解。Table2注释将NSD与count error最优值一起写0，但NSD通常越大越好；不据该笔误改变表内原值。当前项目保留空目标的ROI成本、patient内系列等权，须清楚说明其分母与这篇不同。

对项目的改变：native任务能力必须先测，原发布模型在其他协议失败是可发生的，但不能仅凭文献就给当前失败诊断病因。纯2D真实anchor病灶区域表示可作为以后新开发路线，然而该机制已有直接先例；不能凭添加2D头称新方法。任何低分辨率robust task predictor必须保留小病灶、失败和整patient split。

## FGAS：基础模型伪标签、跨平面一致与连接正则已有组合先例

*Reconstruction from multi-planar MRI with foundation models for uterine fibroid analysis*，2026，DOI [10.1038/s41746-026-02780-6](https://doi.org/10.1038/s41746-026-02780-6)。[正文](source_cache/predicted_region_fulltexts_2026-10-03/fgas_2026_maintext.txt)，0–94方法/结果/讨论与四表实际核读；95–97补充材料入口未读。为了可读，工具输出省去重复LaTeX序列，保留紧随其后的公式扁平表达；不声称已视觉核查公式。

流程65–93：source nnUNet生成initial masks；由它们的bbox和连通成分centroid自动生成positive prompts给nnInteractive，再用refined与initial的Dice≥.5筛查，并保留LCC。以伪标签微调task模型；跨views softmax MSE、TV/volume-normalized compactness及foreground centroid Gaussian加权约束。σ=5等按经验/grid search确定。这里「differentiable connectedness」是形状代理正则，公式并未给出严格拓扑不变证明；centroidGaussian/LCC也不保证保留多个真实病灶。预测彼此同意不等于它们与真实label一致。

来源12–13：public source300 sagittal sequences（270训练/30source测试）；private620人/1853多平面T2，100人/300scans人工标为final test；method68另写67人/201scan、20epoch target微调。ablation41写50测试/30epoch，和主配置不一致，不能合并为同一统一实验。论文13同时说统一世界坐标、正交图像来自同一个volumetric scan，35又讨论不同views运动misalignment；当前正文不足以认证每个view都提供独立真实采集信息。不能把其multi-view数直接当额外观测对照。

Table1：source-only mean39.8%，FGAS70.6%，fully labeled target-only73.5%；Abstract中的baseline42.8与表不一致，报告依具体表。Table2与ablation支持组合机制；但grid-search的独立validation角色和上述数据使用细节未由已读正文完整认证，不自行补全。Discussion56报告小于5mm的26人性能下降，仍不能把论文宣称「无complete miss」变为对本项目的保证。

对项目的改变：基础模型指导、pseudo-label refinement、跨view loss、connectedness penalty组合也不能当首创。当前项目仅同一稀疏volume的重切视图时不增加真实观测信息。若将来研究「病灶保护的局部修正」，要保留所有真实病灶成分、区域面积预算、错误ROI反证，和已有形状/任务/动作风险强对照；不能用平滑/连通性看起来好代替原生像素和完整任务真值。

## 收窄后的候选与下一步

目前三篇新正文都排除了宽泛模块首创，未证明可发表新方法。剩余可探索问题是：在真实稀疏观测可定位但边界不确定时，是否能识别并禁止对病灶有害的局部修正，同时在完整缺层获得重建收益。它必须超越既有SafeRestore动作风险、MoEDiff区域专家、普通误差头、固定alpha、预算匹配随机和task-feature对照。旧线性收益/误差等价与旧岭失败继续保留。

先执行[16系列native能力对照](../MC_RC_NATIVE_COMPETENCE_CPU_PLAN_2026-10-03.md)。若native和sparse都无足够定位能力，当前checkpoint提供的ROI停止，不能据此否定所有观测区域表征。若native较好而sparse失败，新方向也首先是representation/采集稳健性的研究准备，而非已有成功claim。真正未用于设计、窥见或拟合的确认患者仍0；原45人固定VS-SEG完整任务主分析仍需等待全部独立核验完成。
