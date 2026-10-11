# MC-RC 第2版：非像素患者身份与发布清单审计

执行前证据：经数据 DOI 认证的 TCIA 官方页面明确 Version2 Updated2026/06/04，增加133 series/126 timepoints。现版本表为160人/427 studies/487 MR series，顶层摘要卡仍显示124；必须以实际目录核实，不能默默混用版本。

官方页面称58名与VS-SEG重合的患者ID以 `VS-SEG-` 开头，不重合患者以 `VS-MC-RC-` 开头；8个重合序列提供CSV。为新重建方法确认，必须排除全部重合患者，不能只排除8序列。不同defacing也不能用于图像哈希证明无重合。

本次限定三项公开metadata请求：

- 已有项目使用的 NBIA `getSeries` endpoint，Collection=`Vestibular-Schwannoma-MC-RC`、Modality=`MR`。
- 当前官方页面实际提供的 `series_overlap_between_VS-MC-RC_and_-VS-SEG.csv`。
- 当前官方页面实际提供的 `Vestibular-Schwannoma-MC-RC_v2_20260604.tcia` 纯文本manifest。

每请求30s、8MB响应上限、最多3线程、无重试；下载原始响应并存URL/状态/时间/SHA。清单不触发Data Retriever，不请求getImage、不读取标签数组或MR像素。

CPU联结：UID唯一性、manifest全集与API全集、患者ID规则、study归属、CSV与旧VS-SEG目录UID关联。完整列出排除的患者与候选非重合患者；统计以患者为主，重复扫描不算独立人。失败或缺失单列，不因标签公开就认证同grid。序列description只作待查线索，不能认证T2/薄层/3D序列。

这些结果仅用于来源资格和后续分组准备，不是患者性能验证，也不影响运行中45例队列。后续须逐扫描原生DICOM采集参数、标签路径/空间和模型训练病例身份，再冻结全新方法的未见确认。
