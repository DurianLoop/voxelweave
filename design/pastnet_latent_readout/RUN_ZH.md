# 运行记录

当前状态：全量探针失败，停止；没有下一条full训练指令。下面仅是助手已完成的只读诊断与小型闭式拟合复现入口，不是需要用户执行的任务。

```powershell
Set-Location D:\MRI
$env:PYTHONPATH='D:\MRI\design;D:\MRI'
& D:\conda\envs\MRI\python.exe -B -m pastnet_latent_readout.run --smoke
& D:\conda\envs\MRI\python.exe -B -m pastnet_latent_readout.run
& D:\conda\envs\MRI\python.exe -B -m pastnet_latent_readout.verify
```

前两个命令发现已完成结果会拒绝覆盖。原网络冻结；全量入口只有train数据，无validation/test入口。结果存于 `results/v1`，smoke单独存于 `results/smoke`，不会混作准入证据。

不提供延长迭代、修改ridge、改变分组或重启旧frequency变体的命令。后续新模型应建立独立协议和入口，不能覆盖当前实验。
