# 正式19series训练在运行：接续要点

这是本次公开工作状态接续，不是隐藏历史聊天导出。长期goal active、可发表claim尚未独立确认、科学确认患者0。所有新增只在innovation；不动根环境/.gitignore、不控制用户终端训练、不委派代理；用 `D:\conda\envs\MRI\python.exe -X utf8 -B`。

## 第一优先：继续已有进程，不重启

**session99542** 正在运行原共同初始化CPU正式训练的 invocation02。

入口 `experiments/run_mc_rc_3d_19series_common_init_cpu_wall_v2_2026_10_07.py --attempt 02 --stop-after 19998 --wall-limit 108000`。

最后真实poll chunk9b531c（2026-10-07本地16:01附近）仍返回session99542、非terminal：native已到198更新，本次invocation新99，累计正式训练进程墙钟851.5000s；PCHIP此前99。此时总正式更新297，其中只有两臂前99合计198已独立核验。不得从JSON complete推测真实工具退出，不打开中间任务效果。

输出目录 `experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07`，实时 `invocation02.json` 每99步提交，逐步 `native_reference_history.jsonl` / `raw_pchip_history.jsonl` 更新更快。rolling `*_resume.pt` 与history可被入口继续写；`*_segment99.pt` / `*_segment99_history.jsonl` 是已冻结不可变副本。代码/config/流/共同初始权重和原protocol已SHA绑定，不修改。

## 已完成

- 原FOV计时41977实际exit0，metadata核验chunka6601a实际exit0：native19series1139tile358.198666s，PCHIP395.832575s，总807.466788s，GT0/评分0/新更新0。低LR阶段总览、成本、真实退出ledger写完；归档chunk847493实际exit0，新172文件/累计678证据/36,904,253bytes，原503证据全未变；closing receipt保存。
- 新共同初始化preflight chunk4c2d75实际exit0：完整19,998步独立流一致，每患者1818；共同随机初始state SHA364373c851ea5c3ec5eb8b07b2fdeb610f64d68fa5a3302f50897a5197c512cd；24合成optimizer更新验证12连续 vs6+保存恢复+6的参数/AdamW/loss严格相同，不计MRI训练。
- invocation01 session16984实际exit0、577.184514s、两臂各99正式更新保留。独立核验session96593/chunk92a614实际exit0、123.067104s；全198真实input/GT/primitive、两臂流/GT、不可变checkpoint/historySHA、AdamW全99有限moments、三head functional/threshold和float64 BCE+Dice通过。仅最后batch检查，未独立重训99、未跑FOV评分。
- 新正式99更新median native2.370748s、PCHIP2.365756s；旧33资源资格1.71s的两臂19h估算偏乐观，原因未知。修正完整纯更新26.3113h、剩余（99时点）26.1810h，均不保证；原90,000s/25h资源合同保留，新显式wall-only补充设108,000s/30h累计进程上限。科学19,998/臂、总39,996、LR=.0001/AdamW、同容量/初始化/数据/GT/增强/最后checkpoint/原能力gates未改。
- 不可变99阶段+准备归档chunk673a2f实际exit0：新32文件/累计713证据/56,788,357bytes；前678证据全部SHA重核。归档显式保留own_live_runs=[99542]、full_training_exit=null、final_execution_closed=false，不能把archive.complete当整个训练完成。`SESSION_CHECKPOINT_RECEIPT_19SERIES_COMMON_INIT_2026-10-07.json`绑定manifest/receiptSHA与实际exit0。
- 最新GPU实际query2026/10/07 15:56:03.783：1394MiB free/util95%，无新GPU更新。原8GB启动/4GB运行余量/2.5GB峰值资格保持；本正式CPU实验不可中途换设备/精度。

## 下一科学步骤

1. 先poll99542；无需重启训练或重复99独立核验。guard每步检查时间/RAM/磁盘，250MB全阶段保存、8GB RAM/磁盘余量、CPU4/1、below-normal、float32。若失败保留并显式审计，不自动改预算或跳样本。
2. 两臂最终19,998权重同时冻结、全39,996完成且工具实际exit0后，写新完整退出receipt。确认流/AdamW/GT/最终SHA完整；不能改原freeze或挑中间模型。
3. **最终全56FOV评价尚无可执行入口。** 已有 `MC_RC_3D_19SERIES_COMMON_INIT_FINAL_EVALUATION_PREPARATION_2026-10-07.md` 及metadata准备JSON：两臂开发19+已见验证9，共56预测packbits原始115,491,840bytes，不含NPZ元数据。可在长训练期间继续写有界评价和独立functional/坐标重放入口；不运行它直到上述终态满足。
4. 原四验证患者020/022/024/025、9series gates完整保留：patient-first fullDice>=.70/missingDice>=.65/fullrecall>=.70/fullabsRVE<=.50，四患者full/missing均正、9series fullTP>0；两臂都报告。full/anchors/missing/tail全分母，空undefined保留。011标签roundtrip失败不删。
5. 验证能力合格之后才公平6×5、同observed直接任务、分辨率随机化和真实病灶修正残余。方法候选仍受Madras/Mozannar defer、SafeRestore/MoEDiff约束；单收益头不是首创新法。原3原文/3摘要阅读已归档，不重复计数。原低LR两臂单001拟合已通过，但不同初始权重不是SR效益比较。
6. 8确认030/029/019/028/031/026/027/015及locked IXI test保持关闭；当前科学确认0。最终方法/端点/预算/阈值冻结且强对照合格后才确认及第二独立训练任务网。

## 可见对话与最新入口

已冻结 `SESSION_VISIBLE_DIALOGUE_LOW_LR_CONTINUATION_2026-10-07.md`（1–12及摘要缺失说明）、`SESSION_VISIBLE_DIALOGUE_19SERIES_COMMON_INIT_2026-10-07.md`（13–17及最终公开答复文本）。不要修改这些SHA绑定文件。本文新增的公开更新18为：“训练已继续到 native 第 198 步，仍在运行。前 99 步的不可变证据和后续准备已单独归档，累计 713 个证据文件核验通过；续训日志保留为实时文件，后续可继续接续。完整模型评价方案和预测存储预算也已保存。”

最新总入口 `CURRENT_RESEARCH_STATUS_19SERIES_COMMON_INIT_2026-10-07.md` 是冻结快照，继续工作需要新状态文件，不改已归档内容。`SESSION_EXECUTION_PROGRESS_19SERIES_COMMON_INIT_2026-10-07.json` 为15:58左右快照（native139/PCHIP99），亦已冻结，不能当作后续实时步数。真实进度读invocation02与两个rolling history。
