# 双锚点查询位置对应：计算前协议（2026-09-24）

## 已有证据与不同假设

小波主干 full 25.585002 dB，相对修复 control +0.017549，23/23 患者提升，但未达到 +0.10 门槛。停止，不做 J1，也不将该权重叠到新模型。局部/全局 coarse-query 对应也曾分别只有约 +0.0025/+0.0090 dB，不能重复其同一机制。

原 gate 将五个编码特征做逐像素加权平均。旧对应方案用 coarse 特征作为 query 分别查找锚点；线性 coarse 可能含两个边缘的叠影。本次只检验新的对应证据：**同一查询位置在一对候选左右坐标的内容一致性**，在产生单点平均之前比较两端。空间 z 不是时间，组织出现/消失不一定能用位移解释，因此只作为可学习的补充特征，linear coarse 和原主干始终保留。

## 一个主要模型变量

复用现有 slice encoder 的左/右/coarse 特征，池化到 1/4、1/8，共享 64→16 描述子（初始每四通道平均，可学习）。对每个查询 t∈{.25,.5,.75} 和 25 个二维整数候选 d∈[-2,2]²，比较 L(x−td) 与 R(x+(1−t)d) 的归一化内积。候选覆盖全分辨率 ±8/±16 像素；不声称是真实运动估计或物理形变场。

亚像素取样由固定双线性 5×5 stencil+unfold 实现，无 grid_sample 或可学习 offset。边界无效候选严格 mask，零位移始终有效。softmax 温度初始10，约束[5,30]，固定位移惩罚 .05|d|²。保留整个分布，不回归单个 flow。按 t 混合左右搬运特征，同时输出一致性差值；与 coarse 编码差及两尺度差值经零初始化 1×1 投影加到原 transferred feature，再进入原 fuse 与 wide MA3。

不增加采集信息；新增的是两端成对一致性和随查询位置变化的坐标联系。无新 loss、FFT、3D、输出 refiner 或数据增强。原四锚点、bounded residual、latent 和原 dual-domain 保留。本机制参考 [BMBC，ECCV 2020](https://www.ecva.net/papers/eccv_2020/papers_ECCV/html/2095_ECCV_2020_paper.php) 的 bilateral cost volume 思路；本实现不使用其源码、预训练权重或视频性能结论，也不主张理论原创。

匹配容量消融 stationary：结构/参数/初始化相同，只让零位移候选有效，仍可利用未搬运的双锚点/非线性 coarse 差。不是删除新分支。先 bilateral 对修复 control，通过后再 stationary full。

## 先验检查与停止门槛

1. 双线性 stencil 常数保持、零位移恒等、边界 mask、概率归一、交换左右并反转 t 的一致性（FP32 <=1e−5）。已知平移合成特征的中心区域，相比零位移混合 MSE 至少下降50%；仅检验机制。
2. 初始预测与 G086 control 一致、326 tensor 完整映射；原梯度 max差 <=1e−7，新增投影梯度非零。非零投影时 checkpoint=0/5 梯度一致 <=1e−6，不读取 target。
3. 固定修复 train 前两 series 的 z0/z4，共4区间，各臂96步原完整loss。**冻结旧网络，只训新增路径**，原 adapter lr1e−4/AdamW，无EMA。bilateral需MSE下降>=5%、MAE不增、新参数实际更新且有限梯度。失败停止，不修改阈值或扫半径/温度救实验；stationary结果只作能力参照。
4. 两臂256² trainer smoke，恢复加载、独立指标复算、同合同完整 forward 效率、正式入口preflight。microbatch2/checkpoint5，必要时只增加checkpoint数量控制24GB内约20GiB。无人工显存填充。

## FULL 与晋级

修复manifest（1356 train/69 val、23 val患者），从原G086初始化，与修复control相同80epochs/min30/patience15、有效batch16、原完整loss、AdamW+warmup cosine+EMA；新增路径按原规则前3轮独立训练。不从小波或修复best续训。仅validation PSNR选best。

bilateral−修复control >=+0.10 dB，即seed3407 >=25.667453；患者配对CI下界>0、>=60%胜出、困难四分位不退，SSIM/MAE/MSE/NCC/Dice与HD95 intensity-proxy方向不退、tail10 MSE不退，forward延迟/显存<=1.5倍。任一失败停止，不改学习率/继续训练。通过才做stationary full，bilateral−stationary >=+.03dB并通过同守卫，才支持位移对应的增量贡献。

最终候选需匹配3seeds，锁定后IXI/NingXia。G086历史与长期validation开发依赖须如实说明；fastMRI test24只是development test。旧代码/权重/论文测试表不变，新源码/协议/入口在首次full后冻结。
