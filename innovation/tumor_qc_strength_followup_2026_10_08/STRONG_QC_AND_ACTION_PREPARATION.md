# 脑肿瘤 QC 强对照后的后续试验准备

状态：准备，不是已训练QC/收益模型。本轮新增论文原文和CPU代数/定义审计；session29823四分支2992步训练继续，不改其配方或源；尚未启动新验证。

| 条件/比较 | 准备的实施方式 | 完成前不得作的结论 |
| --- | --- | --- |
| 四分支真正exit0 | 原capture_training_terminal核四state/11968日志，再evaluate_matched完整36FOV两实现，capture_evaluation_terminal，summarize_matched | 完成步数、医学通过或空间增强有效 |
| matched capability | 同输入spatial2992−intensity2992；原parent及99步仅描述 | 把额外训练预算当空间增强贡献 |
| 能力不足 | 继续普通强基线：充分训练/空间强度增强、同容量对照、来源合格预训练加scratch | 进入收益头或未见确认 |
| 能力满足且可修正余量存在 | 冻结动作、单位、合法部署特征与费用口径，开发patient-fold外生成raw/动作后真实任务结果 | 由绝对QC相关性推断实际动作改善 |
| cheap confidence控制 | 同一分割概率的binary entropy；开发内边界/距离/体积聚合，明确RF/特征费用 | 只比较平均entropy就称优于强QC |
| learned QC/error控制 | 合法observed T2+query mask/同可用feature，绝对DSC或error map监督；按query恢复FP/FN，再做error-cost/defer | 把signed错误方向当新信息或首创 |
| uncertainty ensemble/MC控制 | 另立开发方案，训练时加入合适dropout，明确定义H(mean)、variance、MI；预算公平 | 给当前无dropout模型推断时加随机dropout后称已忠实复现 |
| action-benefit控制 | 同输入、同容量、同patient-fold、同label生成与训练预算；比较raw保留、always-action、随机/静态费用匹配、QC-error/defer、联合动作 | 用弱无训练规则替代强控制；相加单动作收益当联合收益 |
| 最终确认 | 冻结后8未见患者12series一次；独立任务网、完整患者分母、全费用与coverage | 从accepted子集Dice或已见4患者结果宣称独立确认 |

Jungo原文的102 radiomics+RF是更强聚合先例。本机不得为此安装依赖；可先明确项目已有特征能否覆盖边界距离、体积和形状信息。若只实现部分特征，应称部分控制，并列出与原论文不同处。物理距离使用mm而非直接照搬原1mm图像的三voxel边界带，带宽只能在合法开发折固定。不能利用部署GT画病灶ROI或预先知道遗漏病灶大小。

患者fold必须把同患者所有series及所有动作结果放在同fold。QC/error和收益控制享有相同合法特征；收益监督同一基础分割state，在fold外患者上生成。不能使用验证4患者/9series或确认GT作为QC训练、label-bin采样、阈值/费用权重/动作选择来源。开发训练平衡真实DSC bins可以探索，完整确认分母保持自然患者分布，不按真实DSC筛除病例。

费用账本分别计分割路径、QC额外forward、MC/ensemble重复次数、特征/RF、恢复/补层动作、缓存构建/复用、拒绝后实际处理及训练label生成。QCResUNet主结果3个模型不等于单模型费用；Jungo ensemble10个模型与50次MC（50是QCResUNet设置，不假定Jungo主文也固定50）应单独记录。若对照先执行两路径再比较两绝对质量，必须计两路径费用。

QC误差质量以患者先汇总并保留missing/tail分区、FN/FP、recall、absRVE、empty/zeroTP病例；模型好坏最终仍由所有患者真实动作后任务结果决定。不得把error-map Dice、QC r、校准ECE或拒绝后accepted Dice替代原六能力门槛。仅observed T2而无缺失原slice/native或人工定位；标准原文四模态的高r不可直接迁移。

下一轮可以实际做的准备：补核当前任务模型是否含dropout及合法observed feature接口（只读代码），规划已有runtime的部分形状/距离聚合；只有完整训练terminal核验且能力通过后，才加载开发动作结果开展fold外QC/增量收益试验。当前未训练这些控制、未取作者权重、未执行8未见确认。
