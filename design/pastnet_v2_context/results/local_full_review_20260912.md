# E1 trajectory_local full 复核（2026-09-12）

结论：**容量对照健康检查通过，允许执行 E2；没有候选晋级。** 冻结协议、代码、数据、checkpoint 哈希一致，23名 validation 患者完整配对；未使用 test。

| 项目 | 结果 |
|---|---:|
| seed / 总轮数 / best epoch | 3407 / 71 / 56 |
| validation PSNR | 25.566130 dB |
| 相对原 control | +.004119 dB |
| 患者配对 bootstrap 95% CI | [.000872,.006842] |
| 改善患者 | 20/23 |
| 原 control 最差四分位平均 PSNR 增益 | +.005826 dB |
| SSIM / MAE / MSE / NCC | .8351995 / .0246173 / .00309596 / .9396117 |
| Dice / HD95 强度 proxy | .9772101 / 5.3349734 |
| tail10 MSE | .02693838 |
| 训练 allocated / reserved 峰值 | 19.7399 / 20.4648 GiB |
| 训练循环记录时长 | 13.0252小时 |
| forward 每缺失层中位耗时 | 49.5626 ms |
| forward 时间 / 显存相对原 control | 1.03919 / 1.03729 |

时长取 history 的训练循环记录，不含初始 validation 和另行 forward benchmark。Dice/HD95 为强度阈值 proxy，非解剖分割质量。单seed bootstrap 仅描述开发集中的配对效应，不代表独立确认。

E1 预登记要求是 PSNR 不低于原 control 超过 .02 dB、forward 时间/显存均不超过1.5倍。本次全部满足。统计上的小幅正增益不能冒充具有实用意义的模型突破；E1 仅建立相同容量的局部观测对照。

E2 只开放远端真实槽，保留完全相同结构、G086初始化、训练recipe和有效batch。它仍需同时达到 local+.10、原 control+.15 dB，即本seed PSNR≥25.712011，并满足CI、胜率、最差四分位、质量、效率全套guards。E2若失败停止，不追加loss或学习率调整。

E2 已有真实smoke的代码哈希和checkpoint核验通过，没有因本次文档更新改变冻结源码。助手未启动E2 full，交由用户运行：

```powershell
Set-Location D:\MRI
.\design\pastnet_v2_context\full.ps1 -Variant trajectory_extended -Seed 3407
```

[机器可读完整复核](local_full_review_20260912.json)；[正式健康判定](local_health_seed3407_20260912.json)。
