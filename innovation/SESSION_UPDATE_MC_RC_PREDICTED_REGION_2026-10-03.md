# 本阶段实际进展

阶段状态progress，研究目标active；没有可发表且独立患者确认的新claim，不暂停研究。GPU未使用、用户终端训练未操作、锁定IXI test未读取、根environment/.gitignore未改，没有新代理或委派。

已完成：实际poll77501至exit0，完整15预测ROI全部失败，errors=[]；启动29338并poll至exit0，1069原头、268真实anchors、15新前向、759缺层×6策略及原label/坐标/患者平均复核，errors=[]。[理想区域](MC_RC_OBSERVED_REGION_PROPAGATION_RESULT_2026-10-03.md)和[预测区域报告](MC_RC_FROZEN_PREDICTED_REGION_CPU_RESULT_2026-10-03.md)已补写。

实际执行[分母更正](MC_RC_SOURCE_DENOMINATOR_CORRECTION_RESULT_2026-10-03.md)，exit0：三批24来源当前16合格/8开发人、8拒绝或pending；旧15遗漏002第二时点。原合同、源码、失败保留。更正不增加科学独立患者。

4query返回41条索引，新增取得/核读SynthSeg、轴位T2-MS、FGAS三篇正文，372个相关提取段落，含方法/结果/讨论/表和图注。[排重报告](literature/2026-10-03_predicted_region_fulltext_reading.md)记录实际阅读范围、DOI/hash和文内配置/分母不一致。SafeRestore旧PDF第5页另视觉复看。新PDF0、新JATS3、训练复现0。

16系列native能力对照和独立重放队列80884已实际启动，等待29338成功proof后进入native_diagnostic；[新合同](MC_RC_NATIVE_COMPETENCE_CPU_PLAN_2026-10-03.md)和[后续准备](MC_RC_NEXT_REPRESENTATION_AND_ACTION_PREPARATION_2026-10-03.md)保存，成功目录不可覆盖，不自动retry。本阶段是历史快照，不等于完整16结果或新native proof已完成。

原83910实际poll仍live，17:50UTC历史快照最近完成228、正在229核验；322推断完成不等于全队列完成。原45 CISS主名单、HAT−pipelinePCHIP固定方向及001/202改善反证保持，全部核验后才运行预写筛选敏感性。

[创新判断](INNOVATION_DECISION_AFTER_PREDICTED_REGION_2026-10-03.md)、[公开对话](SESSION_VISIBLE_DIALOGUE_MC_RC_PREDICTED_REGION_2026-10-03.md)、[checkpoint](SESSION_IMPORTED_CHECKPOINT_PREDICTED_REGION_2026-10-03.md)、[继续入口](SESSION_HANDOFF_MC_RC_PREDICTED_NATIVE_QUEUE_ACTIVE_2026-10-03.md)。归档验证以SESSION_ARCHIVE_VERIFICATION_MC_RC_PREDICTED_REGION_2026-10-03.json实际returncode/errors为准。
