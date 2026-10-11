# 本批阅读、CPU探索及后续准备

本批新增核读FastSurferVINN与BraTS病灶集成两篇不同主文，补完此前HTTP500的公开作者稿缺口。论文来源、原文、核读范围、原表计算及工具记录都在本目录；旧失败不覆盖。本批没有新患者医学效果，尚无可发表且独立确认claim，goal保持active。

- [主文与创新判断](PRIMARY_READING_AND_INNOVATION_DECISIONS.md)：spacing/latent interpolation/原位标签及lesion-aware ensemble均有先例；主候选为充分任务适配后，真实采集可见性对具体病灶修正收益的增量预测价值。
- [CPU原表核验](table_audit_attempt01/receipt.json)：24个HTML table重新抽取一致，68次Fraction/Decimal差，5456组公式检查；28端点中PP改善13/退化11/持平4，ensemble低于最佳单模型18。仅源表均值，不是本项目患者显著性或新医学效果。
- [来源与实际核读范围](READING_PROVENANCE.json)：两主文、明确未读图像/其他附录/源码，128–137截断另读；获取/提取记录的未阅读flag保持原值。
- [后续试验与强对照](NEXT_TRIAL_PREPARATION.md)：先原医学评价、再充分强基线/真实动作余量、同信息cost/defer/QC/静态/随机/去采集控制与全费用，最后冻结患者确认。
- [可见对话](VISIBLE_DIALOGUE_TURN30.md)、[收到的交接原文](RECEIVED_HANDOFF_TURN30.md)：后续公开回复另后附；actual工具返回为本目录gzip JSON和PART02。

最近真实f882d8仍live：第四raw_pchip_spatial1100/2992；前三臂各2992，整个session29823未观察terminal。de0ee2仍live：真实管线5952/35904，full-chain/isolated最大2.86102294921875e-6，shared-post2.384185791015625e-6，support7.438494264988549e-15、coordinate1.1368683772161603e-13。已完成字段仍在门槛内，不能写全通过。训练整个exit0后优先原36+36FOV医学评价。

GPU已授权；5dd886实际free1394/total24455MiB，未达8192MiB新阶段门槛。原CPU任务不迁移，未枚举/控制其他PID。disk资源ad39dd为8,030,920,704bytes、8GB储备外约31MB，仍不足完整LOPO/六臂新训练；不降储备。11开发/19series、已见4验证/9series保持，8未见/12series及lockedIXI关闭，root hashes未变。

上一待执行turn29归档已真实752221 exit0：6376旧logical hashes重新核对、新增36、累计6412；原透明压缩后的旧字节不变。当前新归档接6412，以本目录APPEND_PROOF.json为准，rolling训练/管线文件不冻结。归档成功不能代替医学成功。
