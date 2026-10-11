# 继续研究：三篇风险正文与无GPU假设审计

用户目标保持active：“一直研究探索验证下去，直到达成一个可发表的claim，注意不要动我现在终端训练的进程”。原请求要批量读论文、结合项目找创新点、可验证者先试、不能验证者准备，并把本轮全部内容保存到D:/MRI/innovation。本阶段有实际进展，但目标尚未达成。

## 本阶段新增证据

1. 全局收尾缺少的read-only核验已补执行：29PDF、1197 evidence、1609本地链接，零错误。这是阶段开始时的快照，新增文件后的最终数另行刷新。
2. [有界风险方法检索](literature/2026-10-02_risk_action_assumptions_search_plan.md)与[精确题名补充](literature/2026-10-02_risk_action_exact_query_addendum.md)保留62条返回记录，不是62篇相关论文/去重作品或全文阅读。首轮SURE/Stein普通词造成无关召回；Crossref首三结果未命中eSURE原论文，不能说它不存在。
3. 实际取得并核读三个新增公开正文：Ramani等TIP2012风险参数选择；Aggarwal/Pramanik/Jacob ICASSP2021 ENSURE；Janjušević等MRM2026 Rep2Rep。准确DOI、PMCID、正文、段落、图表文字和访问失败都在[碰撞矩阵](literature/2026-10-02_risk_action_fulltext_collision_matrix.md)。这三篇是JATS/XML，注册PDF仍29。ENSURE会议版另置完整证明、Rep2Rep补充和逐图视觉核查未完成，不借核读升级证明/复现层级。
4. [预写合成CPU审计](RISK_ACTION_ASSUMPTION_CPU_PLAN_2026-10-02.md)执行，六随机条件各200k、无患者/模型输入。固定phase相同观测可对应+0.75/−2.25缺层MSE收益；相关噪声下对角SURE差可把−.272误判为+.112，完整Σ公式恢复正确期望；独立重复可容许同次空间相关，共享重复噪声会改变收益。它们验证已知假设，不是新理论或真实CISS分数。
5. [独立标量Gaussian quadrature](experiments/risk_action_assumptions_cpu/independent_quadrature_verification.json)以不同方法枚举270配置、40准确比较，最大差2.78e−16，零错误；核准确期望与随机汇总，不声称逐draw回放。全部准确/Monte Carlo结果见[CPU结果](RISK_ACTION_ASSUMPTION_CPU_RESULT_2026-10-02.md)。
6. [后续具体准备](RISK_ACTION_FOLLOWUP_PREPARATION_2026-10-02.md)连接001局部oracle、多开发患者空间、同预算收益头/误差头/固定混合对照、确认来源及SURE/ENSURE/Rep2Rep数据合同。当前不训练收益头，不把数学或单患者结果当可发表claim。

## 为什么这些结果影响创新判断

2012已做无真值MRI参数选择，且直接写零空间完整风险不可一般估计；2021已做随机采样operator的加权风险训练；2026已做独立MRI重复监督、噪声适配与空间相关处理。宽泛的“自监督风险估计+回退”“多phase”“重复观测”不能直接充当首创。两个模型输出分歧也不能被替换成独立扫描。

值得继续但未验证的窄问题仍是：实际固定动作的局部净收益是否有足够空间、能否由同观测特征预测，且优于固定混合与普通误差头，并在未用于设计的患者/来源确认。当前001的raw动作只多.118 dB，pipeline病灶守卫失败；本阶段没有通过新训练或噪声模型“解决”它们。

## 同一个固定队列

session83910多次实际poll仍live，没有终止、重启或启动第二个高负载队列。2026-10-02 11:05:59 UTC观测12/45主患者七条件完成、215进行中；这是进度，不是患者效果量。驱动器仍在inference，之后自动逐患者再生成与完整分析。最新进度需继续看同一handle/log。

最后实际poll在11:17:14 UTC成功live，13/45主患者七条件完成、216的pipeline PCHIP完成；未读任何动态分数。新风险stage核验46静态文件/12锚点/62检索记录/270配置/40比较/189主冻结代码协议，write与read-only零错误。此前task/through-plane与local-action stage各44/57文件，README更新后刷新并read-only零错误；全局刷新与read-only结果保存在工具输出及archive_manifest.json，运行中的整个VS-SEG stage仍不视为最终snapshot。

合同SHA256 061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5；45 CISS+1 TSE、七条件、HAT−pipeline PCHIP主要联合方向不变。没有读取动态子集统计，没有改挑SwinIR。001和202任务Dice改善仍是反证；全量之后按冻结主比较审，再运行筛选次要分析。

GPU、用户终端训练、锁定IXI test、environment.yml和.gitignore未进入新增任务。没有新建/委派代理。只做公开文献请求、CPU合成计算、只读队列状态和innovation内归档。

## 失败和修复记录

- 首四个查询SURE普通词匹配不相关；保留原方案/响应，另写有理由的精确题名补充，不改原查询使其显得命中。
- 两个Europe PMC全文500，原150/151字节响应、状态与哈希保留。三次公开EFetch成功，独立核DOI和JATS正文，不把HTTP200当阅读。
- 一次PowerShell向python -c传递双引号被剥离，产生SyntaxError；只读失败，改用PowerShell ConvertFrom-Json读取，不修改来源。
- 一次rg使用ds007045通配路径触发Windows路径语法错误；随后以明确目录读取。既有33例保存的是CSV/JSON，未宣称其拥有完整保存数组或启动新推断。
- 多个合并读取输出超过预算，分块重读必要方法/实验/讨论。未显示的IRLS递推不计逐式核推。
- 全部合成条件预写后执行一次，独立复查一次；未改种子/加次数/调阈值使结果通过。未发生模型或队列失败。

## 归档与续作

本阶段[静态核验程序](literature/verify_risk_action_stage_archive.py)验证12文字锚点、原请求/提取/代码哈希、合成合同/proof和主冻结代码/协议；阶段manifest在[这里](literature/source_cache/risk_action_stage_archive_2026-10-02.json)。其scientific independent patient count为0，运行日志不纳入该静态snapshot。

README链接更新后刷新原任务/局部动作静态清单与全局文献清单，并read-only复查；完整VS-SEG stage仍运行，不能叫最终全量验证。新静态清单完成仅证明归档一致，不等于科学claim。后续仍继续同一83910、整批再生成、固定主分析、旧筛选次要分析及候选方法的实证门槛。

[本阶段可见对话](SESSION_VISIBLE_DIALOGUE_RISK_ACTION_2026-10-02.md)与[接续入口](SESSION_HANDOFF_RISK_ACTION_QUEUE_ACTIVE_2026-10-02.md)保存进度和所有新证据入口。此前摘要访问、001oracle和四篇task/through-plane全文仍在原文件，没有把历史记录改写为新结果。
