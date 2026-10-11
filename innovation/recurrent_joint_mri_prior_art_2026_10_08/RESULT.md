# 本轮结果：MRI 路由与联合重建先例已核读

新增两篇原文的核读，完整文字 35 页（含 1 页参考文献），实际看图 23 个不同原文页，另外 7 个同页表格放大图；39 页提取不等于39页阅读。阅读和两轮窄查询的真实 ID 去重已记录。窄 joint-title 查询首 8 + 后续 11 = 19 unique；额外 recurrent/attention 5，相关两轮合计24 unique。本阶段16个题名摘要中其余14篇未核正文。SERANet 仍未取得，不宣称系统综述或整体查新完毕。

两篇关键发现：MMAR 的动态损坏模态权重使用合成 corruption 辅助监督，且没有真实损坏测试；其单模态训练 split 中 15 个宏平均组合均低于普通多通道 U-Net。XLSTM-HVED 已联合缺 MRI 模态补全与分割特征交互，但各输入组合的 Dice/HD95 改善与退化并存。两篇均不支持把本项目的宽泛 attention/联合任务思路称首创。

CPU 公开表复算已实际完成：MMAR 七张表宏平均列、XLSTM Table 1 的 mmformer/Ours 逐行三病灶 Dice/HD95 和 Table 2 六端点已视觉转录、对照提取文本和 Decimal 算术。XLSTM-HVED Table 1 发现三个打印汇总不一致：Ours WT HD95 17.86 vs 行平均18.0626667，mmformer ET Dice 52.99 vs53.0606667，Ours ET Dice53.83 vs53.404。原 PDF/转录均保留，不推断原因。v1 因首个不一致 exit1，v2 将差异作为来源发现显式记录后 exit0；v2 complete 不表示原论文汇总正确。公开表复算不是本项目MRI收益，也没有重建患者显著性。

当前候选贡献进一步收窄为**固定 observed CISS、同容量充分适配、完整费用下的病灶修正净收益选择**。需要最强静态、同额外监督曝光、风险/defer、双路径成本/DC 和共同投影顺序控制；新准备明确 corruption 标记、pretraining、checkpoint 选择机会与费用也要配平。此处是待验证假设，尚无可发表 MRI claim。

最近归档前真实 training poll 2fd3d5 仍返回 session99542，无 terminal exit；raw_pchip 提交到4950，invocation累计新增24750，不能把后者叫 raw单臂步数。最近GPU87363b：2026-10-08 07:40:51.044，free1394MiB、util92%，未满足新增作业8,000,000,000bytes储备，未启新GPU作业。原训练不重启、不迁移、不修改其他PID。归档后的更新另在post追加。

本轮0新MRI/标签/模型array加载、0新神经/GPU forward、0新医学训练、0收益头拟合、0新action label、0代理委派；未见8患者确认与lockedIXI未打开。原训练自身的更新单独保留，不计作本轮新实验。Python资源守卫已测可用RAM/disk储备；PowerShell CIM查询拒绝访问和误写提取路径等问题保留，不误称资源验证成功。

[原文阅读](PRIMARY_READING.md) · [逐页来源记录](READING_PROVENANCE.json) · [CPU公开表结果](table_audit_attempt02/receipt.json) · [后续实验准备](SUPERVISION_ROUTING_AND_CHECKPOINT_PREPARATION.md) · [全部可见对话及交接入口](VISIBLE_DIALOGUE.md) · [实际工具观测](ACTUAL_OBSERVATIONS.json)。本轮是有实质研究进展，长期goal active。
