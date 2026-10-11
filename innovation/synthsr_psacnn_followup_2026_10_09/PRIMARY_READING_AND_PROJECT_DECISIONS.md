# 本批原文结论与项目决策

新增完整核读两篇不同原始主文的公开期刊XML、公式、图注及全部5张内置表；逐块实际读流见READING_PROVENANCE.json。没有读取图像像素、外链补充材料、参考文献中其他论文、作者源码或权重。PSACNN只取得索引，Katayama2026 VS/CISS已读过，不计新主文。本批没有新的患者医学效果或独立确认claim。

当前优先候选仍是：充分任务能力后，合法采集可见性是否对具体修正动作的真实病灶损害变化和全费用提供增量价值，超过同信息/容量/监督/预算的QC、error-cost/defer、静态、随机和去采集控制。两篇新论文进一步限制这一假设，不能由阅读就宣布首创。

## SynthSR 2023：病变填补与任务引导的重建都已有先例

[SynthSR: A public AI tool to turn heterogeneous clinical brain scans into high-resolution T1-weighted images for 3D morphometry](https://doi.org/10.1126/sciadv.add3607)，Science Advances，2023-02-01，[PMC9891693](https://pmc.ncbi.nlm.nih.gov/articles/PMC9891693/)。原XML SHA fe06742070d2cb02780635983a5dd97d03091661f42c9420ccba73206a1b018e。本批blocks0–111全部实际核读，其中科学正文0–91；3张原表直接XML cells与保存提取逐格一致。

机制（blocks12、70–78）：训练输入随机合成病变，输出是清除病变后的MPRAGE，目的明确为正常组织填补，让FreeSurfer/SPM等解剖测量或NiftyReg配准可运行。它并不承诺保持病灶诊断信号。论文52明确用途不是临床诊断图像；53主动讨论连续肿瘤浸润建模不足及大卒中填补的解剖幻觉。把它直接当病灶保持SR基线，会把另一任务的设计目的混入比较。

训练（59、64、72、77–89）：20 OASIS 1mm MPRAGE，36脑区人工label加自动脑外label；14健康/6probable AD；另注册60 held-out ADNI/BraTS/ATLAS病灶label合成病理。主体是随机GMM、方向/spacing/thickness/noise/bias及线性/非线性形变。L1图像回归加冻结分割UNet的soft-Dice loss，λ=.25在小held-out集目视选；Adam lr1e-4、250000 iterations、RTX8000约两周。两网络5levels、每level两个3³conv、ELU、首层24channels。推断去掉生成器和分割网，先重采样1mm、padding到32倍数、min-max归一化。输入分辨率随机化、标签空间保持和分割loss指导MRI重建不是本项目新意。

作者报告CPU速度有15s（介绍14）与约20s（方法89）两种口径，GPU<3s；不据此替换本项目实测全流程时间。训练真值影像也不能公开提供（97），开源仓库不意味着完整训练数据可复现。未下载执行作者实现。

证据范围：MGH9146扫描，结果段称1110patients，方法段称1110sessions，身份边界未由本批认证；体积相关子集为435扫描/41subjects，参照为1mm T1的FreeSurfer结果。Table1 scan相关.47–.99，subject内median聚合后.72–.99，不是独立435患者，也不是原生病灶Dice。辅助segmentation loss对9项相关中7项改善、2项不变；不能升级成所有结构/病例病灶安全。

Table2 spacing<=4/4–6/>6mm分别197/110/128扫描（合435）。海马相关.89→.69→.56，苍白球.67→.41→.27，脑室均.99。说明结构/spacing依赖已有实证，但三组观察性分层并不能分离所有contrast或病例构成，更不是合法visible-feature收益策略。

AD实验（27–32）50AD+50controls，5mm FLAIR→MPRAGE，用FSL体积；4个原1mm参照分割失败被排除，组别及各端点确切剔除范围未详述。SynthSR与真MPRAGE的AUROC为.76/.81，median组间差481/543mm³；填补消融.75。统计分离/体积相关和萎缩保留，不能代替VS病灶体积误差或missing-lesion召回。

肿瘤实验（34–40）BraTS-Reg140patients/1252landmarks，QC后1075；用合成正常组织图像估计变换，原MRI和原病灶label再映射。10–20%landmark误差下降是配准效果，不能写成SynthSR恢复了肿瘤。ATLAS655病例中，Table3仅598个单半球主导病灶纳入；其解剖不对称关联不是生成图上病灶保持端点。

项目决定：如果将SynthSR列候选，应明确作为配准/解剖路线而非病灶保留的默认动作；其输出不能直接替代原T2或作为VS真值。任何去填补变体另立模型/训练版本并重新验证，不能靠CLI名称假定保留病变。我们的部署政策须对每种具体用途分别测实际损害，不能把高全脑相关或较易配准解释为病灶安全。

## VSRAD 2025：高相关、诊断AUC与绝对一致性需要分开评价

[SynthSR-generated 3D T1-weighted MRI from routine 2D clinical images: Validation for VSRAD analysis](https://doi.org/10.3389/fneur.2025.1645891)，Frontiers in Neurology，2025-10-16，[PMC12571571](https://pmc.ncbi.nlm.nih.gov/articles/PMC12571571/)。原XML SHA dc530fee35b0876fdf8ea11c3a14e37b4cdfeb769fe119f9500bdf50e2e00b67。本批blocks0–70全部实际核读，科学主文0–51；全部2表。Frontiers图像alt-text声明可由生成AI生成，本批未以其外观描述当像素观察证据。

单中心retrospective，同日75患者，平均83.5岁（61–107）。1.5T GE，2D PROPELLER T1为6mm/105s，3D SPGR T1为1.5mm/232s；既改变分辨率又改变序列，不是同raw-data或纯分辨率实验。SynthSR 4CPU平均77s，生成1mm MPRAGE样图，再重定向、NIfTI→DICOM并做VSRAD/SPM8/DARTEL。参照是标准3D自动分析，没有人工结构GT；不是1mm独立病灶医学确认。

75例都生成，11例排除（4萎缩分割错、5motion、2卒中），64例进入定量。作者报告卒中区域被正常组织填补（33），不是一个意外细节；它与原模型训练目的一致。全队列剔除14.67%，不能把成功生成75/75解释为病灶分割成功75/75。原2D未含parietal区域，生成也未恢复，不能用未观测区域承诺完整原生脑体积。我们仍保持全部主患者/FOV分母、明确失败路径。

Table1全部7指标绝对差显著，correlation .40–.74；高相关与绝对偏差共存。AD29+normal8的ROC报告AUC .90/.96，不同于完整75例，阈值来自同数据Youden Index，未报告独立test或预定义等效/非劣界。非显著DeLong不证明等效。原DeLong Z=.009、CI−13.85到13.97单位未清，Results41 Youden=.84但Figure7/Discussion=.86，原值均保留，不擅自修正。

原表CPU核验 [receipt](table_audit_attempt01/receipt.json) 实际44f97f exit0。Table1声称7项Bonferroni，但7行adjusted/raw与约9倍相容，与7倍即使考虑显示精度仍不相容。7倍或9倍均保留原显著性，这不推翻其差异结论。Table2 median±1.5IQR边界最大显示算术差.015，全部可由隐藏小数/显示四舍五入解释；outlier百分比与64例分母相容。不能把显示的.01差异认定统计错误。

Table1的difference of medians与Table2的median paired difference不是同一统计量。即使体积符号看似不同，也不由汇总值直接判原始配对数据错误。未取得原paired数据、最终PDF或分析代码，绝对一致性和DeLong只能保留限制。median±1.5IQR亦不自动是本项目95%患者安全保证。

费用算术：采集阶段节约127s；加已报77s生成，仅两个串行阶段节约50s。DICOM转换、重定向、VSRAD、失败复核和人时都未齐，不能宣称全流程净省127s或50s。本项目的净效用仍须包含定位/QC/动作/下游分割与失败成本。

## 收窄后的创新候选与否定条件

| 候选 | 本批新增约束 | 下一可证伪比较 |
| --- | --- | --- |
| 采集可见性对具体病灶动作收益有增量价值 | 方向/spacing随机化、task-loss重建和分辨率分层都有先例；泛用SR可主动消病变 | 足够强且matched的raw/直接任务/增强后，比较QC/error-cost/defer与同容量加入真实采集支持的收益策略；无稳定增量则否定 |
| 多局部修正的联合损害不是单动作可加 | 正常组织填补与IN的全局依赖都说明任务效应可能跨区域；联合模型选择也已有先例 | 实际执行联合输入、独立任务网复核，对比同预算联合优化及静态/随机，不用合成加和假标签；联合控制能解释就否定独立贡献 |
| 同一MRI修正对不同任务有相反效用 | 原SynthSR已经以填补换取配准/解剖收益；冲突现象本身并非新意 | 仅可作动作合法性/任务端点的机制控制，不能单独包装为创新；没有病灶净收益就不做正向部署claim |

原六医学门槛、last checkpoint、完整FOV及患者先均值不改。包含11全体GT的19998父checkpoint不作严格LOPO初始化。已见4验证/9series不用于选本轮精度/模型阈值；8未见确认/12series与lockedIXI继续关闭。
