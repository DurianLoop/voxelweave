# MRI 创新研究接续：SynthSR、临床端点与强度修复

本批新增完整核读2篇原始主文、全部5张内置表，并完成原XML的独立表算术核验。重要发现：SynthSR主动用正常组织填补病灶，便于配准/解剖分析；高体积相关或诊断AUC不能证明VS病灶保持。潜在创新仍是合法采集可见性对具体动作真实病灶损害变化与全费用的增量价值，尚无独立确认发表claim。

阅读入口：[原文结论与创新判断](PRIMARY_READING_AND_PROJECT_DECISIONS.md)、[可执行依赖与后续实验](NEXT_TRIAL_PREPARATION.md)、[逐段来源登记](READING_PROVENANCE.json)、[原表CPU核验](table_audit_attempt01/receipt.json)。

强度修复全部271场资格实际2ce605 exit0，独立审计b422fd exit0，[审计结果](../intensity_precision_failure_diagnosis_2026_10_09/repaired_terminal_audit_attempt01/receipt.json)。原失败的三种模式回归误差0，完整chain最大1.9073486328125e-6；门槛3e-6不改，旧独立reference与正在运行的训练源不改。这是数值资格，不是病灶效果。

完整新重放session90446从头执行35904，[冻结协议](../full_real_intensity_v2_2026_10_09/FULL_REAL_PIPELINE_PROTOCOL.md)、[真实启动句柄](../full_real_intensity_v2_2026_10_09/ACTUAL_FULL_REAL_PIPELINE_SESSION.json)。原74234失败及6216成功前缀保留，不能接作新版通过。一次启动wrapper因重复interop setter实际ac715d exit1，发生于main/MRI读取之前；用同冻结脚本直接启动3d3b7d，无source改动。

原四臂session29823仍live，前三臂各2992，最新本批归档前观察b584c7最后raw_pchip_spatial2090/2992。全程结束后才四last/journal审计→原36production+36functional完整FOV评价；不按中间loss挑分支。新重放306bd9观察2568/35904，仍live，已完成项最大full-chain1.9073486328125e-6；滚动进度不是完整通过。

GPU授权保持；实际总24455MiB、空闲1394MiB，低于既定8192MiB启动余量。磁盘/RAM8GB储备不降，原医学评价3MB保留；储备外约29MB且原训练仍须写最后state，不能假定六臂或11折训练资源合格。8未见确认/12series和lockedIXI继续关闭。

[本轮公开对话](VISIBLE_DIALOGUE_TURN32.md)、[终态与下一步](STATUS_AND_HANDOFF.md)。实际工具返回以ACTUAL_TOOL_OBSERVATIONS_TURN31.json.gz、TURN32_PART01/02.json.gz无损保存，保留原工具截断、空输出、session_id和exit字段；不含模型私有推理。

本批增量归档接原6441不可变来源，真实新数量见APPEND_PROOF.json；历史index不覆盖，当前两个live目录除frozen_config外不冻结。数量是证据文件数，不是论文数。科研goal仍active。
