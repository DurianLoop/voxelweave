# IXI-STC 原始训练恢复与完整日志捕获（2026-10-06）

**2026-10-09状态更新：** local与extended均已完整完成80轮，恢复入口退出码0。extended对local的validation增益+0.00340356 dB，未通过预登记+0.10 dB门槛，停止此路线，不再执行恢复或追加训练。[完整结果与审计](../pastnet_ixi_context/RESULTS_ZH.md)。下文保留2026-10-06故障时的状态和恢复方法，属于历史记录。

当前 local seed3407 已完整完成80轮，validation best29.60343255 dB；extended 已提交4轮，在第5轮中断。已完成训练不重跑，extended从上一完整epoch恢复，第5轮未提交部分重跑。

原 full.ps1 的 PowerShell transcript 只有启动/结束信息，没有捕获 Python 的 stdout/stderr 和异常堆栈。因此目前缺少原始错误文本，不能把中断直接归因为 AMP、OOM、数据或代码。终端读取所需的 @oai/sky 组件未能加载。候选输入只读检查在epoch4权重下全部有限，不等于已复现或排除epoch5故障。

后续系统审计发现直接相关的时间线：Windows Update 于08:58:35开始安装 NVIDIA Display Driver Update (32.0.16.1088)，08:59:15.173重新安装nvlddmkm服务，08:59:19报告安装完成。原AMP日志最后写入08:59:15.900，与驱动更换同秒。当前驱动为610.88。这是中断与驱动更换高度相关的证据，但没有原始堆栈，因果关系仍属推断；没有据此改动训练的数值算法。

已从epoch4正式checkpoint复制到本包独立scratch，使用冻结trainer恢复epoch5，完成至少160个microbatch、20次正常参数更新，无AMP overflow。发现上述系统事件后，助手主动结束隔离GPU恢复检查，未完成原计划的192-update故障窗口重放；不把它报告为确定性故障复现或排除。正式checkpoint及冻结训练代码哈希检查保持不变。详细记录见 `driver_update_timeline.json`、`system_events_20261006.json` 与 `diagnostics/20261006_134448_191538/`。没有启动正式full，没有使用test。

本包修复的是日志捕获缺陷：Python父进程统一接收子进程stdout/stderr、用UTF-8逐行写文件并显示，保留真实退出码。使用冻结的原 trainer --resume，未改变模型、损失、采样、学习率、精度、预算和原manifest。完整故障日志位于 sessions/时间戳/extended_stdout_stderr.txt，provenance.json另存当前Python/PyTorch/CUDA/驱动版本。本包与恢复审计单独哈希，不篡改冻结包。已验证stdout、stderr、中文和完整Traceback均能捕获，子进程非零退出码不丢失。

只读预检查：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\MRI\design\pastnet_ixi_context_recovery\resume.ps1 -Preflight
```

使用此入口按原配方继续恢复；如果再报错，直接检查上述完整日志，不再依赖PowerShell transcript：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\MRI\design\pastnet_ixi_context_recovery\resume.ps1 -Variant pair -Seed 3407
```

local检查后直接跳过，extended完成后仍按原validation协议生成配对报告。该命令是完整训练恢复，由用户执行；助手仅完成只读检查、隔离日志测试和有限GPU恢复检查。训练期间避免再次更换显卡驱动；助手没有改变Windows Update设置。

## 启动阶段也捕获日志（2026-10-06 13:53）

用户再次报告报错，但没有生成新的训练session，新的错误文本尚不可得。这不能解释为已复现之前的驱动问题。相同参数的只读preflight已通过，local/extended checkpoint没有变化。

新增纯Python标准库 `bootstrap.py`，在导入PyTorch及研究包之前创建日志，捕获启动阶段的stdout/stderr/导入异常以及非零退出码。PowerShell入口已改为调用它；另提供ASCII `.cmd`入口，运行命令如下（默认pair、seed3407、恢复已有进度）：

```powershell
D:\MRI\design\pastnet_ixi_context_recovery\resume.cmd
```

该命令为full，仍由用户执行。启动即打印 `Startup log: ...`。完整日志位于 `startup_logs/时间戳/stdout_stderr.txt`；`exit.json`保存实际退出码。训练阶段仍保留内部 `sessions/` 日志。新增入口只负责启动与日志，不是针对尚未知晓的原始错误进行数值修复。

只读预检查：

```powershell
D:\MRI\design\pastnet_ixi_context_recovery\resume.cmd --preflight
```
