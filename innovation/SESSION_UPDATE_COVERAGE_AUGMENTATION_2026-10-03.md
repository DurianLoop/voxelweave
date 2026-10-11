# 阶段记录：论文阅读、覆盖×增强完整核验与下一真实CPU训练

用户继续授权基于MRI既有工作批量读论文、探索可验证创新、准备未能验证项，并将本轮内容保存在D:\MRI\innovation。既有goal工具读到active，目标为“ 一直研究探索验证下去，直到达成一个可发表的claim，注意不要动我现在终端训练的进程 ”。本轮不标complete/blocked。没有创建/委派代理，没有操作GPU、用户终端训练、锁定IXI test、根环境或.gitignore。

## 实际执行与状态

| 工作 | 实际证据 | 状态 |
|---|---|---|
| 接续既有CPU训练 | session25480首先实际poll；不重启，不修改绑定的运行脚本/协议 | 三新臂4000×3=12000训练完成，最后实际exit0 |
| 独立四臂核验 | session53787；16000draw SHA，四臂完整标签/计数/affine距离，首中末4×3=12plane | 实际exit0，errors=[]，global12/local48重放调用 |
| 结果分析与科学图 | 完整四臂表/四域计数、曝光、主差/交互；独立检查JSON反算公式 | reporter实际exit0；PNG已实际view_image检查，SVG一并保留 |
| 追加正文完成 | 交接前103块，本接续读完102块；被截断的图注89/90重新完整输出 | 两篇累计205文字块，正文/公式/表格/图注，不是205独立段或作者复现 |
| 阅读登记 | reading_provenance绑定原始XML/block/text和实质阅读报告SHA | register实际exit0；不改获取时actual_reading_completed=false的历史记录 |
| 19series后续输入/采样预检 | session31096，608rng结束状态、608旧增强SHA、608新无增强reference SHA、1216完整patch映射 | 实际exit0；网络前向0、训练0、GPU0 |
| 新多患者能力训练 | session4831，11患者19series，同初权重、原始输入/标签SHA；每步克隆旧rng核SHA | 实际启动且poll返回仍live；[冻结启动观测](literature/source_cache/no_augmentation_training_launch_observation_2026-10-03.json)时1200/20000，不是训练完成 |

四臂full Dice .865311916/.965504055/.747640783/.914331078；两个无增强条件过原fit gate。原采样去增强+10.0192个百分点。新单case计数/表面/plane重放通过只能说明实现与完整拟合能力，不代表新患者效应、新重建贡献或第二独立任务模型。

本轮已完整结束的新真实训练12000步（复用旧臂新训练0）；新训练4831还有独立动态预算20000，当前部分更新不加入“已完整结束”数。完成因子的生产global12216/local12864，核验global12/local48，已结束分支调用合计25140；不混入旧loss/plane/冻结模型历史调用。19输入预检和阅读无模型调用。新的live训练调用只按动态记录/结束实际值计数，不能预填20000完成。

所有新增Python使用D:\conda\envs\MRI\python.exe -X utf8 -B。CPU单线程、资源守卫只降低自身优先级；新训练第一10实际更新平均.159344秒，输入cache1,934,265,736bytes，观测资源磁盘约17.45GB、内存约107.9GB，均高于预写下限。新训练没有synthetic额外updates，没有读取新验证/确认效果。

## 保存的内容与错误记录

[用户接续原文](SESSION_USER_PROVIDED_SUMMARY_COVERAGE_AUGMENTATION_2026-10-03.md)、[公开对话](SESSION_VISIBLE_DIALOGUE_COVERAGE_AUGMENTATION_2026-10-03.md)、[创新判断](INNOVATION_DECISION_AFTER_COVERAGE_AUGMENTATION_2026-10-03.md)、[后续准备](MC_RC_NO_AUGMENTATION_NEXT_TRIAL_PREPARATION_2026-10-03.md)及全部原始JSON、脚本、checkpoint、预测、图、阅读来源都在innovation。README/queue原字节更新前保存到literature/source_cache/coverage_augmentation_entry_snapshot_2026-10-03。

工具读取中有两次猜测旧入口路径未找到（train_mc_rc_global_local_task_cpu.py、mc_rc_global_local_task_cpu_preflight/attempt_01.json；以及误写旧protocol名称），随后rg定位run_mc_rc_global_local_task_training_cpu.py并读真实源绑定。没有用缺失路径重建假结果，也没有修改旧文件。部分长输出被截断，正文遗漏图注已重新读取；普通旧代码/目录输出的截断不算全文阅读。所有本轮真实训练/独立核验/预检均无新的失败attempt；此前failed70121等仍原样保留。

最终归档验收为[literature/coverage_augmentation_stage_manifest_2026-10-03.json](literature/coverage_augmentation_stage_manifest_2026-10-03.json)及[全局验收](SESSION_ARCHIVE_VERIFICATION_COVERAGE_AUGMENTATION_2026-10-03.json)。动态新训练JSON只通过带时间的不可变观测记录归档，不对变化中的结果SHA作永久绑定或断言完成。

归档首轮全局check实际exit1：29PDF/2172 evidence/2669链接，唯一错误为本记录链接到尚未生成的最终验收JSON。已保存[首轮失败](SESSION_ARCHIVE_VERIFICATION_COVERAGE_AUGMENTATION_2026-10-03_failed_attempt_01.json)，补齐验收记录再重跑stage、全局write/read和stage全文件哈希复查。此项是归档链接错误，不是实验或自动审批拒绝。
