# 核心设计与SOTA判定范围

## 已有证据约束

原G086控制组25.562011 dB（干净validation23患者、观测归一化）；geometry、correspondence-only、STC的full净收益都远低于预设门槛。线性残差探针主要校正预测自身偏差，且PSNR收益伴随MAE退步；加入MAE不退约束后仅剩+.002331 dB。不能再用这些小收益支持重复续训或堆模块。

但低容量线性/凸探针只检验指定函数族，不能排除非线性结构交互。它们并未测得Bayes风险或证明G086达到信息上限。LACV据此提出一个独立结构假设，不修改旧gate。

## 与原网络的区别

核对本地 `pastnet_v2/vendor/model_ma.py` 与 `model_ma3latent.py`：四个真实锚点和coarse各自编码，先通过gate做同位置加权和，进入主干；多尺度latent mixer随后混合三个待生成query位置。

LACV复用上述真实锚点编码，但在新路径保留独立锚点轴，直到三层(masked anchor×x、anchor×y)交互完成，再按查询读取。旧coarse与主干路径保留，零投影保证初始化不改变原函数。表示里被保留的是原观测之间的关系，并非增加扫描信息。是否克服了实际瓶颈仍需full验证，不能从网络图直接推出性能增益。

相同容量消融将平面kernel看到的邻近真实锚点替换为重复的当前锚点，保留全部卷积参数；最终query readout仍能看到四锚点。这是检验“先跨锚点空间交互”的单变量对照，不是假装per_anchor完全不含跨切片信息。其functional卷积已纳入本包部分算子FLOPs统计，避免因未触发module hook漏算。

本轮新增的是因子化空间-z交互，原FFT与原query latent模块原样保留。既不以输出3D refiner修图，也不同时改loss/物理条件/上下文范围。跨平面结构本身不是首次提出，只有实验和消融支持后才讨论具体贡献。

## 相关工作核验（2026-09-14）

| 工作 | 核验事实 | 对本项目的含义 |
|---|---|---|
| I3Net，TMI2024 | 含inter/intra-slice分支、面内频域处理和cross-view block；本地源码`external/I3Net/model_zoo/i3net/basic_model.py`可对应 | 不能把“跨视图”本身写成首次提出；应比较真实锚点轴上的具体机制。[原论文](https://arxiv.org/abs/2405.02857) |
| ACVTT，2025 | 标题和方法针对CT跨视图纹理迁移与多参考非局部注意力 | 本地主表已有MRI适配结果；LACV没有复制这套non-local attention。[原论文](https://arxiv.org/abs/2509.20242) |
| DP-NSL，ECCV2026 | 采用观测一致性投影、混合B-spline、局部一致性decoder；论文的MRI实验为185例IXI **T1** Hammersmith | 已纳入后续强基线核对清单；不能把其T1原文分数与本地T2直接比较，也不能把“超过旧I3Net”自动称为2026SOTA。[原论文与实验设置](https://arxiv.org/html/2606.26716v2) |
| CoInS-Net，2026预印本 | 联合连续位置插值与分割，使用物理spacing和任务交互 | 任务合同不同，先核对监督和输入条件；不因标题相关就把论文分数直接放入本地插值表。[原论文](https://arxiv.org/abs/2608.09391) |

DP-NSL的[官方索引](https://github.com/DeepMed-Lab-ECNU/Medical-Image-Reconstruction)已列出[独立代码仓库](https://github.com/eeeric-code/DP-NSL)。本地 `external/Medical-Image-Reconstruction/README.md` 仍只列I3Net，说明本地副本滞后；本轮未修改或pull该目录，未声称已完成DP-NSL复现。

## 什么才算达到目标

本地历史表中，G086 fastMRI development-test分数已超过I3Net，但IXI G07落后，NingXia没有同候选完整复评。这不能支持三域SOTA结论。当前所有筛选继续用validation，test24不作为新候选选择依据。

完整确认需同时具备：注册的总体与机制消融通过、固定三seed配对、质量和效率完整报告、候选锁定、IXI/NingXia同协议外部评估，并补齐适用的近期强基线比较。DP-NSL等的本地比较目前未完成，因此“2026SOTA”仍是目标，不是现有事实。新强基线适配与本候选实验分开记录，不能引入预训练数据或评价口径混杂。
