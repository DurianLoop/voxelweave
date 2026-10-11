# 充分适配、固定任务网和完整FOV的下一阶段准备

这份准备由新读论文的两处设计直接触发：TADT以新backbone及Baseline预训练+后续路由训练比较；medical-shift的诊断网只训原始图且只评估60–130slice。本文件不冻结三臂正式预算，不启动医学训练、不生成action label。原final→56FOV→六gates/strict→三臂真实资源/实际退出全部先完成。

三臂名称和观测边界不变：legacy_dense / direct / common_projected_dense，共享availability/valid/target，CPU/GPU/优化器/初始化/增强/患者曝光一致。native_reference只有能力参照角色，使用额外未部署MRI信息，不作为部署action或收益label。医学checkpoint不能加载上一轮人工synthetic checkpoint。

| 评价单元 | 将来估计什么 | 不应改写成什么 |
|---|---|---|
| 各输入自己的充分适配任务模型，三臂对角比较 | 各可部署表示在相同训练合同中的真实病灶端点 | 固定弱模型受输入失配影响的动作gain |
| 同冻结任务模型在不同输入的交叉诊断 | model-input失配、domain specialization | 各表示的充分适配效应、跨pipeline确认 |
| 同冻结模型/固定部署action版本生成的真实配对label | 当下该action对完整病例任务ΔQ | 其他任务网、旧弱label或native额外信息下的ΔQ |
| 同backbone静态固定序列、等量继续训练 | route/selector相对强静态的余量 | 整个架构改变或额外曝光的全部收益 |

资源实测后另冻结主要三臂对角训练和评价预算。交叉输入/模型最多作为可选诊断计划，不预先承诺9格全部医学FOV；是否加入由真实资源决定并在看结果前固定。若加交叉诊断，case/role/field/semantic/checkpoint/content SHA和完整cost单独绑定，防止误用于主要label。三臂梯度、患者stream和disk-resume资格已存在，不原样重跑当新方法进展。

任务评价仍采用原真实几何和完整FOV，不根据GT选择slice、crop或丢掉负slice。全FOV/观测层/缺层标签几何和每series至patient汇总均沿冻结端点；slice均值、3D voxel Dice、RVE、recall分别记录不互换。完整FOV弱能力未达门槛时，不通过阳性slice评分放行selector。所有数据相关threshold、calibration、特征标准化和选择器仅开发拟合；已见4/9用于能力，8未见/12series仍不读。

静态对照获得与selector/router等量的额外训练曝光（包括backbone预训练后的继续训练），共同初始化、监督、增强和可见信息不变。标签生成/selector拟合属于开发成本，deployment特征/probe/action/task/postprocess属于完整部署费用，禁止用FLOPs直接换秒。随机路由若未来采用，sampling实现和seed重复性须事前冻结；本项目不因TADT用Bernoulli就新建未资格控制器。

后续可证伪决策：若充分适配后三臂task余量消失，先确认数值/资源/完整端点，再停止用旧失配优势训练gain head；记录对训练分布的依赖。若余量存在但仅在交叉诊断/额外曝光/非完整FOV/代理费用下存在，不能称部署收益。只有固定可部署观测、同充分训练、完整任务/成本以及最强静态控制后余量成立，才准备未见患者确认。

公平性论文用于解释评价条件，不把本项目11开发患者加人口学分组变成未经准备的fairness claim。公开表的字面不一致保留在table_audit_attempt01/receipt.json；不得猜补原作者患者/测试人数。
