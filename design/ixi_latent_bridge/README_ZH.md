# IXI I3Net–PAST 潜特征桥接：full入口

2026-10-10，新独立包。当前旧STC路线已停止；本包所有正式full由用户启动。训练前助手完成真实数据合同、显存、两臂smoke与断点恢复核验。

模型固定已有I3Net作为预测基点，以其成熟64通道跨平面latent引导PAST小波MA3查询残差。PAST保留四锚点rich conditioning、64通道宽MA3、多尺度latent、dual-domain和有界残差。新修正限于±0.05，零初始化，两臂初始预测完全等于冻结I3Net。

这是包含I3Net和PAST的混合模型，两份已有预训练权重都是方法的一部分；实际部署仍计算I3Net。不能把结果描述为从头独立PAST或与I3Net同总参数/训练预算的架构比较。超过I3Net是预设评价目标，需要实际结果证明。

## 现在只运行这一个full

在PowerShell或cmd中直接运行（默认pair、seed3407）：

```powershell
D:\MRI\design\ixi_latent_bridge\full.cmd
```

等价PowerShell入口：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\MRI\design\ixi_latent_bridge\full.ps1 -Variant pair -Seed 3407
```

脚本顺序执行只读preflight、完整58例冻结I3Net validation基点、blind full、latent full、配对报告。每臂最多80轮/min30/patience15，只有validation选EMA best。blind屏蔽进入新读出的I3latent，latent开放它；两臂初始化、容量、教师预测、采样、优化与预算相同。

完整代码见 [model.py](model.py)、[run.py](run.py)、[report.py](report.py)；数据、晋级和停止规则见 [中文协议](PROTOCOL_ZH.md)。

## 显存与日志

固定micro-batch4×累积4=effective batch16、7/10个MA3重计算块；BF16桥接训练，冻结I3Net与loss为FP32，validation全部FP32，三个区间合并推理，每个窗口只计算一次I3Net。正式训练前3轮只更新读出，之后解冻PAST；显存测量和smoke已按PAST全部解冻计算最坏路径，并包含I3Net、EMA及AdamW状态。实测峰值allocated约19.23GiB（约20.65GB）、reserved约20.91GiB，保留24GB设备余量。桥接可训练参数1,001,972（读出9,153），另含冻结I3Net 23,205,197参数，总部署参数24,207,169。

实测选择与完整检查见 `results/memory_micro4_cp7.json`、`results/contracts.json`、`results/smoke.json`、`results/checks.json`。避免同时再开另一份GPU训练。

启动器在导入PyTorch之前创建 `logs/时间戳/`；所有启动/训练stdout、stderr、Traceback与退出码单独保存。开始即打印日志路径。训练每100个microbatch及每轮打印进度。FP32全量validation可能一段时间没有训练epoch日志；validation逐患者打印。

## 中断恢复、完成状态与分开运行

中断后重新执行同一条 `full.cmd`。以last.pth为epoch提交点恢复模型、EMA、AdamW、随机状态、历史和best；未提交epoch重跑。已完成的臂核验后跳过，已有基点直接复用。无须手动删除run或修改manifest。训练开始后保留代码、协议和执行配置，不能调参覆盖。

如需要分开运行：

```powershell
D:\MRI\design\ixi_latent_bridge\full.cmd --variant blind --seed 3407
D:\MRI\design\ixi_latent_bridge\full.cmd --variant latent --seed 3407
```

这两个命令分别执行两臂；全部完成后用默认pair入口核验并生成配对报告。两臂结果目录分别为 `runs/full_blind_seed3407`、`runs/full_latent_seed3407`；自动报告 `results/gate_seed3407.json`。

只读检查可单独运行：

```powershell
D:\MRI\design\ixi_latent_bridge\full.cmd --preflight
```

## 晋级后才运行的另外两seed

必须先等待seed3407结果审计。latent对blind≥+0.05dB、对冻结I3Net≥+0.10dB，两项调整97.5%患者CI下界均>0，患者胜率、困难病例、全部质量和配对效率守卫均通过，才继续；否则停止当前机制。入口会拒绝未通过seed3407门槛的其它seed。

通过后按顺序分别运行：

```powershell
D:\MRI\design\ixi_latent_bridge\full.cmd --seed 2027
```

```powershell
D:\MRI\design\ixi_latent_bridge\full.cmd --seed 9103
```

三seed各自全部通过后锁定：

```powershell
$env:PYTHONPATH='D:\MRI\design;D:\MRI'
& D:\conda\envs\MRI\python.exe -B -m ixi_latent_bridge.freeze
```

这些是固定历史初始化上的3次适配seed。当前没有test入口；锁定后另行准备IXI/NingXia的匹配外部评价。本包尚无超过I3Net或SOTA的结果。

启动错误捕获已通过：stdout、stderr、UTF-8中文、Traceback和非零退出码均保存至日志（故意触发的probe不是训练故障）。每轮validation只计算一次，最佳轮复制完整评分；最终best若仍为epoch0，也按实际混合模型重测推理成本。

助手已预先完成58例/5,595缺失层冻结I3Net validation基点：PSNR 31.65224732 dB，SSIM 0.93323661。默认full会核验并复用缓存；该基点属于validation，不能与主表test排名混比。运行核验报告见 [SMOKE_REPORT_ZH.md](SMOKE_REPORT_ZH.md)。
