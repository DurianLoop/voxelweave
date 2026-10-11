# COBRAI 与 crossMoDA 新来源：正文和公开元数据核查计划

接续已保存的动作选择检索与 crossMoDA 2026 作者稿。只读公开文献与数据目录，不读取新的 MRI 像素或标签，不申请账户/发信，不使用 GPU，不改同一 session 83910 的冻结合同。

执行前限定：

1. NCBI EFetch 取得 EuropePMC 已认证的 PMC12183417，必须核 DOI `10.1002/nbm.70079` 和正文；提取方法、COBRAI 构造、调参/选择数据与验证合同。只取得摘要不得算全文。
2. EuropePMC 精确查 crossMoDA 作者稿引用的 Kujawa2024题名 `Deep learning for automatic segmentation of vestibular schwannoma: a retrospective study from multi-center routine MRI`。实际结果核题名、年、DOI/PMCID，取得认证的公开正文后再核原生 T2、患者独立性、标签与数据访问。不能预先猜 DOI。
3. 读取已获得的官方链接 `https://crossmoda2022.grand-challenge.org/dataset/`、论文给出的 Zenodo record6504722 metadata API 与 Synapse entity syn51236108 公开 metadata。Zenodo仅列文件名/大小/校验和/访问和描述，不下载包；Synapse只读实体元数据，不请求受控文件或登录。

每请求30秒、最多3线程、每响应8MB、无自动重试；保存原始响应、HTTP状态、时间、最终URL、SHA256及失败。后续请求只基于本次实际返回、限定精确来源。

补读 crossMoDA 作者 PDF 的评价和讨论相关完整页；Fig1 B/D 图注已发现互换，按实际图轴报告。保存提取/渲染工具与哈希、实际读取范围。

创新判断不能使用无关检索或访问失败来声称没有先例。新确认必须完成独立来源/患者去重、原生采集、人工T2标签和空间一致性核查；challenge图像公开本身不放行。
