# IXI-STC：复用六锚点稀疏上下文路线

此前没有候选已经证明能在 IXI 超过 I3Net。优先复用 STC，是因为 IXI 比 fastMRI 短 volume 更适合检验真实长上下文：train/val 约87.5%区间具备六个不同锚点。fastMRI 原 STC 的 +0.00109 dB 负结果保留；不能由本次选择反推此前已经成功。原方案、实现、checkpoint 均不修改。

本次保留已完成的 IXI 小波底座，并复用原 STC 的查询条件多尺度潜特征轨迹模块，建立同容量 local/extended 两臂。新增42,096参数，总计1,034,915参数。初始新增投影为零，两臂起点完全相同且输出等于固定 IXI 小波 best；只是 extended 可以读取额外远端两个真实锚点。local 负责区分容量/额外训练收益与远端信息收益。两臂都不会加载对方训练后的权重。

## 用户现在运行

一个命令顺序运行两臂并生成 validation 报告：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\MRI\design\pastnet_ixi_context\full.ps1 -Variant pair -Seed 3407
```

先 local，再 extended；每臂各最多80轮、最少30轮后的patience15。两臂是两个完整训练，预计需要数天，不能把它当成一个80轮实验。它们共享已建好的缓存；不另复制16GB数据。保持GPU独占，不把两臂同时放到24GB卡上。

正式配置：microbatch2、累积8（effective16）、checkpoint5/10。smoke实测 allocated约20.82 GiB、reserved约21.54 GiB。前3轮只训练新增STC参数，随后全参数训练；旧小波gate也属于旧参数。

每臂开始时先评估全部58位validation患者，可能一段时间没有epoch日志。训练期间每500个microbatch打印进度，完整epoch结束打印质量和显存。

完成后告诉助手。脚本自动生成 `results/gate_seed3407.json`；助手审计后决定是否还有晋级价值，不自动打开test。

## 意外中断恢复

保留已有代码和文件，不删除run，执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\MRI\design\pastnet_ixi_context\full.ps1 -Variant pair -Seed 3407 -Resume
```

已完成的臂只核验后跳过；已提交epoch恢复模型、EMA、AdamW、AMP scaler、随机状态与history；尚未开始的臂正常初始化。未提交epoch会重跑。初始化validation尚未完成、没有last.pth时的中断先交由助手检查，不手动删除记录重开。

如希望分开执行，分别使用 `-Variant local` 和 `-Variant extended`。两臂都完成后，手动运行配对报告：

```powershell
$env:PYTHONPATH='D:\MRI\design;D:\MRI'
& D:\conda\envs\MRI\python.exe -B -m pastnet_ixi_context.report --seed 3407
```

## 固定判定

只用validation。extended对local需≥+.10dB、10,000次患者配对bootstrap的95%CI下界>0、至少60%患者获益、困难四分位不退、所有质量守卫不退、时间/显存比≤1.5；extended对共同固定初始化还需≥+.15dB。失败就停止，不改LR或延长训练补救。

PSNR/SSIM使用主表的每张GT强度范围，双方输出clamp[0,1]、只评缺失层、按患者等权。MAE/MSE仍显示归一化强度，不能直接与主表原始单位混排；Dice/HD95为强度代理，不是旧auto-mask定义。此次脚本不提供test入口。IXI test已在上一轮探索中查看，不能成为本次调参依据；即使validation通过，也不能直接宣称超过I3Net或SOTA。

结果目录：

- `runs/full_local_seed3407/` 与 `runs/full_extended_seed3407/`
- 自动终端记录 `logs/pair_*.txt`
- 溢出记录 `results/amp_*.jsonl`
- 检查/预登记见 [PROTOCOL_ZH.md](PROTOCOL_ZH.md) 与 `results/checks.json`

此处运行指令已准备，full由用户启动；助手只运行了验证和smoke。

## 2026-10-06 中断后的恢复入口

local已完整完成80轮，extended提交4轮后于第5轮中断；中断同秒存在Windows Update更换NVIDIA驱动的系统事件。原PowerShell transcript没有保存Python异常，现使用独立的 [恢复与完整日志包](../pastnet_ixi_context_recovery/README_ZH.md)：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\MRI\design\pastnet_ixi_context_recovery\resume.ps1 -Variant pair -Seed 3407
```

该入口保持原训练代码、配方和checkpoint，跳过完整local，从extended的第4轮末恢复，并保存完整stdout/stderr和驱动版本。原始异常原因未被堆栈证实；没有改动训练算法。
