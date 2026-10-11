# 下一能力实现与公平矩阵：本轮结束时的具体准备

当前可直接复用的事实： [19开发case](experiments/mc_rc_current_development_input_preparation/attempt_01.json)、[19×4输入合同](experiments/mc_rc_development_training_input_cpu/attempt_01.json)、[354真实observed层/76输入独立证明](experiments/mc_rc_development_training_input_cpu/independent_all19_observed_inputs_and_label_axes_attempt_01.json)、[两个失败训练及checkpoint](MC_RC_SPARSE_TASK_TRAINING_CPU_RESULT_2026-10-03.md)。这些是已完成状态，禁止重启当前attempt覆盖结果。现在没有live训练队列。

下一轮先实现强任务能力，而不是直接执行6×5后解释弱网络差距。原4000步/122,609参数不是足够能力的证据；单病例也仅Dice .555。新的架构/预算要单独事前登记为开发，不复写本轮合同；012/013已被看过效果，仍可开发但不能称未见确认。

| 可执行准备项 | 已落实 | 下一实现与冻结要求 |
| --- | --- | --- |
| 已知训练身份/随机初始化 | CPU支持实现、初/终weights SHA、10patient/18UID排除013、19包完整SHA | 正式用11开发/19系列，不加载可能见过确认患者的作者权重；同患者均匀权重再均匀系列 |
| 大小/物理上下文能力 | 单病例完整FOV反例、训练patch低Dice、.35mm像素96patch仅约34mm上下文 | 实现更充分预算与全FOV上下文基线，记录原生spacing；结构选择只用开发/4验证，不能因此声称新方法 |
| 输入接口 | reconstruct/normalize不收label/native，raw linear/PCHIP和两统计已逐案核 | native完整MR参照要独立接口，只用于训练曝光/能力；验证稀疏加载新allowlist和原头/observed独立证明后才开任务效果 |
| 验证患者 | 020/022/025/024固定4人9合格系列，来源grid/身份已核 | 先准备仅这些验证患者的observed包；按预写预算/checkpoint/阈值规则检查任务能力，读过后仍只叫验证 |
| 6×5矩阵 | [原始规格](experiments/task_input_contract_matrix_preparation_2026-10-03.json)，3训练曝光×2统计×5评价输入 | native/raw/mixed共享总update、patient draw/augmentation/初权重/容量；训练schedule与checkpoint规则冻结；原20,000updates仍提案，需资源实测 |
| 直接分割/随机分辨率 | 四篇本轮原文与此前TumorSynth/SynthSeg已清晰限制宽首创 | 同observed信息与预算；额外标签提示分开合同，不用同一体积三方向冒充额外采集 |
| 局部修正 | 旧oracle/反例/强raw PCHIP保存 | 只有合格评价器且适应后还存在可修复残余时实现；对照固定系数、无条件、同容量taskloss、随机策略 |
| 最终确认 | 030/029/019/028/031/026/027/015固定8人，16候选/12合格 | 方法/训练身份/阈值/端点冻结后启用；先按患者聚合再患者bootstrap；8人小样本不能预先保证发表 |

任务指标保留完整FOV的full/anchors/supported missing/tail、物理ASSD/HD95、漏检和signed/absolute volume error，undefined/空GT按本轮实现显式报告。单病例体积反例说明不能用volume符合掩盖空间错位。不要把人工真值ROI/crop、隐藏MR统计或确认集最大Dice阈值引入部署。

现有CPU重现命令（仅用于读懂已完成脚本；不要在现有目录重跑）：`D:\conda\envs\MRI\python.exe -X utf8 -B innovation\experiments\run_mc_rc_sparse_task_training_cpu_pilot.py` 与单病例run脚本。它们强制CPU且目录exist_ok=False，不是正式GPU训练入口。新的GPU/正式矩阵loader、native接口与更强模型尚未实现，本文件不提供虚假的可运行GPU命令。当前GPU仍占用，不启动GPU或操作用户终端训练。

下一CPU可推进事项是更强基线实现/估时、验证observed-only包与诊断split启用记录；进入科学效果前先把新architecture、预算、sampling、loss/augmentation、validation checkpoint和固定阈值写成机器可验合同。本轮已有完整实现的输入/模型/计数/物理surface可复用；不再把归档验收作为科研推进。
