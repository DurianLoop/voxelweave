# 三篇新主文与创新边界

本轮新增实际核读三篇不同论文的主文，共414提取块：Borges 213、AMDU 139、Bézier 62。提取块包含标题、摘要、正文、公式文字、图注、部分声明；不等于414独立段落/实验。Borges与AMDU的11表在正文核读，Bézier另读5表全部结构化行；Borges表4另核结构化行。原MathML仅定向核Borges式1/2和AMDU式4，其他公式主要读文字表达，不冒充全面排版核验。未读图像像素、独立补充材料、参考文献全文、作者源码或publisher PDF，未执行作者模型。来源与具体实际工具绑定见READING_PROVENANCE.json。

## 1. 采集参数输入、UQ与模拟扫描选择已有直接原文

[Acquisition-invariant brain MRI segmentation with informative uncertainties](https://doi.org/10.1016/j.media.2023.103058)，PMC7617170。索引首次发表2023-12-07，期刊卷年2024；当前PMC含EMS198236作者稿标识，不假定排版与publisher final逐字一致。

正文38直接把sequence参数通过两个FC层送到编码和末端feature；41把同患者同patch的多contrast组成batch并加feature一致性约束；53把MPM→静态MPRAGE/SPGR生成改为训练时augmentation。使用R1/R2*/PD quantitative maps与GMM生成的GM/WM/CSF软PGS，27患者、18/4/5划分、5fold；不是肿瘤手工GT或本项目单轴CISS抽层×4的前向模型。

它已经实现了“采集信息+分割/UQ”“按采集参数探索task uncertainty”宽思路。正文163–169用模拟参数网格与校准volumetric uncertainty检查sequence选择，且明确不是代替真实扫描优化；无noise-model导致低信号SNR影响未建模。不能把我们的metadata/UQ组合或测量参数建议当宽泛首创。

Table2尤其限制增量假设：SPGR GM的Strat-Aug Dice IoD/OoD为.936/.920，加入参数支路的Phys-Strat-Aug为.930/.913；WM为.935/.897与.921/.899。参数输入不是各组织/分布普遍更好。正文145中不含显式参数的Strat-Aug年龄回归最好，179也认为多contrast augmentation是更主要成分。因此必须在充分普通增强后验证合法采集feature的净增量，而不是只比单contrast弱baseline。

真实外部验证范围：ABIDE组织分割以SPM输出作参照，不能升级为手工病灶真值；ADNI 1233图像用于scanner比较，PSACNN另用ADNI pseudo-parameters重训，信息和训练预算并非完全相同。其50MC样本、按验证数据校准组织volume bounds也不直接给CISS病灶recall保证。正文128明确为保持contrast与参数关联而省去gamma，说明普通强度增强与condition信息一致性需单独检查，不能无条件拼装。

当前XML保留的待核差异：正文118称11 sites/614相关图像，表4只有10个site rows且两行均写UCLA1；不自行补行或从表重建最终纳入队列。正文91的SPGR参数向量含exp(-TI)，与该sequence参数列表不同，作者源码未核。式1/2的负pair-L2在普通最小化时与拉近feature的描述相反；仅字面版本诊断，不推断作者实际训练错误。

## 2. 域遗忘是已知强控制，敏感度与FP须同时评价

[Adaptive multi-stage domain unlearning for white-matter lesion segmentation](https://doi.org/10.3389/fmed.2026.1875760)，PMC13474016，2026-07-31。

FLAIR-only nnU-Net默认包含空间、gamma、noise、blur、低分辨率模拟与mirror；在多个encoder阶段增加scanner-domain classifiers，先warm-up，再按classifier accuracy/patience触发unlearning。40源患者中32train/8val；另50 WMH unseen scans用于选stage/schedule，之后不再作为独立测试。外部MSSEG/MSLJ/ISBI共103scans与60seen WMH用于最终评价。不是“目标域标签完全从未参与任何开发”：50 WMH源外样本参与了配置选择，但三个最终外部域未参与，需区分开发域与独立域。

默认nnU-Net与AMDU的MSSEG Dice .588→.635、TPR .479→.563，同时LFDR .281→.384；MSLJ Dice .523→.574、LFDR .151→.273；ISBI Dice .609→.674、LFDR .154→.203。不能概括为每项病灶安全指标均改善。全部六stage遗忘在Table2 Dice仅.629，深stage4–6 adaptive为.715，支持“抑制哪部分信息”必须验证，不能把全部采集信息删除当理所当然。

Table5外部方法是文献结果，不是同流水线重训，input modalities、训练样本、target supervision均不同；LST-AI在MSLJ Dice .743高于AMDU .574。本文的域遗忘组件、adaptive schedule已有先例；我们的task-side suppression/metadata gain branch不能仅凭结构组合声称首创。

正文96/98/128以低RVE解释FP较小，但式9只计|Vpred−VGT|/VGT。实际CPU反例显示GT100/pred100、TP50/FP50/FN50时absRVE=0、Dice/recall=.5：低体积误差不能独立认证低FP。作者同时报告其他指标，反例不否定其完整实验；它要求本项目继续保留独立FN/FP、recall、病灶检出和signed/abs体积端点，不把volume metric当安全替代。

当前式4是负KL；普通最小化时uniform不是最优，但正文另提gradient reversal。执行作者实现前需核实际gradient路径，不能仅凭符号断言作者代码相反。domain classifier接近chance也不认证latent所有scanner信息都消失。

## 3. 区域对比度增强是应加的普通控制，当前配置仍不足以精确复现

[Region-Wise Bézier Intensity Augmentation for Domain-Generalized Brain Tumor Segmentation with a Mamba U-Net](https://doi.org/10.3390/jcm15145508)，PMC13413108，2026-07-14。

233患者/3064个contrast-enhanced T1 2D slices；患者5fold且内部val也按患者分离。训练GT仅用于foreground/background分别取曲线的式2，不送网络、不用于目标域推理。使用ImageNet-pretrained encoder、256²三通道复制，与本项目3D CISS网络/冷初始化不同，不能直接借其.896 Dice作为能力门槛。

应用概率.5、monotonic比例.5、偏离identity上限.5；同backbone消融：no aug .854、geometric .869、global Bézier .881、region .896；外域均值.700/.726/.757/.783。两外域指BRISC去重与BraTS-2D，不证明真实厚层CISS/任意phase泛化；external病例数、具体BraTS release/slice选择等未在读到的主文充分列出。训练期禁用增强使推理架构成本不变，不等于训练准备成本为0。

原文提及可平滑窄boundary band，但没有在已读主文给确切sampler分布、非单调x→y inversion约定或band宽度/实际是否启用。Table3 A3/A4同时勾global和region，正文40称“replacing global”，保留差异，不能自行决定为只region或两次叠加。没有核作者代码，因此只准备合法适配，不叫精确复现。

实际CPU固定单调曲线toy：常数输入.5，foreground输出.725/background .275，mask边界出现.45跳变，.5阈值可在该fixture准确恢复mask；global同曲线没有边界。Bernstein与展开多项式误差0，标签几何不变。说明label-aware强度增强可能创造额外边界信号，需做hard-region/明确seam平滑/global匹配控制；使用训练GT本身合法，不能由这个toy宣布论文泄漏或网络实际利用shortcut。

## 当前保留的创新候选

| 优先级 | 待证伪的具体主张 | 现阶段判断与必须完成的控制 |
| --- | --- | --- |
| 1 | 充分3D任务训练和普通分辨率/对比度增强后，合法观测采集信息能否改善具体SR动作的患者级病灶净收益选择 | 仍是核心MRI实证假设；必须超同信息同容量action-risk/QC/defer、去采集feature、metadata-only、static/always/random和全费用控制，尚无独立确认 |
| 2 | 在实际paired动作结果中保留跨体素/跨动作依赖，能否比边际volume-UQ更好约束FN/FP损害 | CPU仅证明边际分位数之和与总体积posterior不同；计算正确joint统计或已知期望效用规则本身不是新算法，须真实动作标签与严格患者fold |
| 3 | task侧泛化抑制与action侧合法采集信息分开使用是否有增量 | physics-conditioning、domain-unlearning均已有先例；需要强增强、参数branch、unlearning、同容量组合与去信息完整factorial，不能靠组合命名称新意 |

病灶区域强度增强、support/reliability输入、低分辨率模拟与Bayesian效用均优先作为强对照。若它们消掉动作余量，保存负结果并收缩claim，不把普通增强换名当创新。原开发Dice约.861–.881、已见验证.463–.522支持优先泛化诊断，但不同患者队列不是单因素因果证据。8未见确认患者12series及lockedIXI仍关闭，原六医学门槛不变。

本轮5项CPU准备诊断真实2e2bbd exit0，全部synthetic；没有新增患者MRI效果、作者模型复现或发表确认。[完整反例](cpu_diagnostics_attempt01/receipt.json)与[下一尝试准备](NEXT_TRIAL_PREPARATION.md)保留所有适用限制。
