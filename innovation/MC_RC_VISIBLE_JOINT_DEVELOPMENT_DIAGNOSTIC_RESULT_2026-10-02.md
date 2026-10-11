# 五患者可见特征诊断：固定联合政策失败，收益标签与误差标签等价

按[新事后开发合同](MC_RC_VISIBLE_JOINT_DEVELOPMENT_DIAGNOSTIC_PLAN_2026-10-02.md)，实际提取五名既有开发患者的30项观测/候选/采集特征，并做五折leave-one-patient-out岭回归。每折仅其余四患者标准化、拟合、选择共同alpha；留出患者人工label/隐藏reference只用于最终监督复核和评分。240内部缺层、34,872支持tile，固定phase0/x4/tile32，alpha网格0/.25/.5/.75/1，λ=.01，无搜索/新网络推断/GPU。

[完整结果](experiments/mc_rc_visible_joint_development_diagnostic/attempt_01.json)和[合同](experiments/mc_rc_visible_joint_development_diagnostic/run_contract.json)保存13个固定政策、每患者全部端点和归档文件hash。可见包与监督包独立存放；可见函数不接收人工ROI、reference、oracle系数/alpha或身份。病灶监督为ROI内SSE除以可见支持tile像素数，不要求部署知道真ROI分母。这仍是开发，不是新确认。

## 失败结论来自完整患者，而非平均收益

| 患者 | 仅支持收益政策gain dB | 联合政策gain dB | 训练患者共同alpha gain dB | 联合两病灶guard | 联合完整门槛 |
| --- | ---: | ---: | ---: | --- | --- |
| 001 | -0.042501 | -0.066440 | -0.125196 | 均失败 | 失败 |
| 002 | 0.165214 | 0.039271 | 0.172735 | 均通过 | 失败（低于.1dB） |
| 004 | 0.570419 | 0.493958 | 0.548277 | 均通过 | 通过 |
| 005 | -0.035562 | -0.031182 | -0.633136 | 均失败 | 失败 |
| 006 | 0.450114 | 0.367433 | 0.380403 | 均通过 | 通过 |

gain参照该患者raw/HAT较低支持域NMSE端点，病灶guard参照各项raw/HAT较小端点；不把它改成raw-only。即使与raw相比，001的联合病灶目标等权/像素加权分别恶化约10.74%/9.80%，005分别恶化约2.49%/8.16%。不能用联合输出相对原HAT更稳或选择若干有利tile替代患者结论。

患者等权平均支持NMSE：完整支持政策0.0016835433、完整联合政策0.0017034239、固定alpha=.5为0.0016965550、训练共同alpha为0.0017255142、phase/采集尺度政策0.0017606066、动作幅度政策0.0017336177、匹配接受数量及alpha集合的随机控制0.0017709256。联合政策虽优于预写四项控制的平均值，却劣于固定.5，且三患者未过完整门槛，所以fixed_visible_joint_diagnostic_gate_passed=false。完整支持政策也仅3/5过门槛，不能改挑它称联合目标成功。

按合同停止这个固定30特征/线性岭/grid政策，不通过事后改lambda、增加特征、ROI或门槛救结果。原五人raw無约束与三pipeline门槛失败保持；前一阶段真值约束oracle上限仍成立，但尚未由可见信息兑现。

## 收益监督不是独立的新信息

两坐标使用相同10输出头、同输入/样本权重/训练标准化/λ、截距不惩罚，不单独缩放目标。绝对误差为五支持动作误差和五病灶动作误差；收益坐标保留两个raw误差头并将其他误差替换为raw−动作误差。

设冻结训练设计矩阵X、权重W、惩罚P，拟合算子H=(XᵀWX+λP)⁻¹XᵀW。上述标签满足Y_gain=Y_error T，因此B_gain=H Y_error T=B_error T。相同动作排序/联合条件经坐标还原应一致。本数据预测最大坐标差不超过6.085e-16，支持/联合alpha逐tile完全一致。此处是固定线性算子的普通代数性质，不是新定理，也不能外推“所有神经网络训练都必然等价”；改变共享表征/目标缩放/约束可能改变优化，但不能宣称仅收益名字增加信息。

与此前[六篇先例](literature/2026-10-02_constrained_oracle_prior_art_recheck.md)相连：SafeRestore的动作风险路由、MoEDiff-SR的区域门控、病灶聚合UQ与任务指导已有先例；当前结果进一步否定“只换收益监督即可创新”的路线。

## 独立复核与错误记录

[最终proof](experiments/mc_rc_visible_joint_development_diagnostic/independent_refit_and_pixel_verification.json)已完整exit0/errors=[]。以增广加权lstsq替代执行器正规方程，重新拟合全部五fold/四组模型，最大预测差约1.16e-15；核全部政策/共同alpha/随机匹配、患者分割和训练标准化。重新解码原数据（复用此前认证decoder），独立Hermite替代SciPy PCHIP，实际像素复算全部240目标×13政策及34,872tile×10监督值，共348,720标量监督。核全部支持/病灶tile数及可见权重，独立抽查25行30项原生特征、可见函数依赖和包字段；没有声称全部特征重新独立实现、没有新decoder独立性或全HAT再生成。

执行器首跑在五可见/监督包及首fold模型保存后，NumPy bool的JSON输出失败。原[失败目录](experiments/mc_rc_visible_joint_development_diagnostic_failed_attempt_01/failure.json)、原脚本/合同及第一折模型/政策保留。仅将guard布尔值转为Python bool后全量重跑成功，科学设置不变。

复核首跑只有五项随机控制不一致：Python赋值先求RHS，导致复核器permutation先于choice，颠倒固定随机抽取顺序。原脚本/proof保留，显式分步恢复choice→permutation后全通过，未改生产seed/政策/数据。[修复记录](experiments/mc_rc_visible_joint_development_diagnostic/independent_verifier_failure_correction.json)和追加全监督核验前的成功proof也保留。数值实现通过不等于开发门槛通过。

## 具体下一步

[更多开发来源准备](experiments/mc_rc_visible_joint_development_diagnostic/next_developer_source_preparation.json)已实际从既存71/159标签目录冻结007/009/010的全部7系列、527个API对象、API FileSize合计261,941,288。包含MPR派生描述，未来透明拒绝；尚未发下载/解码新MR/新label，不是合格原生或确认人数。患者全部时间点已整体归开发，不能再称盲确认。

后续优先核这些来源/标签资格，再为新的病灶可见表征另写合同。需要冻结任务模型预测区域/边界信息、普通误差头/风险路由与同容量对照、完整任务和新患者划分；不能把当前失败解释成局部动作空间不存在，也不能把新网络/更多患者自动称新意。原session83910继续按固定合同，不读动态效果。科学goal active，暂无可发表且独立验证claim。
