# 当前研究状态：共同初始化多患者训练在运行

**可发表claim尚未独立确认，科学确认患者0，长期goal active。** 本文件是2026-10-07本次接续的状态快照，不应将此前写下时点的“未运行”描述当作最新状态。用户允许GPU，但实际空闲1394MiB，不达原8GB启动门槛；本次正式实验冻结为CPU4/1、float32，未操作用户终端训练进程。

## 已完成并核验

- 新增3篇原文、3篇重点摘要的阅读已在低LR阶段记录；不是系统综述。HCC任务端点存在改善/退化混合，learning-to-defer原文已直接覆盖预期两路径成本选择，单独收益头不支持方法首创。阅读来源/版本、错下论文和HTTP403失败原样保留。
- 单001低LR两臂各1024全骨干更新，两臂原拟合gate通过，生产/functional/坐标/四域核验通过。native旧空预测未复现；不同初始权重，不能当公平SR效果。完整结果full Dice .967647/.963253。
- 全19开发series资源资格66更新全部丢弃；两臂各1139tile无GT完整FOV计时358.20/395.83s完成，metadata核验通过。低LR阶段172新增文件/678证据文件、36,904,253 bytes新阶段文件已冻结；前503证据SHA全部未改。
- 新的共同随机初始化预检：19,998完整流独立重建一致，每开发患者1818更新；12连续与6+保存恢复+6合成更新得到严格相同权重/AdamW/loss（实际合成24更新，不计MRI训练）。
- 新正式训练第一段两臂各99，**198更新保留**，11开发患者各9步、19series全覆盖；主训练session16984及独立核验96593均实际exit0。独立重建全198真实batch、不可变checkpoint/history、optimizer step99/有限moments、三head functional/阈值和float64 BCE+Dice通过。没有独立重训99步，没有完整FOV评分。

## 正在运行

正式接续session **99542**，入口 `experiments/run_mc_rc_3d_19series_common_init_cpu_wall_v2_2026_10_07.py --attempt 02 --stop-after 19998 --wall-limit 108000`。两臂同新随机初始state、AdamW恒LR.0001、同完整patient/series/GT/增强流、同容量和原最后模型规则，共计划39,996更新。两臂依次进行，只有两个最后模型同时冻结后才打开开发/四已见验证任务效果。

实际第一99 median native2.37075s、PCHIP2.36576s。原资源测试估值19.00h保留；新正式纯更新估值26.31h，剩余约26.18h，I/O/checkpoint/资源波动另计且不保证完工。原因未知。原累计25h资源cap由显式新资源补充改为30h，原协议/config/源码保留；训练步数/LR/所有能力门槛未调整。触发资源或数值失败即停止保留，不能把未完预算称充分能力。

当前进度JSON在入口中每99步提交；`*_history.jsonl`逐步记录，因此JSON进度可以落后于实际不超过一个提交块。rolling resume/history是续训文件；`*_segment99.pt`和`*_segment99_history.jsonl`为不可变历史副本，独立核验绑定后者。不要重启本session、重跑attempt01或覆盖原freeze。

## 后续条件与记录位置

最终19,998/臂结束且真实exit0后，登记完整训练/flow/模型SHA，再准备执行两臂开发19+已见验证9的全56FOV评分和独立functional/坐标重放。后续评价尚无执行入口，已有协议及metadata准备，56预测packbits原始115,491,840 bytes。原四验证gate为患者先均值full Dice .70/missing Dice .65/recall .70/absRVE .50、四患者full/missing均正、9series full TP>0，失败保留；不能只报均值或选最好checkpoint。

能力合格后再推进完整公平矩阵/直接任务/分辨率随机化，以及具体病灶修正余量的defer/双路径成本/风险/预算随机对照。若强适配消除余量或收益无法由observed预测，停止此候选正向claim。八确认030/029/019/028/031/026/027/015及locked IXI test继续关闭。

[本批阅读与低LR归档总览](SESSION_RESULT_LOW_LR_CONTEXT_2026-10-07.md) · [创新判断](INNOVATION_DECISION_AFTER_DEFER_READING_2026-10-07.md) · [正式协议](MC_RC_3D_19SERIES_COMMON_INIT_CPU_PROTOCOL_2026-10-07.md) · [99步结果](MC_RC_3D_19SERIES_COMMON_INIT_SEGMENT99_RESULT_2026-10-07.md) · [30h资源补充](MC_RC_3D_19SERIES_COMMON_INIT_CPU_WALL_ADDENDUM_2026-10-07.md) · [后续评价准备](MC_RC_3D_19SERIES_COMMON_INIT_FINAL_EVALUATION_PREPARATION_2026-10-07.md) · [本次公开对话](SESSION_VISIBLE_DIALOGUE_19SERIES_COMMON_INIT_2026-10-07.md)。

所有新增文件仅在D:\MRI\innovation；可见请求/公开进度/摘要/脚本/结果/失败都留存。未展示的历史逐字对话不伪造；本文不是声称整段历史聊天已自动导出。
