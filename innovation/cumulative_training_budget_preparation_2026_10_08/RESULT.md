# 本阶段结果：跨进程累计预算与未封闭日志的CPU资格

新增标准库执行原语及独立复核已通过，资格真实afd169=0，独立c170ee=0。原三臂模型/优化器/RNG磁盘资格未重跑。本阶段没有新论文、MRI或checkpoint数组、神经/GPUforward、医学训练或action标签；可发表claim仍未达成，goal active。

三次正常交易各3个SHA256工作标记，共9；另在自有child中写完3个标记后**受控exit17**，总实际CPU标记12。这是受控非零退出，不是GPU OOM、断电或硬杀死进程测试。4个work child+7个只验证child总11进程；后者不执行标记，不import torch/numpy。新进程正确重载第1封闭账，预算预留不足、quota用尽、未封闭pending以及累计费用/arm序号/expected-head三个fault均在新工作前拒绝，真实验证进程exit3。

独立verifier未import新core、未再次执行标记，重算正常3个不可变receipt及journal/closing proof/source SHA、三arm序号/共同token和整数纳秒sum，另核受控exit17产生的3行和pending、拒绝结果。正常完整controller交易记录实际271,998,200ns≈.2719982s；保守收费3,246,692,800ns≈3.2466928s。其差来自每次固定1s封闭余量，不能把保守charge称实际墙时。failed区间elapsed另存且未封闭，resume被阻断，不能悄悄清pending把这段当免费。

- [资格原始结果](attempt01/receipt.json)
- [独立复核](independent_attempt01/receipt.json)
- [执行前冻结来源](attempt01/PRE_EXECUTION_SOURCE_BINDINGS.json)
- [正式接入限制与下一步](INTEGRATION_PREPARATION.md)
- [本轮可见对话](VISIBLE_DIALOGUE.md)及[真实执行观察](ACTUAL_OBSERVATIONS.json)

这只是预算账的人工执行准备。资格contract固定60s/3markers-per-arm、拒绝非synthetic用途；不是医学正式更新预算，也不允许直接给现有训练加此模块。controller bootstrap、外层资格准备/汇总不在该原语计费区间，完整医学资源、全部training/action费用仍需未来入口实际测量。首次加入医学runner时必须另版本化冻结stream、source/data/checkpoint、共同监督曝光与预算，重做必要的医学端到端资格；不能拿本轮CPU哈希秒数推断MRI速度/训练充分性。

原训练d72143实际仍live99542，raw_pchip4356、invocation02 new24156、累计55705.773029200034s，terminal exitnull；GPU1dfd10（2026-10-08 07:17:49.729）free1394MiB，不满足新GPU作业8GB储备。未改根文件、训练进程、能力gate或确认患者。归档接续前4759 SHA及上一阶段post五文件；成功后最新观察另append，不改成功manifest。

