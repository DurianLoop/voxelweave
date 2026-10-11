# 冻结观测ROI到当前3D缓存成本：事前协议

问题：已冻结observed-only预测区域的原覆盖/面积结果，与当前3D原window/batch成本是否同时可用？旧QDA/LDA覆盖失败已知，本轮不把该失败计成新发现；新增证据是同一冻结ROI在当前3D窗口下的条件重算成本。上一轮GT oracle支持不能冒充部署定位。

固定旧mc_rc_anchor_qda_cpu全部16series/8患者，恰为当前19开发series的16子集；011/012/013缺少该旧预测，单列not_available，不外推或填0。主方法保持joint_QDA，另外appearance_QDA/coordinates_QDA/joint_LDA全部作为既有解释对照，不择最优更名。旧模型患者剔除、原posterior=.5、先验、shrinkage与2mm配置不调参/重拟合/重新分类。

只读冻结NPZ里的anchor二值预测、旧metadata/独立proof、当前19开发metadata及上一轮annotation支持结果。没有新MR像素、GT数组、checkpoint或网络读；不使用当前训练中间权重。核旧contract/result/proof及每NPZ文件和数组hash，核16×patient/UID/native/grid映射一致、患者全部系列剔除及predictions_saved_before_full_label_scoring。只记录缺层覆盖/边界/32tile原指标为**来源既有值**，独立实现不重新执行GT评分。

每内部缺层z，用其两侧真实观测层的冻结预测并集、原2mm物理disk扩张；同间隔三个缺层共享该ROI。不沿z扩张、不引入label。正支持映射固定原physical_mr（0.5mm中心网格、trilinear、align_corners=False、零padding），原PATCH64×128×128、原50%重叠/顺序、原batch2；触及tile则完整batch重算。支持是假设同号非零修改的几何范围，不是真实MRI变化或实际SR动作。

每series/method报告anchor预测/完整缺层ROI原生体素及SHA，全部缺层plane的ROI计数与SHA、physical支持体素及SHA、受影响tile/batch ID、完整N/条件重算k、1−k/N、五同支持替代动作含初始化比(N+5k)/(5N)、最少动作数floor(N/(N−k))+1。空ROI对应零重算并记empty/no proposed edit，不能当有效动作或无限速度。保留全部失败，包括条件省但覆盖不足、可复用空间消失和五动作未省。

汇总患者内series等权、患者間等权，并单列N/k总工作量；报告有条件省且原覆盖≥.99/边界≥.99的交集（已知原结果失败）；原32tile≥.995/面积≤.05/32tile面积≤.10门槛只保留，不当当前3D/真正预算门槛。不能与GT radius2**体素**包络直接称同支持比较（此ROI是2**mm**）；可引用上一结果为oracle几何背景，不当效益对照。

独立核验从同预测NPZ重放，用显式原生物理disk结构元素+binary_dilation，避开生产distance_transform_edt；用有理数Boolean OR中心邻居，避开torch插值；独立lattice/tile/batch/Fraction成本和患者汇总。独立性仅指这些实现，旧ROI覆盖端点只核来源hash和值，不重新读GT或伪称新科学确认。

只对自身设CUDA不可见、CPU4/interop1及below-normal，RAM/磁盘8GB储备，900秒/输出5MB；原session99542继续，GPU授权保留但新run先满足8GB余量。任何失败保存，改动新version/attempt。新claim、MRI益处或风险证书不由这个计算审计产生。
