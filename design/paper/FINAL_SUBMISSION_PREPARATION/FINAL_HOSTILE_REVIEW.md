# 最终五位严格审稿人模拟

这是对五种反对意见的书面模拟，不是真实审稿、独立专家评审或接收概率评估。回应只使用冻结证据及明确标注的事后敏感性。

## Reviewer A：目标掩膜制造20/20结果

**最强批评：** target-derived mask把目标信息用于选像素，可能排除背景或高误差区域，产生有利可观测比例；即使各条件使用同一mask，也不能自动代表真正acquired-only审计。

**精确证据：** 补充support全20对表与 `CROSS_ARCH_SUPPORT_SENSITIVITY.csv`，同一预测改用既有nearest phase-0 foreground union及full common finite support。两队列各三支持区域均20/20正同时CI，最差模型对效应排序rho .997、最多移一名。并未重训或按结果改阈值。

**仍未解决：** O的计算本身仍依赖目标；这里只排除了这两种替代合同下的支持依赖，不能验证缺目标的局部误差概率估计。acquired union只取固定A侧证据，虽事先写入本轮协议且保持配对，仍非所有可选合同。正文改为“under the tested support contracts”，不称target-free observability estimation。

## Reviewer B：phase变动混合身份与几何

**最强批评：** companion从phase0到phase2不仅换measurement identity，还改变左右位置、周围解剖、归一化和模型响应；任何O变化都可能由这些构成。旧same-model IXI mirror无显著结果不能替新跨模型实验背书。

**精确证据：** 补充geometry全20对表与 `CROSS_ARCH_GEOMETRY_SENSITIVITY.csv`。residue1/3单独、等权平衡、nearest-distance {1,3}匹配均20/20正同时CI；IXI严格四邻锚双residue平衡也保留。fastMRI严格合同NA，未虚构锚。

**仍未解决：** 新mirror差异有fastMRI8对、IXI6对同时CI排零。它们是实质orientation警告，已写入摘要/主文/结论。反射类平衡不是相同解剖的有符号几何交换，也不控制完整网络感受野。删除“pure identity effect”式理解，只保留“现象在平衡后仍存在，干预同时改变剩余上下文”。这是最应收缩的科学主张。

## Reviewer C：相关集成误差是旧思想

**最强批评：** energy identity是平方展开，ensemble covariance、negative correlation learning、输入/梯度多样性及系统误差早已研究；给它命名MIRA并不等于方法学突破。MRI场景可能过窄，且没有新网络或有保证的估计器。

**精确证据：** 主文Related Work对ambiguity、negative correlation、random subspace、gradient diversity、MRI systematic error逐项归属；图4是固定不同架构、同一目标、物理锚身份登记的完整干预矩阵，图3是acquired-only有限响应和固定边缘coupled/independent验证，表3展示可执行审计输出。

**仍未解决：** 证据支持实验设计、审计合同与边界呈现的贡献，不证明新的代数理论。没有非MRI广泛影响验证，也无实际uncertainty方法的统一优势。题名选择Auditing Shared Measurement Dependence；是否满足CVPR新颖性/影响要求仍取决于真实审稿判断。不能靠增加无关baseline掩盖这一点。

## Reviewer D：长期回顾与数据反复使用

**最强批评：** 从最初ranking目标转为local O、控制反转修订、多轮数据开发及后续support分析，均可能反映选择性推理。事后hash只能保护本轮结果，不能恢复未观察到的历史选择自由度。

**精确证据：** 补充provenance保留rank-primary历史、one-case smoke之后的control修改、TopCoW亮掩膜开发史、所有负结果。新补丁在计算前区分A/B/C并哈希3955数组；全部20对和三个支持区域完整报告，未改阈值、未选子集追逐效应。统计上共同resample examinations，不把共享模型对称为独立replicas。

**仍未解决：** 没有已认证未接触队列；bootstrap不计历史研究选择。hash不是第三方preregistration。正文明确retrospective与post-hoc，不称独立confirmatory study。NingXia仅八患者，fastMRI训练/验证存在既知一个患者重合且test无本地ID重合；不能重命名划分来消除历史偏倚。

## Reviewer E：没有可用的校准failure score

**最强批评：** MIRA的关键O需要GT，影响探针增加计算而未给出阈值、概率或可用abstention，不能帮助部署时判断单次重建是否错。报告卡可能只是昂贵的回顾性分析工具。

**精确证据：** Algorithm1和主表3明确独立字段及NA；图3a/b显示acquired-only响应与误差alignment有条件关联，但主文把ranking另列。补充完整guard有fastMRI零正例、IXI每pair仅二正例，全部12个guard-baseline同时AP区间跨零；旧选择、jackknife、residualization失败也保留。

**仍未解决：** 没有个体正确概率、临床决策收益或经过外部校准的failure detector。结论明确“MIRA measures when agreement loses observability, not whether an individual reconstruction is correct.” 它是一套研究审计框架，不能作为实用uncertainty score来出售。按停止规则不再搜索新scalar。

## 最终判断

最强接受理由是跨架构、替代支持区域、残差平衡与有限响应试验构成可复核且边界明确的局部现象证据链；最强拒绝理由是贡献仍可能被认为是已有相关误差思想在回顾性MRI场景的审计实现，缺乏未接触确认与可用校准输出。身份的纯因果解释必须继续减弱。现有范围内继续加实验不合理；只在作者主动提供真实未接触、来源和授权完整的新队列且观察结果前另立协议时，才考虑新确认研究。
