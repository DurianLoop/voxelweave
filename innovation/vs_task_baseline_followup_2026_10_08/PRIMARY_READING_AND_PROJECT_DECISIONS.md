# VS/T2直接先例：能力基线、插值增强与完整费用

新增实际核读两篇不同原始研究的期刊公开XML主文及主表。43/20总命中的两个查询各只返回8条，有重复；不把16条索引计成16篇全文，不称系统综述。已有crossMoDA2026、Kujawa2024 MC-RC、2025VS cascade等明确去重。新全文原fetch因题名Unicode连字符严格断言失败，保留1de6d5 exit1；两XML已经取得，991f9d local-only资格归一标点核DOI/PMCID，零新增GET，不把原失败改成成功。

本轮所有创新判断仍以本项目能力/公平控制/未见确认为前提，没有已确认可发表claim。普通增强、局部细化、QC/拒绝、体积测量或临床工作流分析都有先例。

## 临床VS报告研究：高internal Dice不保证外部每例免修订

[Artificial intelligence for personalized management of vestibular schwannoma: a multidisciplinary clinical implementation study](https://doi.org/10.1093/jamiaopen/ooaf163)，JAMIA Open，索引firstPublicationDate2026-01-06，PMID41502533、[PMC12772638](https://pmc.ncbi.nlm.nih.gov/articles/PMC12772638/)。实际XML SHA54fa48e991a4db6a84a9e514658815dfd3f80ee9a9211a22aacf5b7a8de0cf88，完整核读提取blocks0–126，其中科学主文0–88、其他作者/数据/补充入口89–126，Table1全部单元格。外链supplementary ZIP中的AppendixA/B未取得；未审原图像素、源码、模型权重或真实患者决策。

方法用nnU-Net default 3D fullres UNet两阶段whole及intra/extra-meatal分割，自动线性/体积特征与报告。内部模型开发/调参/测试用UCLH MC-RC；外部模拟MDTM用KCH MC-RC50患者，作者明确两者不重合。详细split、训练和内部表在未读AppendixA.1/A.2/B.1，不能声称本轮认证完整250k-budget配方、患者身份crosswalk或外部模型Dice。

50患者接受两次模拟会诊，第一次standard，第二次CAS在35天后；随机改变病例呈现顺序，没有随机或counterbalance两种会诊的先后。决策不影响实际患者care。这是临床实现pilot，不是前瞻性患者结局的确认，也不是本项目补层动作实验。

主文block54把两阶段internal whole-tumor Dice .9392±.0351记给T2、.9331±.0354给T1C；摘要block6的模态映射相反。保留冲突，不拼成无歧义的单一模型分数。两阶段后的internal高Dice也不能移用为KCH50患者外部Dice或本项目稀疏T2能力。

外部50患者中36（72%）全部accepted、8（16%）一个session拒绝后人工量线性特征、6（12%）至少两个session失败而整例人工修订；全部50留在报告，不能只保留36成功例。失败包括小瘤过分割、欠分、完全miss和intra/extra边界错。自动图/人工量线性特征的目标和成本不完全一致，不能称全部14例都完成了人工mask纠错。

时间的两个原表口径不能静默混算。Mean-per-case：preparation156→174秒，MDTM81→75秒；前期多18秒、讨论少6秒，两个阶段顺序相加多12秒/例，仅是原均值算术。Table1 totals：preparation7650→8724秒，MDTM3756→2904秒，相加多222秒（3分42秒）。这些totals不等于原mean×50（后者差600秒），正文未解释差异；不据此造新显著性或真实净工作流结论。

两阶段时间也不是person-time：会诊同时有多位专家，正文列九位临床成员外加协调员/neuroradiologist；没有逐参与者出勤/额外预读报告耗时，不能据名册认定固定k位全程参与。CPU仅分别保留两列假定k下的算术：均值列18−6k秒/例，total列1074−852k秒；break-even分别3与179/142，差异本身要求核原始时间。自动分割、特征/报告生成、PACS/信息准备、人工修订及训练费用尚未完整提供。减少MDTM讨论不自动等于完整pipeline净省时。

作者解释preparation多耗时可能来自学习曲线、额外校验/体积信息/信息负担；NASA-TLX从45.5到48也是更高准备负担。未随机化会诊先后和信息内容差异使单独算法因果归因受限。工作流更清楚或改变治疗建议不代表建议更正确；仍需真实适应证及患者结果。原文block41称肿瘤“more than 1 axial slice”时不展示volume，语义与通常预期有疑问，未查代码前不修正。

对本项目：error-cost/defer必须报告所有原患者及拒绝后实际路径和费用，不能以accepted子集或高QC相关性替代真实动作收益。没有人类时间实测时，只能报告模型计算时间及显式成本假设/敏感性，不能称临床workflow收益。此类临床report、守卫、拒绝/人工fallback和全费用问题已有直接VS先例。

## 耳内T2薄结构：只增强图像、保留标签也有直接先例

[Deep Learning-Based Inner Ear Subregion Segmentation in 3D T2-Weighted MRI Using Label-Preserving Data Augmentation](https://doi.org/10.1002/nbm.70266)，NMR in Biomedicine，索引firstPublicationDate2026-04-01，PMID41821500、[PMC12983123](https://pmc.ncbi.nlm.nih.gov/articles/PMC12983123/)。实际XML SHA10cd90b719c5ad6f82e4d86775bfd5b84123d4e5d94f350fe391fb86bc485ad3，完整核读blocks0–89，其中科学主文0–62，Table1/2逐单元格。没有阅读外链docx补充文件、FigureS1像素/TablesS1-S2实值或作者代码。

任务是三种耳内解剖分区，不是VS病灶；外部数据虽来自VS-SEG八例，但GT由radiologist重新标内耳，不能把其Dice当VS肿瘤端点。内部74 MRI exams，50训练/24时间独立测试；文字不能证明74独立患者或多exam同患者隔离。内部评估左右耳各算一sample，Table1 N48对应24 exams；外部Table2 N16对应8 images。t-tests以耳side样本描述，主文没有证明按患者相关性聚类或多比较校正。

内部3T GE fast spin echo，0.3125mm平面/.4mm厚；外部1.5T Siemens有CISS（.47mm平面/1.5mm）或FSE（.55mm/1.5mm），模态/协议/分辨率一起改变。不能统称全部CISS，更不能分离成纯spacing因果效应。

原文blocks23–25认为nearest labels在thin canals旋转/缩放后可能断裂，提出只对图像先变换再逆变换，原label不动；有限插值会改变图像。验证限x-axis rotation和scale。模型Swin UNETR、96x96x32 crop、500epochs、Dice+CE等权、AdamW lr1e-4/weight_decay1e-3、单TitanXP12GB；双方其他noise/smoothing/sharpening/flips相同。主文没有完整angle/scale range、概率、batch/实际updates、pad/axis处理或seed初始化matched说明，不能宣称忠实训练复现或严格相同总费用。输入crop是训练randomcrop，完整推断视野/ROI方案还待源码核查。

后处理用connected-component mask和argmax清除FP；没有在主文完整给出阈值/组件选择细则。它不能移植成当前VS模型保留所有病灶的已认证守卫，也不能改变当前固定.5/无LCC评价合同。

内部Table1各区域Dice .902/.881/.926→.905/.880/.929，mid-to-apical稍降；不是所有区域Dice都改善。外部Table2为.872/.802/.866→.956/.887/.913，区域均值约.847→.919。HD表未在主文明确本文实现的距离单位/HD vsHD95细则，不填未经核的mm/HD95。Discussion54称internal统计未达显著，与Results41的vestibule DSC/IoU显著叙述不完全一致，图上pvalue未视觉核查，保留限制。

Discussion56把线性插值soft标签称limited to binary segmentation，但multiclass逐one-hot channel软标签在数学上也可以定义；此说法不能当本项目多类方案禁令，本文也未完整分析所有多类实现。两方法在low contrast下仍失败（block59），作者明确其他复杂/小结构和其他旋转轴需后续验证；本项目VS改善尚未证实。

对本项目：普通resolution/contrast随机化、image-only roundtrip、preserve原GT、小结构/标签插值保护本身已有先例。可把roundtrip作为能力不足时的普通增强候选，必须加充分训练和same-parent/same-exposure控制，另计两个resampling的费用。它保持标签位数组，不保证有限FOV中每个结构信号/拓扑或诊断信息无损。

## 本轮已执行探索与创新决策

[临床表算术](clinical_time_audit_attempt01/receipt.json)真实560478 exit0，保留两种时间列与全50患者分母；非本项目医学效果。[全尺寸synthetic原型资格](roundtrip_synthetic_attempt01/receipt.json)8fb81e exit0、[checker/wide补核](roundtrip_texture_attempt01/receipt.json)49f6f4 exit0：图像双插值后不是identity，GT逐位不变；常量全patch在zero padding下平均降至.861393且边缘可0。三轴Euler角同顺序逐一取负并非逆矩阵，预定点误差10.359869voxel；完整齐次矩阵求逆+独立物理oracle正确。

32点两级八邻域独立oracle最大误差约1.86e-8/2.98e-8，通过3e-6；物理坐标与matrix composition通过3e-12。此覆盖固定点，不是所有synthetic概率体素独立核验，也不是医学图像/任务确认。新apply_roundtrip模块保留标签与母输入，可用于后续具体配方准备；它不是作者实现。

已另外冻结[真实开发输入资格协议](REAL_DEVELOPMENT_ROUNDTRIP_ENTRY_PROTOCOL.md)，真实b2c07b exit0完成11开发患者/19series、两输入38batch源/GT配对和finite检查，用时127.913055秒。MRI输入加载38次、GT19次，网络state/forward/更新均0；GT逐位不变、两输入母geometry/primitive匹配。结果见[开发入口receipt](real_development_entry_attempt01/receipt.json)。它不评价患者Dice或证明临床改善。原session29823继续，最后state未齐之前不评分四验证。尚无可发表新claim，8未见确认/lockedIXI未打开。

仍保留的具体候选问题：充分能力之后，针对合法observed信息和冻结动作，能否预测并实现超越强raw、直接任务、充分增强、QC/error-cost/defer的真实missing病灶损害变化与净费用。两篇新原文补强baseline和费用口径，不证明该候选为首创或正结果。
