# 本轮继续研究结果与入口

目前没有可发表且独立确认的claim。最优先假设仍是强普通泛化基线后，合法采集信息能否改善具体SR动作的病灶净收益决策。

[结合既有项目的证据与具体创新假设](PROJECT_EVIDENCE_AND_NARROW_CLAIM.md)给出四分支开发/已见验证对照、原六医学gate、gain与risk差的等价、必须超越的同信息控制和否证路径。开发full Dice约.86–.88，已见验证约.46–.52；没有用训练病例能力代泛化。严格LOPO不使用含11GT的parent。

[本批三篇主文与作者实现边界](PRIMARY_FINDINGS_AND_NEXT.md)、[阅读来源](READING_PROVENANCE.json)保留DG-TTA、UAF-AIMM、PEIL共341提取块/11表，以及Phys_Seg/AMDU定向源码、4合成诊断。图像像素/补充材料未读，PEIL图像公式未完整解读；摘要/索引/下载不额外计主文阅读。该阅读是继承本轮已完成工作，本次没有再计3篇。

优化独立reference的[完整542字段终态](../direct_oracle_efficiency_2026_10_09/all_patient_stress_attempt01/receipt.json)actual4eaf2e exit0，无session_id；[独立审核](../direct_oracle_efficiency_2026_10_09/all_patient_terminal_audit_attempt01/receipt.json)actual59e97f exit0。11患者19series、38MRI输入、316,813,040 target voxels和20,299额外Fraction probes；全pre/post强度误差0，坐标最大1.1368683772161603e-13。与v1图像逐位相同；fallback727659与v1的727667数量差来自区间实现，不是图像差异。

[GPU六分支结果、两次失败和下一资格](../gpu_graph_cost_smoke_2026_10_09/FINDINGS_AND_NEXT.md)：actual9897da exit0，independent09b462 exit0，固定一开发患者、6forward/6backward、完整12patch；peak reserved2,334,130,176bytes，未更新权重。checkpointed图仅固定synthetic与原图输出/loss/全部gradient逐位核验，不能升级为所有病例的gradient oracle或医学收益。

[完整35904从头协议](../full_certified_schedule_2026_10_09/FULL_REAL_PIPELINE_PROTOCOL.md)及[启动记录](../full_certified_schedule_2026_10_09/ACTUAL_FULL_REAL_PIPELINE_SESSION.json)：新session44317正在运行，未结束。fresh计算forecast为42,538.72秒（11.82h）、预设wall64,800秒。原2992schedule/5984geometries、两输入×三模式全比较，旧失败prefix不继承。静态启动/进度记录可冻结，live attempt输出排除；未称完整资格成功或六臂训练就绪。

[最新整轮资源forecast](fresh_forecast_attempt02/receipt.json)在GPU小诊断后仍有24,035MiB GPU空闲；全部训练family保留8GB储备及原allowance，另GPU1MB，磁盘snapshot短缺14,324,295bytes，未启动新训练。此前1000冻结文本NTFS压缩节省20,929,057bytes且逻辑SHA全保持。这里不请求再次GPU授权，继续做可行准备。

下一入口：先收齐44317实际terminal；只有整体exit0才执行已备audit_full_real_terminal.py，然后做checkpointed AdamW/full-inference/capture成本资格与fresh资源准入。之后继续普通GIN/SSC/TTA强控制及患者fold cold-init，确认真实动作余量后才训练收益/风险决策。8未见确认患者12series及lockedIXI均关闭，原医学gate不降低。

[之前可见对话](VISIBLE_DIALOGUE.md)、[本次公开接续](VISIBLE_CONTINUATION_TURN42.md)、[原继承范围](INHERITED_STATE_AND_BOUNDARIES.md)、实际可用工具返回gzip、失败与后续方案均在本目录；新APPEND_INDEX/PROOF将核旧6997所有逻辑SHA并只追加已冻结证据。科研goal active。
