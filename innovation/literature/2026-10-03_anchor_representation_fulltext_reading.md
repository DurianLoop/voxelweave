# 三篇稀疏标注/轮廓正文：与稀疏采集的输入差别

本阶段四条固定查询返回47条索引记录，年代补查再返回8条，共55条响应记录，含重复及无关分类工作；不是55篇全文。实际新增阅读三篇公开正文、正文相关序号256段（包含重复图注、标题和表格），新增PDF为0。两篇EFetch只有front/abstract，注释说明不提供XML正文，保留失败；随后正常公开PMC HTML取得对应正文，未绕过访问控制。第三篇取得DOI一致的JATS。没有下载/读取补充、没有视觉审阅图像、没有复现训练或逐式核推。必要被截断段落已经另读。

[检索合同](2026-10-03_anchor_representation_search_plan.md)、[选择及年代补查](2026-10-03_anchor_representation_fulltext_selection.md)、[初始原响应](source_cache/anchor_representation_search_2026-10-03/attempt_01.json)、[EFetch/年代补查](source_cache/anchor_representation_fulltexts_2026-10-03/attempt_01.json)、[正常HTML获取](source_cache/anchor_representation_fulltexts_2026-10-03/html_alternate_attempt_01.json)。

| 正文 | 实际核读范围 | 已有机制 | 本项目不能偷换的条件 |
| --- | --- | --- | --- |
| Payer等，Medical volume segmentation by overfitting sparsely annotated data，2023，DOI [10.1117/1.JMI.10.4.044007](https://doi.org/10.1117/1.JMI.10.4.044007) | [公开HTML段落](source_cache/anchor_representation_fulltexts_2026-10-03/sparse_overfit_2023_html_maintext.txt)25–109，85段 | 每volume新模型、仅部分标签监督、规则Keep_n/SSIM选slice、MITK距离场/cubic和Slicer morphology已有 | 稀疏的是标签，模型对未标注层仍取得真实影像；自己的观测缺层MR不可得。每病例稀疏人工标签不是现有MRI-only部署输入 |
| Zhao等，Contour interpolation by deep learning approach，2022，DOI [10.1117/1.JMI.9.6.064003](https://doi.org/10.1117/1.JMI.9.6.064003) | [公开HTML段落](source_cache/anchor_representation_fulltexts_2026-10-03/contour_interpolation_2022_html_maintext.txt)23–118，96段 | 两侧manual contours+中间影像、浅3D U-Net、局部patch、形状/强度结合已有；两anchor间三个目标也已有 | 输入含全部五真实CT层；预处理由真值器官范围决定crop。不能把中间真实CT输入或各层真值crop搬到稀疏MR |
| Zhuang等，Efficient contour-based annotation by iterative deep learning for organ segmentation from volumetric medical images，2023，DOI [10.1007/s11548-022-02730-z](https://doi.org/10.1007/s11548-022-02730-z) | [JATS段落](source_cache/anchor_representation_fulltexts_2026-10-03/iterative_contours_2023_maintext.txt)0–74，75段；75–77补充入口未读 | 2D contour表示、多尺度、CNN vertex deformation、FFD人工调整、SDF二阶插值及迭代监督已有 | 主要是有强shape先验的腹部器官，完整影像可看、人工修正可迭代。形状平滑或正确topology不能认证未知不规则病灶，也不认证MR局部动作风险 |

Payer正文57–70清楚说明2D预测器及每volume训练。BraTS19 T1ce实际用12/259 volumes，经PCA+k-means选择；MSD-Heart用7/30，FLARE21用6/360并按slice数选择。不能把259/360全量或三个任务说成大量未见患者确认。网络用ImageNet/Instagram初始化，超参在12代表volume上sweep；不是完全无先验。从Table4的12.5% Keep_n看，U-Net/MITK Dice为.943/.948；50%为.984/.993，简单插值在这任务胜过网络。BraTS19 20% MAnet .874，50% Keep_n .915。这些是各自任务均值，不能预测当前VS区域覆盖。作者数据段称left ventricle，图注称left atrium，保留语义不一致；随机crop段IoU .1587/.1087与表注 .01587/.01087相差十倍。讨论“up to30min”与Table7 FLARE21 88.47min也不一致；不移植其速度承诺。论文的domain agnostic判断不是当前无标签来源泛化的实验证据。

Zhao正文34–61：1174 datasets、19963 patches、840 validation、3167 testing；Table1各库422+450+130+82+190实际合计1274，与正文1174不一致，保留分母疑问。第46段明确同患者同器官patch不跨training/validation，但这句话不足以认证整个患者所有器官及test完全隔离；不自行认定泄漏已发生，也不称whole-patient拆分已充分认证。每器官真值crop加10pixel平面内和2pixel纵向margin，再resample128×128；本文数据条件比我们的full-FOV观测输入强。浅3D网络真实五层影像+仅两端mask，不能因为缺三个mask就称缺三个MR。Table2全体Dice .95对SBI .94，挑选的286 difficult patches .91对.86；不是286独立患者。brainstem新器官两者.92且p=.09，不能将全部新器官差异都写显著。作者自己的MBI/MBILII实现可能非最优，7slice大差异案例仍会失效。Table3胃3D均值.79对.97，但列差-.01，不符合两展示均值简单相减；不修造原数据。

Zhuang正文35–37：腹部CT20 volumes，四fold，5初步train、10新增proofread/retrain、5test；两操作者记录人工时间。16.19±2.58分钟/volume对29.79±3.50，来自该人工任务，不能作为当前无人工输入部署预算。还试胸片704 images（21train）、心脏超声88 images（66train）、肺肿瘤CT64 volumes（16train/48test四fold）；未由本文段落逐项证明image均是不同患者。正文72直接承认不规则肿瘤可能更适合voxel表示、训练中未见的病灶扭曲形状仍会失败。故“更光滑/更一致”不可当病灶保护证明。其SDF二阶插值和boundary/shape多尺度不构成本项目独立新意。

年代补查的RFDCR（DOI10.1016/j.neuroimage.2020.116620）目前仅索引/摘要；森林分割与CRF有直接先例，未取得/核读其正文，不拿它的细节作已认证结论。其他radiomics分类与分割不同，未作为逐pixel模型复现证据。

对当前方向的决定：新增论文进一步排除“真实anchor监督/2D表征/距离场/形状传播/少量label训练”宽首创。尚可研究的问题仍是**真实稀疏观测能否识别病灶局部有害修正，同时取得完整缺层重建收益**；差异在可观测信息、动作约束及公平实证，不能只是网络模块表。当前[轻量QDA/LDA合同](../MC_RC_ANCHOR_QDA_CPU_PLAN_2026-10-03.md)是计算可用的表征诊断，九通道joint主模型固定，另外三个解释对照保留。它不添加scikit-learn、不改环境、不用GPU；若区域几何好，也仍须真实重建收益、SafeRestore/误差头/fixed-alpha/预算随机强对照及真正未见患者确认。旧岭失败、线性坐标等价、旧checkpoint失败都不被它替换。
