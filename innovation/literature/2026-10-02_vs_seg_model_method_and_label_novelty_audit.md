# VS-SEG 方法论文、标注转换与候选创新：本轮核读

本轮新增核读两篇方法全文，并继续核对已归档的数据描述论文及两篇任务感知重建先例。两篇转换工具论文目前只核实了元数据/摘要，不能计作全文阅读。当前没有独立验证的可发表 claim。

| 文献与阅读层级 | 实际方法、结果及限制 | 对当前 MRI 工作的影响 |
| --- | --- | --- |
| Wang et al., MICCAI 2019，DOI 10.1007/978-3-030-32245-8_30；新增全文 | 245 人，178/20/47 划分；TensorFlow/NiftyNet，手动 100×50×50 mm 裁剪；2.5D 卷积、监督注意力、hardness-weighted Dice。Table 2 最佳 Dice 87.27±4.91%，ASSD 0.43±0.31 mm。当前取得的是 2021 年修正作者姓名的 9 页正式版本；Table 1/2 已渲染核对 | 不能把 2.5D、层间上下文、注意力或病灶困难体素加权称为本项目新意。它并未进行同观测锚点下的 x4 重建方法→完整体积任务干预；但不能把其 47 人测试名单替代当前已认证的 46 人名单 |
| Shapey et al., Journal of Neurosurgery，DOI 10.3171/2019.9.JNS191949；新增全文，PMC 作者稿 BioC | T2 单模态、T1 单模态、联合模态和五网络多数投票；T2 ensemble Dice 88.25±3.90%、ASSD 0.416±0.209 mm、RVE 9.77±7.56%。人体标注等效性结论仅明确支持 T1/联合模态；文章承认扫描参数泛化和不确定性评估缺口。摘要写 243/177/20/46，正文写 246/180/20/46，冲突保留 | 不能把 T2 的结果说成人类等效，也不能把该稿与 242 人 TCIA 发布合并成独立来源。五网络 ensemble 不是当前单个 MONAI 权重。讨论中的 >20% 体积增长不是本项目可直接借用的临床伤害阈值 |
| Shapey et al., Scientific Data 2021，DOI 10.1038/s41597-021-01064-w；已有全文重点复核 | 242 人发布；原 JSON 可能离 T2 平面，RTSTRUCT 已经 GammaPlan 插值。Fig.2 的 182 例已展示原 JSON 掩膜比 RTSTRUCT 多首尾整层；作者用相同 SlicerRT 转换两者，T2 平均 Dice 97.6±2.2%，全部 >88% | 本轮在 182 上得到 0.884017 并复现首尾两层差异，是验证已知方法，不能包装为新发现。当前转换门槛已关闭，可准备独立任务研究 |
| Fischer et al., 2023，arXiv:2308.02631；此前已核读全文，本轮复查碰撞结论 | PHiRec 在 SKM-TEA 中把重建样本不确定性传播到分割并评价任务误差关联 | 排除“首次将 MRI 重建风险关联到分割”的宽泛主张。脑 T2 层间插值的具体同观测干预仍须独立验证，换部位本身不是创新 |
| Morshuis et al., 2024，arXiv:2407.18026；此前已核读全文，本轮复查碰撞结论 | 同一测量下用分割梯度引导扩散重建，评估任务边界及重建指标 | 排除“第一次任务引导重建/任务多样性”的主张。今后为当前 wavelet/残差网络加分割损失，也不能仅凭组合就声明新方法 |
| Sunderland et al., 2015，DOI 10.1117/12.2081436；元数据与公开实现 | 原论文题名与 DOI 经 Crossref 核实；转换类公开源码已逐 Git blob 核验。源码链接的旧大学网页返回 404；本轮未取得方法原文 | 动态规划轮廓三角化、端帽和分支处理属于既有转换方法。不能用实现复现代替方法论文全文审查 |
| Pinter et al., Medical Physics 2012，DOI 10.1118/1.4754659；摘要/元数据 | Europe PMC 元数据确认 SlicerRT 工具论文，未列 PMCID，OA 字段为 N；本轮未取得全文 | 工具集及 RT 轮廓转掩膜已有明确出处，不是本项目算法贡献 |

与本项目的具体连接是：IXI 训练好的 HAT/SwinIR 作为冻结重建器，是否能在原生病灶 T2 的完整体积上同时改善图像误差和冻结分割器的任务终点；强解析基线、全部余数和原始标签是否会改变此前四层目标的结论。原生标注与独立名单现在可用，但正式队列的重建/任务结果仍未取得。

优先保留两个可反证的问题：一是“同处理 PCHIP 对照下，全图收益与病灶 Dice 收益是否分离”，二是“按少数病灶切片筛选是否改变小/短病灶的评价覆盖及方法排序”。后者不能仅凭现有 96/242 的特定规则上界就推导为普遍偏差或性能排序反转。论文已报告的标签边界变化应作为这两个问题的敏感性分析，而非第三个新发现。

当前 MONAI 发布 README 明确说明它与早期论文网络不同：残差连接、stride 卷积取代 max pooling，以及额外 dropout。应以本轮认证的发布权重、代码、176/20/46 名单作为实际任务模型合同；早期论文的平均分数只用作背景。没有证明这些论文或 CrossMoDA 提供第二个独立来源。

可复查来源：正式方法 PDF 原始响应和全文抽取为 [Wang PDF](source_cache/vs_seg_original_mask_routes_2026-10-02/wang2019_springer_pdf.response)、[正文](source_cache/vs_seg_original_mask_routes_2026-10-02/wang2019_fulltext.txt)、[Table 1 页图](source_cache/vs_seg_original_mask_routes_2026-10-02/wang2019_table1_page6.png)、[Table 2 页图](source_cache/vs_seg_original_mask_routes_2026-10-02/wang2019_table2_page8.png)。临床方法作者稿为 [BioC XML](source_cache/vs_seg_original_mask_routes_2026-10-02/shapey_method_bioc.xml)及[正文/表格抽取](source_cache/vs_seg_original_mask_routes_2026-10-02/shapey_method_fulltext.txt)。原始 DOI/PMC/arXiv 查询及 XML 500、PDF 403 等失败均保存在 [来源目录](source_cache/vs_seg_original_mask_routes_2026-10-02)。本轮没有联系作者或发送任何消息。
