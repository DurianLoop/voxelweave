# 本轮创新方向更新：先证明动作有用，再预测收益

本项目 HAT/SwinIR 插值重建、层间上下文干预和病灶任务已有大量先例与反证。优先考虑的增量问题是：**在同一观测、同一预算和固定动作集合下，何时采用另一重建动作能取得净收益，并保持病灶表现？** 本轮尚无可发表且独立确认的 claim。

[新增正文/作者代码核读](literature/2026-10-02_author_code_ensure_long_and_mslesseg_reading.md)补强了 ensemble UQ、无真值风险训练和共享分割偏差的已有先例；[CPU 排序审计](MASK_DEPENDENT_ACTION_RANKING_CPU_RESULT_2026-10-02.md)表明两动作作差不能自动消除 mask 依赖偏差；[新来源资格](MSLESSEG_SCAN_METADATA_AND_HEADER_RESULT_2026-10-02.md)尚不能供应原生薄层病灶确认数据。

| 分支 | 本轮判断 | 下一项可失败的验证 | 推进条件 |
| --- | --- | --- | --- |
| 当前图像质量与病灶任务联合比较 | 继续固定 45 CISS+1 TSE 的 CPU 队列，尚未统计 | 全部七条件、逐患者输出再生成核验完成后，审 HAT−pipeline PCHIP 两个预写主要方向 | 两主要患者 CI 上限均 <0 才支持原联合方向；任何主失败如实保留 |
| 有真值监督的局部固定动作收益 | 最值得先做开发诊断；已有单病例 oracle 不够 | 多个开发病例、固定 32px tile，raw PCHIP→HAT；pipeline PCHIP 动作及固定 α=.25/.5/.75 对照 | 完整缺失层增益和两种病灶守卫同时成立，且最差病例可接受；否则停止收益头分支 |
| 仅部署特征预测动作收益 | 尚不训练 | 新冻结 train/validation/calibration、同容量绝对误差头、分歧阈值、常数混合、phase/spacing、动作幅度、匹配接受率随机对照 | 仅真实观测/输出可用特征；同预算；患者级完整评价，不仅报告接受 tile |
| 无真值动作风险差 | 降低优先级 | 核实际算子、真实独立观测/重复、Σ 与风险域，及选择后的独立评价 | 当前 fixed-phase magnitude 抽层不满足；合成独立 mask 不等于新观测 |
| MSLesSeg 新确认 | 未放行 | 补剩余七个头、时点差异与原图标签映射 | 即使空间映射通过，也只能按实际原生参数定义用途；1mm MNI 不算薄层参考 |

旧[固定动作准备](RISK_ACTION_FOLLOWUP_PREPARATION_2026-10-02.md)和[GPU 任务准备](GPU_FOLLOWUP_TASK_FIDELITY_PREPARATION_2026-10-02.md)继续适用。这份增量不会改其历史状态。

当前 45 例队列结果一旦用于动作设计，就不能再作为新选择方法的未见确认。不存在经认证的新确认来源前，不声称收益泛化，亦不为消耗空闲时间启动 GPU。用户现有终端训练、锁定 IXI test、根环境和 `.gitignore` 均未改变。

队列全部完成后，驱动器先自动 regenerate，再固定主分析；之后才运行已有 `experiments/vs_seg_selection_sensitivity.py`。次要筛选/标签/模型结果不替代主要失败。001 和 202 的 HAT Dice 改善继续作为反证；不要改挑 SwinIR 以制造原方向成功。
