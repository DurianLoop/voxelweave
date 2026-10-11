# 后续可执行准备：区分网格分辨率、真实观测及动作收益

本文件是开发前准备，不是冻结已完成实验；具体actions、head容量、预算和患者折须在相关来源可用、任务能力通过后另绑定。8未见确认/12series和lockedIXI不读取。原六医学门槛、full患者/series分母、lastcheckpoint、3e-6/3e-12/二值零差不改。

## 当前必须完成的医学依赖

真实轮询29823直到整个任务exit0且无session_id；不能提前从完成三臂里选配方。保存完整真实terminal→spatial_adaptation_matched_2026_10_08/capture_training_terminal.py→evaluate_matched.py→保存评价真实terminal→capture_evaluation_terminal.py→summarize_matched.py。四last2992、11968journal、11人各272曝光先核，再36 production+36 independent functional完整FOV。已见4验证9series仅本既定方案评价，不能用其结果挑新support/噪声/threshold。

74234完整35904field真exit0后保存terminal，再既定audit_full_real_terminal.py。若失败，保留failed_field和terminal，先诊断，不放宽3e-6或去除难患者。未完成前不修改running source/frozen_config/绑定依赖。技术完整通过只是后续普通训练的数值资格。

新GPU阶段fresh totals需free>=8192MiB且余量满足实际计划，授权已具备；不迁移CPU既有训练，不查询其他PID。磁盘/RAM8GB储备和journal/医学评价预留继续。当前储备外约31MB，不足22个LOPO task权重（旧实测推123.7MB，还未计teacher/labels/head）或完整新六臂文件，不能启动。无需询问已授权GPU；资源满足后按冻结计划前进。

## 强任务基线和机制拆分

| 对照/因素 | 输入与监督 | 匹配要求 | 用途 |
|---|---|---|---|
| 原充分强度与空间训练 | 各自合法observed-PCHIP；native仅upper bound诊断 | 固定last及同曝光/预算 | 先确认任务能力，不归因额外更新 |
| intensity / image低通 / 合法roundtrip | 原位GT、真实observed context、相同support不足策略 | 同parent/schedule、2992prefix、每人272曝光、同optimizer/reset | 区分普通降质正则与人工crop边界机制；完整35904资格前不训练 |
| VINN式feature归一化基线 | 同observed及physical scale；continuous latent采样，native skip/原位GT | 从严格折内random初始化、同参数/updates、同推理预算；新module另资格 | 排除仅spacing/latent interpolation已有先例；不是直接忠实复现T1 2.5D权重 |
| 同容量attention与静态额外训练 | 同信息和监督 | 参数/额外曝光/全部费用对等 | 排除capacity和额外训练造成伪机制贡献 |

不直接把VS二值背景当SynthSeg多组织生成器；不使用未采集native薄层作为部署影像。原grid名义spacing、观测z间隔/phase、有效support和未知scanner PSF分开记录；当前retrospective x4 phase0不能认证真实厚层/任意phase/多中心泛化。

## 动作策略的最小完整对照矩阵

一套固定、可部署finite actions和全FOVpaired成本C_a；G_a=C_0−C_a。开发GT只用于监督actual actions之后的完整FOV评分。不用GT框筛候选，不用只剩下被接受病例的Dice做主端点，联合动作按实际联合输入重算，不相加单动作标签。

| 策略 | 必须得到相同信息/预算 | 需要记录 |
|---|---|---|
| strongest static / always-none / always-action / 同预算random | 同任务网、候选定义、额外训练曝光 | 所有患者及全部探索/失败路径费用 |
| error/QC、双路径cost、一般cost-sensitive/defer | 与gain head同features/总容量/监督和校准患者 | 期望gain与P(gain>0)目标分开；既有方法优先强实现 |
| SafeRestore式双风险排序 | 其部署可见特征的MRI合法适配，候选生成和各detector费入账 | 不拿自然图像任务latency当MRI实测 |
| CV rank固定ensemble与预测mask cluster策略 | 权重按训练CV固定；仅可部署mask/radiomics | 不能在评估时用GTcluster；所有候选网络算费；PP作为独立新增系统 |
| 含observed可见性的策略及去采集控制 | nominal grid +实际observed lattice/support +同固定预测 | 单独证明真实采集量超spacing/QC；同信息强defer也得到这些features |

主候选的incremental机制比较为：在共享基础feature中，给所有强策略同样的observed采集feature，再比较谁能更好选择实际动作；不能只给我们的gain head采集信息。另做完整pipeline患者折外的去采集/随机打乱feature控制，打乱须只在训练fold进行且不从验证效果选方式。若claim包含feature本身有用，使用同一个已知cost/defer方法的with/without feature比较，而非把它误写成新selector算法。

初始合法feature可包含距已采集平面的physical distance、固定phase/x4 sampling、局部有效source support，以及由固定预测得到的component z extent。实现前须明确coordinate/flips/tail、空预测定义和所有feature计算费用，不代入GT形状。Spacing metadata不足以知道scanner PSF，未知项不能由native补填。

GT radiomics可用于开发内训练分层；整个任务/定位/QC/gain训练、特征变换、cluster选择与校准必须fold内。全11GT训练的last19998父模型不能冒充严格LOPO初始化；head-only LOPO另称诊断。患者外标签生成训练成本也要统计，不能只报selector CPU毫秒。未见确认前冻结patient聚合、主端点、完整比较family/全预算和第二任务网复核；保持原28相关endpoint算术不能代替病例因果证据。

证伪条件：充分强基线没有真实动作余量；可见性增量不能超强cost/QC；收益只来自弱基线/额外监督/额外训练/删小CC；全费用同预算下失效；独立患者确认或第二任务网不能复现。任一出现，保留反证并重定研究范围，不降低医学门槛、删患者或重新挑确认端点。
