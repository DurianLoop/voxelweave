# 2026-09-25：未完成 full 的恢复核验

本地完整调度I3Net运行记录最后提交于2026-09-25 06:21，第236轮；检查时GPU占用0、无Python训练进程。缺少completion与efficiency文件。固定300轮协议在236轮不会正常早停，因此当前状态是中断，原因未从现有产物确定。

已在CPU严格加载last模型与Adam状态，核验浮点状态有限、scaler状态存在且scale为正、四类RNG状态存在、236条history与checkpoint逐项一致。当前源码、修复数据manifest、训练配方与执行配置全部匹配。best模型严格加载成功，epoch41及25.1442674691dB与逐轮记录、已存validation汇总一致；这不是本次独立GPU指标复算或最终full结论。

last SHA256：`2bba959d7e09f4aa4990b2f673ceef99e7835f02a7de4ce481d91fd70c021c46`。

继续使用原正式脚本的`-Resume`，从epoch237恢复，保留优化器、scaler和RNG，按原调度跑到300，不增加预设预算。剩余64轮，最近30轮每轮中位210.63秒，估计3.74小时。未由助手启动耗时full。

```powershell
Set-Location D:\MRI
powershell -NoProfile -ExecutionPolicy Bypass -File .\design\i3net_repaired_reference\full.ps1 -Seed 3407 -Resume
```

机器可读证据：`resume_audit_20260925.json`。旧源码、协议、入口与checkpoint未修改。
