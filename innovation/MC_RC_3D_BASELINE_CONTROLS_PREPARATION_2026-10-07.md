# 本次新证据后的基线控制与后续准备

这些是准备项，不是已训练模型、已验证MRI收益或已确认创新。当前单001两臂骨干接续训练的完整1024预算不改；最后结果和独立核验才决定能否进入下一训练阶段。

## 必须区分的三个因素

| 因素 | 当前证据 | 可执行后续控制 | 不能据此声称 |
|---|---|---|---|
| 训练空间/context覆盖 | 旧两个crop主head可拟合，但全FOV失败；16tile head改善仍失败 | 本次全16tile、所有参数接续优化；保留所有空tile和相同最终模型规则 | 局部head改善代表19series强任务能力 |
| 最粗特征网格的窗口起点 | 19series/1139tile中11series/341tile非8倍数；metadata独立核验通过 | 在高端增加0–7 voxel padding，使全部起点与步幅8对齐；两输入与标签同样处理，完整FOV全部评分 | 当前偏移已经证明导致MRI任务失败；对齐就能令IN网络严格整图等价 |
| 背景crop的分布 | 原均匀体素中心经clamp形成边界原点的概率原子 | 同预算比较均匀合法crop起点；保持FG规则、初始化和监督，预写pair stream | 均匀体素中心等于均匀合法起点；改变采样是新方法 |

源：[tile结果](experiments/mc_rc_3d_tile_lattice_audit_2026_10_07/attempt01.json)、[独立核验/IN非局部反例](experiments/mc_rc_3d_tile_lattice_audit_2026_10_07/independent_and_in_locality_attempt01.json)、[crop完整概率枚举](experiments/mc_rc_3d_crop_origin_sampling_audit_2026_10_07/attempt01.json)。

以001的270轴、patch128为例：合法起点143个，原clamp规则把65/270质量放在起点0、64/270放在起点142；两端合计47.7778%。均匀合法起点两端合计2/143=1.3986%，比例34.1611。这个比较仅描述名义背景采样，未评估FG采样或训练效果；不改正在运行的事前固定tile流。

## 19series训练前的资源和方法资格

4线程实际单001测量1.59426秒/更新，使20k纯更新约8.86小时/臂，两臂约17.71小时；50k约22.14小时/臂。排除19series加载、真实随机sample_batch、资源波动和评估，不能视为真实全19训练完工承诺。暂不启动这种长CPU训练。

GPU门槛仍为fresh nvidia-smi free>=8,000,000,000bytes；原2.5GB peak/4GB运行余量/float32/3600秒pilot保留。满足后执行既有 totals_v2 新attempt02，测实际显存、速度与拟合；正式19series预算须在真实资格后另行冻结，不使用Tiny GPU的CUDA mem_get_info取代共享物理显存观测。

正式训练需要患者均衡、患者内series流和相同种子的真实augmentation，所有19series均进入；保持标签和数据角色、阈值和最终checkpoint规则。增加已知class-balanced loss、head bias initialization或学习率warmup只能作为标准优化配置的开发对照。当前batch包含前景而loss仍高不能自动诊断成某一个梯度机制，更不能先改门槛或隐藏失败。

## 统计控制的定位

新核读TIN的Eq2直接给出外部参考统计标准化算子；KIN给出缓存/邻域平滑统计并附下游分类评估。上一阶段reference-IN实现和三项同输入重放仍有价值，但只作为机制对照；更换为PCHIP参照、3D扩展和epsilon不构成该算子独立首创性。

若能力合格，可用同一部署observed包、相同tile plan、固定checkpoint比较ordinary/reference-statistics；报告额外参考流前向成本。参照不得读取hidden native或GT。两条流串联，差值不是全网可加的统计因果百分比。TIN/KIN的整体或邻域参照可作为适用性开发对照，不能把作者病理染色收益搬成MRI结论。

## 剩余创新候选的继续/停止条件

候选：在真实observed限制下，预测**某个明确缺层修正动作**带来的病灶任务paired收益。任务模型必须先充分适配，强PCHIP、同observed直接任务和分辨率随机化必须足够可靠；已读SafeRestore、MoEDiff、误差预测/任务指导先例继续约束首创表述。

当前全部目标收益/策略标签只可在11开发患者构造；原4已见验证能力gates全过后才做公平矩阵。稳定、可修正残余不存在则停止这个候选；可见信息无法预测收益则保留失败，不把oracle上界/线性标签重命名当贡献。最終动作、权重选择、阈值、患者端点和预算冻结后，才打开8确认和第二个独立训练的任务模型。当前独立确认0、已确认可发表claim0。
