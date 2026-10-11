# 2026-10-08 真实上下文入口与固定作者源码（含训练配置接续）

[实际结果与研究决策](AUTHOR_CODE_AND_ENTRY_DECISIONS.md)记录76个真实开发MRI字段逐体素独立重算，以及FastSurfer v2.3.0四文件2361行固定commit核读。两项已完成工作不代表患者分割收益，本轮新增不同论文正文数0。

[真实入口协议](PROTOCOL.md)、[真实MRI结果](real_context_attempt02/receipt.json)及[作者源码获取](vinn_code_attempt02/receipt.json)保留具体参数、SHA、失败首跑和来源。没有运行作者代码或下载其模型。

[训练链核读结果](AUTHOR_TRAINING_CHAIN_FINDINGS.md)新增七个固定版本文件1609行；全阶段共11个作者文件3970行。三个方向发布配置实际启用内部尺度因子高斯扰动，静态调用链已核；仍不认定为2022论文精确训练版本。新增不同论文正文数仍为0。[普通基线候选政策](ORDINARY_WHOLE_PATCH_POLICY_PREPARATION.md)与 `analyze_whole_patch_eligibility.py` 准备在真实完整资格后分析全patch支持/identity分布；没有启动新训练。

[全2992步资格协议](FULL_SCHEDULE_SUPPORT_PROTOCOL.md)对应新独立CPU session56132，5984候选往返geometry；该任务仍在运行，滚动receipt/journal不得先冻结。[terminal后审计准备](FULL_SCHEDULE_TERMINAL_AUDIT_PROTOCOL.md)规定真实exit0后另进程核全部5984行并用原sample_batch重放全部2992母label。

[来源登记](READING_PROVENANCE.json)、[前轮公开对话](VISIBLE_DIALOGUE_TURN25.md)、[本轮公开对话](VISIBLE_DIALOGUE_TURN26.md)和[交接](NEXT_STAGE_HANDOFF.md)集中保存可用材料。原四臂session29823继续，最新实际a260a1已完成native两臂2992；raw两臂仍待，session仍live。fullschedule最新a54ac5为3600/5984、active1082、FG不足0，不能外推全量。GPU实际1ed717为free1394MiB，低于原新阶段8192MiB储备。8未见确认12series和lockedIXI关闭，目标active；归档只纳入已完成内容与两任务的immutable frozen_config，两个rolling目录都排除。
