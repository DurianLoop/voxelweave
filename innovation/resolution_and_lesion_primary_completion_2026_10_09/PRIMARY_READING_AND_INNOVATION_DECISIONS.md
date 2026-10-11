# 两篇待读主文补完后的科研判断

新增两篇不同科学主文，来源为已公开 PMC HTML，精确 DOI/题名/PMCID 已匹配旧索引。旧 EuropePMC XML HTTP500失败保留；本次不同渠道200、真实工具 c485b9 exit0。原 HTML 无损gzip及原/压缩SHA见 sources_attempt01/receipt.json。获取与提取当时的 actually_read=false 保留，实际核读另登记。

VINN 实际完整文字范围为 blocks15–199，以及202–212：覆盖科学主文15–151、致谢/缩写和 inline Appendix A1/A2/A3，及Table6–8。128–137在合并工具输出被截断后由a2b97d单独补读。未核Table5 label ID清单、Table9–16完整单元格、脚注/参考全文；图注已读，图像像素未读，作者源码/权重未取未执行。21个HTML table中5个是公式，不能写成21张科学结果表。

病灶集成主文 blocks20–86 完整文字核读，含全部三张表/图注/致谢；未核图像像素、引用全文、容器/网页实现和潜在额外补充。它是一篇不同主文，不是同一主文不同版本再计数。

## FastSurferVINN：物理分辨率归一化和原位标签均有先例

[FastSurferVINN: Building resolution-independence into deep learning segmentation methods—A solution for HighRes brain MRI](https://pmc.ncbi.nlm.nih.gov/articles/PMC9801435/)，DOI10.1016/j.neuroimage.2022.118933。方法针对结构T1及0.7/0.8/1.0mm训练、0.9mm外部测试，不是稀疏观测T2病灶SR。

第一个encoder和最后一个decoder的pool/unpool换为feature-space interpolation，内层统一1mm，输入和输出保留原网格；native高分辨率skip保留。scale使用已知physical voxel size，允许整数输出尺寸的微调；inSA在scale factor上**加**α~N(0,.1)，不是图像域强度/噪声或采集厚层PSF增强。内层真实spacing感知、latent roundtrip、原位标签、用skip保留边界这些一般表述已有明确方法先例。

三个独立解剖方向的2.5D网络，最后加权平均（sagittal半权），不是单个完整3D分割器。78训练类别恢复为95区域，主要监督是FreeSurfer7.1.1 silver labels。人工参考为Mindboggle78 cortical/子集20 subcortical，以及6个RS病例三种经人工修订结构；不能写成全测试病例独立手工95类GT。

对照有价值：CNN*与VINN共用microarchitecture、pre/post blocks和相同硬件/hyperparameters；attention对照调feature数量保持参数数目，并未达到显著改善。外部scale augmentation用image bilinear+label NN，internal用连续features且不改label。Table6中给VINN再加外部增强时四个显示均值都变差，但这不能在本项目直接证明label插值造成损害：多个机制同时不同，采集/病灶任务也不同。需要原位标签退化、feature归一化、普通空间增强在matched预算下区分。

Mix训练120人（60 native1mm+60 submillimeter），70epochs，每方向至少23k slices、batch16，V10032GB，AdamW lr.001/cosine restarts。Big训练1315人，增加训练语料同时增加epoch内update量，不能当成仅更换resolution策略的等预算消融。各作者对照可比，不意味着本项目2992步就已达到同等充分训练。

粗分辨率1.4/1.6mm是cubic重采样、reference多数投票下采样后的实验，不是新前瞻真实厚层采集；作者也预期8倍信息减少/PVE。原网格大小与有效采集信息量分开，不能把固定重采样网格1mm等同实际observed层间信息。低显存2.5D也不是未经任务验证可直接替换我们的强3D基线。

原文用Wilcoxon+BH，没有从不显著差异证明equivalence。Table6 bilinear subcortical ASD=.293，Table7/8=.303；显示源值全部保留，不猜哪个是正确实验值。作者对比声明同硬件/hyperparameters，不等同完整部署费用已实测；本批未从“<1min GPU”外推我们的latency。

## 病灶集成：任务固定权重，预测mask驱动后处理

[Adaptable Segmentation Pipeline for Diverse Brain Tumors with Radiomic-guided Subtyping and Lesion-Wise Model Ensemble](https://pmc.ncbi.nlm.nih.gov/articles/PMC13148016/)，DOI10.1007/978-3-032-16365-3_41。BraTS2025，PED261/91、MEN1000/141、MEN-RT500/70、MET1296/179训练/验证；前三种多模态描述须例外说明MEN-RT仅native T1CE，不是所有病例四序列共同输入。

训练分层用GT whole-tumor mask提取14shape+每MRI序列93appearance radiomics，PCA保留90%variance、k-means/silhouette选簇，簇内分5fold。这是训练期分层监督，不能把GT形状用于部署。主文未完整披露所有患者ID、纵向MET患者是否跨fold，不能自行认证严格患者隔离，亦不能据此断言泄漏。

nnU-Net v2、ResEnc M、MedNeXt M各5fold，共15模型；patch128³、200epochs、SGD/Nesterov .01/.99/wd3e-5，A10040GB。CV lesion-wise Dice/NSD等的case-wise rank聚合为F，再产生**每任务固定**三模型ensemble权重；它不是逐病灶在线预测动作收益并只调用一个便宜模型。ENSi是每模型5fold概率平均；MEN-RT STAPLE文字另称15fold predictions更好，但表仅列Ensemble，未给出完整可对应版本标注，保留该限制。

ensemble后从预测mask重算radiomic cluster，cluster/label内按0..500voxels、步25筛小CC，并按label/WT体积比做label conversion。部署按新病例预测mask分簇，阈值来源CV GT和confusion matrix。合法预测mask可部署，但小CC删除可能同时移除真小病灶，不能借此改我们的无后处理主合同。论文未在所核主文给出全部训练/feature extraction/15推断/ensemble/PP的实测总费用，不能拿“GPU-free heuristics”当系统GPU无需成本。

三张原表56次精确端点差以及VINN12次差已由 [CPU核验](table_audit_attempt01/receipt.json) 实际7e3666 exit0：28个验证端点中Ensemble相对最佳单模型18个更低；PP相对Ensemble13个改善、11个退化、4个持平。MET global PP Dice ET/TC/WT分别−.045/−.045/−.050，RC+.202；PED LW ET Dice−.027。MET validation为global、testing为lesion-wise，不相减或拼成泛化降幅。不能从这些不同相关endpoint均值推逐患者退化比例或统计显著性；它们也不是本项目新医疗效果。

正文W_i=(sum_{j≠i}F_j)/(sum_jF_j)在n=3时权重和为2，Table1四任务权重均和1。原HTML公式再次核实无1/2。n2..6、F1..4的5456组合exact Fraction核和=n−1；**归一化后**两者可保持相对权重，但未经作者源码不能断言其代码具体如何归一化，也不能仅凭公式显示差异否定其临床结果。

## 创新优先级和当前证据缺口

已有先例进一步覆盖physical-spacing-aware、latent interpolation、label-preserving augmentation、lesion-level objective、GT训练分层、预测mask分簇、adaptive post-processing和模型ensemble。defer/SafeRestore此前真实阅读继续说明有限候选的relative cost/gain选择本身已知。

唯一主候选仍作为可证伪的MRI机制/应用问题：**在充分能力的直接任务、PCHIP与增强基线后，真实采集可见性是否能预测具体修正的完整患者病灶损害变化，并在相同信息/容量/监督/总费用下超过强QC、cost/defer和静态/随机控制？**需分开nominal output grid spacing与observed sampling/support；不能仅增加spacing通道就称方法首创。

本轮新增两篇主文和原表/公式核验，新增患者医学效果0、训练更新0。原四臂与35904真实管线仍live；原门槛未通过前不开放确认/训练收益头来制造正claim。若充分基线消除动作余量，保留负结果而停止该正向机制。下一实验准备见 [行动与强对照方案](NEXT_TRIAL_PREPARATION.md)。
