# 完整队列主分析与固定敏感性的标量重算

本计划写于原 CPU session 83910 仍在逐患者独立再生成时，不读取动态子集效果。原45 CISS名单、HAT−pipeline PCHIP主比较及双终点判据保持冻结。新程序仅在原队列 terminal complete、全部45人七条件独立proof及预测哈希通过后读取效应。

从保存且已有像素/任务指标独立复核的记录重新建立两个主终点和八对固定次要比较的支持NMSE及六种Dice敏感性，共58个统计条目。独立使用math.fsum患者均值、逐draw循环和手写linear分位插值，复核5,000次患者bootstrap、n/seed/draws/负值和零值人数、每个敏感性的included/null名单，以及交并判据。共享原完成门槛、记录/哈希加载及NumPy随机数生成器；不复用原paired_bootstrap或分析函数。这是实现独立复核，不是新科学确认。

同时从全部七条件/两标签重新计算自动完整报告的14行均值、中位数、空预测和边界非有限计数；证据绑定completed_analysis、status、合同和全部记录的hash。不重跑MR/分割推断，不修改运行脚本，不用GPU或locked IXI test。若发现差异，保存首失败及原因，不挑终点或覆盖原结果。次要区间继续描述性、未familywise校正。

执行：`D:\conda\envs\MRI\python.exe -B innovation\experiments\verify_vs_seg_complete_analysis_cpu.py`。队列未完成时只输出门槛信息，不读取患者效果。需要全部真实proof通过后才据此核读主要方向，软件复核不自动宣布发表。
