# 持续研究记录：复现、来源与已知 profile 证伪

持续目标仍是“研究探索验证直到形成可发表 claim”，并且**不操作用户终端中的训练进程**。上一轮的位置通道 CPU 小试属于实质进展但没有完成发表门槛；本续作以当前文件和进程状态重新核查。`Get-CimInstance Win32_Process` 因权限拒绝，后用只读 `Get-Process` 可见 Python 进程；没有终止、暂停、修改训练进程，也没有调用 GPU 推理/训练或读取锁定 IXI test 影像。

本次完成了四类工作：

1. [实测环境与源码审计](PUBLIC_ONLY_RUNTIME_PROVENANCE_2026-10-01.md)：Python 3.12.13、NumPy 2.4.3、pydicom 3.0.2 等九项直接依赖和十份源文件 SHA-256 的只读检查通过，`pip check` 无依赖冲突。根 `environment.yml` 的 `numpy<2` 与缺 pydicom 问题保留；没有改根环境或安装新环境。最初审计常量抄错一个 SwinIR 模型哈希，已纠正，源文件本身未改。当前仍缺在全新安装上复跑的锁定环境/可分发包。
2. [重复采集来源筛查](REPEAT_ACQUISITION_SOURCE_SCREEN_2026-10-01.md)：官方 Zenodo 8234101 的五人、多扫描仪、两次 T2w SPACE/FLAIR 线索被随包限制性 EULA 挡住；TCIA RIDER Neuro MRI 的 19 人约两天内重复影像受 NIH controlled access 管理，而且公开页未证明存在符合本试验的匹配 T2 原生系列。只读官方记录、许可与 DOI 元数据；两个影像包均未下载，也没有访问目标像素。Zenodo 的两个小 PDF 曾仅为阅读条款临时下载，随后删除，本地保留来源 URL 和许可审计结论。
3. [有界 OpenAlex 搜索](literature/2026-10-01_context_overlap_openalex_result.md)：四个冻结查询各 25 条，96 个不同 work ID，原始 JSON/哈希和题摘索引归档。首屏偏旧、无关项多且无 2026 文献，不作为新颖性阳性证据；一篇 2020 diffusion MRI uncertainty 论文与一篇 2021 tomography hallucination 论文仅审阅摘要，进一步限制宽泛声称。
4. [训练内已知 profile 小试](KNOWN_PROFILE_HOLDOUT_PILOT_RESULT_2026-10-01.md)：方案先写、后读 IXI train 的 IXI013/015/017 像素。两真核×两层距×三患者 12 条件和 36 候选无失败。留出观测选对设定核 5/12，真实模糊条件 0/6；相对固定零核无目标 MSE 改善、两条件恶化。[只读复核器](experiments/verify_known_profile_holdout_pilot.py)与前向矩阵数值检查通过。停止这个固定线性逆/留出规则的正向路线，不在同三人上事后调参数。

可发表性没有因此自动通过。当前最强候选仍是 IXI 权重、MSValid 和 ReMIND 的**回顾性发布层上下文审计**，其线性伙伴、MPR、相位内容/几何共变和目标排序阴性结果都必须保留。[发表门槛](CLAIM_PUBLICATION_GATE_2026-09-30.md)中的新意查新、全新环境复现、权重/代码再分发、作者与投稿场合确认尚未闭环。原始采集身份路线需适当授权和完整采集记录；真实厚到薄路线需可信薄层参考。当前没有理由把有限小试写成新方法或临床正确性保证。
