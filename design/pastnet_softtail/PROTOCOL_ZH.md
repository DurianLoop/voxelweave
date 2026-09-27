# S-CVaR PAST-Net：固定尾部质量下的平滑风险（2026-09-16）

本轮是独立训练目标实验，**没有提出新网络结构**。QGCR/LACV/其他旧分支及其失败门槛不变，不从失败候选checkpoint续训。保留G086结构的全部正证据，专门检验用户原始优先项“平滑tail-risk objective”。

## 单变量

原目标的risk为每个缺失slice上最大的 `k=ceil(.1*N)` 个平方误差的均值，权重.2。新目标只将此项替换为

`min_eta [eta + tau/(k/N) * mean(softplus((e²-eta)/tau))]`。

tau固定.002（观测归一化后平方误差单位），尾部质量固定k/N，权重仍.2。采用原已冻结 `pastnet_v2.losses.smooth_cvar` 的28次二分求eta，使用包络导数。不是detached硬分位数；没有alpha/weight curriculum，不调用旧累计risk变体的ramp。保留Charbonnier、MSE、梯度、Laplacian、z、symmetry、residual和base_guard的全部系数与计算。

这不增加原始信息，改变的是误差排序临界点附近的训练权重分配；hard权重为0或1/k，soft权重为sigmoid((e²−eta)/tau)/k，和约为1。CVaR和softplus平滑均为已有工具，不主张首次提出。它可能减少排序切换引起的梯度不连续，也可能稀释对极端误差的关注；性能仍需full验证。

## 前置检查（助手执行）

1. hard实现必须与旧objective的loss与参数梯度一致；soft减hard必须恰好等于.2倍risk差。两臂网络初始化和forward逐位相同，参数均992,179，旧target不读合同保留。
2. 数值合同：梯度权重非负、总质量误差<5e-6、最大权重≤1/k+1e-7；小温度极限逼近hard；soft≥hard、soft−hard≤tau*二元熵(k/N)/(k/N)+1e-6；固定eta方向有限差分与包络导数匹配。
3. 使用已有train residual缓存，所有340区间、1,020个slice的control残差。给prediction加入固定seed随机N(0,.001²)扰动，分别计算两种risk梯度相对变化范数。按slice→series→patient等权，soft平均变化需至少比hard低20%，质量约束数值合同通过；否则停止。记录有效像素数1/sum(w²)与hard-tail像素所得soft权重质量。这仅验证梯度机制，不当作优化收益或额外训练标签。
4. 固定训练series `100850027829_t2_axial_2_concats`、`100944022770_ax_t2`，各z=0、4，4区间。hard/soft各从原G086重置，所有参数训练96步，AdamW lr2e-5、weight_decay2e-5、betas(.9,.99)、microbatch2、AMP4096、clip1；相同批次交替、原完整loss只差risk。固定最后一步，soft相对自身初始MSE需下降≥5%，MAE不退且梯度有限。hard同步报告，不按两臂拟合分数选步数。无能力checkpoint用于full。

这些训练患者已经见过原网络，能力与梯度检查都不是泛化证据。失败不更改tau/权重/步数救援。只有全部通过，且真实trainer smoke、恢复、显存和效率核验通过，才交付full。

## full协议

模型与初始化完全同control（G086原checkpoint），仅risk函数改变。相同seed3407、80轮上限、原patience15/min_epochs30、旧参数冻结3轮、AdamW/warmup-cosine/EMA、lr2e-5、有效batch16、数据采样及normalization。冻结前三轮两臂都不更新参数。checkpoint5/microbatch2×累积8，目标约20GiB，允许只调整checkpoint数以适配24GB。

已有 `pastnet_v2/runs/full_control_seed3407_vram20` 是相同网络、初始化、recipe、seed和hard objective的直接单变量对照；不重复消耗一个hard full。新增源码与协议哈希写入manifest，显式记录soft_tail variant；trainer和所有旧源码不改。

正式晋级要求相对control患者等权PSNR≥+.10 dB、10,000次患者配对bootstrap95%下界>0、≥60%患者改善、control最差四分位PSNR不退、SSIM/MAE/MSE/NCC/Dice/HD95 intensity-proxy均值方向不退、forward时间/显存≤1.5倍；**另要求tail10 MSE均值不退**，避免平滑损害原硬尾部。只使用23名clean validation患者选epoch。

任一失败停止，不调tau/权重、不续训、不加模块。通过后补齐control/soft_tail各2027、9103，共3对seed，重做全部统计、质量与效率；锁定候选后另行注册IXI/NingXia。当前入口拒绝test/外部域，不把历史test24用于选型。当前没有SOTA结果。

本包所有根目录Python、本协议、full.ps1及原v2源码在首次full后冻结。用户运行full，助手完成前置实验和结果核验。
