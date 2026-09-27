# 架构覆盖后的主张—证据矩阵

| 主张 | 适用模型 / 队列 | 信息合同 | 正结果 | 空结果 / 稳定性失败 | 推断家族 | 稿件落点 | 本轮影响 |
|---|---|---|---|---|---|---|---|
| A：共享/分离证据改变局部可观测性 | 原五核心；fastMRI24/IXI115，原同模型两架构另含NingXia8患者 | 主矩阵同目标 target1% support；原支持/几何敏感性不变 | 原每队列20/20有向对同时CI正 | orientation差8/20与6/20；浅层fastMRI严格四邻锚NA | 原20对/队列/端点；扩展八模型/队列/支持单列 | 主现象图、覆盖表；补充全部扩展表 | **仅澄清覆盖**。新增同输出对照 shared O=0为构造；不能把正ΔO当八次独立机制验证 |
| B：架构多样性不保证独立误差 | 原 HAT/SwinIR/SAINT/I3Net/CycleINR 五模型 | 固定A0，B0→B2；共同目标与支持；无TTA | 原主矩阵不变 | fastMRI fixed-A排名0/20，IXI16/20；几何混杂未完全解除 | 原20对同时家族不变 | 主跨架构图与讨论 | **仅澄清覆盖**。未新增可证明B的跨模型矩阵，不将八个self-control冒充B证据 |
| C：连续局部响应影响超出锚数 | HAT/SwinIR/SAINT；两个脑队列 | 掩膜、量程、扰动均acquired-only；目标只用于alignment评估 | 新SAINT fastMRI .032751 [.015435,.050067]；IXI .132790 [.125627,.139953]；fixed-count .379778/.417380；均PASS | 历史SAINT空结果保留；I3Net/CycleINR历史FAIL且本轮接口NA；五个可用接口未跑 | 原HAT/SwinIR每队列2模型家族原样；SAINT新2队列/端点家族，不混称全五模型校正 | 更新图3、全核心数值表、报告卡 | **增强有界证据**：新增非Transformer实测支持；不支持普遍性 |
| D：局部协方差模型描述有限神经响应 | HAT/SwinIR/SAINT；同12个IXI检查 | 固定上下文、共同锚、8平衡场、Cartesian独立构造、epsilon0=.0025；不读取目标 | SAINT四幅度mean同时区间均负；48例全部aligned | 原HAT/SwinIR worst126.4%保持；无opposing实证；不保证全局Jacobian | 原8模型幅度对比家族保持；SAINT单列4幅度家族 | 图3c、补充全部幅度表 | **增强有界证据**：非Transformer局部趋势；未缩小原实测最坏边界 |

13 个名称代表本地重建实现，不等于13种结构独立架构或13个MIRA机制基线。ArSSR与内部CycleINR共享代码谱系；实验使用的权重和接口绑定另列。

NEEDS HUMAN CONFIRMATION：NingXia机构/IRB或豁免/同意或豁免/脱敏/许可，以及精确fastMRI release与授权。计算不能替代真实文件。
