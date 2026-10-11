# 第二个下载尝试：受限环境中的TLS凭据失败

第一个下载实际47bafb / exit1：两个curl均exit35，schannel AcquireCredentialsHandle / SEC_E_NO_CREDENTIALS。没有获得PDF、没有提取或读正文。原源码与失败receipt保留。该失败是TLS运行环境错误，没有自动审批拒绝。

使用新 primary_attempt02 目录，在受限环境外只对原索引明确的两个公开 arxiv.org/pdf 版本发起HTTPS GET。仍验证TLS，不用-k、不发凭据、不改环境或项目文件；仍每份10MB/30s、最多两并发、阶段30MB和RAM/disk8GB储备。尝试2入口另存v2并绑定第一入口及修订、资源guard，不改已执行的第一入口。

此前进度提到任务导向扩散作为可能核查方向，但现有已筛查TADT身份实际为自然图像Task-Aware Dynamic Transformer，不是扩散论文。本阶段只读已经明确选中的TADT和医疗重建后任务/fairness来源；不从缩写推测模型类型，不把另一方向当已读。
