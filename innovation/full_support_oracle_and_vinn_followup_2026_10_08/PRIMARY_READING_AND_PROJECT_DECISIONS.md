# 本轮结论：真实上下文值得进入普通基线，支持证书不能替代病灶收益

本轮新增完成两篇不同论文的**作者稿正文文字、公式、图注与内置表格核读**：FastSurferVINN（2022）及病灶级模型集成（2026；MICCAI 2025 challenge proceedings）。前一轮已读GOUHFI和claustrum。本轮没有审阅图像像素、外链补充材料、作者源码或执行作者实现；这不是系统综述。具体来源、逐段实际工具返回和哈希见 [登记](READING_PROVENANCE.json) 与 ACTUAL_TOOL_OBSERVATIONS_PART01–04.json。

最值得继续验证的方向仍是：**只用合法采集可见性、支持范围与预测信息，判断具体病灶修正动作能否改善任务损害，并计入全部费用**。这是一项待证伪研究假设，尚未形成可发表、独立确认的claim。本轮主要完成强基线资格和新意排重，新增患者分割效益评价为0。

## FastSurferVINN：特征内插值与原位标签已有明确先例

[FastSurferVINN: Building resolution-independence into deep learning segmentation methods—A solution for HighRes brain MRI](https://doi.org/10.1016/j.neuroimage.2022.118933)，NeuroImage 251:118933，PMC9801435 / PMID35122967。PMC页头明确“Author manuscript; available in PMC: 2022 Dec 30”，final edited form日期2022-02-03；issue date 2022-05-01。原HTML SHA256 `c3013ac688177b8276e394ad00fe8124deffdb8a78ebbf3c242da41f8bdbbd8b`。原文blocks0–147及其后文字、Appendix A和16张数据表均实际核读；21个HTML table节点包括5张公式布局表，不能称21张数据表。

机制（§3.2）：保留原生分辨率输入和输出，在首个encoder和最后decoder的尺度转换位置插值连续特征图；native skip connection回传未插值特征。由已知voxel size确定内层归一化到1mm的SF，调整整数feature尺寸；不是通过定位网络学习变换，不是单纯把原图先重采样到1mm，也不是往返图像增强。三视图2.5D独立模型，sagittal权重为另外两视图的一半；不是本项目的3D二值VS任务网。

外部exSA（§3.5）：scale U(.8,1.15)，图像bilinear、标签NN。内部inSA：`SF=Res_inner/Res_native+α`，`α~N(0,.1²)`；这是**加性扰动**，不能照抄成乘法比例，也不能把此公式直接移植成当前图像增强。标签不被重新采样，但特征插值本身仍不保证信息无损。

训练（§3.7、Table4）：主要Mix为120 subjects，60标准1mm+60HiRes（HCP30、RS30）；独立验证80。coronal/axial/sagittal各训练70epochs，batch16，V10032GB，lr.001、cosine warm restart最初10epochs、之后倍增，文中给momentum.95；具体optimizer实现仍需代码核查。作者按相同hardware/hyperparameters比较architecture，不能把本项目从19998父checkpoint额外2992步称作复现这种充分训练。Big训练1315（正文/Table4），并非仅增加一个head。

关键消融（Table6）：CNN*→+exSA：subcortical DSC88.85→88.79，cortical88.01→88.33；VINN+inSA达到89.05/88.93，再加exSA降到88.83/88.60。说明外部增强在不同结构、不同架构下效果不同；不支持“一律禁用空间增强”。attention在参数数目受控时未改善，HiRes loss主要改善皮层（Table8）。因此“标签不变”“插值移到特征里”“加attention/边界loss”均不适合单独当我们的新意。

参照与范围：多数评价使用FreeSurfer silver labels；1mm Mindboggle人工参照皮层78人、subcortical20人；HiRes只有6例专家修订的WM/GM/hippocampus，作者未做小样本统计。1.4/1.6mm来自合成降采样：label majority voting、image cubic，不能称独立原生厚层病灶验证。T1全脑解剖和0.7–1mm跨分辨率泛化，不能替代异质T2/VS病灶真实性。

保留作者稿内不一致，尚未核最终PDF/勘误/源码：Table6的bilinear subcortical ASD=.293，而Table7/8对应baseline=.303；正文0.8mm cortical ASD=.273而Table10 VINN=.246；正文manual subcortical DSC=80.26而Table12=80.06；正文/Table4训练n1315而Table16列头n1300。正文“九数据集各结构均最好”也超过Table9：ADNI subcortical DSC88.58<88.65、ASD.310>.307。不能抹平这些差异后复述普遍最优，也不能由文本差异直接认定作者实现错误。

GOUHFI引用VINN对internal/external scaling的方向判断有原文依据，但GOUHFI自身合成生成器关闭downsample并非VINN等价实现；两论文也没有证明本项目应作相同选择。VINN不构成“薄层病灶可以可靠恢复”的证据。

## 病灶级集成：强后处理与病灶选模也已有先例

[Adaptable Segmentation Pipeline for Diverse Brain Tumors with Radiomic-guided Subtyping and Lesion-Wise Model Ensemble](https://doi.org/10.1007/978-3-032-16365-3_41)，PMC13148016 / PMID42099437，proceedings日期2026-04-01，页头Author manuscript于2026-05-07可用；属于MICCAI2025挑战赛文集，不能写成MICCAI2026主会论文。原HTML SHA256 `26784007d15eee45963d1f0a3a4fa4f785ecfaa08ee1f6ea38024e66e0000b1d`。blocks0–79、全部3张表已实际核读，reference list以外文献未代读。

数据（§2.1）：PED train261/val91，MEN1000/141，MEN-RT500/70，MET1296/179。前三者中的PED/MEN/MET提供多参数MRI；MEN-RT只有原空间T1CE。多病理、多标签脑肿瘤和本项目VS二值异质T2合同不同，不能照搬ET→其他label重定义。

§2.3用训练集**GT WT区域**计算每序列14shape+93appearance radiomics，PCA解释90%variance、kmeans并按silhouette选择cluster、cluster内分五折。此GT允许训练期分层，不是部署期可观测输入。推理时在预测mask上计算cluster、选最近cluster（§2.7）；不能把训练GT radiomics直接喂给我们的部署收益头。

三个backbone：nnU-Net V2、ResEnc M、MedNeXt M；每个5fold、patch128³、200epochs、SGD Nesterov lr.01/momentum.99/wd3e-5，A10040GB。15fold模型加ensemble并非“GPU-free训练”，也未报告足够的完整工作流成本给我们直接采用。

§2.5以训练CV候选的lesion-wise多标签DSC/NSD等case-wise ranks组合F；§2.6按每个模型整体F加权。Table1每个任务列是固定三个权重（MET .295/.296/.409），**不是每个病灶实时输出一组动作收益权重**。§2.7按cluster/label搜索CC阈值0–500voxels、步长25，及label/WT体积比例重定义；显然已覆盖“自适应阈值、小病灶过滤、病灶级指标选模”新意。

文中公式`W_i=(Σ_{j≠i}F_j)/(Σ_j F_j)`对3模型的权重和应为2，Table1四列却各为1；复现须明确最终归一化。未核代码，不能认定其执行未归一化。CV表述同时出现“训练集5fold CV候选”和“训练集five-fold-averaged probability outputs”，OOF映射/是否每例平均了曾见该例GT的模型尚不清楚；我们的折外资格必须自己明确保证。

收益不均匀：PED ensemble→PP：ED LW Dice .868→.967，但ET .677→.650；MET validation是global Dice，PP使ET .744→.699、TC .765→.720、WT .769→.719，而RC .705→.907；MET testing是lesion-wise，不能与validation作同指标相减。MEN有局部改善；MEN-RT表中MedNeXt .804/.671、ensemble .796/.654、PP不变。测试只给最终pipeline均值/SD，没有成套held-out test各backbone消融，因此正文泛称“始终超过任一单模型”不能照写。平台验证无GT访问及封闭测试是有用证据，但不能推出每个后处理动作都安全。

此论文已经逼近“病灶级策略”主题。我们的潜在差异应是显式合法采集可见性、**具体动作前后实际任务损害差**与全部费用/失败路径，并对强cluster-QC/CC/defer等控制建立增益；普通模型集成、漂亮形状或整体Dice不能承担这一claim。

## 已实际完成的开发资格

1. 旧oracle失败保留：verify_full_geometry_support原尝试7011eb exit1，坐标误差超3e-12。直接旋转物理基向量的V2不用两个大数相减，diagnostic对38patch全通过；旧19/38失败、最大8.157e-12，新最大5.684e-14。原门槛未放宽。prepare_v2记录实际原SHA但未预先assert硬编码原SHA，新增padding补充协议明确此区别。
2. V2全体素资格：f75c96 exit0，38独特几何patch/39845888目标体素，两条路径共76 fields，独立SciPy误差最大7.128e-14、二值差0。这个“full”取的是padded physical cache，不是每格点真实采集信息。
3. [标签重叠结果](development_label_support_attempt01/receipt.json)：aeef07真实exit0，86.998秒。11开发患者/19series/38patch，19完整physical_label SHA和母batch SHA全部匹配，旧76二值support SHA重放一致。5series有z padding；新增无padding影像域38 fields与独立SciPy全体素比较最大6.783e-14、坐标5.684e-14、二值差0。没有读取MRI/model，标签26patch有FG、12为空，所有保留。

| 支持域 | 完全充分patch/38 | FG支持不足patch | 前景支持不足曝光体素/611350 | 背景支持不足曝光体素/39234538 |
|---|---:|---:|---:|---:|
| crop-only缓存 | 0 | 9 | 51803（8.4735%） | 10649393（27.1429%） |
| 完整padded缓存 | 8 | 0 | 0 | 1001795（2.5533%） |
| 无padding的resampled影像域 | 8 | 0 | 0 | 2731802（6.9627%） |

这些是patch**曝光**体素计数，重叠patch可重复看到同一解剖体素，不能称611350个独立病灶体素或26个独立患者。无padding域仍只是native→physical映射后的几何域，不能保证raw-PCHIP格点真的采集过，亦未审计该首次插值的全部native stencil。

本批38stress几何中，真实上下文能消除原crop-only的FG支持缺失；基于输入几何mask屏蔽不足位置不会直接删掉此批FG目标。但会删除背景监督，改变false-positive训练与整个loss分母；尚未核完整2992geometry分布，不能按GT选择identity/禁用策略，不能宣称mask-loss没有医学代价。

4. [归一化合成核验](normalization_support_attempt01/receipt.json)：820d92真实exit0。中心4³输入相同、外部置零；3³均值卷积的中心2³输出差0，但InstanceNorm后的差达3.8565；独立SciPy卷积/NumPy population variance最大误差1.155e-14。当前网络确实有InstanceNorm且默认无running statistics。该实验只证实一种非局部依赖机制，没有患者forward、checkpoint或医学效果；输入support mask不能单独认证任务输出安全。

## 下一步与停止条件

原CPU训练session29823仍须继续真实轮询。四last2992与11968journal及真实exit0齐备后，原顺序capture_training_terminal→evaluate_matched→capture_evaluation_terminal→summarize_matched，36生产+36独立functional完整FOV。六医学门槛、3e-6概率、3e-12坐标、零binary差和全部患者分母保持不变。

若任务能力仍不足，先比较普通支持合法的roundtrip/low-pass基线；halo和mask作为实现资格，不包装成新医学方法。训练前要覆盖完整schedule几何、测所有成本，明确padding处理及InstanceNorm影响。masked loss只能作control，不能称“输出免受缺失影响”。见 [后续准备](NEXT_TRIAL_PREPARATION.md)。

只有能力和真实动作余量足够，才做11患者内cross-fitting的动作收益预测。任何包含全部11开发GT训练的19998父checkpoint均不能作为严格折外任务模型；每外折模型/定位/QC/收益头/校准必须不见外折患者，且全部series按患者归组。8未见确认12series与lockedIXI继续关闭。
