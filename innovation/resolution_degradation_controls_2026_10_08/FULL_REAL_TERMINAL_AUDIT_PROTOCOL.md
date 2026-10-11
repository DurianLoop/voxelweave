# 完整真实管线结束后才执行的独立日志审计

前置条件是实际工具观察session74234 exit0且无session_id；保存该完整工具返回为 ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json，增加 observed_unified_exec_session=74234。此文件当前不存在；不得用rolling receipt的complete、耗时或没有输出替代terminal。

audit_full_real_terminal.py另进程只读完成日志、冻结source与原5984几何/17952 metadata决策，不新读MRI、GT或模型，不重做数值fields。检查35,904个唯一(step,patch,kind,mode)键、两种输入三模式完整曝光、11患者每输入每模式544fields、19series正事件覆盖、所有原3e-6/3e-12/zero binary门槛、原valid-domain体素数、padding分辨率阶段零差及逐字段enabled匹配原primitive。确认累计每模式每输入1785 enabled和6,041,370,624 valid曝光体素。

数值fields的独立性来自前一过程的Torch/SciPy与独立強度实现；本进程是日志/来源/分母审计，不冒充重新生成35,904张支持mask或独立患者医学评价。任何字段、来源SHA或分母不符则原样保留失败，不开启训练/未见确认。

CPU1/本进程低优先级、墙钟600秒、全部本目录5MB与磁盘/RAM8,000,000,000bytes储备保持。先核这些fresh资源；输出上限150KB，预留后再执行。新训练和完整训练/推理费用仍另外资格；training_ready继续false。
