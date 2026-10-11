# 这轮阅读后仍值得验证的方向

当前确认claim0、科学确认患者0。新增3篇原文使“缓存局部计算”“复用参考IN/GN统计”“跨扩散步复用高层特征”三类宽泛首创进一步不成立。它们保留为已知方法对照与计算准备；原Madras/Mozannar收益选择碰撞、SafeRestore/MoEDiff、PCHIP及冻结task负结果不删除。

本轮新得到的是工具能力：在一个已见开发MRI、旧已认证单001PCHIP最后模型上，保留原batch可减少一半候选forward并达到全体积逐位等价。新增MRI任务效益证据0。合成19series成本预检不是确认19例疗效或数值资格。

| 下一问题 | 可检验的潜在claim | 最关键排除项 | 当前状态 |
|---|---|---|---|
| 同observed、同容量/监督/预算充分适配后，SR/修正还有多少病灶任务余量？ | 严格预算下仍存在可由observed预测的剩余修正收益；或充分适配消除了原先SR收益 | 强PCHIP、同observed直接任务、matched-init强SR task；训练/teacher/动作生成/评价成本全计 | 第一优先；等19series最后两模型共同冻结并按原gate评价 |
| 单动作收益会否因组合后非局部task响应而失效？ | 特定MRI条件下，单动作加和与真实联合全FOV收益的偏差可预测、可被更合适策略减少 | 相同已知defer/双路径cost头、joint evaluation、同预算随机；不能用IN已知非局部性独占方法新意 | 有结构探索资格；尚无真实有益动作或联合收益标签 |
| 动作面积能否代表真正推断成本？ | 基于实际window/batch足迹的预算分配，在患者效果和真实成本之间优于面积代理 | 一般cost-sensitive策略已知；必须同总训练/推断预算、同feature/容量，包含无节省series | 19series仅支持成本proxy偏离；真实策略收益未测 |
| 扩散cache的自然图像相似是否保持MRI小病灶端点？ | 同真实吞吐下恢复/任务tradeoff的可复现结论 | DeepCache固定/非均匀刷新、减少sampling步、完整推断，fixed seed/anchors；强task必须适配 | 当前没有本轮合格MRI diffusion执行基线；留准备，不优先扩展大训练 |

## 最短的后续科学验证链

1. 继续当前session99542，CPU/float32及共同初始化固定配方不变。只使用native和PCHIP各19,998更新最后模型。需要真实terminal exit0与39,996更新receipt，然后执行已准备56FOV主评价和独立重放。训练loss及本轮旧单001模型都不能替代四已见验证gates。
2. 若任一臂原gates失败，先做充分适配/软件定位，不生成“恢复任务收益”结论，不开放八确认。若通过，以开发患者预算先核SR/直接任务公平适配入口，冻结候选动作生成和主端点。强PCHIP效益被充分适配消除时停止该正向claim。
3. 仅当有真实开发残余收益时生成paired label。GT只在开发完整FOV打分，部署动作候选只依赖observed，不能用人工病灶框或GT选ROI。本轮中心ROI只是结构试验，不成为策略训练候选。缓存先对实际动作逐例做完整路径核验；一旦不等价即退完整推断，不改原门槛。
4. 检验动作交互：在同输入、同随机性和同任务最后模型上记录Δ(a)、Δ(b)、Δ(a∪b)，报告interaction=Δ(a∪b)−Δ(a)−Δ(b)。多个候选共享窗口会影响成本；节省或收益都不能机械相加。此定义已知，本轮未产生任何此类MRI效益label。
5. 学习策略至少对比同feature/capacity的双路径cost头、既有cost-sensitive/defer、普通risk/error头、全不动作/固定动作、同真实预算随机、强PCHIP与直接任务。真实动作生成、teacher、label计算和cache初始化也入总成本；面积或forward数不能冒充端到端wall time。
6. 在开发/四已见验证范围完成选择并冻结策略/门槛，再依据原确认协议评八保留确认及独立任务网；不在八患者上挑动作或阈值。仅patient-first效果/失败完整保留、预算公平和独立确认一起支持窄claim。当前这一步未执行。

## 立即可准备、暂不执行的条目

- 实际动作缓存key：model SHA、baseline observed/reconstruction/input SHA、统计量、完整grid/affine、window顺序、batch位置/形状、blend、precision/backend/device/线程、模型mode；逐series最多约0.805GB概率RAM缓存。
- 标签成本ledger：缓存初始化与实际重新forward分开；完整reference核验计入资格成本，不能藏在训练预算外。ROI宽32/64无节省的两series保留为完整计算分支。
- 交互记录schema：patient/series/action ids、candidate和union输入SHA、完整/anchor/missing/tail预测/GT计数、actual union window ids、端到端成本、empty/undefined、全部失败；本轮不虚构MRI标签填表。
- SIGE reference-statistics近似作为机制control，而非新方法；DeepCache先例作为未来diffusion baseline候选，先确认存在适配MRI的可用模型及同吞吐对照再启动。

[三篇阅读证据](literature/2026-10-07_incremental_inference_primary_reading.md) · [实际缓存资格与成本](MC_RC_3D_LOCAL_EDIT_CACHE_QUALIFICATION_RESULT_2026-10-07.md) · [此前创新判断](INNOVATION_DECISION_AFTER_DEFER_READING_2026-10-07.md)。
