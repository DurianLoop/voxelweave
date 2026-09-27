# 保留解剖坐标系的方向共享锚点上下文：2026-09-22，计算前登记

## 出发点和可证伪假设

D4随机方向增强得到25.656399 dB，相对control +0.094388，95%CI[0.043520,0.149981]，17/23患者提升；但未达到+0.10，且HD95 intensity-proxy +0.158420、95%CI[0.061572,0.264209]，SSIM均值下降。因此该分支停止，不调整其概率/动作集合/损失、不继续训练或补seeds。

这些结果同时留下两条证据：方向敏感性确实存在；将整个解剖图像随机改变方向不能保证多指标改善。新假设是将全局解剖坐标先验与局部结构的方向共享分开：保留G086完整主干和原方向训练，仅让一个新局部锚点上下文分支在D4方向上共享同一组非线性映射。

本模型称frame-context：原linear coarse+bounded residual、four-anchor MA3宽主干、多尺度latent和dual-domain保留；在主干fuse后、十个wide blocks之前注入方向共享的锚点结构特征。新增的是同一稀疏观测在多个方向的共享表示约束，不是额外采集层、target信息或物理测量。它是相对G086的新结构假设，群平均本身是已知方法，不能宣称理论原创。

## 唯一核心结构变量

输入取原cond中的coarse、phase、signed/absolute inner difference、两端validity、masked outer differences、curvature共9个标量场。1/4和1/8尺度avg_pool不使用目标；每个尺度使用同一个9→24→24→24的3层3×3卷积/GELU映射f。共享方向分支为A(x)=mean_g T_g^-1 f(T_g x)，g遍历D4八动作；回到原坐标后汇总，再双线性插值到主干尺寸，共享1×1投影24→64，以0.1系数注入原fuse输出。

1×1投影权重和bias初始化为零，原G086所有326个tensor严格映射，初始预测逐位一致。新分支不替换主干、不对完整样本做增强、不使用输出端3D refiner、Flow或新FFT模块。D4只覆盖新增低分辨分支，主干仍能表示原解剖方向。仅新增分支满足D4等变性；完整网络不保证严格等变，不能混淆。

匹配消融plain使用同样输入、尺度、参数、初始化、注入位置，但只计算g=identity，不作方向共享平均。先full shared对既有control筛选结构收益；若通过，再单独full plain测量共享约束的净作用。此顺序在训练前固定，不能因结果改对照。

## full前实现与可学习性检查

先检查全部8动作的分支等变误差（FP32 max<=1e-5），训练输入不含target、原输入未修改、z反转语义仍由原loss处理、初始预测与G086逐位一致、原参数映射严格、shared/plain参数相同。将投影暂设为非零测试，避免零输出使等变性检查空泛。

固定4个train区间（manifest前两个series各z0/z4），shared和plain从原G086初始化，各96步、AdamW旧参数2e-5/新参数1e-4、原完整loss、microbatch2、checkpoint5、无EMA做容量检查。不得以两个分支的相对好坏选模型；shared必须有限梯度、canonical MSE下降>=5%、MAE不增、分支确实产生非零响应，才能运行full；否则停止新结构。固定训练样本不用于证明泛化，临时权重不保存。

最后真实trainer smoke、初始及保存best指标重算、恢复、full脚本preflight、同合同推理效率。24GB卡目标约20GiB，执行设置允许只因资源测量调整；不改变有效batch或模型宽度。

## 固定full与晋级

原G086初始化，不加载失败的orientation checkpoint，不做D4数据增强。复用冻结v2所有RECIPE、loss、EMA、sampler、数据、归一化和评估。80轮/min30/patience15，有效batch16，microbatch2/checkpoint5起测；新参数沿原adapter规则前3轮独立训练，之后一起训练。validation只单次原方向forward；计算新分支8个低分辨方向属于模型内部，效率如实计入。

shared对control：PSNR>=+0.10dB，CI下界>0、>=60%患者提升、困难四分位不退、SSIM/MAE/MSE/NCC/Dice和HD95 intensity-proxy均值方向不退、tail10 MSE不退、延迟/显存<=1.5倍。未通过则停止，不调整分支宽度/注入系数/门槛或加其它模块挽救。

通过后plain对照full；shared对plain还需>=+0.03dB，CI下界>0、同质量守卫。若仅新增分支有效而方向共享不成立，不能宣称方向共享贡献。最终候选需要3407/2027/9103三seed配对统计和效率，锁定后才运行IXI/NingXia。当前只交付shared seed3407，不提前启动外部评估。

源代码、协议、入口、旧v2依赖与checkpoint哈希纳入manifest；已有包源码、旧权重、test主表保持冻结。理论背景：[Cohen & Welling, ICML 2016](https://proceedings.mlr.press/v48/cohenc16.html)。本实现为有限群平均上下文分支，并非该论文群卷积的官方复现。
