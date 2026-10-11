# 直接观测物理表示的精确线性秩及同统计合成见证

本轮新增证据解释当前两通道direct/PCHIP基线的输入差别，不声称原raw数据来源不同或原流程比较无效。两路仍使用相同合法原始观测；**相同原始源不自动保证最终任务网输入含有相同有效信息**。线性重采样、PCHIP非线性和重采样不交换本身均非本项目首创。

[生产](experiments/observed_projection_information_2026_10_08/attempt01.json) 真正工具退出f505cc=0、.042580s；[独立核验](experiments/observed_projection_information_2026_10_08/independent_modular_rational_attempt01.json) 真正退出078eec=0、.142675s。仅读已冻结19系列两通道资格JSON和源码，0新MRI/GT/模型数组、神经/GPUforward、训练更新，原live训练单列。不读4验证、8确认或lockedIXI。

## 全19系列结果

在归一化统计已固定的条件下，稀疏normalized numerator到统一physical grid的线性矩阵是三轴插值矩阵的Kronecker积。availability只由固定观测mask决定，固定零padding不改变理想实数秩。

生产用Fraction稀疏消元；独立用另外的整数坐标公式重建全部系数，在两个预定素数1000003、1000033下核rank。全部22个不同axis map均达到matrix行/列维数上界，分母与素数互素，因此是有理数秩证书，不只是两个近似浮点rank相同。全部19series的轴、维数、患者合并及汇总复核一致。

- 19/19保持观测z方向全列秩，没有观测anchor因该理想z映射形成全零列。
- 12/19存在面内线性零空间。原normalized observed强度维数总86,999,040，映射rank总58,334,368。
- 每患者全部series维数先合并后计算rank/原维数、再患者等权，保留维数比例为0.6746856073。**不是MRI信息量、病灶可恢复性或像质损失百分比**。

典型及完整分组（UID完整值保留JSON）：

| 面内native→physical | 系列数 | 面内rank/原维数 | 说明 |
|---|---:|---:|---|
| 256→270（两轴） | 2 | 1 | 原256列均保留 |
| 512→520（两轴） | 3 | 1 | 原512列均保留 |
| 384→420（两轴） | 1 | 1 | 原384列均保留 |
| 384→400（两轴） | 1 | 1 | 原384列均保留 |
| 512→440（两轴） | 1 | .7385253906 | 患者005一series |
| 512→360（两轴）或512×384→360×270 | 9 | .4943847656 | 两轴线性缩小 |
| 640→400（两轴） | 1 | .390625 | 患者006一series |
| 512→400（两轴） | 1 | .6103515625 | 患者010一series |

精确实数rank不证明实际float32算子逐位可逆、数值条件良好，也不证明实际解剖信号落在丢失方向。PCHIP是非线性，不能赋予上述同一个线性rank或宣称其总信息更多。当前输入模块曾明确只保证同raw源；本轮是新增实证解释，未推翻其正确性资格。

## 实际模块上的固定合成见证

[v1协议](OBSERVED_PROJECTION_INFORMATION_PROTOCOL_2026-10-08.md)在任何合成评分前写下，随后核实际源码发现首尾linear fallback；因此另写[v2执行合同](OBSERVED_PROJECTION_INFORMATION_PROTOCOL_V2_2026-10-08.md)，绑定真实内部四anchor PCHIP、首尾linear与tail复制，并替换预先固定见证。v1未执行、无效果用于选择v2；两份均保留，不称运行失败。

native r4/c1/z16、observed z0/4/8/12、physical r2/c1/z12。两个预定观测数组A/C的mean=1.5、variance=1.5、元素数16完全相同，使用实际模块同observed统计归一化：

| 路径的A/C比较 | float32逐位相同 | 最大绝对差 |
|---|---|---:|
| direct sparse numerator→physical | 是 | 0 |
| availability→physical | 是 | 0 |
| 先面内投影的observed anchors | 是 | 0 |
| native local PCHIP→physical | 否 | .0425258428 |
| 共同投影anchors→local PCHIP→z physical | 是 | 0 |

独立有理数Hermite/斜率/fallback/显式像素中心插值得到PCHIP差.0425258636，各输出与生产最大误差≤3.81e-7，远小于预定1e-5容差。无需假设外部不同统计即可出现：direct最终输入完全相同而native先PCHIP的最终输入不同。合成维度用于反例，不声称该幅值/信号实际存在于MRI，不测任务收益。

## 对下一项实验的具体影响

原两路公平workflow比较仍可回答“同raw观测预算下哪个流程更有效”。若要解释差别来自恢复先验或任务网利用能力，应附加**共同投影observed anchors后再分支**的预处理控制，并保留原native-PCHIP先生成参照；新的共同投影路径不能悄悄替换已资格模块或原观察保持合同。先测输入差异和额外费用，最终合格模型上再做完整患者paired任务比较。

原训练99542真实退出并两臂最终冻结后，仍先原56FOV/全部6gates/strict。本诊断不会改变门槛，也不能替代强适配或确认。准备见 [后续计划](PROJECTION_AND_SELFSUPERVISED_ACTION_PREPARATION_2026-10-08.md)。
