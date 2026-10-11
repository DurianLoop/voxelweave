# 当前接续：native队列80884和原83910

目标active，未完成，checkpoint不暂停研究。保持GPU/终端训练/locked IXI test边界；不启动代理，不重启成功实验，不调旧失败策略。

已终止成功：77501（完整15预测ROI主失败）和29338（独立15前向重放，errors=[]），均实际poll exit0。已关闭handle可能不存在，以保存proof为准，不盲目重跑。

需要实际poll：

- 80884：mc_rc_native_competence_queue.py，单次native16能力对照→独立16 native+遗漏sparse重放，已进入native_diagnostic。日志experiments/mc_rc_native_competence_queue/native_diagnostic_attempt_01.log，状态mc_rc_native_competence_cpu/attempt_01.json。512×512×144的两新前向可能较慢。全16结束/新proof成功前不称已复核，不自动retry。
- 83910：旧45 CISS+1 TSE队列，17:50UTC实际poll仍live、最近完成verify_VS-SEG-228且状态正在229（历史快照）。合同SHA256 061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5。322推断已完成，仍有逐患者再生成；全部结束后做原主分析与vs_seg_selection_sensitivity.py，不能挑模型或病例救方向。

先实际poll，再读最新状态；不重启/终止两队列。

来源更正：三批当前16合格/8开发人，旧15遗漏002第二时点UID213711595575218613093188251544325434833。旧15输入配置保持，遗漏采用已复核拟合几何；这个时间点仍归已开发患者002，科学确认患者0。

本阶段新增3全文、372相关提取段落，补充文件和新图像未读；[排重报告](literature/2026-10-03_predicted_region_fulltext_reading.md)。尺度域随机化、2D区域、基础模型多平面/连接正则都有先例。窄问题仍为真实稀疏观测可得的病灶保护局部修正；旧线性收益/误差等价及30特征岭失败不变。

完整native结果经独立proof后写报告：native也失败时不能把sparse失败全归于抽层；native成功/sparse失败也不自动给domain shift或profile因果解释。新representation需不同合同、同容量误差/SafeRestore风险/fixed alpha/预算随机强对照及未见患者确认。

归档验证排除live native/原队列文件，只纳入历史snapshot。后续native或原队列完成时另存结果和验证，不能用static通过冒充模型/科学完成。

本阶段结束前再次实际poll：原83910仍live，已完成230核验；native80884仍live，在native_diagnostic，12/16已保存成功，无执行错误。两者继续运行，不暂停研究。77501和29338已exit0不要再重跑。原45人全部核验后才运行敏感性；native全16及独立17重放完成后才写新的完整能力结果。归档24项原检查全通过，补充对话/hand-off之后另记录stage与全局manifest的write/read-only核验。
