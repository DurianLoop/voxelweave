# 为固定CISS局部净收益实验新增的对照要求

已有候选仍是充分适配后固定合法action的病灶增量与完整费用选择；此次新增原文排除了“segmentation loss/pseudo-attention+训练课程”和摘要层面的“语义引导MRI动作选择”宽泛首创。新的医学效应还没有测试。

此次可具体补充三点（不是新正式预算/runner冻结）：

1. **采集与修正的信息合同分开。** Xu摘要的action实际买一条新k-space line，能改变观测。当前本项目只能用既定observed CISS，不能把新增native slice、更多k-space、GT ROI作为deployed action，不能把采样policy对照强行移植后比较不等信息。若另研究主动采集，必须另有数据与采集费合同，不改变当前任务。
2. **课程带来的额外易样本/信息也要配平。** Acar开始近全采样输入，ITFS让任务网看完整MRI，这些不同于只调优化器。后续如果加训练课程或teacher输入，要给最强静态和risk/defer等相同训练患者、完整target/标签许可、mask日程、原始影像信息、每患者曝光、全部训练/选择费用；另加固定目标mask训练控制，报告全部机会。不能以同updates就声称同信息。当前正在跑的两臂仍保持现配方。
3. **所有评价使用相同固定分母。** 本项目主要病灶任务指标沿既有full/anchors/missing/tail完整FOV和患者优先聚合，不随着predicted ROI改变分母。若附加ROI图像分析，需要在开发协议前定义统一truth-derived评估ROI或统一部署mask来源，给所有method同一ROI；truth ROI只用于事后评分，不能用于action生成、路由或推理定位。同时保留全图、漏检、体积变化和伤害患者，不能只报被选中的局部PSNR。

Acar Table2证明局部图像增益与全图损失能同时存在，未证明病灶分割受益。后续action标签必须由固定充分适配任务模型、同一真实state的实际合法action测配对ΔT，而不是pseudo-attention强度、focused PSNR或课程前后训练loss。ROI漏掉病灶/背景异常仍计入完整FOV；实际联合actions重新评估，不能累加单action收益。

强对照仍包括最强静态、同额外曝光/容量、概率反馈/固定循环、同特征风险/误差、cost/defer/DC、预算随机、双路径费用、preview候选费用及union-aware greedy。理想anchor支持、QDA小ROI或只计forward次数均不够，沿原19series真实费用证据继续。

医学执行依赖保持：原两臂final真实exit0/完整来源/权重冻结→56 FOV/全部gates/独立strict→真实三observed臂19series资源→据资源另冻充分适配预算/runner→固定合法state/action实际余量及全费用→上述强控制→全组件冻结后8未见确认。4已见验证不能称独立确认，lockedIXI继续关闭。论文全部取得不代表这些实验已完成。

当前可推翻候选的情形明确：强静态/充分适配消除余量；value不能超过风险/随机；完整费用不优；Dice提高但漏检/体积或其它患者伤害；合法信息合同不满足。这些结果必须接受并记录，不能以新attention模块改名躲避。
