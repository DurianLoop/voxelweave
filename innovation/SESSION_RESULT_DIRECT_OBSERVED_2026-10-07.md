# 本轮结果：三篇原文核读与公平直接稀疏基线资格

本轮推进了可执行的公平基线准备，尚未确认新的可发表claim。研究仍应回答：充分适配PCHIP/直接task/SR之后，有没有可由observed信息预测的真实病灶修正收益，以及联合动作在实际总预算下是否优于已知risk/defer/union-greedy。

新增核读Uhrig2017、Eldesokey2019、Jaritz2018三份作者原文的方法与主要结果。成功PDF39页、实际完整选读29页、6页render并view；不是作者实验复现。三篇共同排除了“mask输入”“连续confidence传播”“直接从稀疏观测做分割”作为概念首创。Jaritz还提示普通CNN配方/容量可以改变结果，不能预设mask方法必然更强。

- [两篇稀疏/置信度原文笔记](literature/2026-10-07_direct_observed_primary_reading.md)
- [Jaritz普通CNN反向证据笔记](literature/2026-10-07_sparse_dense_counterpoint_reading.md)
- [完整阅读范围和页级证据](literature/source_cache/direct_observed_primary_2026-10-07/reading_provenance.json)

两通道dense-PCHIP+availability和direct-observed numerator+availability的主资格真实exit0，用87.9708秒逐stream检查11开发患者/19series。所有PCHIP native及physical SHA匹配过去冻结输入；观测值native处逐位保留，缺失处0，两臂同mask。模型均1,401,795参数，比旧一通道多432；mask初权重0，其余与session99542 canonical seed20261007相同。合成one-vs-two及functional前向最大误差均0；两臂全分支梯度及mask梯度有限非零，两步训练的连续/恢复完整tree相同。实际6次合成更新，MRI forward/训练/GT/native/validation/confirmation读取均0。direct_after1合成checkpoint16,890,125bytes，整个主资格输出约17MB，低于25MB限额。

独立核验真实exit0，14.2867秒，19series每channel共12,857个physical坐标，包括固定随机位置和anchor附近/边界。独立float64理想坐标与torchfloat32实现的numerator最大绝对差3.79902e-5、availability8.22648e-6；**通过的是预固定atol3e-5和rtol3e-5结合的allclose，不是单独绝对误差≤3e-5**。native和physical整体SHA匹配。独立functional实现的两次合成direct更新准确重放loss/model/optimizer，after1 tree逐位相同、after2 model SHA相同；checkpoint RNG由保存状态恢复并验证无随机消耗，不宣称独立从seed重构之前所有构造器的全局随机流。

- [主资格结果](experiments/mc_rc_3d_direct_observed_qualification_2026_10_07/attempt01.json)
- [独立资格结果](experiments/mc_rc_3d_direct_observed_independent_2026_10_07/attempt01.json)
- [后续公平训练执行条件与失败路径](MC_RC_3D_MATCHED_OBSERVED_BASELINE_NEXT_RUN_2026-10-07.md)

关键实现合同是direct `s*numerator+t*availability`、dense `s*dense+t*valid_grid`，mask不做灰度变换、padding0。合成native增强再映射/physical增强最大差2.38419e-7。它与当前训练的全patch shift不同，必须另立共同配方并保留原one-channel参考，不能将两通道比较中的所有变化归给mask机制。

现有正式session99542持续live。最近实际tool chunk42bef7报告native第5940，invocation02新增5841，累计12618.774595899973秒；PCHIP99是之前历史快照，不称当前实时进度。未观察terminal exit，不读取中间MRI效果，不迁移设备，不启动重复训练。GPU已授权，最新实际19:16:35.293仅1394MiB，仍未达新GPU既定8GB启动门槛，本轮GPU forward0。

原两臂各19998的完整训练、最终56FOV评价和原四validation gates仍待完成。没有任务资格就不开放8保留确认；软件资格不是病灶收益或可发表结果。原MIRA另有MSValid84人外部确认，“确认0”仅本病灶线；不能把整个项目历史抹成0。

[本轮用户上下文](SESSION_USER_HANDOFF_DIRECT_OBSERVED_2026-10-07.md)、[公开对话记录](SESSION_VISIBLE_DIALOGUE_DIRECT_OBSERVED_2026-10-07.md)、[实际工具台账](SESSION_EXECUTION_LEDGER_DIRECT_OBSERVED_2026-10-07.json)已保存。新增仅innovation，未修改根环境/忽略规则/旧冻结证据，不操作用户进程。后续归档核验将以新manifest和receipt保存，live训练文件明确排除。
