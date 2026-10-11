# 脑肿瘤 QC 原文、创新边界与本项目决策

本轮新增核读两篇不同论文的主文：QCResUNet 作者预印本 v2，以及 Jungo 等人2020年的期刊公开XML。原文获取、正文阅读、作者源码静态审计与本项目医学实验分别登记；没有新增患者医学结果，也没有独立确认或可发表 claim。此前已读的 SynthSeg+、BigAug、SafeRestore、MoEDiff、cost-sensitive/defer 与联合分割先例继续有效。

## QCResUNet：预测质量与错误位置已经有直接先例

来源：[QCResUNet: Joint subject-level and voxel-level segmentation quality prediction](https://doi.org/10.1016/j.media.2025.103718)，PMID40945175，索引 firstPublicationDate 2025-08-27、卷期年份2026。本轮实际核读的是作者 [arXiv2412.07156v2](https://arxiv.org/html/2412.07156v2)，更新2025-07-04；Crossref/arXiv题名与全部五位作者匹配，未声明与最终期刊版本逐位一致。保存HTML SHA256为8cc2f419bbc8e87e84769dd9e875b28d144556e3a3733263ef28ad901bdd0508。核读 blocks 0–107主文及172–199同HTML附录；参考文献部分只选读若干条，未视觉审查图像像素或独立PDF。

方法输入为MRI模态加待评估的query segmentation。3D ResNet34 encoder和较浅decoder共同预测患者/体积级绝对DSC、NSD以及WT/TC/ET逐区域二值SEM，另有ECA注意力聚合。主文评价的是质量预测和错误定位，末尾提出人机反馈/后续修正潜力；没有验证本项目具体稀疏T2补层动作的全患者净收益。因此，“QC+错误图”“定位该修哪里”“多任务质量头”均不能作为宽泛创新。已有cost-sensitive/defer及恢复动作先例也意味着“另加收益头”不能单独宣称首创。

数据为BraTS2021共1251患者，固定内部测试251患者，其余1000在三次划分中按667/333训练验证；不能自动改写为三次轮换覆盖全体患者的标准测试三折。外部BraTS-SSA40患者与WUSM175患者。nnUNet/nnFormer、弱/强中间state、多模态组合和SegGen人工扰动生成不同质量segmentations，DeepMedic作为训练未见分割器。样本/segmentation数不是独立患者数。

训练与测试都按真实DSC十个bin重采样（block30）；测试重采样后4753/1204/2693个segmentations覆盖各质量水平。这是分层质量诊断条件下的结果，不能直接代表自然患者分布的筛查收益、部署coverage或总体净费用。将此策略迁移到本项目时，可以在开发训练内平衡标签；确认评价仍必须保留所有原患者、所有series及自然分母。

四模态主结果与本项目仅observed T2差别很大。主文Table4报告DSC预测r在内部/BraTS-SSA/WUSM为.968/.964/.912，SEM平均Dice在Table6为.769/.702/.684；Appendix E的T2-only对应r为.581/.635/.538，SEM Dice为.429/.363/.349。附录T2也是原BraTS预处理MRI，不能当作本项目稀疏异质T2的已验证可迁移效果。

训练A100、100epochs、batch4、AMP，含普通空间/强度增强与调参。主结果由三个模型质量均值和SEM多数投票组成；Table F的16.59M参数、296.64G FLOPs为单架构，不能据此声称完整QC pipeline只耗一次单模型forward。应另计分割路径、样本生成、三模型训练/推断、阈值/特征提取与调参费用。原文未提供本机完整pipeline时间。

### 原文歧义及静态源码审计范围

Appendix A block176把正确background描述为FP；UMap公式block180仅列50次softmax概率均值，未显式应用entropy/variance；SEM Dice loss写了1/V归一化且CE公式只列正类项；MAE“比MSE更敏感outliers”的解释可疑；learning-rate搜索上限2e-4而最优表列2.1e-4。保留原文，不自行修正作者计算，也不据这些文本歧义判整篇结果无效。

作者公开repo [sotiraslab/QCResUNet](https://github.com/sotiraslab/QCResUNet)，本轮固定commit e9ddc2418c72cc1c20b69bd3074b7f96b8b5f408。仅完整读README、utils.py、dataloading.py、main.py四文件；未clone、安装、import/执行作者代码、下载权重或审完整repo。commit API403失败、初版HTML解析KeyError均保存，V2仅解析已取得HTML，无新增GET。

静态AST加独立Signature.bind发现main74/75的RegDataLoaderV1调用只有五个必需位置实参，定义需六个，因此缺batch_size；README中qcresunet34/50例子不在已读main argparse choices。main使用CSV scalar目标与单二值query/label mismatch SEM；四文件不足以证明完整DSC+NSD+多区域论文pipeline。main导入losses中的DC_and_BCE_loss/PearsonCorrLoss，所读根清单无losses.py，实际loss实现与指标生成CSV尚未核。以上均是固定快照的准备缺口，不是作者论文运行失败的实验结论。

[已执行CPU静态/语义审计](static_semantics_attempt01/receipt.json)真实2b1bbc exit0：16个GT/query解剖标签组合中6个逐区域XOR错误图不满足WT/TC/ET嵌套关系，因而Appendix D按解剖标签重新合成的可视化不保证等价；这只限定可视化代数解释，不否定原逐channel SEM评价。单二值任务中E=P XOR GT，FP=E AND P、FN=E AND NOT P在全部四组合精确成立，signed-error方向可由query加error恢复，本身不足以构成创新。该审计未读取MRI/GT/model数组、未神经forward、未初始化CUDA。

## Jungo2020：强 uncertainty 对照应包括合理聚合

来源：[Analyzing the Quality and Challenges of Uncertainty Estimations for Brain Tumor Segmentation](https://doi.org/10.3389/fnins.2020.00282)，Frontiers in Neuroscience，2020-04-08，PMID32322186、[PMC7156850](https://pmc.ncbi.nlm.nih.gov/articles/PMC7156850/)。精确DOI身份匹配后取得公开fullTextXML，SHA256 7c71cfa634f58afa53c79c3787de61091a818406482766ee400cc45e73fda6aa。核读提取blocks0–115，其中主文科学内容0–97；表1逐单元格核读。未取得外链补充文件，未审图像像素或作者源码，未核TableS5数值。

BraTS2018共285患者，四模态，训练100、验证25、测试160，按肿瘤grade分层。架构是五连续轴向slice输入、预测中间slice的2D+1D U-Net，输出三个独立sigmoid区域；不是本项目稀疏VS任务，也不是同样的3D上下文模型。共同50epochs、batch24、CE训练，验证Dice选择best，没有数据增强。作者主动限制调参以减少分割能力差异，但也承认不确定性改进可能来自分割本身改进。

最关键原始定义（blocks19–25、32–34）：概率均值p_bar用于分割；不确定性使用归一化二值entropy H(p_bar)。这与QCResUNet Appendix B仅写UMap=p_bar不同。不能凭文本认定QCResUNet实际作者代码遗漏entropy，但本项目后续实现必须明确区分mean probability、predictive entropy、sample variance与mutual information。禁止将p_bar直接高阈值化后称已忠实实现Jungo uncertainty。

比较包含单次sigmoid entropy、四种dropout布局/概率、aleatoric、10-model ensemble、auxiliary error预测网。auxiliary feat.用分割feature map加三层1x1卷积，auxiliary segm.用四模态MRI加三label maps，直接学习分割错误。这是2020年已有的脑肿瘤错误位置/FP-FN监督先例，比“新加signed错误头”的说法更直接。

U-E以error与thresholded uncertainty的Dice计算，只在25验证患者从.05到.95以.05步长选择阈值。校准评估包含脑内而非大量颅外背景，报告患者ECE均值；数据集整体校准好不代表每患者校准好。原文WT/TC/ET患者underconfidence比例39%/30%/21%，overconfidence25%/32%/41%，well-calibrated仅36%/38%/38%；这是其原研究结果，非本项目估计。

患者聚合比较负mean、边界/距离/体积先验的九种组合加RF、102个radiomics特征加RF。负mean接近随机、ET甚至AUC<.5；更强的边界/距离及自动特征聚合改善failure检测，不能只用平均entropy做唯一强对照。shape sphericity、run-length nonuniformity的重要性是既有先例。表1ensemble WT U-E .436、Dice .880；baseline .427/.869；center-low+MC .435/.881。方法差异有分割质量混杂，且auxiliary error网未显著胜过简单基线。原文并未验证具体修正动作后的患者净收益。

失败定义用BraTS2013文献inter-rater Dice，因为BraTS2018未提供该值；原文也明确标签/标注修订可能不同。本项目保留既定六医学门槛，不能移用上述阈值。Youden accuracy通过ROC曲线最大Youden点报告；正文没有给出独立部署阈值冻结的完整证据，不能当作独立确认后的部署accuracy。外链补充的RF训练细节、抽样次数、表S5与成本仍是缺口。

## 仍值得探索、但尚未确认的窄候选

研究对象仍为异质T2，不能把全部series统称CISS。候选应落在：在仅合法observed输入下，针对明确缺层动作，预测动作前后任务损害的变化，并用全患者质量与全部费用验证是否优于强QC/error-cost/defer和直接任务基线。关注missing/tail区域的小病灶FN及体积损害，但不把这些区域、收益监督、患者分组或预算约束单独当新意。

要成立，首先native与合法raw分割须具备原六医学能力；然后在合法开发fold内取得具体动作真实可修正余量，比较预算/容量/输入/监督匹配的控制，包含联合动作交互、拒绝/保留及失败成本；最后冻结后只开8未见确认患者/12series一次，并增加独立任务网。当前原训练与99步pilot均未过医学门槛，新2992步四分支仍live，因此尚不能进入收益头claim或未见确认。

原QCResUNet/SynthSeg+都以绝对质量为重点，区别并不能自动证明动作净收益首创：此前SafeRestore、MoEDiff与defer/cost-sensitive先例已读。本轮收紧对照与实验边界，而非作“无人研究”的结论。具体后续准备见[可执行条件与公平控制](STRONG_QC_AND_ACTION_PREPARATION.md)。
