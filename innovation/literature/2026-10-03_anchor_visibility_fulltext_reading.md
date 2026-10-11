# 新增两篇正文核读与本项目的具体边界

本阶段新增取得并核读两篇JATS正文，不是新增PDF。固定三条索引查询返回29条记录（15+0+14），正文获取2/2成功。正文、DOI、许可及hash见[下载索引](source_cache/anchor_visibility_fulltexts_2026-10-03/attempt_01.json)。分块实际读完113和39个提取段落，包括Methods、Results、Discussion、表格及图注文字；没有取得补充文件、没有逐幅视觉检查这些新文章的图，不声称复现训练。索引中Hsu2026等仍只读摘要。SafeRestore第5页与MoEDiff-SR第4页另外复看此前保存的渲染图，新增获取为0。

## Giraldo等2024：PRETTIER，真实切片profile及冻结病灶分割已有直接先例

*Perceptual super-resolution in multiple sclerosis MRI*，DOI [10.3389/fnins.2024.1473132](https://doi.org/10.3389/fnins.2024.1473132)。[正文](source_cache/anchor_visibility_fulltexts_2026-10-03/ms_perceptual_2024_maintext.txt)。

正文19–33/Table1：192位MS患者、429个HR结构MRI，来自6个来源。学习为163人（204 FLAIR、140 T1），独立评价为29人（15 MSSEG1 A、14 HUN），后者含43 FLAIR/42 T1；HUN有同一人的两次访视。学习内train/validation按各来源的image sessions随机7:3划分，已读段落未认证每位纵向患者都保持整人分组，不能自行补充该保证。评价来源与学习来源独立的配置仍是实质强项。前处理包括非局部均值去噪、N4、HD-BET及1mm统一空间，不能直接当未经处理的原始像素性能。

正文35–54：明确采集模型`y = D B R x`，厚度5mm、spacing6mm、1mm gap，三种正交方向。它使用slice profile模糊而非只抽掉plane。fine-tune EDSR与RealESRGAN，VGG19五层perceptual+L1，后者还有GAN项；3个相邻面片映射为3通道，两个面内方向滑窗并平均得到体积。100epoch、Optuna按验证content loss选参数与最优weights；本轮未复现。不同方向输入只是同一个LR体积的面内重切与模型应用，不应误读成额外真实正交采集。

正文66–74/Table3–4：比较SMORE、SOUP-GAN；在相同重建后的FLAIR上应用公开LST-lpa和SAMSEG，同时评LR与HR，另将直接LR→HR分割的WMH-SynthSeg纳入对照。PRETTIER-EDSR的体积FLAIR PSNR为25.5±1.4dB，SMORE24.6±1.3。LST-lpa Dice为LR .47、EDSR .53、HR .58；SAMSEG分别.41/.47/.53。前述Dice是对手工病灶真值，HR自动分割只是参考表现，不是数学上绝对的性能上界。Table4没有同一完整病灶评价下的raw/pipeline PCHIP列，也没有本项目保留真实phase0观测的完整缺层合同，不能把不同实验数值直接换算为本项目优势。

正文95–110：论文已分别考察precision、recall、体积误差，讨论边界改善、生成纹理、真实采集profile和只测试一个任务的限制。图3文字直接描述LR中病灶边界丢失，不能因本批VS主要标签成分接触观测层，就说所有病种均不受抽层损害。

对创新的约束：首次MRI perceptual/多邻片/跨方向/物理profile/任务分割评价均不成立。可以研究本项目固定真实稀疏输入、病灶边界动作与强PCHIP的关系，但更多模块和更完整评价本身没有证明新方法。若要真实厚层泛化，必须把观测模型profile/gap固定后实际验证，不能把当前thin3D抽层称厚层采集。

## Haeusler等2023：层厚与真实小病灶检出的临床证据已有先例

*Detection of brain lesions after catheter ablation depends on imaging criteria: insights from AXAFA-AFNET 5 trial*，DOI [10.1093/europace/euad323](https://doi.org/10.1093/europace/euad323)。[正文](source_cache/anchor_visibility_fulltexts_2026-10-03/axafa_dwi_2023_maintext.txt)。

正文10–16：AXAFA总体674人，333人做MRI、12扫描不可分析、321人进入本子研究。25中心，在消融后3–48h同患者先标准5–6mm DWI、随后2.5–3mm hrDWI，后者多耗时30–90s。两位核心实验室专家独立阅片，声明对临床/随机治疗/场强/层厚信息盲法；但作者承认片数不同，盲法不能完全抹去可见采集差异。1.5T52人/3T269人并非同患者交叉场强试验。

正文20/Table2：hrDWI为84/321人检出至少一处、共165处；标准为60/321人、104处，论文P<.01，更多hrDWI病灶体积≤50mm³。这里是两个真实采集的阅片检出数，没有外部无误的独立病灶真值、没有SR或固定自动分割，不能把差值直接称确定的true-positive敏感度或本项目四倍模拟的效应。

正文25与Table3存在报告不一致：段落写268位3T及68人28.6%，主分母/Table3是269且68人25%；本报告用主321与表格，不修造患者级数据。正文35明确该子研究未专门为厚度/场强差异power设计，无消融前MRI、只有一次术后时点，不能排除更早病灶；coil/vendor等其他采集参数不能完全调整。统计未作多重检验校正。没有取得补充TableS2，因此不能声称除了厚度之外所有协议参数完全相同。

对创新的约束：首次证明薄层改善小病灶检出、首次强调厚度不能由spacing替代均不能成为本项目宽泛贡献。本文需要真实增加观测和扫描时间，而当前项目仅保留同一thin3D体积每四层之一；标签接触稀疏plane既不等同MRI可视性，也不能当真实厚层认证。

## 与本轮CPU证据连接

[固定15系列标签诊断](../MC_RC_LABEL_ANCHOR_VISIBILITY_PLAN_2026-10-03.md)主phase0未发现完全隐藏的26邻接成分，4phase的最大成分全部接触观测层。010某一系列在phase1/2/3有一个48体素小成分无观测接触，主phase0无；这只能作预写相位敏感性，不改主结论或把小成分称独立临床肿瘤。

这项反证将下一假设从“病灶完全无观测”收窄到“有观测接触，但区域/边界的可见表达能否识别局部有害修正”。真实标签只能用于开发监督与诊断；部署ROI需来自真实稀疏输入或冻结预测。SafeRestore已有动作特定风险与双端点，MoEDiff-SR已有区域专家门控，分割区域UQ与任务指导亦已有先例；仍需同容量误差头、固定混合、随机/面积预算和未见患者完整任务确认。
