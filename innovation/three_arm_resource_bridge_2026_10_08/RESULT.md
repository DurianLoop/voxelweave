# 三条同观测路径执行桥接结果

此前共同投影输入已在19series资格化，但资源worker仅能执行dense/direct。本轮补上 [three_arm_resource_worker.py](three_arm_resource_worker.py) 和 [医学资源入口](run_three_arm_real_resource.py)，三臂为legacy dense、direct、common projected dense。没有改变旧worker、原输入模块、原训练或已冻结结果；不是新恢复算法，也没有MRI病灶效应。

| 已实际完成 | 证据和范围 |
|---|---|
| 三臂完整PATCH人工输入路径 | [合成receipt](synthetic_attempt01/receipt.json)，实际exit0：12更新、36forward、63.1143321s，3臂内存恢复model/optimizer/RNG exact、各代表8tile FOV两次exact |
| 独立输入/增强/标签重算 | [独立receipt](independent_attempt01/receipt.json)，实际exit0：9batch SHA exact、3臂共有mask/labels、同初值和1,401,795参数；未导入新worker、未独立重跑网络/恢复/FOV |
| 实际退出来源连接 | [SYNTHETIC_OBSERVED_EXITS.json](SYNTHETIC_OBSERVED_EXITS.json)，真实生产chunk84810c=0、独立6c8fd2=0；旧19series输入资格继续绑定，不重新加载 |
| 原资源入口的明确扩展 | [生成record](RESOURCE_ENTRY_GENERATION.json)与[九项源码diff](RESOURCE_ENTRY_DIFF.patch)，生成实际exit0；保留原readiness、CPU/GPU资源/telemetry合同，新权重仍不保存 |
| 医学入口当前先验门槛 | [cpu_attempt01](real_resource_cpu_attempt01/attempt01.json)，实际exit3、complete=true/prerequisite_deferred、errors=[]；神经模块未导入、MRI/GT/更新/CUDA全部0 |

人工源是真正通过现有observed结构和旧/new输入构造：两个固定33×35、native17、stride4的synthetic ObservedMRI，映射到core65×129×133/padded68×132×136。标签为独立人工二值target；不是MRI患者、也不从MRI/GT产生。两条direct实现仅在这两个人工源逐位相同；旧19真实系列相同事实沿用原证据，不把两个人工源扩大成新的医学核验。

每臂一次共享物化draw（crop、foreground/random、flip、scale/shift），同canonical初始化/监督/容量，baseupdate/标签几何/完整FOV原函数均复用。common dense明确选择common_dense并走`s*x+t*valid_grid`，direct走`s*numerator+t*availability`，未知arm实际被拒绝。三个共享字段在view中保持对象别名。没有以人工loss选择新MRIwinner。

新的真实loader实现一次读取同开发observed并构造三路，核legacy/new19输入及原GT SHA；六field数组总5,729,136,000bytes是计划数组量，**尚未实测真实RAM/GPU峰值**。真实资源予定每臂33draw+1恢复更新、共102，权重丢弃；它不是正式任务训练。原能力和资源资格通过后才据实际费用另冻正式三臂预算。

新入口当前8项原final相关条件未满足：两臂terminal/最后冻结/真实退出、完整56FOV/实际退出、两臂全部六能力门槛、独立strict/真实退出。旧先验checker其余已资格条件保持。本轮exit3是正确延期，不是能力通过、不填写final退出receipt。原direct ideal absolute失败保持。

实际0新论文、0医学数组、0MRIforward/训练、0GPUforward、0head fit、0未见患者确认。这里**合成**神经forward为36、合成资源更新12；不能笼统写成所有forward或所有更新0。原训练session99542仍live、不重启/迁移；GPU许可保持，但最近空闲1394MiB未达8GB新作业储备。长期goal active，可发表claim未达成。

接续顺序与真实命令见 [NEXT_STAGE_HANDOFF.md](NEXT_STAGE_HANDOFF.md)，公开对话见 [VISIBLE_DIALOGUE.md](VISIBLE_DIALOGUE.md)，实际退出/资源与根文件校验见 [EXECUTION_LEDGER.json](EXECUTION_LEDGER.json)，累积证据由本目录ARCHIVE_MANIFEST.json及ARCHIVE_PROOF.json追加冻结。
