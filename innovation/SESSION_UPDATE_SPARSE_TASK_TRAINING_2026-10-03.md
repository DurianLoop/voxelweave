# 本批完成记录：真实输入、四篇阅读与CPU任务训练

用户目标持续：结合MRI既有工作批量阅读、找创新点，GPU占用时先CPU探索；不能验证的留证据和后续准备，全部新增材料在D:\MRI\innovation。既有goal保持active，科学发表claim未达成。本批没有新增代理或外部通讯。

已完成：

- 接续原session1480实际exit0，没有重启生产或复核。19开发系列/354observed层/76输入/19label轴独立证明通过，原始隐藏MR不解码；角色合格分母修正40总/19开发，11/4/8患者角色不变。
- 四篇原始研究正文实际核393个非空文字块：JDL39/Soft spinal160/DRIPS113/LGE81；31检索题名行含重复，不计31全文。DRIPS所读版本明确是预印本；没有新增PDF或单独补充材料视觉复核。
- LGE efetch得到正确DOI/front但无body，原失败保留；公开PMC HTML追加attempt02成功，标准库解析无需安装bs4。joint_scar不是SR，选择/报告已追加纠正。
- 事前写定的CPU主pilot实际session42682 exit0：10开发患者18系列/随机初始化122,609参数/4000updates，013整人留出，最终012/013两输入各全FOV推断；能力失败。
- 主独立复核session76319实际exit0：4×完整域计数、物理cKDTree surface、12个完整plane checkpoint重放与013排除训练通过；50+50训练patch固定模型诊断，未追加优化。
- 新协议之后单病例session38788实际exit0：仅012随机初始化、同4000步/同architecture和初权重；full Dice .555150、missing .557284、体积误差1.3602%，可拟合性门槛失败。独立计数/物理surface和3完整plane重放exit0。
- 开发稀疏全FOV图与loss图已保存并目视QC，显示参考与散在预测；GT选显示切面仅用于事后查看，没有改变输入、推断或指标。
- 两次真实训练8000updates，含合成预检/验证共13,779次forward调用，GPU未初始化、科学确认0；本轮不能继续称“全部新前向0”。任务能力仍是下一科学门槛，完整6×5未执行。

失败和局限均保留：原LGE XML AssertionError；两项科学门槛失败；一个ad-hoc rg查询使用了不存在的旧文件名和PowerShell不展开的*.json路径（exit1），随后按真实目录/rg --files更正，后续无文本命中exit1属于正常查询阴性。若工具输出截断，相关块已定向重读再登记，未将不可见文字直接计阅读。没有依据模型效果换系列/改角色/挑checkpoint/调阈值，没有把输入核验或实现一致性描述为科学确认。

解释限制：18系列不等于18独立患者；小模型/4000updates能力失败不是对直接分割的否证；单病例效果是训练内，不是泛化；两个指标验证共享模型architecture，独立部分是标签轴/计数/物理surface/规则tile枚举，不是全独立重训。8确认保留小样本不能预设足够发表。

当前资料： [阅读报告](literature/2026-10-03_sparse_task_joint_fulltext_reading.md)、[输入/分母结果](MC_RC_DEVELOPMENT_INPUT_CPU_RESULT_2026-10-03.md)、[训练结果](MC_RC_SPARSE_TASK_TRAINING_CPU_RESULT_2026-10-03.md)、[创新判断](INNOVATION_DECISION_AFTER_SPARSE_TASK_TRAINING_2026-10-03.md)、[后续准备](SPARSE_TASK_CAPABILITY_AND_MATRIX_NEXT_PREPARATION_2026-10-03.md)、[公开对话](SESSION_VISIBLE_DIALOGUE_SPARSE_TASK_2026-10-03.md)、[用户接续原文](SESSION_USER_PROVIDED_SUMMARY_SPARSE_TASK_2026-10-03.md)。原始科学日志/权重/预测/SHA按链接保留。

本批结束状态：上述CPU队列均实际结束，无需重启；GPU与用户终端训练未操作，locked IXI test未读取，根.gitignore/environment.yml未写入。接续工作是实现/验证更充分任务能力，按正式合同开放4验证角色，能力过关后才做同容量预算矩阵与可观测修正；8确认保留继续不开效果。
