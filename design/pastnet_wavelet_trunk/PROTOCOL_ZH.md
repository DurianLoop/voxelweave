# 主干内共享核小波空间算子：2026-09-23，计算前登记

## 证据和假设

修复版control为25.567453dB，对旧数据control仅+0.005442，虽所有质量守卫通过，但未达到+0.10。正确的序列修复保留，作为后续统一数据合同；本轮对照就是该修复版control，不再把数据变化混入模型改动。

此前低中频误差占约91%，单纯成熟latent分频读出和多个附加分支收益不足。MA3十个主干block的空间卷积均为全分辨率3×3，后端才有9×9 mixer/context/latent。GroupNorm和channel attention含全局统计，因此不能声称全模型只有局部感受野；问题是逐层、带空间位置的跨尺度关系是否欠缺。

新假设：在主干的十个depthwise算子中直接传播小波多尺度空间信息，使用原已训练核，避免依赖随机新特征投影；保留完整wide MA3、四锚点、linear coarse+bounded residual、多尺度latent和dual-domain。新增的是可利用的空间联系和尺度共享约束，没有增加观测、层数或target输入。

## 唯一主要结构变量

将每个主干block的depthwise K替换为：K(x)+g*(W_J(K,x)-K(x))，g=.5*tanh(a)，a为每通道零初始化参数。W_J先做正交2D Haar分解，四个子带均用同一个原3×3 depthwise K（无bias）；LL递归到第J层，其余细节子带在对应尺度保留和滤波，逆变换重建，最后加原bias。不是丢弃高频或把插值结果当观测。

候选J=3（最粗1/8），10×64=640个新增gain参数。所有原G086 tensor、键名、形状保持；g=0时输出及原参数梯度应与原结构相同。新增gain通过已有核的多尺度响应学习。没有随机新encoder、独立大head、新loss、Flow、3D模块或图像方向增强。不是官方WTConv复现；共享已有核与零初始化有界混合是本地warm-start适配。

后续匹配消融J=1：参数量、原初始化、训练全部相同，仅递归尺度数变化。先筛选J3对修复control；通过后才full J1，检验更深多尺度传播的净作用。不在小样本容量结果中选择J。

## 前置检查与停止

Haar FP32重建及能量相对误差<=1e-5，奇数尺寸padding/crop正确；identity核的递归路径仍还原输入；非identity核impulse证明算子有3×3之外的空间支持（只评价算子，不作为全模型感受野上界）。零gain下模型预测、原参数梯度与原control一致，gain梯度非零，checkpoint重计算输出/梯度一致，不读target。

固定修复数据manifest前两个train series的z0/z4，共4区间；J3/J1各96步原完整loss、旧参数lr2e-5、新gain lr1e-4、AdamW与原betas/weight decay，无EMA容量检查。J3需MSE下降>=5%、MAE不增、gain实际更新、有限梯度才能full；它只证明可训练，不用于两分支相对选型。失败则停止，不追调层数/混合系数救实验。

真实256²trainer smoke、恢复加载、独立指标复算、正式入口preflight，实测完整模型成本。microbatch2/checkpoint5先测，目标24GB卡约20GiB；必要时仅调整checkpoint数量，不更改有效batch、宽度、J或目标函数。额外functional卷积要计入Conv/Linear部分FLOPs，Haar变换/元素操作不计入部分FLOPs，并明确其非总FLOPs。延迟和显存实测包含全部算子。

## 固定full协议

使用pastnet_series_integrity的修复manifest，train1356/val69。从原G086相同checkpoint开始，不从修复control best继续训练；原80轮/min30/patience15、AdamW+warmup cosine+EMA、所有loss和有效batch16保持。gain按原adapter规则前3轮独立训练，其后主干一起训练。只按原方向clean validation PSNR保存best。

J3对修复control至少+0.10dB，即seed3407至少25.667453；配对CI下界>0、>=60%患者提升、困难四分位不退、SSIM/MAE/MSE/NCC/Dice/HD95 intensity-proxy均值方向不退、tail10 MSE不退、延迟/显存<=1.5。失败停止，不继续训练/调LR或门槛。通过后J1 full；J3对J1至少+0.03及同守卫，才能归因深层尺度贡献。最终候选仍需3seeds，锁定后IXI/NingXia，不用test选型。

临界采样Haar不保证单像素平移等变，可能出现网格/边缘代价；通过重建并不证明不存在这些学习风险，正式质量守卫保持。G086历史预训练仍包含旧数据问题，所有组共同继承，不声称全流程干净预训练。旧源码、checkpoint和论文test表保留，新包代码/协议/入口/修复数据哈希在full后冻结。

参考：[Finder等，ECCV 2024，Wavelet Convolutions for Large Receptive Fields](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/07137.pdf)。该工作展示了小波卷积扩展空间作用范围的思路；本实现不是其官方模型，不能引用其性能作为本模型证据。
