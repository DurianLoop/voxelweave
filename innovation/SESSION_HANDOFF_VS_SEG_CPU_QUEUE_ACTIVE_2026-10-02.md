# 当前长队列接续：避免重复启动

本阶段固定协议、335 文件合同、首个独立病例 VS-SEG-202 七条件推断与再生成核验、45 人实际源覆盖均已完成。科学目标仍 active，无可发表 claim。

**正在运行一个长队列驱动程序，不能再次启动同一队列。**

- 命令：D:\conda\envs\MRI\python.exe -B innovation\experiments\vs_seg_full_volume_queue.py
- unified exec session ID：83910。
- 轮询：write_stdin(session_id=83910, chars="", yield_time_ms=1000)，或只读取下列 JSON/日志。
- 状态文件：experiments/vs_seg_full_volume_queue/attempt_01.json。
- 推断 stdout/stderr：experiments/vs_seg_full_volume_queue/inference_attempt_01.log。
- 新条件输出：experiments/vs_seg_full_volume_cohort/patients。
- 合同 SHA256：061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5。

驱动程序已输出 queue_started=true/cpu_only=true。当前阶段为剩余固定名单推断。完成后自动逐病例调用 frozen verifier --regenerate，复用已有效核验的 202，再生成完整结果 JSON/Markdown。剩余推断按首例约 7 小时，之后约需另 2 小时多核验；都是估计而非承诺。程序遇资源/技术错误就保留日志并退出，不控制用户训练进程。不要终止它只为了给出阶段总结。

阶段结果见 VS_SEG_FULL_VOLUME_COHORT_PROGRESS_2026-10-02.md；会话、论文、预检、失败及准备见 SESSION_UPDATE_VS_SEG_CPU_COHORT_2026-10-02.md。不要将动态子集解释为正式主要结果，不改主比较/45 人分母，不因首例任务改善改挑另一模型。所有代码更改必须保持已冻结合同；确有必要应先记录偏离和新方案，不能悄悄更新。

启动前归档 write/verify：VS-SEG stage 10,546 文件，3,126,906,806 字节，12 作者 Git blobs，零错误；全局 29 注册 PDF、1,155 evidence 文件、1,531 本地链接，零错误。此后新对话/启动记录/运行日志及结果属于增量；最终刷新两个 manifests。新三篇全文是 XML/BioC，不增加注册 PDF 计数。

等待推断可继续核读既有候选或准备静态分析，不要启动第二个高负载 CPU 队列。完成完整主要结果和全部保存输出验证后，核读强 raw PCHIP 对照、原 JSON/RT、完整/观测范围、1 mm 带排除、空值、病灶 NMSE 两种汇总及筛选覆盖。只有固定联合方向成立仍不能自动宣布可发表；如失败，要保留并继续研究。

本阶段没有其他待轮询命令：开发检查、首例推断、首例再生成核验、45 人覆盖、45 人独立覆盖核验及所有归档校验都已结束。唯一长期 session 是 83910。
