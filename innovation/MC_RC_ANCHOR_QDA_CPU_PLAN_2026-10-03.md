# 真实观测层轻量表征：逐患者留出 QDA 诊断合同

本合同冻结一个新的开发诊断，不是新颖方法，也不是旧 30 特征岭动作政策的复活。完整 native16 首跑已结束，独立重放仍在执行；没有用部分 native 平均或挑选系列设计本试验。只有完整16队列与独立 proof errors=[]且 hash 一致后才启动。本次统一使用全部16合格系列/8开发患者，患者的所有时点同组；不按任何模型表现删来源。原 checkpoint/2 mm 配置失败保持。

问题：不增加 pretrained checkpoint，不使用 GPU，真实观测 MR 的简单局部外观及坐标先验，能否通过原缺层区域覆盖/成本门槛？这是评估下一表征投资价值的低成本基线。QDA、LDA、多尺度高斯和空间位置均为既有方法；结果若好也不自动产生 claim。8 人已反复参与设计，LOPO 只能算开发泛化诊断，科学独立确认仍0。

输入严格为 phase0 原 MR planes 0,4,…。所有 MR 像素只解码 anchors；已读 native 隐藏像素不使用。每系列仅以自身 observed MR 的全体像素 1/99 百分位归一化并 clip[0,1]（range 最少1e-6）。逐 plane 构造六个外观通道：强度、高斯均值0.5 mm/2 mm、强度减1 mm高斯均值、1 mm局部标准差、1 mm平滑后的物理梯度幅值；Gaussian reflect、truncate4。另有三个坐标为 header affine 将 native r/c/z 映射至 RAS 后，相对于同体积八个角点的轴向范围归一化到[-1,1]，不做图像配准、label crop、伪跨层 image 或后验模型选择。

训练监督只解码真实观测 label planes。逐系列计算全部观测像素的两类一阶/二阶矩，不抽样、不用缺层 label 作 fit。每患者内系列等权、再训练患者等权；像素在每系列内等权。对每个留出患者，剔除其全部系列矩，使用其余7人；同一患者的第二时点不会进入自身训练。类先验为上述等权分布下的真实前景占比，不使用50%平衡先验。协方差固定 shrink = 0.9*C + 0.1*diag(C) + 1e-4*I；QDA分别用两类协方差，LDA用类先验加权公共协方差。posterior ≥ .5 等价于 log likelihood ratio ≥0；无阈值搜索、无LCC或label纠正。

固定四个模型：joint_QDA（9通道，唯一主模型）、appearance_QDA（前6）、coordinates_QDA（后3）、joint_LDA（9）。后三个为解释对照，不能选其最优重命名主模型，不把不同特征数称严格同容量。保存每系列两类质量/矩、每fold模型参数、全部预测 anchor masks、输入hash、模型membership和最小decision margin。每系列预测全部保存后才读取完整人工 label 用于评分；holdout anchor labels虽在其他fold作为合法监督，但不进入本fold参数、特征、posterior或ROI。

ROI仍为包围每个内部缺层的两个预测 anchor masks 并集+2 mm；完整全部内部缺层，原门槛 foreground≥.99、boundary≥.99、tile32 foreground≥.995、ROI fraction≤.05、tile fraction≤.10。主终点为全16系列joint_QDA过门槛数量，是否16/16；并报全部其他模型、观测Dice/recall/precision、区域各端点、所有失败、患者内系列等权。没有生成 missing MR，无完整体积task或SR收益 claim。

单进程、CPU BLAS/OMP1、低优先级、每plane特征矩阵≤100MB、单label plane≤32MB、workspace磁盘≥15GB、可用内存≥8GB。新代码只在 innovation；不安装包或修改 environment.yml，不碰用户终端训练/IXI locked test。失败无自动retry，成功目录不覆盖。

需要另一个复核脚本从原 ZIP headers/anchors 与 label 重新验证输入及只observed监督、8fold排除、全部矩/参数、全部anchor预测及原label缺层 physical-disk ROI计数。共享 SciPy 滤波库/特征提取实现明确标注，不将其称完全算法独立。任何数值/输入差异必须记录；复核失败不解释阳性结果。不因失败改阈值/半径/先验/shrinkage。本基线若失败，不能据此否定所有 learned representations，但不足以支持本配置投资或可部署保护。
