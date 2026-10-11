# 本阶段索引：指标核读、队列程序与冻结后的 CPU 推断

用户要求继续基于既有 MRI 工作批量读论文、找创新点，用空闲 CPU 验证可行部分，把不可验证方向及准备、全部本轮内容放到 D:\MRI\innovation。持续目标仍 active，尚无独立验证的可发表 claim。

## 已完成与执行中的工作

| 工作 | 保存位置与实际状态 |
| --- | --- |
| 恢复已有阶段核验 | 修改新文件前，旧 VS-SEG manifest 核验 10,489 文件/3,124,349,104 字节，12 作者 Git blobs，零错误；全局 write/verify 为 29 注册 PDF、1,145 evidence 文件、1,498 本地链接，零错误 |
| 对话归档纠正 | 上一阶段末尾的“最终答复归档”实际上未发送，已改为“拟交付答复，尚未发送”；没有改写实验结果或旧冻结协议 |
| 三篇指标方法全文取得及重点核读 | [阅读/新意边界](literature/2026-10-02_task_metric_reading_and_innovation_limits.md)；[原始来源索引](literature/source_cache/task_metric_papers_2026-10-02/attempt_01.json)及全文 XML/BioC/text。不是三份独立 MRI 数据来源，也不声明所有附录均已读 |
| 通用数学与推断流程 | experiments/vs_seg_full_volume_runtime.py；与开发例 001 的全部七条件重建逐位相同、support NMSE 零差；一条件分割逐位相同 |
| 物理边界、空值、统计模块 | experiments/vs_seg_full_volume_metrics.py；全对物理点距离、轴置换、体积边缘、不同边界点数、单体素、空预测/空参考核心和 bootstrap 患者循环检查 |
| 修订版技术检查 | experiments/vs_seg_full_volume_development_checks/attempt_02.json：零错误，CUDA false，206.935 秒；448×448×80 八窗合成输入仅由已见 001 零填充构成，64.518 秒，不是科学终点 |
| 可续跑完整队列 | experiments/vs_seg_full_volume_cohort.py；保存每条件预测、统计、哈希和失败；原子写入；磁盘缓存限制；不从动态子集产生正式统计 |
| 新协议及合同 | [执行协议](VS_SEG_FULL_VOLUME_COHORT_PROTOCOL_2026-10-02.md)；[合同](experiments/vs_seg_full_volume_cohort/run_contract.json)，335 文件，SHA256 061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5。45 CISS + 1 TSE，首次推断前 freeze 和 verify-only 成功 |
| 固定队列首例执行 | 使用 --max-patients 1 按固定顺序执行 VS-SEG-202 的七条件。其状态由 experiments/vs_seg_full_volume_cohort/status.json 与 patient 条件文件报告，不把首例当确认 |
| 首例完整结果 | [首例/阶段进度](VS_SEG_FULL_VOLUME_COHORT_PROGRESS_2026-10-02.md)：七条件 574.707 秒。HAT − pipeline PCHIP 支持域 NMSE −0.000317304，原 JSON Dice +0.015698680，未支持单例任务损失方向 |
| 冻结统计分母/联合判定检查 | experiments/vs_seg_full_volume_analysis_dryrun/result.json：合成 45 人三种方向与 44 人不完整场景全部通过；与实际患者输出分目录、不混入科学结果 |
| 独立输出复查程序 | experiments/verify_vs_seg_full_volume_cohort.py；独立 full-grid EDT 与混淆计数，两标签/范围/边界敏感性，可 --regenerate 再生成重建并核对内容哈希。不重复推断分割器 |
| 真正旧规则覆盖 | experiments/vs_seg_full_volume_coverage.py 在冻结后准备；仅源图像/标签，不读取模型分数。区分第一结构标签的目标规则与旧 literal TV 名称限制；阶段报告另行填写实际结果 |
| 实际覆盖及独立复查已完成 | experiments/vs_seg_full_volume_coverage/attempt_01.json、independent_verification.json；全部 45 人，两标签实际覆盖 19/45、18/45，literal TV 再缩至 16/45、15/45。原 JSON 入选/被排除体积中位 5.228/0.701 cm³，仍未验证模型排序 |
| 首例独立输出复查完成 | verification_VS-SEG-202.json：七条件零错误，重建再生成哈希、两标签、边界距离/混淆计数均通过，180.794 秒 |
| 长队列自动续跑/核验准备 | experiments/vs_seg_full_volume_queue.py：调用冻结程序，先完成全固定名单再顺序复查新结果，复用有效的 202 核验。保存阶段退出码、日志和最终完整研究文件；可发表目标仍需人工评审 |
| 后续 GPU 准备 | [候选动作、数据/对照/停止门槛](GPU_FOLLOWUP_TASK_FIDELITY_PREPARATION_2026-10-02.md)。尚无新收益头/任务保真模型训练，未把既有模块组合称为创新 |
| 可见会话及恢复文本 | [当前可见对话](SESSION_VISIBLE_DIALOGUE_VS_SEG_CPU_COHORT_2026-10-02.md)；[用户给出的恢复摘要](SESSION_HANDOFF_VS_SEG_CPU_COHORT_RAW_2026-10-02.md)；此前阶段会话文件继续保留 |

## 成功和失败的解释

development_checks attempt 01 的旧边界实现使用两个方向均值等权平均。复核论文后，明确 pooled ASSD 与方向均值平均 MASD 的区别，修订为同时输出两者并新增不等边界点数样例；旧源文件快照分别保存在 development_checks_v1_snapshot.py、metrics_v1_snapshot.py，旧 attempt 01 保留。该修订发生在独立队列推断前，attempt 02 重新检查全部条件通过后才冻结。

论文检索中，两篇 Nature Methods 的 Europe PMC fullTextXML 返回 HTTP 500，NCBI BioC 成功；Taha 的 JATS XML 直接成功。所有 URL、摘要候选、精确标题匹配、正式 DOI、原始响应 SHA256 与提取 SHA256 都保存。没有联系作者或其他人。

恢复时发生过几项无状态变化的读取/查询错误：PowerShell 默认 Get-Content 编码导致显示乱码，改用 -Encoding UTF8；数次读取了猜测但不存在的 helper 文件名，随后用 rg --files 找到实际 probe/fetch 文件；一次 rg 搜索 JSON 的排除规则范围不准导致巨大响应，改为明确文本文件/短输出；一次 Python -c 把文字转义的换行写成命令文本而产生 SyntaxError，后续用脚本文件处理。未用这些失败解释科学结论，也没有改环境。

新检查仍限定 CPU 单线程、禁止本进程初始化 CUDA，仅降低新进程自己的优先级。全部写入位于 innovation。未修改 .gitignore、environment.yml 或用户当前训练进程，未读取锁定 IXI test，未创建或委派子代理。旧现存代理未用于本阶段工作。

新研究把原四目标方案的失败保留；主比较与双主要终点、45 人分母、seed20261012/5000 次 bootstrap 不因单例结果改变。即使统计方向成立，仍需 raw PCHIP 与两标签/范围/边界敏感性、实现独立复查及范围受限的新意判断。当前科学目标未完成，未标记 complete。

## 长队列接续

queue --check-only 已通过：合同不变，7 已完成条件，VS-SEG-202 的复查可以复用，45 主病例 + 1 次要病例完整名单可续跑。下一条执行命令是 `D:\conda\envs\MRI\python.exe -B innovation\experiments\vs_seg_full_volume_queue.py`。启动后状态保存在 experiments/vs_seg_full_volume_queue/attempt_01.json，子进程 stdout/stderr 保存到该目录 inference/verify 日志；统一工具会返回可继续轮询的 session ID。若队列尚在运行，不启动第二个驱动程序。

预计剩余推断约 7 小时，随后对新输出逐病例核验，已经成功的前向和有效核验不重复。队列完全结束后自动生成 VS_SEG_FULL_VOLUME_COHORT_COMPLETE_RESULT_2026-10-02.md 和 completed_analysis.json；这两个文件目前尚不存在，不用缺失未来文件冒充已完成结果。最终仍需要核读强对照/敏感性并决定创新是否成立。期间应继续基于现有证据审查，而不是因启动长任务就把持续目标标为完成。

本阶段哈希/链接核验记录的是长队列启动前或启动附近的快照；持续产生的条件结果/日志是增量文件，队列结束后需再次 write/verify 清单。原始来源、已验证输出和所有新增对话/报告都实际保存在 innovation，不以哈希快照宣称未来文件已核验。

长队列已经启动，unified exec session 83910，queue_started=true、cpu_only=true。[运行交接](SESSION_HANDOFF_VS_SEG_CPU_QUEUE_ACTIVE_2026-10-02.md)保存具体轮询方式与唯一活动命令。归档启动前阶段 write/verify 为 10,546 文件/3,126,906,806 字节、12 作者 Git blobs；全局为 29 注册 PDF/1,155 evidence/1,531 本地链接，均零错误。新增对话、启动记录和持续结果另作增量保存。
