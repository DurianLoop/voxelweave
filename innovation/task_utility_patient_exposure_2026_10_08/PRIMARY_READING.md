# TACKLE 与 DynamicDPS 原文核读及本项目碰撞

本阶段新增独立原文两篇，取得固定版本后阅读。DynamicDPS 11页全部文字，包括参考文献；TACKLE 完整文字页1–12、15–19共17页，13–14参考文献仅部分定位、输出曾截断，不计完整阅读。合计28个完整文字页。实际视觉核看六页：DynamicDPS 4/7/8；TACKLE 7/11/15。历史 extraction/visual receipt 中 read=false 保留，另见 [阅读 provenance](READING_PROVENANCE.json)。未运行作者代码或复现论文实验。

公开索引首批三查询及收紧三查询来自 [原索引 receipt](index_attempt01/receipt.json)、[收紧 receipt](index_followup_attempt01/receipt.json)。TACKLE题名检索受词干匹配影响、两条精确措辞返回0，不能据此说文献不存在；收紧摘要词检索实际找到正确题名 Learning Task-Specific Strategies for Accelerated MRI。Crossref近似题名排序混入大量无关记录，不拿669368总命中做相关论文数量或系统综述。原文URL来自实际Atom PDF链接，未猜ID。

## Wu等：Learning Task-Specific Strategies for Accelerated MRI

[arXiv2304.12507v3](https://arxiv.org/abs/2304.12507v3)，2024-11-06版本，首页 IEEE Transactions on Computational Imaging 2024；索引 DOI [10.1109/TCI.2024.3410521](https://doi.org/10.1109/TCI.2024.3410521)。核读的是 [19页作者PDF](primary_attempt01/tackle.pdf)，不声称与出版社版本逐字核过。

方法覆盖：sampler + E2E-VarNet retriever + task predictor 联合训练。先用全FOV PSNR预训练采样器/检索器，再加入随机初始化任务头、全部finetune（p5）。下游包括半月板ROI重建、脑/膝组织分割、BraTS FLAIR切片胶质瘤存在性分类。retriever明确可以输出不符合通常图像相似度的任务表征（p4、p8、p19）；所以“恢复未必最优、直接优化任务表示”已被原文覆盖。

观测/采样：可学习Bernoulli概率，训练时容差内采样；测试选top-b、所有volume slices共享同一mask。sampler无需患者输入，只学习全局采样概率矩阵（p4、p16）。ACS占采样预算1/8。作者改变实际k-space采样，既不是固定CISS acquired层的后处理，也不是根据每个患者真实observed在线选择新mask。不能将其称作本项目合法增层动作，但必须作为任务驱动联合优化的直接先例。

强对照和结果：TACKLE_recon分别训练重建及适配任务网，TACKLE_seg端到端任务训练；Table II（p7）SKM-TEA 16x Dice .8232→.8532，64x .8145→.8357。Table VI（p11）提供predictor-only vs VarNet+predictor、预训练消融，直接预测器与联合模块参数约42.2M vs40.5M，属近似容量对照，不是本项目逐参数相等控制。Table V同时分解learned sampling与task-specific training；固定Poisson脑分割 .9257→.9256 并非每个格都增加。不能只用摘要称所有适配因素都有增益。

患者角色：Supplement B p15明确整患者train/validation/test划分；SKM-TEA给2935/1040/987切片而未在这些段落给相应患者数，不将切片当患者。OASIS每volume只取109th coronal slice、SAMSEG四类伪标签；BraTS“healthy/unhealthy”是切片上是否存在ED像素，不是健康患者与患病患者临床鉴别。模型按验证任务指标择checkpoint、10epochs无进步停止、lr在1e-2/1e-3/1e-4中选择（p15–16）。本项目已冻结最后模型规则不受此文回改。

外部/前瞻：p9–11用两个健康志愿者、每volume中间40slice做ROI评价，总80slice；采集硬件/对比/ROI均有shift，但不是80独立患者，也不是病灶确认。论文有slice-wise paired t-test；本项目不能照搬其slice分母作为患者推断。Prospective GRE扫描335→84s为实际采集时间，不是网络全部署时间；不能与本项目固定observed修正的计算费用作数值比较。p12限制指出脑分割/肿瘤分类为由magnitude图模拟的k-space，前瞻只一个GRE序列、需更多读片研究。

结论：排除宽泛“首次MRI任务驱动恢复/直接任务表示/预训练后联合适配”。固定观测下具体缺层动作的患者配对增益、同信息强cost/defer控制、交互及完整费用仍需本项目实测，不由不同数据名自动获得新颖性。

## Kim等：Tackling Hallucination from Conditional Models for Medical Image Reconstruction with DynamicDPS

[arXiv2503.01075v2](https://arxiv.org/abs/2503.01075v2)，2025-07-24；核读 [11页作者PDF](primary_attempt01/dynamicdps.pdf)。标题/版本/作者与Atom及首页一致。没有下载单独补充或验证作者仓库实现。

方法覆盖：conditional IQT预测作warm start；DCATS用与test分离的reference数据，在各diffusion time构建平均观测likelihood memory bank，再将测试预测的scaled likelihood匹配选起始t（p5 Eq4，tau=.4）。之后用无条件diffusion prior和data consistency修正，Wolfe line search动态选步长，DC loss含L2、Sobel和SSIM，权重.5/.1（p6）。这已覆盖“按观测一致性选修正强度/跳过扩散步骤”的宽想法。

适用条件：p4 Eq1的退化含gamma、downsample、Gaussian blur及噪声；本项目原生层几何/PSF未知时不能直接照搬A。Eq2又用线性伪逆/零空间形式A+与I−A+A；gamma一般是非线性映射，原文这些页未给线性化说明。此处只登记模型解释的适用条件，不宣布其完整方法/理论错误。未约束的nullspace中“更像先验”不构成个体真实病灶无幻觉证书；本文提供经验组织体积证据，不能搬成我们的病灶保证。

数据：模拟测试600images，IND 2.8mm/gamma=.7，OOD gamma=.4或4.2mm；p6这些段落未报告600images的独立患者数和完整subject split，保持未核实，不指控泄漏。真实0.36T T1是1×1×7.2mm，slice thickness6mm、gap1.2mm，对应HF注册主要用于视觉（p6–8），不同于本项目CISS x4缺层任务。

任务/指标：FastSurfer组织体积误差用 `2|Vpred−Vgt|/(Vpred+Vgt)`（p8），本项目absRVE以Vgt作分母，不能把百分比直接拼入同表。Figure3b与正文声称关键组织改善超过15%，图无逐病例表/误差条，不能从图估出本项目患者效应、显著性或病灶保真。论文未提供本文所需同observed、强充分适配任务网、双路径cost/defer病灶比较。

费用：Table1 p7 DPS196±.6s；Ours+UNet37±.8s；Ours+ESRGAN38±.8s，平均50 vs1000 diffusion steps。“5%步骤”与“5%总费用”不同：37/196约18.88%墙时，下降约81.12%。Wolfe每步可能有额外objective/gradient评价；引用step数量不等于所有forward调用。表中纯UNet/ESRGAN及无warm-start Ours时间为“-”，这些页没有硬件、完整cold-start/IO/reference bank预计算范围，完整成本边界未明。不能声称已实现本机加速或训练/teacher费用免费。

结论：固定观测一致性与自适应修正先例很近，需明确加入观测residual/DC-based动作强度选择控制；若后续MRI diffusion模型满足合法source/退化合同，可另立运行合同再比较。此文的医学目标主要组织体积与IQT，未直接证明或覆盖本项目强控制下的稀疏CISS病灶配对净收益。

## 这两篇改变哪些下一步决定

任务适配和表示必须放进同容量矩阵；若未来探索联合training，则增加固定观测下reconstruction-pretraining→task-finetuning，仍保持同source/augmentation/标注/预算。采样器不得读取隐藏MRI或修改当前observed集合。DCATS式可观测一致性排序属于已知强对照，不包装成新创新。

剩余候选定位为可检验的MRI机制/应用问题：同raw观测、足够适配后仍有可修正的病灶余量时，当前状态下的修正收益/交互是否可预测、能否在完整成本下超过既有条件成本/defer和固定强动作。现阶段没有真实动作任务标签、没有MRI收益、没有发表claim；普通经验确认与正式风险保证的校准条件继续区分。
