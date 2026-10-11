# 合法采集信息与泛化对照：作者实现和新主文核查

科研问题仍为：强普通增强和合格 3D 病灶 task 后，采集信息是否提高具体 SR 动作的真实 paired 净收益选择。Borges 和 AMDU 主文已读，作者实现尚未核；本阶段先固定公开 GitHub commit/tree，仅下载有关 conditioning/loss/unlearning/schedule 的文本源码，不执行、不安装、不读取权重或病人数组，不把源码阅读计为新主文。

GitHub API 和 Europe PMC 仅发送公开 repo 名和主题关键词。verified TLS、沿已成功的 direct transport；不读取或输出私密环境变量。每 response 上限明确，gzip 保存原文和 SHA；本阶段总逻辑大小 <=2MB，磁盘/RAM 各保留 8GB，另预留本阶段 2MB、数值资格 2MB、原医学 3MB、开发 2.8MB。CPU1/below-normal，单阶段 wall 300 秒，不操作其他 PID。

检索仅筛选，不冒充全文阅读。主文下载后核 DOI/title/PMCID、与既有记录去重；逐块读取正文/实验/局限才计新论文。保持 8 未见确认患者 12 series 和 lockedIXI 关闭，goal active；代码符号的解释以具体 tensor/gradient/optimizer 路径为准，不能以一行公式判作者实现错误。
