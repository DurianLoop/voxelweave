# 后续可执行诊断与创新验证准备

本文件在单012两臂结果全部完成之前登记；不改变当前4000updates、.5阈值和fit门槛。已知第一臂full .865312未过门槛，第二臂未完成。初20k模型训练内full .127947且8TP=0，仅2预测为空；新两篇原始论文157正文块及Appendix A说明采样、loss、patch位置/融合和多seed都有直接先例。下面的分支以最终完整独立核验为准。

| 工作 | 固定准备 | 启动条件与否证标准 |
|---|---|---|
| 当前两臂核验 | verify_mc_rc_global_local_single_case_loss_cpu.py：4000draw重生成、两权重与全域指标、6完整plane重放 | 两臂实际完成且session exit0后单次执行；原始失败或不达fit门槛照常保留 |
| 如两臂未过fit：最小可拟合性 | 另立协议，单012按GT有前景原生z的唯一集合取中位z；仅固定这一已见plane、固定全FOV/两patch位置，无augmentation；从头同architecture/BCE+Dice，固定1000updates；最后完整plane/概率回原生评分 | 检查有限梯度和几何/优化最小链条；预先写plane Dice/recall≥.95、absRVE≤.05及独立计数/完整plane重放。训练标签仅确定训练例；不得称可部署GT裁剪/患者泛化。未通过再查容量/目标插值/优化，禁止直接训练新重建gate |
| 如能fit：覆盖/曝光诊断 | 下一新协议用完整11开发/19系列，记录每患者/前景z曝光量及已固定全部FOV端点；同初权重、采样、最后checkpoint，另冻结预算 | 单病例通过不保证11患者能力；四验证仍用原full/missing/recall/RVE/漏检门槛，不换患者、不调门槛。旧4000/20k失败不覆盖 |
| native能力控制 | 新loader只用于明确完整MR臂，单独核数据/坐标/归一化；sparse分支始终只读observed包 | 需另立输入合同与核验，当前无已可执行native匹配训练入口。不把已做过的外域导入权重native失败当成新训练能力结果 |
| 6×5公平矩阵 | 复用global_local_fair_matrix_followup_preparation_2026-10-03.json与冻结患者角色：native/raw/mixed训练曝光×observed_shared/full_own统计×5输入；强PCHIP始终保留 | 首先任务能力通过；再具体实现loader/同预算、同初权重/患者draw/augmentation/hash和最后checkpoint。它仍未运行，不因single-case差值宣称重建收益 |
| 独立强任务基线 | 直接任务、分辨率随机化与第二任务architecture；同observed信息/监督预算，无额外模态/GT ROI/TTA集成混淆 | 已有直接分割与随机分辨率先例，不算新架构。当前GPU占用，记录GPU计划而不启动；CPU可行性先预检 |
| 可能形成新claim的核心问题 | 任务充分适应后，缺层病灶边界/漏检残差是否仍受具体重建与统计影响；能否从真实observed信息预测“相对PCHIP的动作收益”并作保守修正 | 要优于强PCHIP/直接任务/固定修正与同容量无条件task-loss，守住anchors/tail/FP/体积。先在开发冻结具体特征、候选动作、门槛和预算；旧risk/gate失败候选不重启。八确认患者和第二任务网络一致证据之后才写新claim |

三项暂不支持宽创新：换Unified Focal、中心加权patch融合、patch高分/全体积低分。这些分别有2022/2019/2024直接先例。当前最有价值的工作是建立可靠完整FOV任务基线，随后用公平矩阵验证“适应后仍有可行动重建残差”；这仍是假设，不写成已证实发现。

资源/身份约束不变：新增只innovation、CPU单线程/自身below-normal、15GB磁盘/8GB可用内存、所有同人时点同角色、不枚举或操作用户训练、不读locked IXI test。8保留人030/029/019/028/031/026/027/015仍关闭。不会拿本轮训练内结果选择“最终确认患者”或重新定义门槛，goal active。
