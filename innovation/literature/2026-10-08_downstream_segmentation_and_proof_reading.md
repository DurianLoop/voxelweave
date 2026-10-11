# 下游分割原文及Noise2Same证明补读

本阶段新读一个独立论文，以及此前Noise2Same的单独Supplemental；合计新增9个文字页、4个视觉页。不把补充材料重复计第二篇新论文，不重复上一阶段Noise2Same主PDF／Noise2Void阅读计数。没有作者模型复现或MRI新任务收益。

## Prakash等：去噪预处理与分割微调已经存在

实际取得作者稿 **arXiv1911.12239v3，2020-03-19，5页**，题名 *Leveraging Self-supervised Denoising for Image Segmentation*，Mangal Prakash、Tim-Oliver Buchholz、Manan Lalit、Pavel Tomancak、Florian Jug、Alexander Krull。Crossref精确题名和作者列表匹配，正式DOI [10.1109/ISBI45749.2020.9098559](https://doi.org/10.1109/ISBI45749.2020.9098559)。arXivID来自精确title Atom元数据，并非猜测；[作者稿](https://arxiv.org/abs/1911.12239v3)。全文physical1–5文字实际核读，physical1／3视觉核读；外部GitHub VoidSeg代码／wiki未取未读，未复现其训练。

Figure1及第2页区分四个流程：直接训练noisy→segmentation baseline；固定N2V denoiser后训练下游分割；把N2V U-Net权重finetune为分割；以及固定denoiser后用其权重初始化下游分割并finetune。StarDist架构不同，作者只对它做sequential；不是所有baseline每格都完整。它们已经占位“自监督恢复帮助分割”“预训练再适配”“模块化联合pipeline”，不能只换成MRI缺层任务就说这些机制首创。

实验在DSB2018显微镜细胞核和BBBC004合成核、Gaussian添加噪声、多个标注量下进行，**无MRI／病灶**。Denoiser用可用noisy body训练；正文没有清楚给出其全部无标签来源与测试集的边界，不替作者声明病人隔离部署预算。下游分别在denoised或noisy输入上训练；不能拿固定作者分割器在分布变化后掉分来代替强适配对照。

基线：U-Net 32初始feature maps、batch128、3×3；训练200epochs×400steps、初始lr0.0004、batchnorm、8fold旋转／翻转，border类loss权重5。作者称测试过不同depth并选饱和性能配置。本文没有同等总训练成本的明确计量：denoiser预训练或two-stage额外工作不能视为免费。直接引用结果不能证明本项目相同总预算下收益。

Table1（实际文字／视觉核对）报告AP与SEG，DSB重复8次、BBBC重复5次。DSB n40的U-Net P1 AP从0.4777到sequential0.5608、finetune-sequential0.5944；StarDist P1 AP从0.4796到sequential0.6802。但表也保留不占优格：DSB P7 StarDist AP0.7795高于sequential0.7766；P10 U-Net SEG0.6929高于finetune-sequential0.6870；P10 StarDist SEG0.7150高于sequential0.7141。不能把正文“consistently improve”写为任意指标／标注量每格严格改善。

AP定义为TP/(TP+FP+FN)，SEG为匹配object的Jaccard（匹配需GT对象≥50%被覆盖），不是当前患者病灶Dice。文中说报告指标用maximizes AP的阈值，但此处没有明确该阈值在哪个split选择；不直接推定测试泄漏，也不把这种报告模式当作本项目冻结确认规则。训练数量正文与图轴有细小不一致，不能据图猜本项目预算。没有逐患者跨来源确认、动作收益预测／损害选择或完整成本路由。

## Noise2Same官方Supplemental：实际补完A–F，但理论适用仍有限

[官方补充PDF](https://proceedings.neurips.cc/paper_files/paper/2020/file/ea6b2efbdd4255a9f1b3bbc6399b58f4-Supplemental.pdf)链接来自此前已验证官方摘要。4页全部文字核读，physical1／2视觉核读Eq(9)–(29)；第4页Planaria Figure5只读图注／提取文本，未视觉核其内容。AuthorFeedback仍未取未读。上一阶段“Supplemental未读”是在当时成立的冻结记录，现在补充新provenance，不回改历史。

AppendixA：Eq(14)减去masked输出对目标噪声的条件covariance需独立噪声／masked函数依赖成立；不从普通counterfactual38fold就推出MRI所有条件。第1页解释Eq(16)→(17)时以normalized Var(Xj)=1说明Var(Xj|Y)≤1，这个**点态条件方差推断不能一般由边际归一化推出**。本阶段另立[局部推理检查协议](../CONDITIONAL_VARIANCE_PROOF_CHECK_PROTOCOL_2026-10-08.md)，[Fraction精确结果](../experiments/conditional_variance_proof_step_2026_10_08/attempt01.json)给出VarX=1，而少数Y状态的Var(X|Y)=19.05；全方差仍满足平均条件方差0.9525+条件均值方差0.0475=1。

这只核否一个通用推断，不证明Noise2Same完整Theorem1最终上界错误，也不验证该例符合论文全部mask与normalization合同；总体Cauchy-Schwarz可有其他推导。没有把标准概率例子当新定理或可发表MRI成果。AppendixB针对constant σ的additive noise，还使用conditionalvariance=σ²的更强条件；MRI magnitude及sample-derived归一化是否保持条件无偏／独立未证实。

AppendixC–E新增细节：ImageNet训练60000个128×128patches来自前20000图；Planaria17005个16×64×64训练patches、20张96×1024×1024测试图，三种采集条件混合训练；U-Net默认depth3、96初始maps，取消input→output residual skip；默认mask0.5%、Gaussian替换σ0.2，lr0.0004且每5k step减半。BSD68 λinv从默认2改为**0.95**，依据训练invariance error；所以不能拿默认2理论系数称其所有数值结果。作者明确Planaria无paired noisy、BM3D未用于3D、无公共3D blindspot基线，不能把表空格算通过。Figure5为3D数据的2D projections，未增加MRI证据。

## 候选与强对照因此收紧

可继续检验的是：经过充分输入适配的任务baseline后，真实observed-only特征加任务状态，是否能预测固定合法修正动作的**完整患者病灶配对净收益**，在实测全部成本下优于已知同信息／同容量error／risk／cost／defer／random／union-greedy控制。去噪预处理、task-adapted segmentation和泛称“learn when to restore”已经被本篇及旧SafeRestore／MoEDiff／Morshuis先例占位；还不能声称已完成MRI直接查新或原创。

新增[实际特征成本](../DEPLOYMENT_FEATURE_COST_RESULT_2026-10-08.md)填补了一个可执行准备缺口：一次19series CPU生产路径含冷启动／输出／退出23.8488s，其中已计量生产相位19.3780s；原108.467s资格总时不再代替这一成本。全部17特征与原fold评分exact；没有病灶任务评分／动作收益标签。下一步仍需原final模型→56FOV／6gates／strict→同信息同容量强适配→实际动作余量与成本；不能只挑这些输入特征成功来宣称方法有效。

Crossref一次精确title返回3条，其中只有首条是身份匹配；EuropePMC精确title hitCount=0，这不是证明不存在。arXiv精确title Atom一次给出v3；两个其他Crossref条目仅题名元数据识别，未读全文，不计论文。全部公开GET成功，pypdf对补充PDF提示wrong-pointing-object19（原输出保留）；原PDF未修订。实际工具退出／scope见本阶段provenance与ledger。
