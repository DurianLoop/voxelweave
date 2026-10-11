# 用户提供的上一阶段接续摘要（归档副本）

任务仍 active，尚无独立确认的可发表 claim。所有自身计算已实际结束，当前没有 live 任务。用户允许使用 GPU，但不得操作其终端训练进程；全部新文件只写入 D:\MRI\innovation。

## 本阶段完成

原两臂 CPU 全网络训练各512更新，共1024；已完成独立完整FOV重放和预冻结四增强变体诊断。随后新增6个输出层分支，共6144次CPU参数更新，均已完成独立核验：

| 单个开发系列001上的实验 | native完整FOV Dice | PCHIP完整FOV Dice |
|---|---:|---:|
| 原全网络、两个固定crop | 0.351453 | 0.256330 |
| 固定骨干、两个crop拟合17参数head | 0.590714 | 0.372671 |
| 固定骨干、全部16推断tile拟合17参数head | 0.678448 | 0.475659 |

全部原拟合gate仍失败。局部17参数分支的训练crop Dice为0.943708/0.907710，说明局部特征可利用；不能称架构无法学习，也不能把上述差距当SR损害确认。这些仅涉及001，没有训练完整19series，不是第二独立任务网络。

开发标签往返审计完成11患者/19series：

- 患者内先均值后患者均值，Dice0.96783554；18/19通过诊断gate。
- 微小病例011：native GT163、physical GT76，往返Dice0.87741935、recall0.83435583，保留失败。
- 001标签往返Dice0.98328417，明显高于当前模型0.678448。
- 原生产float32概率比较14/19满足3e-6；最大误差2.3216e-5，但全部19二值预测一致。新增float64坐标核验19/19通过，未改判原float32失败。
- 标签往返是诊断参照，不能称连续预测的数学性能上界。

## 论文与内部统计控制

本次新增核读IN、AdaIN、GroupNorm三份原始PDF，共33页可提取文字；三页公式实际渲染核读。接续CPU阶段原5篇另有738块，合计本研究链8篇；此前nnU-Net两篇另计。Generalised Dice三张SVG数值表仍未视觉核读。

PCHIP参照内部IN模块已实现。数学定义为candidate使用独立参考流的均值/方差；v2以等价残差式实现：

`original_IN(reference) + gamma * (candidate-reference) / sqrt(var(reference)+1e-5)`

两个非同输入primitive与独立float64 NumPy对齐；三项同输入、三个head均0概率/阈值差异。v3只允许认证的observed NPZ，原MR ZIP及NIfTI/GT读取屏蔽。弱checkpoint首tile的输出敏感性不是任务改善或新颖性证明。

保留所有失败：IN v1数值误差超门槛；v2 ZIP守卫误挡NPZ；标签往返v1概率误差超门槛、v2证书路径JSONDecodeError；均另写版本修复。

## 归档与关键入口

[本轮总览](SESSION_RESULT_HEAD_CONTEXT_AND_STATISTICS_2026-10-07.md)包含详细结果、论文、候选与链接。

关键报告：MC_RC_3D_FROZEN_FEATURE_HEAD_FIT_RESULT_2026-10-07.md、MC_RC_3D_ALL_TILE_HEAD_FIT_RESULT_2026-10-07.md、MC_RC_3D_LABEL_ROUNDTRIP_RESULT_2026-10-07.md、MC_RC_3D_REFERENCE_IN_PREFLIGHT_RESULT_2026-10-07.md、INNOVATION_NEXT_AFTER_HEAD_CONTEXT_2026-10-07.md。

新归档实际exit0：89 stage文件、376 evidence文件、88,487,347bytes、34本地链接；旧283证据SHA保持不变。凭证为SESSION_ARCHIVE_VERIFICATION_HEAD_CONTEXT_2026-10-07.json，manifest为literature/head_context_stage_manifest_2026-10-07.json；关闭登记为SESSION_CLOSING_RECEIPT_HEAD_CONTEXT_2026-10-07.json。不要修改已冻结文件。

SESSION_FINAL_REPLY_HEAD_CONTEXT_ACTUAL_2026-10-07.md是预存的科学阶段答复稿，因用户随后要求compaction，尚未实际发出。

## 下一步

1. 优先推进充分骨干训练及context覆盖，不要再把冻结head改善当强任务能力。正式19series schedule仍待真实资源/时间资格后冻结；CPU全网络约3.65秒/更新，单臂20k约20小时，不未经估时启动长训练。
2. GPU最新总量观测：2026-10-07 12:45:16，RTX5090Dv2，free1394MiB、util95%。只有fresh totals达到8,000,000,000bytes才执行 `experiments/run_mc_rc_3d_gpu_fit_pilot_totals_v2_2026_10_07.py --attempt 02`。此入口尚未运行。保持4GB运行余量、2.5GB peak、float32、3600秒；CUDA曾另报约23GB free，不能替代nvidia-smi共享显存读数。BF16未测。
3. 原四验证能力gate通过后，才做同observed直接任务、强PCHIP、分辨率随机化及公平矩阵；有稳定残余后探索具体缺层修正动作的任务收益预测。SafeRestore/MoEDiff等已有先例，宽模块首创已排除。
4. 内部统计模块可用于合格checkpoint的机制对照，新颖性和科学有效性未确认。

持续约束：11开发/19series、4已见验证/9series、8确认/12series角色不变；确认患者030/029/019/028/031/026/027/015关闭，科学确认0。保留旧45CISS反证及addback/QDA/线性失败，不降门槛、不缩分母、不挑checkpoint/阈值。不读locked IXI test，不改根环境或.gitignore，不枚举/操作用户PID，不委派代理。

使用D:\conda\envs\MRI\python.exe -X utf8 -B。不要重启已结束的38045、4611、13677或其他已归档入口；新工作另立协议、源码版本和attempt目录。

本文件记录的是用户交付的历史状态；本接续的新进展见本次总览和实际运行记录，不将历史“没有live任务”误当作新训练没有运行。
