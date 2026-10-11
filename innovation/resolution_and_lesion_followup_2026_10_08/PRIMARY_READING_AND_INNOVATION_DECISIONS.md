# 本批结论：支持不足须先解决，形状合理性不能替代动作收益

本批核读两篇不同原文：GOUHFI 2025、claustrum SynthSeg 2025。三组索引返回 15 条（含重复/非 MRI 任务），不是系统综述。FastSurferVINN 与病灶级集成原文 HTTP 500，未计正文；替补来自已取得索引。上一批 VS 临床工作流和内耳标签保护两篇的归档已接续完成，累计 6111 份证据。

## GOUHFI：高分辨率输出和病灶真实性需要不同证据

[GOUHFI: A novel contrast- and resolution-agnostic segmentation tool for ultra-high-field MRI](https://doi.org/10.1162/imag.a.960)，Imaging Neuroscience，PMC12556684，索引 firstPublicationDate 2025-10-24。实际 XML SHA256 `3f7d71f1c80f186407009d20fb6c600b70d16e56e86891c724a87515992f12da`。逐段阅读科学正文 blocks 0–145、其余提取 blocks 146–174；7 张表所有提取单元格已核。包含主 XML 的 Appendix A.1/A.2 及 A.3 图注；未查图像像素、外部参考全文或作者实现。

206 个训练来源 subjects：HCP80、SCAIFIELD31、UltraCortex15、ABIDE80（34+46）。5-fold 中每折 80% 训练、20% 验证；训练用 label map 生成的 synthetic，验证用真实影像：HCP T2、SCA PD、其余 T1。FastSurferVINN v2.3.0 生成 35 类标签；UHF 标签经 QA，UltraCortex78 人中只取15用于训练。**合成图像和伪标签一致，不等于伪标签符合真实病理解剖**。原文也承认健康训练下扩大脑室导致海马过分割，病理泛化未完成。

生成器沿用 SynthSeg：bias 上界 .6→.9、关闭随机降采样、保留 submillimeter 原生生成；这与另一篇“主动随机降分辨率”策略方向相反。论文只同时改变多个因素，没有同架构/同预算隔离实验，不能证明禁用降采样必然造成改进，也不能推出本项目一律启用或禁用降采样。Appendix A.2 记录 rotation ±20°、scale .8–1.2、translation ±30 mm，downsampling 参数 None。

nnU-Net v2.4.1 residual large，6层，32/64/128/256/320/320特征、192×192×160 patch、batch2、Dice+CE；关闭默认增强。外部统一到 .7mm，image cubic spline、标签 one-hot linear，推理后回原空间。每折500epochs×250 minibatches=125000更新；五折共625000更新，A40 48GB约6天，五模型softmax平均与按验证结果选largest-component后处理。不能把本项目额外2992更新称相同充分训练，不能移植 LCC 到多病灶 VS 合同。

HCP20及SCA-T1 10用 FastSurferVINN silver reference；SCA-MPM用SynthSeg reference，MTw仅4例。Glasgow21是11受试者的21次扫描，对照 iGT。UltraCortex12有经人工修订/专家审核的WM/GM，只有两类且子组8/3/1；不能称35类完整独立手工GT。MPI28和HBA1主要是定性评估；HBA .25mm由同一受试者11次 .4mm scans重建，不是原生 .25mm单次采集。

例如HCP-T2 median27类 DSC .89 对 .87，但小脑 WM .85 对 .87、皮层 .89 对 .91，非所有结构改进。Glasgow median .88 对 CEREBRUM .91，亦不支持普遍领先。STRAT-PARK24 PD/21HC只有putamen达到原Bonferroni阈值；跨组体积差不能替代个体GT或病灶修正收益。Table2/3/4多处CI与median不包含/上下界倒置，主XML式1还写 `∪` 而非Dice的 `∩`；结论把六对比度/七分辨率写反。保存原值与限制，不依这些异常重算显著性，不复制错误公式到本项目。

作者据另一篇 VINN 讨论 external/internal scaling 的结果，不等于本次读到了 VINN 主文。作者代码链接：[GOUHFI v1.1.0](https://github.com/mafortin/GOUHFI/releases/tag/1.1.0)，未取得/执行。

## Claustrum：无GT QC、跨模态一致性与真实准确率分开

[A Contrast-Agnostic Method for Ultra-High Resolution Claustrum Segmentation](https://doi.org/10.1002/hbm.70303)，Human Brain Mapping，PMC12368599，索引 firstPublicationDate 2025-08-01。实际 XML SHA256 `eb876db202b789b50c20c511f7dc7746c593a5ef9f57d3f0964cc653845ebdee`。主文 blocks0–85及 supporting metadata86–87、3张表完整核读；另外读取主XML back中的Appendix A/B。外链 `HBM-46-e70303-s001.pdf` 尚未取得，图像像素与作者代码未核。

是薄片状 claustrum 解剖分割，不是 VS 肿瘤。15 ex vivo samples+1 in vivo scan，共18 hemispheres（12左/6右），Table1是16来源，不是18独立患者。每5层手工标注、SmartInterpol补中间层、逐层/3D审核修订；周边label来自SynthSeg，训练时相邻组织强制WM。不能照搬“补的label就是完整独立真值”。CV写12 subjects/3 validation images/3 test images，但18 hemispheres来自16 sources；主文未完整给出供者身份分折，不能认证跨供者完全独立。

标签裁到56mm、.35mm/160³、左翻右。SynthSeg heavy affine+diffeomorphic label augmentation、GMM intensity、bias/normalization/gamma/smoothing/downsample/up；isotropic resolution U(.35,3.5)、anisotropic U(.35,5)。3D U-Net5层、两3³卷积每层、softDice、lr1e-4、batch1；每fold100epochs=500000steps、6fold，选择真实验证Dice最优epoch。最后全18训练100epochs约7天RTX8000，再在20 IXI上用QC选第19epoch；100epochs预算与被选epoch实际曝露不能混为一谈。

Appendix B：bias后、归一化等后续处理前，95%概率加入独立Gaussian，sigma U(0,100)，是生成器强度单位，不可直接复制到本项目已标准化MR。单fold配对 with/no-noise 的IXI平均QC .555/.490，**不是真实GT Dice、不是六fold训练消融医学确认**。Appendix A确认robust HD为95 percentile；VS=1−|VA−VB|/(VA+VB)，不是本项目absRVE。

CV Dice .632±.061，TPR .676、FDR .381、HD95 1.824mm、MSD .458mm、VS .867；rater Dice .805，模型尚有准确率差距。下采样实验约1.4mm以内变化小、之后更差，不能支持“任意分辨率”无损。

测试FoV通过SynthMorph配准和概率atlas阈值 .001定位，60mm ROI后重采样.35mm；atlas由所有18label建立。CV时atlas也是否折内重建，主文没有明确；需作者实现核查，不能静默认作无GT外部定位。原文也明说中心crop有shortcut风险。

QC是在MNI中将预测与18reference labels逐一比较，取最大Dice，度量 plausible anatomy；作者明确它不是subject-specific准确率。IXI581没有逐人GT，且含选epoch的20人，不是581例全独立未见确认；只检查最低QC50及最小/最大volume各20（重叠人数未给），不能认证全部581例“无严重错误”。扫描场强组QC无显著差异也不是等效性证明。

Miriad69原受试者，缺失3/配准失败5排除后61（40AD/21HC），test-retest .781是同模型一致性，不是GT准确率；FSM T2/T1 .720、PD/T1 .696、qT1/T1 .809同样是跨模态一致性。完整失败分母应保留。主体分割约3分钟/16CPU，含nonlinear QC约10分钟，同机多约7分钟；不能转作本项目实测成本。作者链接：[claustrum segmentation](https://github.com/chiara-mauri/claustrum_segmentation)，未执行。

## 实际探索和创新候选

[support synthetic receipt](support_synthetic_attempt01/receipt.json)真实 7a449b exit0，4.473秒：16个非医学生产尺寸case、32点两级独立强度oracle最大4.336e-8、物理坐标5.684e-14；constant/linear全目标体素检查通过，GT/源数组位级不变。中心/偏心 crop-only constant mean .964442/.591549、边缘min0；真实上下文版mean/min均1。可是checker/wide仍有最大 .55/.66幅度变化，说明信息被平滑；这不是无损插值、不是患者效果。

保守source包围盒约7.56/7.63倍target体素、intermediate约1.72/4.22倍，不是耗时倍数，实际训练成本尚待测。原型上下文不足直接报错，不用反射/复制边缘伪造组织。

[开发几何receipt](development_geometry_attempt01/receipt.json)真实02f3f5 exit0，0.138秒：11患者19series、38旧batch、76patch plans，两输入38对完全匹配；0个保守支持box可全放入fullFOV。60个plan有正权重邻居越出fullFOV直接证人（30个独特配对patch）；余16仅未找到角点证人，不能判定支持够。source box5.53–7.82倍。仅读旧开发元数据，新增MRI/GT/model数组及forward/updates均0，不是新患者医学证据。

| 候选 | 与已有方法的区别需要证明什么 | 当前状态 |
|---|---|---|
| 优先：合法观测条件下预测具体修正的病灶损害变化与全费用 | 在充分能力raw/direct/强增强及QC-error-defer控制后，支持/可见性特征能提高真实paired动作选择收益，并在patient-fold外与8未见确认成立 | 研究问题；未训练收益头，未确认新颖性/患者收益 |
| 基线先做：支持充分的图像退化、原位标签训练 | common target曝光和同parent/schedule预算下，区分人工FOV边界损失、普通low-pass正则与任务能力提升；halo本身作为实现保障 | synthetic通过，真实边界支持不足已记录；不修改当前四臂 |
| 次优先：形状QC很高但修正伤害仍大的病例识别 | 对强几何/概率QC加入合法采集可见性，预测actual action delta而非漂亮形状或高一致性；量化defer全成本与病灶漏检 | QC已有直接先例；需开发外actual actions，暂不宣称首创 |

不建议直接写成“新loss/新路由头/分辨率无关插值/标签不变增强/几何QC”论文，这些层面已有明确先例。下一具体实验见 [准备](NEXT_TRIAL_PREPARATION.md)。
