# Full前核验完成

2026-09-16。新分支只更改训练目标的risk项；模型结构、参数、初始化、其他loss项、数据与full预算不变。所有旧分支继续保留失败结论。当前没有新full结果，助手未启动full。

## 数值与机制

hard loss与旧实现完全一致，全部参数梯度最大差0；两臂初始化与forward逐位一致，target不进入forward。soft差值仅为.2×risk差。CVaR梯度质量误差2.98e-7，权重非负且有界；小tau极限、平滑值上下界和固定eta方向有限差分检查通过，方向导数差2.40e-8。

训练残差缓存来自同预算control checkpoint，患者集合与train manifest匹配，未读取新validation/test结果。111患者/112series/340区间上，人工预测扰动σ=.001下risk梯度相对变化hard .060926、soft .013451，下降77.923%，超过注册20%机制检查要求。soft有效像素比例18.807%，在原hard-tail上的权重质量66.475%；全部slice权重质量最大误差4.77e-7。

这没有测量真实SGD参数梯度方差，也不是新信息或质量收益。尾部关注被重新分配，正式gate额外要求原hard tail10 MSE均值不退。

## 固定样本能力与资源

两臂从相同G086分别训练96步，4个注册train区间，无EMA和warmup，仅为固定能力检查；full仍严格用原recipe。

| 指标 | 初始 | hard最终 | soft最终 |
|---|---:|---:|---:|
| MSE | .002931962 | .001823149 | .001815363 |
| MAE | .024670877 | .019313945 | .019315102 |
| MSE相对下降 | — | 37.818% | 38.084% |

soft满足相对自身初始MSE下降≥5%且MAE不退；hard也能拟合。soft相对hard的MAE略高，因此不宣称在这个拟合集上全面优于hard。没有根据两臂差值选步数、tau或checkpoint，临时能力权重未保存。

完整反传soft峰值19.6463 GiB allocated /20.3145 GiB reserved，约370.45ms/区间，不含IO；hard19.6457/20.3613 GiB、约368.87ms/区间。两者均使用checkpoint5和microbatch2，full有效batch固定16。真实trainer smoke再次测得约19.62/20.31 GiB。

## 执行和来源

soft/hard各1轮真实trainer smoke通过；soft已完成checkpoint的恢复加载通过，不声称验证了中途断电后的逐步位级重放。旧control full的源码、recipe、数据、checkpoint和23名val患者完整性通过；本分支能力/机制/smoke源哈希一致。

本分支soft full入口使用trainer stub核验，没有启动训练或建立full目录。外部test/lock、重复hard full被入口拒绝，smoke被正式报告拒绝。full.ps1语法核验通过。

推理仍是同一模型，992,179参数、446.58966G部分Conv/Linear FLOPs/三层区间。soft实测48.1344ms/缺失层，.858745GiB；与旧control计时比1.00924、显存比1.0。相同推理图的一次计时波动不能归因于新增推理算子；本分支没有此类算子。

## 交付

只交付 `design/pastnet_softtail/full.ps1 -Seed 3407`。full与control相同G086初始化、数据、seed、80轮上限、lr和EMA，仅risk项不同。相对control需≥+.10 dB及全部注册guards；三seed与IXI/NingXia仍未开始。

- [最终来源与入口检查](final_verification.json)
- [训练内稳定性](stability.json)
- [两臂能力结果](capacity.json)
- [推理效率](efficiency_soft_tail.json)
