# 五篇来源全文复核与任务先例：对当前 MRI 创新候选的约束

这轮重新核读的是已经归档的五篇 XML 全文，不把复核计为五篇新发现。原 XML、正文/表格/摘要/后记抽取及 SHA-256 见 [批次索引](source_cache/vs_seg_source_batch_recheck_2026-10-02/index.json)。作者官方模型、源码和日志是新增实现证据；本轮没有训练新网络。

| 论文 | 核读的关键合同 | 对创新/验证的实际影响 |
| --- | --- | --- |
| Shapey et al., Scientific Data 2021，DOI 10.1038/s41597-021-01064-w | 242名神经鞘瘤患者，ceT1/hrT2人工共识轮廓；T2 3D CISS 1.0–1.5mm。原始JSON轮廓可能不在T2平面，GammaPlan导出的RTSTRUCT先插值。论文明确首尾层差异，使用原JSON+SlicerRT训练；T2两掩膜平均Dice97.6±2.2%，原分割测试Dice90.7±3.6%，划分176/20/46 | 提供可复现的原生薄层病灶任务来源。严禁把简单平面栅格化等同作者GT或把训练例预检等同独立验证。官方模型与名单已实际核验，但原掩膜转换尚未复现 |
| Dorent et al., CrossMoDA 2021 challenge，DOI 10.1016/j.media.2022.102628 | TCIA这242人被分为105个有标签ceT1源训练、105个无标签hrT2目标训练、32个无标签hrT2验证；挑战研究是跨模态域适配 | CrossMoDA与VS-SEG公共来源重合，不能当另一独立来源；公开挑战hrT2训练子集本身并不提供当前需要的任务真值。不能把本项目MRI插值描述为首次将hrT2与病灶分割联系起来 |
| Gazi Brains 2020，DOI 10.7717/peerj-cs.2920 | 50正常+50HGG，多个机构/设备，HGG T2共约1056张，即约21张/人；发布准备包括序列配准 | 是病灶标签候选，但目前未证明原生薄层T2及对应原网格标签。Kaggle文件列表获取失败已归档；不能用发布网格分辨率替代原生采集头 |
| Improving the Generalizability of Deep Learning for T2-Lesion Segmentation of Gliomas in the Post-Treatment Setting，DOI 10.3390/bioengineering11050497 | 429人（208新诊断、221术后无重叠），1×1×1.5mm 3D T2-FLAIR，专家复核标签，单FLAIR任务模型 | 任务方法有临床意义，但FLAIR不同于当前T2/CISS合同；不能把它自动当原生T2独立复现源或现成跨对比度任务验证 |
| Extension of T2 Hyperintense Areas in Patients With a Glioma，DOI 10.1002/nbm.5316 | 28人，7T 3D T2WI 0.75mm及专家监督描绘；临床比较有3mm T2与5mmFLAIR，少数用FLAIR替代T2。数据仅合理请求提供 | 更接近薄层胶质瘤来源，但尚不可直接取得/复现。7T与临床影像对比同时改变对比度、伪影与采集条件，不能作为单独分辨率因果证据；本轮未向作者发信 |

两篇此前已核读的紧邻方法先例仍有效：[Fischer 2023](2026-10-01_fischer_mri_uq_fulltext_result.md)把 MRI 重建样本不确定性传播到 SKM-TEA 分割；[Morshuis 2024](2026-10-01_segmentation_guided_mri_fulltext_result.md)用分割梯度引导同一个扩散重建模型并评估任务边界。它们已排除“首次 MRI 重建→分割不确定性/风险”的宽泛新意。仅从膝变脑、从k-space变层间插值，不能自动证明新方法或新机制。

与已有项目结果连接后，可继续检验的具体问题是：在原生薄层病灶、相同观测锚点、冻结重建模型及强同处理插值基线下，完整体积的图像收益与独立任务终点如何关联，稀疏病灶目标选择又改变了哪些患者被评价。它尚未通过独立结果和完整先例审查。分析基线在既有MSD及多来源上下文实验中的反例，使“深网络独有上下文机制”措辞仍不成立。
