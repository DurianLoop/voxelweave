# 已备好的下一尝试及拒绝条件

1. 先收齐费用优化参考实现session31883的实际终态。只有exit0且无session_id才写direct_oracle_efficiency_2026_10_09/ACTUAL_ALL_PATIENT_STRESS_TERMINAL_TOOL.json（observed_unified_exec_session=31883），执行其audit_all_patient_terminal.py。失败保留原field/源码/receipt，不覆盖attempt01，不poll已经真实终态的43633/41230/26848/68707/56080/38725；旧90446/12652/29823/78123也全部终态。

2. 新542资格与独立audit都通过后执行full_certified_schedule_2026_10_09/forecast_compute_admission.py。完整35904 harness已生成并AST解析、独立终态auditor已备；尚未运行，不叫合格。新wall64800秒在执行前冻结，按新完整队列实际费用作25%+1200秒forecast，超预算不启动。准入通过才运行qualify_full_real_pipeline.py，从第一个field开始，绝不继承14673/6216prefix。实际terminal/independent audit进入下一追加链，运行中的output不冻结。

3. 六臂还是原2inputs×3mode、同parent/optimizer reset/2992schedule/每患者曝光272。新runner、forward/backward/capture/inference、augmentation/cache、terminal audit成本仍需另建独立资格；不能因为数值harness完成就声称六臂训练已有入口。native_reference仅诊断上界，raw_pchip是部署输入。单个样本allaxes参考实现费用11.49→1.63秒不是科研创新或普遍加速claim。

4. fresh_forecast_attempt01真实2e4be2 exit0：GPU24035MiB/0%，满足8192门槛；磁盘储备外64,565,248bytes，原六臂71,156,359bytes需求加新三阶段6MB=77,156,359，短缺12,591,111。保留8GB储备与原allowance。1000冻结离线文本再压缩已真正d82d89 exit0，原42,367,037逻辑bytes/SHA均不变，API节省20,929,057bytes，不能拿它当MRI效果。后续fresh snapshot再判，不删历史/MRI/model，不操作用户训练来腾资源。

5. 普通泛化控制准备先于窄创新测试：global gamma/Bézier、区域Bézier及明确seam平滑、三resolution模式；本批新增GIN-only、SSC-only、GIN+SSC、fixed-step consistency TTA与normalization-affine entropy TTA。SSC12通道应有raw复制/同容量与全特征计算费控制；GIN随机网络分布/normalization/support/padding须冻结及独立验证。AMDU必须取得论文实际adaptive配置/commit或明确称“本项目域遗忘适配”，当前公开periodic代码不是已经复现AMDU。

6. task充分且患者级paired真实动作余量存在后，才进入H1：采集信息在同预算下是否提高具体SR动作的病灶净收益选择。先冻结action集、主端点、全病人分母、费用定义、同信息/容量QC与action-risk差/defer、no-acquisition、metadata-only、static/always/random控制。风险差与gain head均保留，不能把已知等价换名当新算法。动作失败/fallback/defer、label生成、校准、选择和完整FOV两条路径全部计费；共同动作实际重跑，不相加单动作gain。

7. 患者严格内/外fold独立cold init，训练/teacher/localization/QC/gain/UQ/cost/feature transform及所有series不见外折；含全11GT的19998parent仅开发能力诊断，禁止LOPO外折warm start。4已见验证病例不当新独立确认；8未见确认患者12series与lockedIXI保持关闭。先冻结方法和统计family再一次确认，原六医学gate及独立第二任务实现必需。不能用低entropy/variance、consistency、参数truth或重建PSNR代FN/FP实际收益。

无paired余量、强普通增强消除采集增量、同信息risk/QC匹配后失效、费用匹配后失效或确认患者不复现，都保存为负结果并收缩claim。目标active，当前没有可发表且独立确认的claim。
