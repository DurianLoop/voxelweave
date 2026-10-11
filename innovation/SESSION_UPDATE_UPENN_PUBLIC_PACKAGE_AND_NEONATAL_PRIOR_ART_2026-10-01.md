# 本轮续作：UPENN 官方文件级目录与 T2 分割先例

目标仍是形成可审稿、可发表的 MRI claim。本轮没有碰用户正在训练的终端进程、GPU、锁定 IXI test 图像或已有 `.gitignore` 修改。已有三来源发布层固定模型对结果以及上轮固定分母控制保持不变；这次产生的新证据集中在临床任务文件资格和更直接的 T2 先例。

1. 从官方 TCIA 页面公开 Aspera 包链接出发，读取 Faspex 网页客户端的公开配置和文件浏览流程，通过其正常 `authorize_public_link` 授权会话列目录。此前未授权 401 只代表缺会话，不再是文件清单获取障碍。[文件级结果](UPENN_NIFTI_OFFICIAL_PACKAGE_INVENTORY_RESULT_2026-10-01.md)和原始树响应的路径/响应哈希均已归档。671 个结构像目录与官方 CSV 的 671 个扫描 ID 完全一致；CSV 标记 232 个修订分割可用，但包中 `images_segm` 仅有 147 个候选链接，另 85 个未列出。薄层 T2 元数据候选由 86 缩为 60。`automated_segm` 的 611 条是自动近似标签，不能补充缺失的专家修订标签。
2. 事前选定的 `UPENN-GBM-00002_11` 有同 ID 的 T2 和分割符号链接，官方文件级传输规格 HTTP 201 成功；令牌和完整规格未存储。包配置 `http_gateway_url=null`，本机无 Aspera Connect/`ascp`，按[预写停止规则](UPENN_NIFTI_OFFICIAL_INVENTORY_AND_PILOT_PLAN_2026-10-01.md)没有请求影像文件、读 NIfTI 头或启动 69 GB 传输。因此同空间配准和病灶实验仍未验证。第一次目录超时后原路径重试成功；早期规格脚本把成功的 HTTP 201 误判为失败，随后 v2/v3 修正并保留审计记录。
3. [Verschuur 2022 PMC 全文](literature/2026-10-01_verschuur_neonatal_t2_fulltext_result.md)确认 T2 运动损坏切片的保形样条插值及八结构分割评价先例，25 个运动病例视觉改善、8 个相邻损坏病例失败，真实坏片无无运动真值。它不做本项目固定双估计器误差对照，却直接挡住“首次通过 T2 插值改善分割”的宽主张；未来同空间肿瘤实验必须比较等信息样条和报告坏邻片/边界失败。

[三来源内稿](PUBLIC_ONLY_MIRA_MANUSCRIPT_DRAFT_2026-10-01.md)、[创新决策](INNOVATION_DECISION_MEMO_2026-10-01.md)、[发表门槛](CLAIM_PUBLICATION_GATE_2026-09-30.md)已同步。当前最强说法仍是发布层同目标、固定参考、切换伙伴上下文时成对误差可见性发生变化；不能宣称原始采集因果、新重建方法、临床任务获益或可部署告警。Kuestner 2024 的方法级排重、同空间 NIfTI 标签实验、权重分发权限和干净环境复现仍未关门。

最终归档以[清单](literature/archive_manifest.json)和 `python innovation/verify_archive.py` 的只读复核为准。

最终独立复核通过：671/671 结构像扫描 ID 与 CSV 精确相同，232 个 CSV 修订标记中包内 147 个候选链接、85 个无该目录项，另有 611 个自动近似标签；Verschuur PMC 正文与资格清单输入哈希一致。归档校验为 29 份 PDF、218 个证据文件、1,031 个本地链接、零错误。当前目标仍在进行中，未宣称形成可发表主张。
