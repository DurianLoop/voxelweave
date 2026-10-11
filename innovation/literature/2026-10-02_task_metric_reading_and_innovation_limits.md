# 指标方法批量核读：哪些问题已有先例，哪些还需要本项目证据

本阶段取得三篇可追溯全文 XML/BioC，重点核读与完整体积任务、短/小病灶、边界实现及患者汇总相关的正文段落。这里不是逐一复现所有补充图和 20 种指标，也不把全文取得等同于全部附录已读。公开检索与两次 Europe PMC XML 500 失败、NCBI BioC 成功均保存在 [检索索引](source_cache/task_metric_papers_2026-10-02/attempt_01.json)。

| 论文、正式 DOI 与实际阅读范围 | 得到的约束 | 对现有工作采取的动作 |
| --- | --- | --- |
| Reinke et al., *Understanding metric-related pitfalls in image analysis validation*, Nature Methods 2024；10.1038/s41592-023-02150-0；[全文](source_cache/task_metric_papers_2026-10-02/pitfalls_fulltext.txt)、[BioC](source_cache/task_metric_papers_2026-10-02/pitfalls_bioc.xml)。重点 P2.1–P2.4、P3.1–P3.5 和 Fig.4–6/Extended Data Fig.1–2 的文字说明 | Dice 对小结构、形状和边界的局限、空输出、边界提取差异、跨患者直接池化、排名不稳定均已明确讨论。换成脑 T2 不能使“PSNR/Dice 不够”成为首创 | 固定患者分母；不丢弃空预测；保存两种病灶 NMSE 汇总；把边界体素、距离对称化和分位约定写进协议；保留 raw PCHIP 和两个标签的全部结果 |
| Maier-Hein et al., *Metrics Reloaded: recommendations for image analysis validation*, Nature Methods 2024；10.1038/s41592-023-02151-z；[全文](source_cache/task_metric_papers_2026-10-02/reloaded_fulltext.txt)、[BioC](source_cache/task_metric_papers_2026-10-02/reloaded_bioc.xml)。重点 problem fingerprint、Semantic segmentation、Step 3、Discussion 和 Extended Data Table 1 | 指标应来自具体问题，不能因为训练用了 Dice loss 就只测 Dice。建议互补的重叠/边界评价；层级数据先逐图/患者评价；技术正确性和临床结局不同。推荐 NSD 处理标注容差不代表任意容差即可宣布临床可靠 | 当前 Dice 为事先固定的技术主终点，体积/物理边界为补充。1 mm 带只做明确的离散敏感性，不能把它当临床容差、标注真值置信区间或自动宣称 NSD 等价。患者配对 bootstrap；不产生不断变化子集的正式推断 |
| Taha & Hanbury, *Metrics for evaluating 3D medical image segmentation: analysis, selection, and tool*, BMC Medical Imaging 2015；10.1186/s12880-015-0068-x；[全文](source_cache/task_metric_papers_2026-10-02/taha_fulltext.txt)、[JATS XML](source_cache/task_metric_papers_2026-10-02/taha_fulltext.xml)。重点 spatial-distance 定义、Multiple definitions、Guidelines、Conclusion/Table 5 文字 | 20 种指标的定义、偏差和任务依赖已有系统分析。其平均距离 AVD 在本文定义为两方向平均距离的最大值；既不等同本程序的 pooled ASSD，也不等同 MASD。该文建议不能无条件替代新共识或具体数据证据 | 记录具体公式；同时输出 pooled ASSD、方向均值平均 MASD 和 pooled HD95。用物理点坐标全对距离验证，增加边界点数量不相等的样例，避免相同尺寸样例掩盖对称化差异 |

两篇 Nature Methods 论文来自同一 Metrics Reloaded 研究线，属于互补方法/建议，不能算两个独立 MRI 实证来源。作者/年份/DOI 按 Europe PMC 精确标题匹配认证，未根据猜测填写。

Taha 的 spatial-distance 段落还明确说距离按 voxel 计算，不考虑 voxel size；当前 CISS 面内 0.46875 mm、轴向 1.5 mm，因此本项目使用物理 mm 并单独验证，不能把其 voxel 距离或 AVD 直接拿来对比本程序 ASSD。

## 收窄后的候选与创新边界

**候选 A：同观测的完整体积图像收益与任务收益是否分离。** 宽泛的“重建指标不代表临床价值”已有上述论文及 Fischer/Morshuis MRI 先例，不能写首创。当前可检验的是特定冻结 IXI 重建器、强解析对照、全部余数缺失层、原生 CISS 病灶体积和完整患者分母下的联合方向；单一数据来源的实证也不是自动可发表。001 的 HAT 对 pipeline PCHIP Dice 提高仍作为反证保留。

**候选 B：病灶切片筛选的实际覆盖以及对方法比较的影响。** 小病灶和汇总偏差已有明确先例。新证据需来自固定原始队列，先计算旧规则究竟排除谁，再检查全部患者与规则子集中的效果量是否不同；不能仅凭 18–19/45 上界宣布排名反转。当前程序主名单始终 45，覆盖分析不得用于删除患者或调整主要比较。

**候选 C：残差修正方向的收益预测。** 与既有 PAST/wavelet 工作相连，但小波、残差 flow、任务损失、误差头和 conformal 都有明确先例。之前的患者级 oracle 诊断已限制简单开关的上限；此时不能用新名称把它重新包装。若 A 的独立缺口成立，再研究有限的局部修正是否能减少任务代价，需要冻结动作方向、同观测数据、强解析/固定混合/误差头对照和另一未用于设计的确认来源。

“原 JSON 与 RTSTRUCT 的边界不同”已是 Shapey 2021 Fig.2 的已发表现象。本阶段不把标注转换作为第三个新发现，也不把本协议、哈希归档或 CPU 兼容性称为科研算法贡献。

## 可以现在验证与需要以后验证的分界

现在用 CPU 完成：输入/标签几何、七条件重建与 001 输出等价、八窗路径、物理边界公式、空值、bootstrap、固定独立患者的任务推断及结果复查。新研究使用的分割器已经冻结，CPU 上可执行，不必等 GPU。

以后用 GPU 并需新实验设计：训练新的收益头或任务保真残差策略；复现任务引导 diffusion；比较新 PAST/wavelet 权重。这些仅做好 [后续准备](../GPU_FOLLOWUP_TASK_FIDELITY_PREPARATION_2026-10-02.md)，没有训练结果，也没有完成可发表主张。
