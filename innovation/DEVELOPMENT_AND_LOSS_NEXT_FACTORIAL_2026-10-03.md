# 下一覆盖/增强因子对照：具体准备，尚未训练

最小固定z38已独立核过：1000updates、16tile各125曝光，native plane Dice .9841105/recall .9693126/面积误差.03007365。它说明链条能拟合这张训练例；多z、augmentation和采样策略同时改变，不能据此判定“是增强导致失败”或“覆盖修复有效”。两4000步完整012仍未过fit gate，11患者20k完整FOV也失败。

下一开发只用012已核observed-only输入，保持原architecture/BCE+Dice/seed/AdamW/cosine4000/最后checkpoint/.5/完整FOV原生全部z与原fit gate，设计覆盖方式×augmentation 2×2。它是训练能力开发，不是新重建方法。

| 条件 | 覆盖 | augmentation | 状态/需要完成 |
|---|---|---|---|
| 原始能力基线 | 一个前景中心/一个全FOV随机patch，原.5 foreground-z选择 | 原flip/90度/强度扰动 | 本轮bce_batch_dice已完成，最后权重完整保存；能满足新draw合同才允许直接复用，不能为了省算力忽略不匹配 |
| 仅更充分覆盖 | 原.5 foreground-z选择；每个z维护独立tile游标，连续两个完整FOV tile循环，确保各z的实际coverage/exposure全部登记 | 保留原augmentation；需要把tile游标定义在增强后的平面，正方形/旋转映射逐项核 | 新协议、实现、合成/标签-only采样核验后单次4000训练，未运行 |
| 仅取消增强 | 原z/patch合同；预生成原随机primitive并消费相同数量随机数，取消对输入/target的变换 | none | 原patch选择依赖变换后label，不能只跳过随机调用就声称matched draws；需要明确原生/增强坐标映射及确切对照，未运行 |
| 覆盖+取消增强 | 与覆盖臂相同z序列和逐z tile游标 | none | 新协议前冻结draw文件，并与覆盖+增强逐例核坐标关系，未运行 |

启动前必须把随机primitive、z选择、patch位置和增强坐标合同做成机器可读draw清单：不同因子需要的不同输入是有意实验处理，同一外生随机变量/预算才是公平性要求。原运行baseline并不自动匹配新primitive顺序；若不能逐4000项证明一致，则新2×2四臂都从头，原baseline只作开发历史，不混入主配对。

预算在新protocol中固定，不能因已见loss/FOV分数改为“训练至通过”。每臂完整报告full/missing/anchors/tail、TP/FP/FN、Dice/precision/recall/RVE与边界，不以训练loss或patch Dice挑checkpoint。独立label/计数/物理距离/首中末完整plane重放；同模型重放不替代第二泛化网络。

若仅覆盖或仅去增强提高训练内fit，只支持这个单病例/固定预算的能力诊断，不称患者泛化因果；需再固定整个11开发训练和4验证能力门槛。若差异消失或无臂通过，保留负结果再查曝光预算/physical target/容量，不直接训练重建gate。

真正创新仍需能力通过后的native/6×5矩阵、直接任务/分辨率随机化、具体observed-only修正与八保留患者确认。GPU当前被用户训练占用，下一全部先CPU资源预检；不枚举/操作其训练。此文件是具体准备，不是可直接运行入口；缺draw生成与独立几何核验时不提供虚构启动命令。
