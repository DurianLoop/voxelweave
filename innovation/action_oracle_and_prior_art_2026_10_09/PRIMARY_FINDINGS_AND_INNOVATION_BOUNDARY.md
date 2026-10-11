# 本批阅读与项目决策

当前没有可发表且独立确认的 claim。更优先的工作是补强患者间任务泛化和实际候选动作，再检验采集信息是否改善动作净收益决策。已有两个whole-series流程的选择余量不足，不能靠新路由头弥补。

本批继承已完成的两篇完整提取文本阅读：330块、22个表文本；另读作者公开toy实现21文件631行。阅读覆盖和原始XML/表/公式/工具范围见 [READING_PROVENANCE.json](READING_PROVENANCE.json)。图像像素、外部补充材料未读，图像公式未完整解读；索引/摘要/下载不计主文，已读范围不重复增加。

## Dynamic expert routing（2026）

原文：[DOI 10.1038/s41598-026-48187-x](https://doi.org/10.1038/s41598-026-48187-x)，[PMC13230987](https://pmc.ncbi.nlm.nih.gov/articles/PMC13230987/)。156块/14表。直接先例包含top-k专家、LoRA、跨模态KL/contrastive consistency、MC不确定性解码、边界损失和课程。实验是BraTS缺对比模态，不能当本项目CISS缺层的效果证据。

原文的300epoch课程为40%WT、30%WT+TC、30%全；3fold×5seed的15配对观测不是15独立患者。held-out fold又被称validation/testing，early stopping在73/75块描述不一致，不能据此认证内折选择与独立外折确认。134/135块承认未按scanner/field strength分层、真实异质临床泛化待验证。

必须保留数字差异：BraTS2019 Table3/5 full WT/TC/ET=.912/.878/.835，Table11/abstract=.918/.889/.852；BraTS2020 Table4/5=.918/.884/.842，Table12/abstract=.924/.894/.861。92块边界数字与Table4不同；Table5“best baseline”不完全等于Table1/2数字。108块提及仅10images配置测试，与全cohort实验的关系未明确。这些差异限制精确比较，不据此断言作者结果无效。

Table6报告38.2M参数/191.6G FLOPs/.82秒/7.4GB；98块另说4 stochastic passes及single-pass .74秒。缺少本项目完整FOV、全部MC/准备/适应费用的对应口径，不能直接作为实际部署费用。20个display公式在XML中是GIF、常有inline符号缺失；不能以toy配置补填正文未读到的P/k/r等值。

## Source-Free Active Domain Adaptation / RUGS（2026）

原文：[DOI 10.3390/brainsci16030300](https://doi.org/10.3390/brainsci16030300)，[PMC13023837](https://pmc.ncbi.nlm.nih.gov/articles/PMC13023837/)。174块/8表。source-free允许没有source数据，但主动选择目标数据并人工标注5%，再用MeanTeacher半监督；不是无目标标签的TTA。

区域选择是SLIC entropy map，400regions/compactness .05、Kmeans K=2、高不确定region数>=βNs且β=.1；约束region数量不保证真实foreground覆盖。pool=5B，uncertainty+core-set diversity，λ=.5；flat-score归一化和tie处理正文不足以认证。2D224²、逐slice重建3D，152/155块承认没有inter-slice建模，且用全4模态。

source7:1:2/300epoch；target20kiter、batch16=4 labeled+12 unlabeled、5fold+earlystop。5%预算按slice还是patient及实际outer fold list仍需核代码，不能从正文认证患者隔离或认定泄漏。Table3 RUGS ET58.42而full fine-tune59.50，不能说超过所有全监督上界；Table8 RUA+core-set的WT/recall比UGCS更高，其他指标另有取舍。Table7的10.17ms仅2D网络推理，不包括全pool扫描、SLIC/Kmeans、core-set、人工标注、20k适应或全volume。

24式有MathML，flattened正文已读；未逐式解析全部XML。公开作者GitHub URL此次返回404，未获得实现、未复现、未联系作者；失败记录保留。

## 作者routing实现能提供什么

[原ZIP与下载凭证](routing_author_code_attempt01/receipt.json)保留Zenodo18331077的17,555bytes原ZIP并核作者MD5。README明写Educational reference implementation / tiny synthetic example；50epoch、4experts/top2/rank8是toy设置，不是已认证论文全配置。

静态读码发现：LoRALinear默认freeze_main=False，encoder没有显式true且训练随机初始化；decoder没有MC/dropout/UQ gate；engine仅Dice+BCE、没有正文CMC/surface/load balance；avail未传给model。专家对全token batch求值后mask，不能由top2直接宣称稀疏计算或两专家的实际费用。toy用互斥y==1/2/3，不是直接可用的BraTS嵌套WT/TC/ET定义。

PatchEmbed实际input/4，最早feature命名s8，decoder最终×8，按源码推导64³将输出128³；slider的range没有补最后start、norm零改1可能漏tail；infer忽略in-path使用toy第一个val。以上是静态推导，未执行作者代码，不称实际runtime已失败，也不推断作者真实研究实现必有这些问题。

## 结合已有项目保留的假设

| 优先级 | 可检验问题 | 本项目需要的新增证据 | 否证后处理 |
|---|---|---|---|
| 1 | 普通分辨率/GIN/SSC等强控制能否改善患者泛化？ | 原预算/原监督六臂、完整FOV、严格患者cold-init fold；SSC需复制通道和同容量对照 | 若只有开发收益，停止用其支持临床泛化 |
| 2 | 新SR/固定TTA等实际动作是否有安全净收益余量？ | 合法observed输入的真实成对FOV预测，完整FN/FP/费用/fallback/defer及患者分母 | 无余量则扩大或改进动作，不训练收益选择器 |
| 3 | 采集信息是否在同信息risk差/QC/defer/强static之上改善选择？ | 去采集、metadata-only、同容量risk差、always/none、费用匹配random；所有规则内折冻结 | 普通增强或risk/QC消去增量，则收窄或放弃此claim |

gain=L(a0)-L(a)与同信息action-risk之差存在等价；换head名字不是创新。缺模态MoE/UQ、region-UQ预算选择已有直接先例。可保留的窄问题是**本项目合法采集信息在明确动作集合和真实医学费用下的额外决策价值**，目前只是待证假设，不称首创。

4已见验证患者不作新独立确认；8未见确认患者12series与lockedIXI关闭。含11开发GT的19998 parent仅用于开发能力诊断，严格LOPO必须cold-init。原六医学gate与数值gate不降低。
