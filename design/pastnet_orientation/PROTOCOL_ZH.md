# 方向泛化单变量实验：2026-09-21，计算前登记

## 问题与身份

官方 I3Net 本地参照已完成：25.172132 dB，PAST control 为25.562011 dB。两者初始化、目标函数和累计预算不同，本地胜出不能推出跨域 SOTA。I3Net 在第32轮达到最佳、100轮按规则早停；此时学习率仍约2.45e-4，早停不是所有优化方案下收敛的证明。

此前正证据都保留；geometry、对应、真实外锚点、crossview、global matching 和 soft-tail 的单变量 full 均未达到原晋级门槛。新问题是：现有模型是否把输入方向当作捷径，使同一真实稀疏信息换一个平面坐标系后产生不同重建？本轮仅验证 **D4 方向增强** 这一归纳偏置。它是标准数据增强，不宣称原创架构或严格等变网络。若成功，可为后续参数共享的方向等变核心模型提供证据；若失败，不把增强堆到其它模块上。

新增的是已知的坐标变换关系，不是新的病人观测、更多层或额外标签。MRI 标量图像与目标一起变换，z 位置和层身份不变。物理轴和面内 spacing 同步变换；未知几何的掩码保持未知。离散90度旋转/翻转无需插值，保留像素值、频谱能量和观测归一化。

## 训练集诊断，先于 full

固定已有 control best，不调参数；使用全部112个训练series的z=4中央区间（111患者），检查全部8种D4动作，反变换到原坐标后计算误差。患者等权，先series后patient。没有读取validation/test；这是已被模型见过的训练集机制诊断，不是泛化估计。

记录 canonical MSE、非恒等7视图平均MSE、相对 canonical 的预测差平方、八视图平均结果MSE。八视图仅作诊断，不作为可提交候选，不依据它改变推理预算。

允许继续 full 的机制条件：患者平均方向预测差/原误差 >=5%，或非恒等视图平均MSE比canonical高 >=10%；同时全部数值有限。该条件只说明存在需要验证的方向敏感性，不保证增强获益。若不满足则停止本方向。

## 独立单变量 full

从原G086相同checkpoint开始；模型为原PAST control，992,179参数，无新层。每个训练microbatch从8个动作均匀抽一个，cond、anchors、target、physical一致变换；动作来自可恢复的torch RNG，独立sampler的样本顺序不变。原loss含z-reversal项保持原样，先平面动作再构造z反转。身份动作概率1/8。validation和推理只用原方向、一次forward，无TTA。

完整复用已冻结v2 RECIPE：80epochs、min30/patience15、AdamW、warmup cosine、EMA、相同有效batch16、旧参数前三轮冻结、原hard-tail和其它loss。与已有control配对，避免额外训练旧对照。显存执行沿用microbatch2、checkpoint5/10；真实反传smoke验证24GB卡约20GiB占用。若资源不足，只调整执行，不改样本顺序、有效batch或模型。

必须先通过：8动作与反动作逐位还原；条件张量重建、几何轴和spacing变换；动作与z反转可交换；不修改原输入；eval输出与control逐位相同、identity loss和梯度相同；真实优化及checkpoint恢复、源码/权重/data哈希、全套指标和效率。

## 晋级和停止

seed3407对已有control：validation平均PSNR至少+0.10dB，即至少25.662011；患者配对10,000 bootstrap CI下界>0，至少60%患者提升，control困难四分位不退，SSIM/MAE/MSE/NCC/Dice proxy/HD95 proxy均值方向不退，tail10 MSE不退，延迟和推理显存比<=1.5。均按原有guard容差。失败停止，不改增强概率、动作集合或目标门槛挽救。

成功后再运行配对seeds2027/9103并报告三seed统计；候选锁定后才评估IXI/NingXia。所有本包Python、协议、full.ps1与冻结v2依赖纳入hash，full后不更改。旧代码、checkpoint和旧test主表保留。

理论背景：[Cohen & Welling, ICML 2016](https://proceedings.mlr.press/v48/cohenc16.html)讨论利用旋转/反射对称性的群等变网络。本轮使用随机数据增强，和其结构性群卷积不同，不能保证单次推理严格等变。
