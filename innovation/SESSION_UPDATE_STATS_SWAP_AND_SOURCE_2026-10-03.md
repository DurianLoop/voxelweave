# 本批成果与科学状态

用户要求在GPU忙时批量读论文、基于既有工作找创新点、能CPU验证的先验证，未验证方向留准备，并把本轮内容存入innovation。当前研究goal保持active，没有达到可发表且独立确认的新方法claim。

新增[3篇原始PDF核读](literature/2026-10-03_masked_normalization_primary_reading.md)：Region Normalization、Partial Convolution、Normalization-Equivariant Networks；28实际已读PDF页、3页视觉重检，范围与未读supplement登记。下载缺pypdf和链接解析两失败保留。排除宽“排未知统计”“掩膜卷积”“argmax强度不变”的首创新意；不复现作者实验。

[固定三人统计互换](TASK_STATS_SWAP_CPU_PILOT_RESULT_2026-10-03.md)全部6交叉CPU前向已继承完成，原79154最终复核实际exit0。输入6+6、72计数、30端点通过。JSON full主Δ+.001410324，逐人负/正混合；三人原post−raw为正而全45为负。全部CSV和采集域/反例保留。

[全45输入统计审计](FULL45_NORMALIZATION_DRIFT_CPU_RESULT_2026-10-03.md)本续作新执行，90旧数组SHA核对，0新前向；独立45/270矩/90RMS/90Fraction差/12手工关联/45CSV通过。std平均−2.4882%、相同anchors归一化scale平均+2.5525%。Pearson约−.30但Spearman近0，不部署排序，不做因果归因或小pilot外推。

[MC-RC角色元数据准备](MC_RC_SOURCE_ROLE_METADATA_PREPARATION_PLAN_2026-10-03.md)澄清71/159，8整患者开发、余63/138仅候选，58共享VS-SEG患者全部排除。[新来源实际预检](MC_RC_011_013_SOURCE_PREFLIGHT_RESULT_2026-10-03.md)在事前固定011/012/013全部5系列后完成230头及5label，3通过、2厚层时点阴性，MR像素未解码、任务效果未计算。首次独立复核额外index容差错误及脚本保留，按原physical门槛修正后attempt02 exit0，不更改输入或producer。

[创新判断](INNOVATION_DECISION_AFTER_STATS_SWAP_2026-10-03.md)与[下一步准备](STATS_SWAP_AND_SOURCE_NEXT_PREPARATION_2026-10-03.md)要求相同输入曝光预算、任务适应、完整新来源/身份/患者角色及独立模型确认。原45和MC-RC8只作开发，新3人只通过来源preflight，科学确认仍0。旧HAT负claim/残差/order_rms/带宽/QDA/native失败均不覆盖。

全部新增在innovation；没有GPU调用、训练启动/停止、locked IXI test读取、根环境或.gitignore修改，也没有新建/委派代理。两个新producer session5765与57881及所有复核已实际exit，不重启历史队列。当前没有本批live后台任务。

可见用户请求/所有当前公开消息/实质工具及错误见[可见对话](SESSION_VISIBLE_DIALOGUE_STATS_SWAP_AND_SOURCE_2026-10-03.md)，前模型用户交接原文见[摘要归档](SESSION_USER_PROVIDED_SUMMARY_STATS_SWAP_2026-10-03.md)。不伪造未提供的早期逐字对话。验收只确认文件/实现证据，不确认可发表claim；见[静态验收](SESSION_ARCHIVE_VERIFICATION_STATS_SWAP_AND_SOURCE_2026-10-03.json)。
