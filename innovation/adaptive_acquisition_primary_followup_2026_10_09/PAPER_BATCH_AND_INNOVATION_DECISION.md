# 本轮三篇原文、项目证据与可检验方向

本轮新增三篇固定版本 primary text 阅读（含 greedy 全部可用附录和漏抽取的 Algorithm1）。图注和表格文字已读；图像像素、参考列表条目、外部 supplement、作者代码没有读，不冒称完整图像/代码复现。OpenMASC 是既有 MASC 系列后续论文，不当独立重复验证。来源和实际工具 chunks 由 reading_provenance_attempt01/receipt.json 绑定。

| 原文 | 关键方法与核对结果 | 对本项目新颖性的约束 |
|---|---|---|
| [Experimental design for MRI by greedy policy search, 2010.16262v2](https://arxiv.org/html/2010.16262v2) | policy 梯度选择新 k-space 列；冻结16-channel reconstruction。gamma=.9 四配置比greedy提升 .0002/.0007/0/.0004 SSIM；greedy对test-GT NA oracle只有 .0017/.0021/.0007/.0008。附录明确 SSIM与PSNR可能偏好不同采样，greedy oracle也会漏掉组合效益。 | 贪心任务奖励、序列策略、适应性与组合效益均已有先例。新增测量不能当固定输入处理动作的证据；NA oracle不是可部署baseline。 |
| [OpenMASC, 2609.32343v1](https://arxiv.org/html/2609.32343v1) | 每cascade DCR、PPO、三阶段co-train。Table3同架构VD随机→full仅+.001 SSIM/+0.09dB；去DCR→full+.067/+6.17dB。autoPET20测试subjects×36slice=720；fastMRI800 knee也是合成metal。 | 大部分整体架构优势不能全归因策略。需要同架构同信息强静态对照。未验证真实植入物；slice配对p值不等于患者独立检验；跨trajectory共享权重需作者代码核验。 |
| [Active few-shot segmentation by reinforcing data selection, 2607.22371v1](https://arxiv.org/html/2607.22371v1) | PPO联合选择support set→人工标注→Reptile适配后validation Dice reward。589 T2/8机构；156 held-outvol、NB/OI；K实际上固定4，K8/16重复pool。另8个带标签validation用于reward。 | 联合集合互补性、按适配后任务收益选择均有直接先例。不是无GT部署处理动作。报告K时需同时交代reward标签、pool与适配费用、患者ID隔离。 |

费用边界：greedy附录Table3只是受cluster/I-O影响的粗略policy训练时间，不包括reconstruction预训练和部署；按wall×GPU数，brain-long greedy约4.5 GPU-days，nongreedy约20。few-shot meta约24h+RL约72h/双A5000，不代表本项目完整费用。表格算术由独立HTML td解析核对，不能从显示均值/SD恢复配对p值或贡献比例。few-shot K4显示差8.2/4.6pp与文字8.1/4.5可能源于舍入，不断言错误；K+8只能计标签槽位，唯一患者及重复使用待查。

greedy实现待核项：Algorithm1显示Update policy weights在acquisition loop内，而附录文字说累积完整trajectory后单次gradient step；此HTML层级差异尚未核作者代码。entropy的HTML alttext显示Σp log p缺负号；本轮计算按标准H=-Σp log p，不猜测作者真实实现或据此指控其图。Figure3/5/6/7和SNR附表明示选test表现最好模型，不能把这些可视化选择当本项目允许的checkpoint选择规则。

CPU可验证的结果：精确枚举6动作、20种3动作可选集合及独立二值图像的120行分布。策略只在可选集合均匀随机，完全不看图像，I(A;M,X)=I(A;M)=log2≈0.693147；I(A;X|M)=0。固定集合真正图像驱动的正控制conditional MI=log2，固定集合均匀负控制=0。熵恒等式、KL求和和另写auditor均通过1e-12 gate。这是一般评估混淆的反例，不是论文曲线复现，也不是本项目临床创新。条件互信息及链式分解本身是经典知识，不能占为新方法。

结合之前工作，主阻力仍是任务能力与合法动作余量：原最终模型医学gate失败，已见4患者9series上的两个whole-series流程GT oracle也只到.5545512725845162、512策略六gate通过0；这只约束那两个流程，不能外推新模型/局部处理都无效。当前六分辨率臂和19series GIN正式训练均未ready，不能靠更复杂selector弥补被证伪的候选动作集。

保留以下候选问题，均未获独立确认，按先决条件排序：

1. **原生采集信息是否能预测某个处理动作的患者净收益，超过同信息风险差模型？** 先获得通过六医学gate的强task，且实际固定输入动作oracle有改善余量；然后在strict LOPO cold-init下学习delta-task效用。对照需含metadata-only、risk-difference、agreement/SSC、强static、identity、random、QC/defer，并同输入信息、同可选集合、同计算预算。贡献必须落在实际患者净收益及跨合法采集条件泛化，不能只是“用metadata/RL/uncertainty选择”。
2. **固定输入上的动作组合是否存在可重复互补收益，超过单动作强对照？** 独立证明局部动作/序列能改善病灶指标后，比较联合模型与固定顺序、单步greedy、随机、最优开发静态组合；显式固定可选集合与动作历史/费用，加入mask-only和条件shuffle控制。本批few-shot已覆盖联合集合思想，greedy已讨论组合非贪心，所以“联合选择”本身不新。只有额外病灶收益和可辨识机制才有潜在贡献。
3. **新增测量与固定输入处理的收益边界。** 当前只有magnitude/重采样工作流时，不把FFT(magnitude)冒称真实raw k-space。真实主动采集研究需要合法原始复杂k-space及forward model、轨迹/测量费用；现在仅列准备条件，不把模拟测量结果嫁接到当前clinical任务，也不开放确认集。

待执行登记见 FUTURE_EXPERIMENT_REGISTRY.json。采用既有医学gate：患者先均值fullDice≥.70、missingDice≥.65、recall≥.70、absRVE≤.50，各患者full/missingDice>0、无series零TP；数值3e-6、坐标3e-12、二值0不改。强task和真实动作余量未达标时停止policy收益claim。所有臂strict LOPO从cold-init；19998 parent只作开发诊断，4已见验证不当新确认，8未见确认12series/lockedIXI保持关闭。新增GPU授权有效，但不能跳过人工失败去跑真实资格。

本轮数值定位另见六分辨率目录 ROUND50_RESEARCH_AND_VALIDATION_RESULT.md：FP64 norm数学通过，完整人工模型参数gate失败；最坏两个小梯度同为正，AdamW首步敏感性解释该差值。它是训练可信度诊断，不能当新医学方法或发表claim。
