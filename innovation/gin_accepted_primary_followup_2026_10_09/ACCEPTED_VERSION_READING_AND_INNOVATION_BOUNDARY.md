# GIN 录用稿全文及本项目后续实验边界

本轮读的是 Imperial Spiral 官方仓储标注 Accepted version 的论文 **Causality-inspired Single-source Domain Generalization for Medical Image Segmentation**，Ouyang 等七作者，DOI10.1109/TMI.2022.3224067。仓储 acceptance2022-11-01、online/issued2022-11-23，对应 TMI42(4)1095–1106（2023卷期）。PDF 首页 VOL.XX/XXXX2020 是模板占位，不能据此改发表年。不是出版社排印 final，也不是新的一篇论文；与前轮 arXiv2111.12525v5 是同一研究的不同版本。

实际读完12页提取文本、逐页查看12张原文render，包括8图、7张编号表、6个编号公式、Algorithm1和73条参考列表。前1–3页在传入轮次已经完整重新展示；4–6页本次独立重新展示，7–9及10–12页分开读取避免工具外层截断。下载/提取时的 false 阅读标志保持原状；另立 provenance，不修改历史receipt。没有读取外部supplement、下载新作者源码、执行作者仓库或获取出版社收费版本。

来源链为仓储公开 SSR 页面中明确给出的匿名 REST content 链接：`https://spiral.imperial.ac.uk/server/api/core/bitstreams/9f1f03f2-fac1-4402-8045-9f9455fdac2d/content`。citation UI 的 download GET 实际405保留，随后正常 GET 公开content成功；没有认证、cookie、HTTP方法或权限绕过。PDF4498435bytes、SHA256 c9b7dc075caceb7bc53743dbd7a138e774637fd1e18697c575ca972f11be8c56。元数据closed并不等于机构不存在公开accepted稿。

| 对照位置 | 早期 arXiv v5 已读内容 | 本次 accepted 稿实际内容及影响 |
|---|---|---|
| 数据/预处理 | blocks76：CT窗[-275,125]，2D192²，MRI top0.5%/zero-mean unit-variance | p7：CT窗[-125,275]，其余上述处理描述一致。两版本窗范围确实不同；本项目当前MRI诊断未应用CT窗，不暗改历史配置 |
| GIN | 4层/隐藏2通道、随机卷积、混合及Frobenius规范 | p5 Eq4、p8 TableIII延续；p9 TableIV增加插值和原图比例消融。去混合alpha=1为5.41，而默认86.04；这是作者腹部实验，不能外推本项目病灶数值 |
| IPA | 低频map、互补混合；TableIV给器官分项 | p6 Eq6、p7控制点间距图长1/4；p10 TableV加入scalar Mixup和六个前列腺方向分项；superpixel仍是已有方法 |
| 无IPA/有IPA | 腹部86.04→86.31、心脏83.83→85.01、前列腺65.10→70.37 | 主要数值相同，不算重复独立结果；accepted CT→MRI +0.27/MRI→CT +0.22均标p>0.05。心脏superpixel85.97高于默认85.01，scalar在前列腺E也更高；不能声称默认逐任务全胜 |
| 损失/训练 | Eq3两视图监督与KL，EfficientNet-b2 U-Net、Adam lr3e-4/2k epoch | p4 Eq3和p7配置保持这一描述，lambda_div10。未澄清固定作者trainer的三视图/只监督第一份/attached KL(mean||each)差别，不能把原代码称本文公式逐字复现 |
| 源域/ensemble | blocks102仅描述源域损失和可能动态架构 | p9–11新增源域分析、TableVI/VII以及基于预测重叠度的明确选择：Dice>95%取ERM、85–95%取均值、更低取DG。端点=两个预测的一致度，不用测试GT作决策 |
| 时间/显存 | 已读早期主文没有相同量化段 | p11：RTX2080Ti，GIN/IPA约19秒/epoch×2k、10.6GB，ERM约9秒/epoch、4.3GB。是作者2D配置，不能当我们3D时间、分辨率加速或实测预算 |

源域ensemble TableVI的ERM target分数不同于TableII；p10脚注7说明这里ERM按source-domain最佳表现选择。比较必须保留这个model-selection差异，不能把两表直接拼成配对收益。本稿主要显示 acquisition appearance shift；因果假设 A/C独立且content跨域不变。患者、病灶或解剖分布变动未自动被此假设覆盖；GIN/IPA合成不是额外测量信息或真实物理采集因果干预。

固定作者commit d4d5056ded88951fc3967f8f294f4a12420e13c6 的README已有3D GIN、3D IPA仍待发布；此前已读七文件1489行，不重复计本轮新增代码阅读。作者代码的norm分母+1e-5、AdvBias离散box factor及最终bilinear与主文cubic描述，仍保留实现边界。当前独立适配器的3D binary TaskUNet、AdamW1e-4、三视图coefficient0.1是本项目公平对照适配，**不是原2D EfficientNet/Adam3e-4/lambda10精确复现**。后续须冻结适配与paper-objective两种明确命名的配置，并把强普通臂及全部费用一并比较，不能因一次诊断失败便调lambda来过gate。

新颖性判断据此收紧：随机卷积、3D迁移、空间混合、破背景相关、基于预测一致度选模型均已有先例；本轮数值排查与内存工程不是新方法。可继续检验的研究假设是：在强task能力和真实动作余量存在时，合法采集信息及实际动作响应能否提高患者级动作净收益，超过同信息action-risk差、QC/defer、metadata-only、static、random，以及本文agreement selector。这个组合的独立新颖性与收益均未确认；确定性变换响应不能声称增加MRI测量信息或保证发现hallucination。

后续冻结顺序：先通过完整schedule、fullFOV、19series optimizer图资格；完善低频3D IPA场的独立检查；在同11开发患者19series/cold-init/母GT/basic几何与强度增强基础上比较basic、GIN-only、GIN+IPA、consistency和源域agreement selector。每臂同时曝光匹配与实测计算预算匹配，普通臂可用同预算更多更新，真实action/全部FOV/cost不得只选有利crop。若没有task能力或动作余量，停止该候选的效益claim。训练parent见全部开发GT，不能作strict LOPO外折init；4已见验证不再当独立确认，8未见确认12series和lockedIXI保持关闭。六医学gate、数值gate、患者级净收益端点均保持。

本轮新增accepted-primary-version全文阅读1次，新增distinct论文0；不能把版本比对当新文献批量数。当前没有独立确认、可发表的claim。
