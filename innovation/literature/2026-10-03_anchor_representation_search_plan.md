# 真实观测层表征与跨层区域：本轮检索合同

在完整 native 能力对照仍运行时，先完成不依赖其结果的查新。检索不是系统综述，下载不等于阅读。截止日期为 2026-10-03；固定四个 Europe PMC 标题/摘要查询，每条最多 12 条 core 记录、5 MB、30 秒，单次请求失败保存，不自动重试。保留原响应、URL、时间、SHA256 和摘要。已有论文不计新增全文。

1. MRI 病灶分割 random forest / decision forest：明确低成本、真实观测监督基线已有方法。
2. MRI sparse annotation / sparse slices 分割：区分稀疏标注和稀疏采集，检查跨层区域传播先例。
3. 医学 mask / label interpolation + distance / shape：检查并集膨胀、距离场和形状插值的已有机制。
4. MRI segmentation physical scale / voxel spacing + forests：检查物理尺度表征及域泛化先例。

后续按直接相关性优先选择最多三篇可公开取得且 DOI/正文身份一致的全文，逐段核读方法、结果、数据单位、失败和限制。记录未读补充和图像。若只取得摘要，明确保持摘要状态。

CPU 试验候选是使用开发患者真实观测 MR 和观测 label 训练的轻量 2D 定位基线，不是创新方法；它用于判断固定作者 checkpoint 失败后，低成本观测表征是否仍值得投入。先完整 native 对照和独立复核，再冻结新的输入、LOPO 患者、容量、预算、区域门槛及停止条件。不依 native 表现筛选有利患者，不使用缺层 label 或 native 像素作模型输入，不把 8 个旧开发患者当独立科学确认。

本轮保持不使用 GPU、不操作用户训练、不读 locked IXI test。文件只写入 innovation。
