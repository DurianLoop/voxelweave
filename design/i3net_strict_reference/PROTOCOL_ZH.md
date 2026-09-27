# I3Net strict validation参照（2026-09-17，训练前登记）

## 目的与身份

soft-tail对control仅+.002913 dB，效应和质量guard失败，按旧协议停止。新HAT/SMamba交接审计发现历史结果不符合其friend strict-val口径，且含style/surrogate实现。因此本轮补齐可信比较参照，而不是再新增PAST-Net模块。

使用官方I3Net的64通道、16个I2Block、3个CrossViewBlock、4→13层x4模型。`basic_model.py`、`dct_util.py`和官方配置已与上游master逐文件核对，除CRLF/LF外相同；源副本SHA及本地commit记入产物。不缩窄模型或替换DCT/跨视图。内存checkpoint只改变重计算方式，须与官方forward及梯度核对。

本轮是**同输入、normalization、validation选模和metrics口径的本地参照**，不是官方IXI原论文数值复现，也不是与G086相同初始化/累计训练预算的单变量架构消融。I3Net从随机初始化训练；PAST-Net control继承历史G086预训练。不能据此直接作SOTA结论。

## 数据合同

复用冻结v2 fastMRI manifest和IntervalDataset：train112series/111患者，clean validation23患者；训练全部1360中央区间，validation固定z%4=0的69区间。观测网格minmax归一化，256²，不读取隐藏target extrema、不clamp预测/target。只用四个真实锚点输入，边界无效槽按原数据合同重复真实端点；不引入额外dense输入。

官方模型输入四锚点[N,H,W,4]，输出13位置，对应相对z[-4..8]；本任务只监督/评价其中索引5、6、7，即中央三个缺失层。输出其余位置不额外获得监督。包装器不读target/physical/cond额外特征，保留模型官方观测位置复制行为。这个中央区间适配须明确记录，不能冒充官方全窗口训练协议。

同一metrics函数计算PSNR/SSIM/MAE/MSE/NCC/Dice和HD95 intensity-proxy/tail10，先slice→series→patient等权，best只按validation平均PSNR保存。没有test入口，不运行IXI/NingXia，不读取test选择模型。无效/非有限指标报错，不能静默跳样本。

## 固定训练方案

seed3407，从随机初始化开始；Adam lr3e-4、betas(.9,.999)、eps1e-8、不加weight decay，与官方Adam默认对应；原生L1损失，但仅中央缺失三层。无EMA、无PAST-Net的额外loss，不加载历史I3Net/G086权重，不使用输出clamp。

预先限定300轮，15轮线性warmup从lr/100到lr，其后cosine降到lr/10；有效batch16，训练sampler generator按seed*1000+epoch。至少训练100轮，之后40轮无validation PSNR改善则早停。梯度clip1、AMP scale4096。官方默认1500轮/批量6不等于本地枚举区间的epoch；本300轮是明确的本地资源方案，不声称官方完整训练预算或最优超参数。

执行设置只在正式full前按真实反传测量选择microbatch和I2Group checkpoint数量，保持有效batch16与模型/优化方案不变，目标24GB卡约20GiB。允许0..8个前置I2Group重计算；forward/gradient与无checkpoint版本核对。full后execution与源码冻结，resume必须完整匹配。

## 前置检查

官方源一致性；输入仅来自真实锚点、target不读；4→13映射与中央三层索引；同权重checkpoint开关的输出及参数梯度；DCT数值有限；完整256²训练更新和全套validation指标smoke；恢复与checkpoint哈希；正式full入口无训练的preflight；实际显存及推理效率。smoke使用完整64通道/16blocks，不使用小模型替代。

执行检查通过即可交付用户full，baseline不以小样本拟合收益选择架构。smoke不用于模型选型，不宣称小样本优于PAST-Net。

## 完成后如何判定

首先核验全部23患者、数据/源码/权重哈希及训练完整性；报告I3Net与现有control的患者配对差、10,000次bootstrap CI、困难四分位、质量与效率；明确训练与初始化不同。单seed只用于刻画参照差距，不宣称SOTA。

额外报告最后30轮validation best增量。若达到预算上限且此增量>.03 dB，标记“预算受限，收敛未证实”；不能通过选用较弱、未收敛基线夸大PAST-Net优势。不得按结果删去基线或把validation分数写入旧test主表。后续三seeds/外部评估仍需独立锁定协议。

所有本包Python、协议、full.ps1、官方源副本和冻结v2源码哈希进入manifest。旧代码/checkpoint和论文表不修改。用户运行full，助手完成实现、smoke和复核。
