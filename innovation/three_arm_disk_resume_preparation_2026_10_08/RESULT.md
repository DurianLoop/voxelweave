# 本轮结果：三臂磁盘恢复执行准备

已补上三臂资源流程此前缺少的磁盘持久提交、跨进程恢复和 journal/step/config/source 绑定。独立核验通过：三臂连续训练与恢复训练的完整权重、AdamW 状态、CPU RNG、配置和终点 step 精确一致；各步 loss、输入/标签 SHA、梯度和 draw 也一致。这里只验证执行可靠性，尚未产生 MRI 病灶收益或可发表 claim。

| 实际完成 | 证据与范围 |
|---|---|
| 两个独立训练进程 | [attempt02 receipt](attempt02/receipt.json)，真实 tool exit 0 / a953c9，连续 9 更新、恢复 6 更新，共 15 人工 forward；共享 PATCH64×128×128 / batch2 / 1,401,795 参数 |
| 三臂完整磁盘恢复精确一致 | [独立 receipt](independent_attempt02/receipt.json)，真实 exit 0 / b27b3a；加载本次 9 个人工 checkpoint，完整树逐项比较，独立神经 forward 0 |
| 六类实际磁盘错误提前拒绝 | [fault probes](attempt02/fault_fixtures)，缺失/多余/截断日志、checkpoint SHA 错、元数据 step 错、arm 错；六 child 均 exit 3，torch/numpy 未导入；正确 binding 的 child exit 0 |
| 首次执行错误完整保留 | [修订说明](ATTEMPT02_AMENDMENT.md)；首尝试3321ac=1，自身 checkpoint hash 被误拦，实际已经 1 更新/forward；原源码、receipt、checkpoint 保留。修正另存 v2，不覆盖旧证据 |
| 实际退出与全部计数 | [QUALIFICATION_OBSERVED_EXITS.json](QUALIFICATION_OBSERVED_EXITS.json)：成功 15 + 首次失败 1 = 本阶段 16 人工更新/forward；训练加载 3 + 独立加载 9 = 12 个人工 checkpoint 数组读取；字节 hash 不算数组读取 |
| 当前医学执行准备入口 | [formal_entry_gpu_attempt01 receipt](formal_entry_gpu_attempt01/receipt.json)，实际 b86ae8=3，complete=true / original_capability_prerequisite_deferred，errors=[]；0 神经导入 / MRI读取 / CUDA / 正式更新 |

执行器复用已有 `arm_view`、draw/update/snapshot；同初始化、同人工监督、同 draw，三个 representation 的实际输入 SHA 不同。common dense 明确用 common_dense/dense 语义；direct 使用 numerator/direct 语义。没有重复此前内存恢复/FOV资格，没有人工 loss 选 MRI winner。

两次训练资格合计 wall 约 62.565 秒，独立核验另用约 2.273 秒，阶段输出约 169.5 MB；CPU4/interop1/BLAS1、自己的进程 below-normal；RAM/磁盘各 8,000,000,000 bytes 储备均按实际字节检查。新的神经 forward 全用 CPU，GPU forward 0。原终端 session99542 实际仍 live，最新 f8a1d6 为 raw_pchip2871、invocation02 new22671、累计52229.77522890002s；未据 metadata 推断 final exit。GPU 2026-10-08 06:19:13.716 空闲1394MiB，仍不足新的8GB启动储备。

正式医学 stream、充分适配更新预算与长程资源合同仍未冻结。现有 `training_engine.py` 只在人工资格下验证，checkpoint provenance 明确 synthetic_only；`check_formal_entry.py` 是准备/延期入口，不能当成已经完整资格化的正式长训练 runner。真实资源资格及新正式预算到位后必须另存正式版本并资格化，不使用人工 checkpoint 当医学初值。

本轮新增论文阅读 0，沿用上一轮联合适配与最强静态控制的查新结论。当前候选仍是固定 CISS 观测下，在充分任务适配与完整费用控制之后，合法动作选择是否保留真实病灶优势；尚未建立。此前弱模型标签、native额外信息、虚构费用和人工资格均不用于支持收益。后续具体顺序见 [NEXT_STAGE_HANDOFF.md](NEXT_STAGE_HANDOFF.md)，对话见 [VISIBLE_DIALOGUE.md](VISIBLE_DIALOGUE.md)，实际状态见 [ACTUAL_OBSERVATIONS.json](ACTUAL_OBSERVATIONS.json)。

累计归档会校验此前4397个文件并绑定前轮post四文件。成功状态以本目录 ARCHIVE_PROOF.json 及 POST_ARCHIVE_OBSERVATIONS.json 的真实退出为准。根 .gitignore / environment.yml 未改变；全部新增仅本目录，goal仍 active。
