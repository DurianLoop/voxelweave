# 本轮续作：四篇任务近邻全文与筛选敏感性准备

用户要求继续基于 MRI 项目批量读论文、寻找创新点；GPU 被占用，能在 CPU 验证的先做，不能验证的保留具体后续方案；本轮可见对话、来源、代码、结果和失败均保存在 D:/MRI/innovation。当前 IDE 的 .gitignore 与 environment.yml 没有为此修改。原终端训练、GPU 和锁定 IXI test 的边界继续保持。

## 本轮取得的实质证据

此前已完成的 50 条有边界检索记录被继续用作入口。此次分块核读三份新 JATS 正文；通过公开 NCBI PMC/EFetch 替代路径另外取得并核读脊髓 ISBI 2025 author manuscript。正文、方法、结果、讨论、完整表格文字与图注都已核读；没有对论文图像作逐幅视觉核验，也没有读胎儿 supplement 或复现其影像。

[四篇合同碰撞矩阵](literature/2026-10-02_task_throughplane_fulltext_collision_matrix.md)集中保存样本、观测/重建、归一化、训练/评价、指标、主要结果与结论边界。机器可复查的 [12 个原文事实锚点](literature/source_cache/task_throughplane_reading_evidence_2026-10-02.json)绑定原 XML 的哈希与段落索引；四篇正式题名来自原 XML。

- Katayama 2026 已有同 raw data 的 CISS / vestibular schwannoma SR-DLR 与阅片者任务评价；只提高面内，没有 through-plane，也未做检测敏感度或人工标签分割误差。不能声称本项目首次 CISS 肿瘤 SR 评价。
- Zhou 2022 已有分割 encoder 感知损失、多邻片数量/距离实验和上下片插值。表 2 的 Dice 改善涉及重新训练的分割网络；表 4 的 through-plane 插值只给图像指标，不能把两实验合并成一个固定分割器增益。
- Sanchez 2025 已有多中心 SR 后生物测量/自动体積偏差及医生感受比较；84 个健康胎儿、252 重建，结论条件于足够质量的重建，未给病理病例或全部失败率的普遍结论。
- Wintergerst ISBI 2025 已有真实各向异性 MRI 的 self-SR、等 spacing linear 和冻结 SCT 分割；预测病灶体积增加及跨模态变异不等于人工真值认证的检测敏感度或已验证的幻觉。

因此“加分割损失”“多邻片”“SR 接任务”“误差与医生感觉不同”“MRI 超分辨率影响病灶体积”都不能单独作为创新。当前窄问题仍需要整队列结果，而不是换更有利的模型或标签。

## 新增可运行准备及已执行检查

[次要分析方案](VS_SEG_SELECTION_SENSITIVITY_PREPARATION_2026-10-02.md)写于见到 001/202 后，明确记录后结果探索身份。保持原双主要比较与固定分母。它将相同完整预测下的全体/旧规则入选/排除组分别评分，再对图像误差单列旧四目标抽样，公开八个模型对、两种标签、两种病灶汇总，共 112 个固定次要终点。患者组成与目标抽样的描述性分解不冒称因果机制或新定理。

新增 [分析脚本](experiments/vs_seg_selection_sensitivity.py)只需保存输出与覆盖结果，不再启动推断、解码影像或访问 GPU。[检查脚本](experiments/verify_vs_seg_selection_sensitivity.py)完成七项模拟检验：[结果](experiments/vs_seg_selection_sensitivity/development_checks.json)零错误。其中一个预设例子能产生方向改变，均一效应例子没有变化；空病灶不填零；无组 bootstrap 保留 undefined；四目标聚合拒绝重复/缺失索引；44/45 队列被拒绝；独立逐抽样 scalar loop/percentile 与实现吻合；完整模拟 schema 生成全部 112 终点。模拟结果只证明软件，不是新患者证据。

实际运行分析脚本得到 [attempt 01](experiments/vs_seg_selection_sensitivity/attempt_01.json)：allowed=false，理由是固定完整队列推断/独立复查未完成；patient_effects_read=false、formal_or_secondary_statistics_computed=false。这不是实验失败，也没有在不断增长的病例子集上找显著性。

可复用命令：

- D:/conda/envs/MRI/python.exe -B innovation/experiments/vs_seg_selection_sensitivity.py
- D:/conda/envs/MRI/python.exe -B innovation/experiments/verify_vs_seg_selection_sensitivity.py
- D:/conda/envs/MRI/python.exe -B innovation/literature/task_throughplane_reading_evidence_2026_10_02.py

## 长队列仍在运行

唯一活跃长队列仍为 unified exec session 83910；本轮已经实际轮询确认，未重启或终止。2026-10-02 09:57:54 UTC 观察到 202–206 共 5/45 个主病例完成全部七条件，207 正在进行。前五例的逐患者再生成复查只有之前认证的 202 已完成；其余按原驱动器在整批推断结束后顺序核验。本轮没有从 203–207 的影像/任务数值生成新结论。

合同 SHA256 仍为 061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5；冻结的 335 文件合同本身及推断/统计/复查代码未修改。主要研究尚未完成，原首例 202 的 HAT Dice 改善仍是对任务降低假设的反证。没有可发表 claim，goal 继续 active。

## 完整失败与修复记录

1. 继承的检索首版 GBK 失败、UTF-8 修订和 attempt 01/02 均保留；未把 50 条返回计数称为 50 篇全文。
2. 继承的全文首版在脊髓 HTTP200 错误文本上发生 XML ParseError，旧脚本和原响应保留。后版校验 XML 根节点，索引正确标未取得脊髓全文。
3. 本轮公开替代请求：PMC HTML 200，EFetch XML 200，Europe PMC HTML 403。原响应/哈希在 [替代索引](literature/source_cache/spinal_lesion_alternates_2026-10-02/attempt_01.json)。没有绕过访问控制。
4. 本轮一次创建验证脚本的 functions.exec JavaScript 包装遇 SyntaxError，工具调用没有执行或写文件；随后改用正确 literal patch 创建并验证。它没有修改科学合同或运行队列。
5. 初次查询猜测两个不存在的脚本名、一个不存在的 verification 子目录，随后用 rg --files/现有源码确认实际路径；仅查询，不导致文件变化。
6. CISS 题名初稿使用了主题性表述，正式元数据核对后在保存笔记中纠正为 XML 的确切题名；不保留错误题名作为来源。

## 归档与后续执行

本阶段静态来源与新增软件用[单独清单](literature/source_cache/task_throughplane_stage_archive_2026-10-02.json)核验，避免把变化中的长队列日志当成最终固定哈希。write 后 verify 通过：44 个阶段文件，4 篇 primary papers、50 条返回记录、12 个事实锚点、七项软件检查、189 个冻结代码/协议文件，零错误。全局 write 检查通过：29 个注册 PDF、1,180 个 evidence 文件、1,571 个本地链接，零错误；对话追加及其链接属于随后增量，收尾再 write/verify。新全文为 XML/HTML，不虚增 PDF 数。此前 VS-SEG 整阶段 manifest 属于旧时点，待长队列完成后再刷新整个动态阶段；当前不能说全部新患者都独立复核通过。

收尾 write/verify 已通过：静态增量仍为 44 文件、12 锚点、七项软件检查和 189 个冻结代码/协议文件；全局为 29 PDF、1,180 evidence 文件、1,575 个 Markdown 本地链接，零错误。09:57:54 UTC 之后的新日志显示 207 的 HAT 也已完成，SwinIR 尚未记录成功，完整主病例计数仍为 5/45。

下一步继续同一 session 83910。全部七条件完成并自动再生成后，先审固定双主要终点及 raw PCHIP、双标签/范围/1 mm 排除、空值、病灶两种汇总，再执行本次次要分析。若主要假设失败，明确保留；次要结果不能提升为预先指定的主要成功。后续动作收益/任务保真训练见 [GPU 准备](GPU_FOLLOWUP_TASK_FIDELITY_PREPARATION_2026-10-02.md)，仍需 oracle/缺口/新确认来源门槛；用户既有训练不因此中断。

[可见对话记录](SESSION_VISIBLE_DIALOGUE_TASK_THROUGHPLANE_2026-10-02.md)保留本轮可见用户原文、助手进度消息与最终阶段报告；继承的历史上下文以已有交接与会话档案为准，不伪造未见的逐字内容。
