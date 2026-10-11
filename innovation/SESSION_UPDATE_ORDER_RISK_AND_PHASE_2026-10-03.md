# 本阶段完整结果、续读与归档更新

工作范围：批量读论文、结合既有MRI工作寻找创新、CPU可验证项先探索、不能验证项保存设计；新增内容仅D:\MRI\innovation。GPU/用户训练/locked IXI test/根环境/.gitignore未操作，未新建或委派代理。

## 已完成的真实实验

| 工作 | 完整范围 | 实际终止状态 | 结论 |
| --- | --- | --- | --- |
| post resize任务 | 45人/45新前向/18端点 | 20644 exit0 | raw强基线仍高于两缩放路径 |
| observable order risk | 45人/180旧数组重放/6规则/5000随机 | 34708与35552 exit0 | 主最低order_rms候选失败停止 |
| 相位梯度能量 | 45人/855间隔/2565缺层/90旧数组 | 44318与15909 exit0 | 统计相位差成立，不证明Dice机制 |
| 归一化技术预检 | 三人/两基线/六对 | 51036 exit1，90226 exit0 | 首torch标记错误保留，fixed missing身份通过 |
| anchors任务pilot | 三人/四条件/12前向/36端点 | 55424与11226 exit0 | post fixed full负向，停止带宽恢复解释 |
| 事后边界计数 | 18条件/108分区/108配对/36汇总 | 新producer与Fraction verifier exit0 | outside正Dice不等于病灶core恢复 |
| 实际预测域审计 | 18对/54 XOR分区/108两标签比较 | 新CPU过程完成，见结果记录 | full包含anchors，另核实际missing输出 |

pilot正式报告、72条件/标签/域指标CSV、108逐人差CSV、36端点CSV已生成并绑定原proof。没有重启旧完成推断。新增两项事后分析只有保存预测/标量读取，没有新MRI像素解码或神经前向。

## 查新

新增8篇公开正文，415重点证据块，无新PDF：前5篇/221块和追加3篇/194块均有DOI核对、原JATS、展平正文及reading_provenance。追加欧洲PMC四查询503保留；Crossref/NCBI备用成功，宽NCBI词扩展过宽已披露，窄三查询返回26条题名而非26正文。一个标称2026年12月条目未选读。作者实验、图像及supplement未复现核读。

新近邻进一步排除宽“改归一化”“分割条件生成”“独立分割器评价”的首创。FeTA明确指出raw pre-SRR→任务影响待系统检查，同时site-SRR混杂；它的SRR参考体积不是本项目原生薄层确认来源。

## 错误与限制原样保留

- 原归一化预检最后torch未导入断言失败；修正版真实torch已导入、CUDA未初始化，首结果静态false无效。
- 首图均值标注拥挤，首图/代码快照/失败QA保留；第二图已实际视觉核验通过。
- README/EXPERIMENT_QUEUE顶段实际字面问号乱码，本次保存修改前原字节快照，再修正当前入口；下文历史记录不删除。
- Get-CimInstance查询内存被当前权限拒绝；CPU分析使用既有GlobalMemoryStatusEx及磁盘gate，未要求提权或干预其他进程。
- 边界分解计划把逐人行数写成324，实际完整设计108；原文件SHA保留，单独[算术修正](ANCHOR_PILOT_BOUNDARY_DECOMPOSITION_COUNT_CORRECTION_2026-10-03.md)及Fraction核验记录，不静默改原计划。
- 若干长输出截断，相关限制/关键正文块用缩小范围重新读取，不以截断输出声称全部核读。
- 首次静态总归档的前28检查通过，第29检查因DOI大小写误判失败；原XML的IMAG和登记imag对应同一DOI。原失败/脚本快照保留，修正strip/casefold后继续剩余6检查，见[修正说明](ARCHIVE_DOI_CASE_NORMALIZATION_REPAIR_2026-10-03.md)。不重跑科学实验。

科学独立确认仍0，goal active，不把静态归档检查当目标达成。[创新决策](INNOVATION_DECISION_AFTER_POST_TASK_AND_PHASE_2026-10-03.md)及[后续准备](POST_TASK_AND_PHASE_NEXT_VALIDATION_PREPARATION_2026-10-03.md)保存候选、强对照、执行前资格和停止分支。
