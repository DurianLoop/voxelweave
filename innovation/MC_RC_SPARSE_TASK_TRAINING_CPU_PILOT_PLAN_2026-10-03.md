# 稀疏输入任务训练 CPU 能力 pilot（运行前协议）

目的：让一个训练身份明确的任务网络真正从 MC-RC 开发患者的稀疏输入学习分割，检查当前数据/实现是否足以支持后续任务适应研究。旧作者网络 native 和稀疏均失败，不能继续用它解释 SR 机制。本 pilot 是能力诊断，不是新方法对照或最终科学确认，也不替代原 6×5 训练曝光矩阵。

固定开发名单沿用当前19系列/11患者。训练排除完整患者013，使用其余10人18系列；013唯一合格系列作开发内部留人诊断，012唯一合格系列作训练内能力检查。这一选择在本 pilot 模型效果之前写定，不按结果更换患者；两人仍属于原开发角色。4验证和8确认保留患者不读取输入或标签，科学split仍未启用。所有模型从随机初始化训练，禁止加载作者/既有任务权重。

输入固定 phase0/stride4、raw四邻 PCHIP、observed_shared z-score；保留原生全FOV/RCZ网格，不缩放、不以真值裁剪推断。稀疏接口仅接已核验 observed-only 包，标签读取单独进行；本 pilot 不解码任何隐藏MR像素，不提供观测层标签作为推断提示。五个相邻原生层为网络通道，z越界复制端层。训练标签仅用于监督和前景采样，不进入重建/归一化。背景归一化值不裁断。

网络：2.5D U-Net，双3×3卷积+GroupNorm(4组)+ReLU，通道8/16/32/64，3次2×2 max-pool，bilinear上采样+skip，1×1输出单logit。GroupNorm仅在每个固定patch上运算。训练patch96×96，batch4；每update均匀抽1患者，再在其合格系列内均匀抽1系列。batch2个patch以前景体素为中心并独立±24像素平移，另2个中心在全FOV均匀抽样；所有z先验均为label监督训练采样，不影响推断。左右/上下随机flip、0/90/180/270旋转；强度乘U(.9,1.1)、加U(-.1,.1)。BCEWithLogits均值+soft Dice loss（batch整体，smooth=1），等权。

种子20261003；AdamW lr=.001、weight_decay=.0001；cosine衰减到.0001，4000updates，无早停，无按013/012选checkpoint，无阈值调优。保留随机初始化SHA、每100步loss/梯度/患者采样累计数、最后checkpoint和运行合同；如资源或非有限值失败停止，保留失败attempt。先仅做10步合成tensor运行估时/反向传播检查，不以真实标签调整预算。单update估时超过2s或GPU初始化触发则不启动4000步。

推断固定96×96全FOV规则tile，stride64，边缘最后tile贴边；五层通道照训练，所有tile等权平均概率，阈值.5，无最大成分或真值ROI后处理。最终对012/013各评raw PCHIP和raw linear（同真实观测、同observed_shared统计）；线性条件仅作固定输入敏感性，不能当训练匹配或同预算新方法。预测存bool压缩包，完整所有z评分，anchors/supported missing/tail另列。每tile覆盖次数检查>0。

指标：完整native grid voxel Dice、precision、recall、绝对/有符号体积误差；3D物理ASSD/HD95采用6连接surface、affine列范数对应spacing；empty/undefined显式记录。主能力门槛预写为：012和013的PCHIP full Dice≥.70、supported missing Dice≥.65、full recall≥.70、绝对相对体积误差≤.50，且全FOV/非有限/身份/CPU检查通过。门槛只决定是否值得扩大能力验证，不构成临床有效性或发表标准。单个013不能估泛化，也不做患者bootstrap。

运行仅本进程CPU单线程、below-normal priority、CUDA不可见并禁止lazy_init；每100updates/每case检查磁盘≥15GB、可用内存≥8GB，不检查/中断用户训练进程。工作cache仅RAM（19体积float32约1.39GB），新增模型/日志/预测磁盘上限50MB。独立核验最终预测计数/物理surface/coverage、013整人训练排除与checkpoint直接前向重放；实现复核不能描述为独立科学确认。

若能力失败，保留固定配置反例，不据两人表现调参后称确认；后续需要更充分训练/容量/物理spacing条件与4验证患者能力评估。若通过，仍需完整6×5同容量/预算矩阵、native能力参照、直接稀疏分割/分辨率随机化对照，最后冻结后使用8确认保留患者。当前publication claim未达成。
