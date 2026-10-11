# MRI 策略／任务目标原文核读

新增两篇原文，33 个完整文字页、11 个不同物理页的视觉核验。另有同一 Diagnostic 第 11 页表格放大核对，不计第 12 个视觉页。提取 receipt 的 text_read=false、渲染 receipt 的 visual_reviewed=false 是生成时来源快照；实际阅读由 READING_PROVENANCE.json 追加记录，不修改原 receipt。

## L2SR: Learning to Sample and Reconstruct for Accelerated MRI via Reinforcement Learning

Pu Yang、Bin Dong；[arXiv 2212.02190v3](https://arxiv.org/abs/2212.02190v3)，下载原文 [PDF](primary_attempt01/l2sr.pdf)，SHA256 `013b46d0a79f9c31a4adc3f3db56def1b0fb2a699f6fcd69ad171d836f1269af`。31 物理页；完整文字读 1–21、27–29，视觉核 7、9、14、16、18、29；22–26 的符号表／证明没有完整阅读，30–31 参考文献没有完整阅读。未访问代码仓库／训练代码，不能称实现复现或独立验证 theorem proof。

方法的动作是新获取 k-space Cartesian column，观测 `y_t=M_t F(x)` 随动作改变。Dense POMDP 用重建 `x_t=R(y_t)` 提供策略状态／每步 similarity increment（Eq3.8）；sparse POMDP 用已获取观测驱动策略，只有终端重建和 `r_T=S(R(y_T),x)`，γ=1（Eq4.1–4.6）。这是减少中间重建与终端收益的既有策略，不能改称本项目的新“只为任务收益执行必要修正”。其 `image-less` 采样阶段仍可做 IFFT／CNN feature extractor（p14 Fig3），不等于无任何图像域运算。

训练分 fixed L2S 和 joint L2SR。后者先预训练恢复器，再交替固定恢复器训练 A2C sampler、固定 sampler 训练恢复器（p11–13／Alg2）；联合训练、适配采样分布和检查 frozen-vs-adapted 已有。Appendix C/D（p28–29）记负 SSIM loss、A2C lr=.0003、alternating reconstructor 10 epochs、lr 每轮按因子 3 衰减；Random 50 epochs、validation early stop，PG-MRI γ=.9。尚无精确统一训练秒数账，文本称 L2SR 训练时间可能为既有 dynamic 的 3–5 倍；不是我们本机的费用记录。

实际训练 similarity 是 SSIM；p13 明确说可换 PSNR、WGAN 或 downstream task metrics，但本篇核读的实证是 PSNR／SSIM，没有病灶 Dice 或分割效应。不能把“可换指标”当已经证明 MRI 下游临床收益，也不能把其明确提及 downstream 后重新包装成完全新概念。

理论范围：Theorem1 是连续函数空间下 joint sup 不等式。Theorem2 还需 terminal mask 全支持、恢复器实现该目标的 argmax 等条件（p8–10，p9 已视觉核）；不是有限容量网络、有限计算、局部最优训练或本项目强适配后的保证。本轮没有完整读 B1/B2 证明，不能声称已经核验其证明，亦不新提同名理论。

数据（p14）：single-coil knee 中心 crop128²，半数 volumes、去除 outer slices；train6959／validation1779／test1715 **slices**。brain 为 multi-coil 来源、crop256²、五分之一 volumes；11312／4372／2832 **slices**。文中分配叙述及这些数不能给出独立患者总数／每 split 患者数；本轮未核 patient ID 清单。其图像形式和本项目固定 CISS native-plane 观测不同，不能直接套 acquisition trajectory。

费用有实质对照（p18 Table3，p15 setup V100）：`TCπ+(T+1)CR` 的 PG-MRI，对比 `TCπ+CR` 的 L2S/L2SR；表中包含策略和恢复器的算法推理费用，不可声称“只报恢复器时间”。knee x4 Base 均值 .0843s vs .0201s，Random/LOUPE .0040s。它支持减少中间重建的费用先例，并提醒 learned policy 比静态便宜 baseline 仍有开销。本篇没有本项目完整患者启动、IO、定位、transfer、组合、失败路径等九阶段实测，不能用 V100 的 knee 均值替换 CISS 完整患者费用。

Table2 p16 的 brain×8 子表列名写 PSNR／SSIM，但数值量级与其他表相反；brain×16 Random 首项原文确实是 80.31。这些是已视觉确认的原文异常，不是提取错误。本轮不猜改数字，不用异常列做量化新结论。其余结果也不是所有设置必胜，例如 knee×8 Base 的 τ-Step Seq 在 SSIM／PSNR 高于 L2SR。p21 明确记录无 alternating convergence guarantee、长 horizon sparse exploration 难度和拟将来适配实际 scanner。

## The MRI Scanner as a Diagnostic: Image-less Active Sampling

Yuning Du、Rohan Dharmakumar、Sotirios A. Tsaftaris；[arXiv 2406.16754v1](https://arxiv.org/abs/2406.16754v1)，原文 [PDF](primary_attempt01/diagnostic.pdf)，SHA256 `35acc0161d68f4ec6f372bd813caeb87e0670684ee3ccaf3c650c0950828d36e`。11 物理页；完整文字读 1–8、11，视觉核 4、5、6、7、11；9–10 参考文献未完整读。代码链接存在但本轮没有打开，不声称复现。

任务是在 fastMRI／fastMRI+ knee slices 上判定 Meniscus Tear。每一步用 undersampled k-space IFFT 后的低质量图输入预训练 classifier，classifier feature 经 pooling 后给 policy，再采新 k-space line（p3–5 Fig2）。所以没有 learned high-fidelity reconstruction 阶段，仍有 IFFT、image-domain classifier 和每步 policy。它已经明确采用当前状态下的任务预测收益训练动作选择，不能称本项目首次“直接优化诊断而非图像质量”。

p4 写 `R=r(y_{t+1},g)-r(y_t,g)`，称 criterion r 为 cross-entropy、并最大化 return；正常 CE 越低越好，单凭这个文字方向不能直接抄为训练 recipe。已视觉核该页，代码实现符号未核。记录文字／代码待核问题，不推断作者实现错误，不从该符号建立新方法。

Classifier 是预训练并保持的环境。任务策略 classifier 用不同 undersampling rates／center fractions 预训练，ResNet50 改 dropout 共25.6M参数；policy11M，使用最后两层特征。重建策略对照用837K U-Net、L1训练、SSIM reward，结果由 full-image Oracle classifier 评价（p5 Table1及描述）。这不是双方都充分用病灶目标适配的强同观测同容量最终 pipeline。讨论 p8 也将 simultaneous classifier-policy training 列为后续方向；本项目必须先满足强适配，不靠 frozen classifier 失配制造收益。

数据 p4：1100 **volumes**、39125 slices；train32035／validation5249／test1841，MT占比分别11.8%／9.3%／11.1%。三 split slice 和等于39125，但正文核读范围没有每 split 患者数／ID不重叠证明，不把1100 volumes或39125 slices直接当独立患者分母。预处理先 IFFT 后 crop320² 再 FFT；这是回顾性数据上的模拟逐线采样，不是本轮记录到的真实 scanner 在线诊断试验。低场／POC 可行性是潜在用途，不是已验证低场临床效应。

训练 p6：classifier／reconstruction 30 epochs，policy20，Adam1e-4；q=8 平行候选只用于训练 reward 估计，推断逐线获取。初始5%=16行，额外64行到25%。Method说耗尽预算或达到user reliability即可停止，但核读结果没给出经校准且实测的临床安全早停规则。25% k-space是采样量，不能冒充相同倍数的完整在线部署墙时节省；本篇没有策略＋classifier每步的完整推断秒数／失败账。

端点必须逐项评估。p6 Fig3和p11 Table2表明 task classifier 较 reconstruction policy 更多体现 specificity 与 recall 的权衡；本輪 CPU 数值核查见 [表格后果](TABLE_AUDIT_IMPLICATIONS.md) 与 [原始复核 receipt](table_audit_attempt01/receipt.json)。按三 center fractions×六sample rates，AUC与Recall各1正／17负、Specificity17正／1负（PC减PR）。这是论文报告的18个相关设置，不是18患者、18独立重复或显著性证据。不存在“在强适配后 task policy 全面优于 reconstruction”的证明。

本篇还指出约19–21行时 policy 行为受 classifier 原先随机采样训练分布影响（p7），并把 classifier/policy joint training 列为限制（p8）。这直接支持我们记录并冻结特征产生模型、动作分布和checkpoint；只训练 gain head，而任务模型同时变化，会令旧feature／收益关系失效。这是已知的模型耦合问题，本轮准备是实验控制，不是新算法首创。

## 对本项目可保留的问题

两篇均通过动作改变获取的 k-space，当前项目是给定 CISS 观测后的插值／投影／任务路径，因此它们不是直接同条件 baseline；其策略概念、任务收益和适配控制仍是实质先例。剩余问题只能诚实写为待验证的 MRI 机制／应用：在**同固定观测、充分任务适配和同容量**下，表示或合法修正能否留下病灶余量；若有，状态特征能否预测相对收益并在完整费用下超过固定强动作、条件成本／defer／DC-based 控制。

已有旧9series标签的弱模型能力未通过、完整cost为null，这些不能训练新正式head；native参照含额外信息，不能当可部署动作。具体准备见 [状态稳定与后续实验](POLICY_STABILITY_PREPARATION.md)。原两臂final→56FOV→全部六能力gates→strict→三臂真实资源资格→另冻正式强适配→余量／全费用→强控制→8未见确认的顺序保留。当前无新MRI效应，无可发表claim。
