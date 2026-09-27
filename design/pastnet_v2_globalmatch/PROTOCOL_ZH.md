# QGCR：查询条件下的全图真实锚点对应（full前登记）

## 独立假设及旧证据

保留所有旧失败结论。LACV E1只提高.014654 dB；图像/latent线性分频读出未满足效应与MAE门槛。这里不是修复这些分支，不加载其训练权重。

G086先融合同位置锚点特征；旧correspondence用1/4、1/2尺度的3×3邻域匹配，LACV为固定局部跨平面卷积。它们未直接检验“每个query位置能否按内容读到真实锚点的远距离空间位置”。本模型QGCR在每个锚点的1/8特征图上做全图对应，按原顺序保留四个锚点的匹配差，再条件读入原MA3主干。

新增可访问的是原观测中非同位置的候选特征关系，不是新的采集图像或标签。是否有帮助是待测假设；低中频残差能量不作为本模型可学习收益的证明。全像素对应已有AMT等先例，不主张首次提出。这里不生成Flow，不做图像warp，不使用INR/unrolling或输出3D refiner；保留旧dual-domain和query latent模块，不新增FFT/3D。

## 核心模型

复用原四锚点和linear coarse的共享64通道编码；avg_pool8到32²，共享32通道q/k投影（coarse为query，各真实锚点为key），独立32通道value投影。单位范数q/k、固定dot-product scale10，使用二维高斯距离偏置σ=(H/4,W/4)，逐锚点softmax匹配。方向为数组坐标，不伪称物理毫米方向。

四个匹配value减同位置value，按锚点身份保留并屏蔽无效槽；拼接coarse value、phase和有效mask，经165→64→64非线性readout、零初始化64→64投影，上采样后注入原fuse输出。零投影与原G086初始化逐位一致。输入仍是四个真实锚点、原coarse及phase，target不参与forward。

**global/local两臂仅一个差别**：local将候选位置限制为同一低分辨率3×3邻域，global保留整图支持；所有参数形状、初始化、距离偏置、归一化、读出、loss和recipe相同。local仍有跨切片输入，不能称为不使用锚点的对照。两臂均采用同一稠密SDPA实现，local用mask，不以漏算attention美化效率。

## 助手执行的能力与执行检查

固定训练series `100850027829_t2_axial_2_concats`、`100944022770_ax_t2`，各z=0、4，共4区间。从原G086初始化，冻结旧网络，只更新新增路径96步AdamW lr=.001、weight_decay=.00002、betas(.9,.99)，microbatch2，原完整objective与AMP4096，梯度裁剪1。固定最后一步后的MSE需比初始降低≥5%，MAE不高于初始，梯度有限；不根据validation选步或调lr。能力检查权重不保存、不用于full。

同时核验：零投影一致、target不读、无效新路径屏蔽、反向顺序合同、相同初始化参数，以及在固定q/k时改变远距离value只影响global、不能影响local中心query。真实trainer两臂smoke、global恢复、source/recipe/data哈希与正式入口前置检查必须通过。

执行目标24GB卡约20GiB：起始microbatch2×累积8、checkpoint前6/10 blocks。只允许根据真实反传峰值调整两臂共同的checkpoint数量，不改有效batch、优化recipe或结构以救援能力检查。若能力失败停止本模型；如执行失败先修复实现并重新完成检查，保留失败记录。

## full晋级与停止

E1 global seed3407从原G086开始，同预算control为 `pastnet_v2/runs/full_control_seed3407_vram20`。唯一主要变化是QGCR新增路径；它的整体收益包含新增容量，不能单凭E1归因于全图支持。

保留80轮上限、min_epochs30、patience15、原AdamW/warmup-cosine/EMA、lr2e-5、新路径lr1e-4、旧参数冻结3轮、有效batch16、原loss、相同采样。只用23名干净validation患者选epoch。晋级要求：PSNR≥control+.10 dB，10,000次患者配对bootstrap95%下界>0，≥60%患者改善，control最差四分位不退，SSIM/MAE/MSE/NCC/Dice/HD95 intensity-proxy均值方向不退，forward延迟/显存各≤control1.5倍。

E1任一失败停止，不续训、不降门槛、不添加新loss。只有E1通过，才运行E2 local，从相同G086及seed重新开始。global对local需≥+.05 dB及同套guards，且E1总体门槛仍成立，才确认支持范围机制；否则停止。

两级均通过后补齐2027/9103，control/global/local各3seeds重新核验配对效果、质量和效率。锁定最终候选后另行注册IXI/NingXia同协议训练及测试；test24继续只作历史development test。本入口不支持外部test。当前没有SOTA结论；近期强基线仍需同协议补齐。

本包根目录所有Python、本协议及full.ps1和原v2源码哈希进入manifest。首次full后冻结；旧代码/checkpoint不修改。用户执行full，助手执行所有前置检查及结果复核。
