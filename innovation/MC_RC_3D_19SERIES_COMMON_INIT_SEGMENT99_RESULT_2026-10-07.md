# 共同初始化正式训练前99步结果

两臂共198次正式更新已完成，主训练和独立核验实际exit0；完整39,996预算尚未完成，MRI任务评分0，科学确认0。它们是正式训练前缀，保留AdamW moments和随机流继续；旧66资源更新仍全部丢弃、不混计。

| 输入 | 正式已完成 | cache s | 更新median/max s | 最后训练loss（非任务端点） |
|---|---:|---:|---:|---:|
| native_reference | 99 | 30.11 | 2.37075/2.92323 | 1.563601 |
| raw_pchip | 99 | 76.46 | 2.36576/2.63037 | 1.563536 |

共同全新随机初始state SHA为`364373c851ea5c3ec5eb8b07b2fdeb610f64d68fa5a3302f50897a5197c512cd`。两臂各19series全覆盖、11患者各9步。全部198输入/GT/primitive由独立实现重建一致；不可变99checkpoint/history SHA、优化器每参数step99/有限moments、两臂GT/增强、全部三head module/functional概率和阈值、独立float64 BCE+Dice通过。未重新训练99步，梯度有限性来自主入口；只核最后batch，不是完整FOV神经重放或任务泛化。24次合成optimizer更新仅用于预检断点资格，不计198。

本次正式更新实测比此前33步资源资格慢，原因未知；原19.00h纯更新估值保留，修正全两臂纯更新median估值为26.31h，剩余约26.18h。cache/保存/资源波动额外计；均不是未来保证。原25h完整执行不宣称成功；依据无任务评分的真实资源测量，另立资源补充将累计训练停止上限设30h，科学更新数19,998/臂、LR/初始化/数据/增强/能力gate不变，源码和原config不覆盖。

后续相同state/AdamW/流续至最后权重；两臂同时冻结后再读开发/已见验证任务效果。最终能力评价准备仍无可执行入口，现有metadata计算56完整预测packbits原始字节115,491,840（不含NPZ元数据）以支持后续独立全FOV核验。四已见验证门槛.70/.65/.70/.50、全部9series TP>0/四患者full和missing均正保留；八确认与locked IXI test关闭。

[正式freeze](MC_RC_3D_19SERIES_COMMON_INIT_CPU_PROTOCOL_2026-10-07.md) · [资源补充](MC_RC_3D_19SERIES_COMMON_INIT_CPU_WALL_ADDENDUM_2026-10-07.md) · [独立短段结果](experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07/independent_segment99_attempt01.json) · [资源实测JSON](SESSION_19SERIES_COMMON_INIT_SEGMENT99_COST_RESULT_2026-10-07.json) · [后续全FOV准备](MC_RC_3D_19SERIES_COMMON_INIT_FINAL_EVALUATION_PREPARATION_2026-10-07.md)。
