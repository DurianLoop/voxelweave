# 架构覆盖闭环：详细中文变更报告

最终 PDF、版面修复、实际引用内容保留核验和入口文件记录见 [交付补记](DELIVERY_NOTES_ZH.md)。完整 MIRA 报告卡位于补充材料，主文保留 13 行覆盖表和五核心模型数值表。

本轮只处理当前CVPR稿件，TMI未改动。工作范围在新实验前冻结：13模型适用性审计、剩余核心的合格 acquired-only 复测、兼容已有基线的相位覆盖，以及稿件和报告卡重组。没有训练、加入新模型/队列、评分公式或阈值搜索。

## 完成范围与实际计数
- 重建记录：13个实现，111个配置；原生PSNR/SSIM/MAE/MSE/NCC、20个预算比较与负结果保留在补充材料。
- 物理相位干预：13/13接口已完成；其中五核心仍为主跨模型实验，另外八个只做明示退化self-control的次要相位敏感性。因此“重建证据之外完全没有相位证据”的模型为0；不等于13模型都验证连续机制。
- 严格acquired-only：3个模型已实测有效（HAT/SwinIR/SAINT）；5个额外接口可用未运行（Linear/ACVTT/ArSSR/ResUNet/SMamba-UNet）；5个在当前精确合同下不合格（Cubic/Res-SRDiff/CycleINR/Pix2Pix-GAN/I3Net）。可用而未运行的模型不得计为验证成功。
- 稳定性：3个实测模型在两个脑队列各自门槛下PASS，共6个stratum。HAT/SwinIR .85、SAINT .90；既有六-stratum aggregate gate仍NA。数值稳定与beyond-count区间阳性分别记录。
- 固定上下文：3个模型有实际IXI证据；新SAINT仅在IXI稳定性通过后按既定12检查/四上下文/四幅度运行。

## 新 acquired-only 结果
详见 [五核心影响审计](FIVE_ARCH_ACQUIRED_ONLY_INFLUENCE.md) 和同名CSV。SAINT的最小稳定性为fastMRI .950686、IXI .996341。beyond-count分别 .032751与.132790；fixed-count分别 .379778与.417380，规定家族区间均为正。
新结果与历史SAINT空结果合同不同，均保留。该变化不是为了正结果重调掩膜、精度、幅度或门槛；本次先固定复用最终acquired-only合同，再推理。直接disagreement的fastMRI beyond-count只有 .002943（描述），不能以alignment的阳性代替直接误差/可靠性结论。

## 新固定上下文结果
SAINT四幅度的median相对近似误差为0.008%–1.069%，worst为3.199%。原HAT/SwinIR的126.4%最坏误差完整保留；48个新例均aligned，无opposing例，不扩张到未观察符号分支。恒等式闭合仍单列为代数核验。

## 扩展基线的解释限制
八个非核心基线均按原master x4 checkpoint与当前五目标注册运行两个脑队列，三种support全部保留。目标自身重复导致shared O=0，是构造事实。新增正ΔO主要确认物理相位响应与接口覆盖，不能当成八次独立shared-error机制验证。原五模型主矩阵未被替换，也没有结果导向扩展跨模型pair集合。
Res-SRDiff的源码实际使用Gaussian随机采样；不能沿用模型注释中“deterministic”的不准确标签。相位实验固定单一外生RNG状态，不搜索种子；这项条件化不自动使其满足原有限响应合同。
ArSSR现有wrapper接受变深度/stride，故列为潜在可用而未运行的有限响应接口；不能仅因为尚未写适配器就宣称结构不可能。CycleINR的既有有限响应合同另有明确四锚x4限制，不能在本轮静默改成双锚。

## 工程修复与可复现性
ArSSR首个目标选算检查发现0.0001220703125 native-unit偏差，超过事前1e-4容差；原结果未进入相位输出，失败日志保留。修复把坐标运算恢复为原wrapper逐步float32运算；两个队列/两个phase与完整wrapper最大差均为0。没有放宽容差。
Res-SRDiff完整体积网络推理耗时较长，采用省略无关输出神经计算的加速；仍逐步消耗每张未用切片的全部采样随机数。两个队列、两phase的首病例对照同时验证输出最大差0及最终CUDA RNG状态完全相同。已完成的原路径病例被保留，剩余才使用等价路径。
所有输入/旧证据只读。原3955数组在推理前重新核验哈希通过；22个本轮脑队列权重完整加载检查，所有张量有限。新响应在目标读取前绑定文件哈希。后续原数组独立重算与稿件保留检查见 REPRODUCTION_CHECK.md。

## 稿件变更
主文新增13行覆盖表，符号区分支持、历史空结果、资格/稳定性失败以及未运行。图3增加SAINT，保留原两模型及原最坏误差；所有五核心进入数值表和报告卡。摘要、引言、方法、结果、讨论、结论明确现象宽度与连续影响的更窄资格。完整重建排行榜仍在补充材料。
原稿快照：original_snapshot/manuscript。新稿：revised_manuscript。核验后仅将经审核的CVPR文件安装到原论文入口；原FINAL_SUBMISSION_PREPARATION交付包和TMI保留。

## 尚未解决的投稿风险
1. 数据与伦理仍 NEEDS HUMAN CONFIRMATION：NingXia批准/豁免、同意/豁免、脱敏及许可，精确fastMRI来源release/授权均不能由代码推断。
2. 方法创新幅度和大量回顾性复用仍是强审稿风险；本轮没有新的独立确认队列，bootstrap不覆盖全部历史选择。
3. 新八模型self-control是弱对照；不能说13模型共同验证MIRA机制。即使数值全部为正，也没有消除该设计限制。
4. continuous influence仍只实测三个兼容模型，且支持的是局部association/covariance趋势，不是全模型普适性、校准可靠性或临床噪声模型。
5. 原空结果、历史稳定性失败、mirror方向效应、弱/空排名、guard无明确收益、NingXia与Res-SRDiff负结果全部有效。
6. 原匿名投稿年份/编号等元数据仍需作者与实际投稿轮次匹配；本地交付不是已向会议提交。

## 终止
本轮边界已关闭。不得根据现在的正结果继续寻找更有利架构、score、mask、阈值或数据子集。论文证据有所加强，但无法从这些回顾性结果推导可信的接收概率。
