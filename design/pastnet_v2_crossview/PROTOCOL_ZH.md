# 真实锚点跨平面交互：独立预登记

目标是实质推进SOTA，但不以历史development-test选型，不把小幅显著或训练过拟合称为SOTA。当前主表IXI最强基线为I3Net，NingXia由SwinIR/HAT领先；fastMRI旧G086虽已超过本地I3Net开发分数，尚不构成三域确认。继续只在fastMRI validation选型，最终三seed锁定后才复评外部域。

## 核心模型与新信息

G086的latent 3D模块交互的是三个查询位置，不是四个真实观测轴。新核心模块 **LACV（Late Anchor Cross-View）** 在1/4、1/8分辨率保留四锚点的独立编码，经过三次跨(anchor,x)和(anchor,y)平面的非线性交互后，才按查询phase读取为一个特征场；注入原宽MA3主干之前。

原linear coarse、bounded residual、四锚点、64通道MA3、multi-scale latent、dual-domain residual及优化recipe保留。没有增加远端采集，没有新物理条件、attention、Flow、FFT或输出3D refiner。模块利用原观测里被早期融合压缩的潜在关系，**不声称增加原始采集信息**。轴向和矢状方向仅指数组平面，不冒充恢复的患者方向。

共享2D slice encoder输出由原模型直接提供；缩至24通道，在真实锚点轴和一个平面空间轴上共享depthwise 3×5卷积，再做逐锚点channel MLP。无效槽在每层严格屏蔽。最终保留锚点顺序拼接，加coarse编码、phase、有效mask，经query readout到64通道；零投影使初始化与G086严格一致。跨视图本身已有I3Net等先例，不主张首次提出；本轮独立检验的是保留稀疏真实锚点轴到非线性交互之后的设计。

与已停止correspondence不同：没有query/key点积、3×3候选匹配或提前softmax锚点平均；与STC不同：没有固定多项式摘要、没有额外远端图像。弱线性残差探针不能排除此非线性特征族，但也不提供其泛化成功证据。

## 助手先做的低成本能力检查

使用原train固定前两例、每例前两个z%4=0区间（共4区间），只训练新增模块，原G086冻结。96步、microbatch2、AdamW lr=.001/weight_decay=.00002/betas(.9,.99)，原完整loss不变，不选最佳步。要求最后一步后的这4区间平均MSE比初始下降至少5%，MAE不高于初始，参数/梯度有限，初始化一致与输入合同通过。

该检查仅证明模块能在极少量样本上学习，不是validation选择或泛化证据。失败则不进入full，不通过延长步数或改学习率救援。能力检查checkpoint绝不用于full初始化。独立测量实际256²全参数反传、对称loss和AMP的显存，再固定full执行设置。

## full次序与单变量消融

**E1 crossview 对既有同预算control**：唯一主要变化是新增LACV核心路径。从同一原G086、seed3407开始，沿用80轮上限、冻结旧参数3轮、原loss、AdamW/warmup-cosine/EMA、有效batch16、原数据采样。当前module带来的总体贡献包括新增容量，不能仅凭E1归因跨平面机制。

E1需validation23患者等权PSNR≥control+.10 dB、患者配对bootstrap95%下界>0、≥60%患者改善、control最差四分位不退、SSIM/MAE/MSE/NCC/Dice/HD95 proxy均值方向不退、forward时间和显存各≤1.5倍。任一失败停止。

**E2 per_anchor 容量对照**：仅在E1通过后运行。从相同G086重新训练，参数形状、初始化、其他路径完全相同。跨平面核改为读取重复的当前锚点，不读邻近真实锚点；保留同一3×5核的所有权重。此对照仍允许最终query readout融合锚点，检验的是提前跨锚点空间交互，而非是否能看到四个图像。crossview对per_anchor需≥+.05 dB及同套质量/统计/效率guard，同时E1总体门槛仍成立，才算机制通过。

E1/E2任何失败均停止本分支，不降低门槛，不叠加新loss或继续微调。通过后固定另两个seed2027/9103，补齐control/crossview/per_anchor三seed配对，重新核验总体+.10与机制+.05和所有guards。仅此之后注册外部训练/锁定协议，才测IXI/NingXia。当前入口不支持外部test。

## 显存与溯源

24GB卡、microbatch2×累积8、checkpoint前6/10主干blocks作为初始执行设置；full前以真实smoke测量决定是否仅调整checkpoint数量，保持两臂相同。约20GB是资源目标，不通过无关张量占用显存。

本包所有Python、本协议和full.ps1及原v2源码哈希写入manifest。首次full后冻结这些文件；保留旧分支源码/checkpoint，不污染论文主表。研究结论必须区分“训练能力通过”“validation总体通过”“机制通过”“三seed与外部SOTA确认”。
