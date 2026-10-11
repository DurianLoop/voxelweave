# 动态路由与医疗重建后任务分布：原文接续

本阶段从此前已经筛查的索引中选取两篇尚未正文核读的来源：TADT 2408.08736v2（Task-Aware Dynamic Transformer for Efficient Arbitrary-Scale Image Super-Resolution），以及 2604.10904v1（Evaluating the Impact of Medical Image Reconstruction on Downstream AI Fairness and Performance）。不重复联网索引查询、不把重复摘要算新发现。TADT 的 task 指自然图像任意倍率 SR 场景，不先假定是病灶任务或扩散方法；身份和范围由实际正文核验。

只下载明确索引版本的公开 HTTPS PDF，每份最多10,000,000bytes/30秒、两并发、TLS验证开启。复用既有 GET/helper，写入重定向本目录，不修改旧源码、receipt或环境。便携pypdf/pypdfium2只读使用；保留原PDF并提取各页，按完整实际读出的文字页和视觉页分别记录，下载/提取不等于已读。公开PDF读取/PNG渲染是read-only，不重导出PDF。若超过限额或下载/身份异常，保留失败，先核来源与预算，不盲重试。

目的：确认动态路径选择的可用信息、训练目标/强静态对照、MACs/实际耗时以及 task 概念；确认医疗重建对下游任务的评价设计、下游模型训练分布/适配方式、patient/slice/exposure分母和公平性指标。既有论文结论或其表格CPU复核不能算本项目新MRI效应。

可执行探索优先对完整公开表格做精确CPU算术/端点匹配，或依据原文明确新的必要对照。只在其条件下讨论效应和机制，不猜补未给出的患者统计或算整患者费用。不得复跑旧57,600gain/registry/dummycost，不从弱模型生成收益label或fit selector。

阶段写入≤30,000,000bytes；新阶段RAM/磁盘储备各8,000,000,000bytes，下载/渲染前另外核50MB磁盘余量；CPU/BLAS1、自己的进程below-normal。神经/MRI/GPUforward及医学训练0，不控制其他PID、不动原训练session99542、不委派代理。原两臂final/真实退出→56FOV/六gates/strict→三臂真实资源→另冻正式充分适配→真实动作余量与全费用→最强静态/充分适配/费用控制→8未见确认的顺序保持。开发11/19、已见4/9、确认8/12、lockedIXI保持边界。根.gitignore/environment.yml不改。

当前goal active、claim尚未成立。上一轮三臂真实磁盘资格通过是执行准备进展；本轮须形成改变下一步的原文证据或实际验证。完成后从上一阶段4546完整SHA校验追加归档，并纳入其manifest/proof/post script/post input/post observations五个文件。当前goal全文/可见对话、真实退出及失败一并保留；成功冻结后新公开信息另存post，不覆盖旧证据。
