# Full 启动前验证记录

2026-10-10，独立包 `design/ixi_latent_bridge`；助手只进行了合同、显存、smoke、恢复和 validation 检查，没有启动正式训练。

## 核心假设与使用范围

冻结历史 I3Net，将同样四个真实稀疏锚点生成的成熟64通道潜特征，交给 PAST 小波 MA3 的 query-conditioned 有界残差读出。新增的是可学习先验表示，不是额外观测。对照 blind 将进入读出的 I3 latent 乘零，候选 latent 开放它；两臂参数初始化、名义容量、教师预测、采样、损失和预算相同。两个模型都参与实际推理，属于使用 I3Net 预训练权重的混合模型。

## 已完成的验证

- 训练/验证/历史开发测试 ID 分别404/58/115，互斥且逐 ID 与历史 I3Net 划分匹配；本轮不打开 test 图像。
- 将全部缺失层改为极端值和 NaN，cond/anchors/teacher anchors/geometry/query 均不变；target 不作为模型输入。
- 两臂全部初始参数一致，FP32 和 BF16 初始输出逐 tensor 等于冻结 I3Net。
- 完整验证病例的 I3 窗口重叠融合相对旧评价入口最大差异 0.0。
- 激活新修正头后，blind 对教师 latent 扰动保持完全不变，latent 最大响应 0.000730073；修正范围始终不超过±0.05。
- 三个区间合批 FP32 推理相对逐区间推理的最大差异 5.96e-08，属于浮点舍入量级。
- 两臂各2轮真实 smoke 完成；latent 连续两轮与第1轮中断后恢复的模型、EMA、AdamW、best、等待计数、Python/NumPy/Torch/CUDA 随机状态逐项相等。
- 用户 `full.cmd --preflight` 入口通过，未启动 full。
- 故意触发启动异常，确认 stdout/stderr、UTF-8中文、完整 Traceback、真实非零退出码均捕获。probe 中的异常是预期检查，不是训练失败。

## 24GB 显存配置

PAST全部解冻、冻结I3和EMA驻留、AdamW已创建状态，3次真实反传更新，loss/梯度均有限。固定 micro4 × accumulation4 = effective16，10块中7块重计算，桥接训练BF16、教师/loss FP32。

- peak allocated：19.227941 GiB（约 20.65 GB）。
- peak reserved：20.908203 GiB。
- 该短探针每microbatch约 2.119 秒，不将其当成全量训练或部署速度。
- 微批4、仅重计算5块与6块的配置因保留显存分别约24.28/23.72 GiB而拒绝；最终采用7块配置以保留余量。
- 可训练桥接参数1,001,972，其中新读出9,153；另有冻结I3Net 23,205,197参数，总部署参数24,207,169。

## 结果边界与下一步

Smoke只验证运行正确性，不证明超过I3Net。正式配对训练默认 seed3407，两臂各最多80轮；仅 validation 选 EMA best，不调用测试集。每轮只做一次全量 validation 并复制最佳评分，避免重复计算；best若仍为epoch0，也重新评估实际混合模型以计入桥接推理成本。

晋级要求相对 blind ≥+0.05 dB、相对同口径冻结I3Net ≥+0.10 dB，两项配对97.5%CI下界>0，同时通过胜率、困难患者、七项质量和效率守卫。失败即停止此机制；通过后才启动2027/9103适配seeds与最终锁定，随后另外准备外部评价。

```powershell
D:\MRI\design\ixi_latent_bridge\full.cmd
```

同一命令可恢复未完成训练，并核验、跳过已完成的臂。输出保存在本包 `runs`、`results` 与 `logs`；旧代码和checkpoint保留。完整协议见 `PROTOCOL_ZH.md`，指令见 `README_ZH.md`。

## 完整 I3Net validation 基点

58位患者、5,595张缺失层全部完成，PSNR **31.65224732 dB**、SSIM **0.93323661**，均为 per-GT-slice range、窗口clamp后均匀融合、患者等权口径。只读统计保存于 `results\frozen_i3_validation\12fa99beab52`，full自动复用；此数值是validation，不能与主表test分数作胜负比较。完整复核见 `results/baseline_audit.json`。
