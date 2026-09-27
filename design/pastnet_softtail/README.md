> **2026-09-17：本分支 full 已完成并按门槛停止。** PSNR 25.564924 dB，增益 +0.002913 dB，未达到 +0.10 dB，MAE/Dice 均值 guard 也未通过。不再执行下方历史 full 指令。详见 [复核报告](results/soft_tail_full_review.md)。下一步：`design/i3net_strict_reference`。

# S-CVaR PAST-Net：平滑尾部风险的单变量full

**2026-09-16：实现、训练内机制/能力检查、smoke、恢复及效率核验全部通过，可以运行full。** 这是目标函数实验，网络仍为原G086结构，没有新增架构或参数。本模型尚无full validation结果。

QGCR已按门槛[归档停止](../pastnet_v2_globalmatch/results/global_full_review.md)。本轮从原G086重新开始，只将hard top-10%平方误差项换成固定尾部质量的平滑CVaR，tau=.002、risk权重.2、其余loss和训练recipe不变。不是旧累计risk变体的alpha/weight ramp，也不使用QGCR权重。

用户当前只运行：

```powershell
Set-Location D:\MRI
.\design\pastnet_softtail\full.ps1 -Seed 3407
```

最多80轮，原早停，microbatch2×累积8、checkpoint前5/10 blocks。真实完整反传峰值19.646 GiB allocated /20.314 GiB reserved；trainer smoke为19.62/20.31 GiB。full结束自动测效率，完成后由助手复核validation。

已完成证据：

- hard对照与旧objective的loss相同，参数梯度最大差0；soft只改变risk项，模型初始化与forward逐位一致。
- 全部340个train区间的小扰动诊断：risk梯度相对变化下降77.923%；这是局部稳定性，不是质量收益。
- 两臂分别96步训练固定4区间：soft MSE下降38.08%、MAE同步下降；hard也下降37.82%。它们是可学习性检查，不能据此判断泛化优劣；临时权重不保存。
- 推理参数仍992,179，部分Conv/Linear FLOPs仍446.590G/三层区间；forward实测48.134ms/缺失层，峰值.858745GiB，推理计算图相同。
- 两臂真实trainer smoke通过，soft已完成checkpoint恢复加载通过，正式入口仅stub核验，未自动启动full。

正式门槛：validation相对同预算control≥+.10 dB（本seed≥25.662011），CI/患者胜率/困难四分位/质量/效率全部通过，另要求hard tail10 MSE均值不退。已有control是直接hard对照，无需重复hard full。通过后才补三seed并锁定外部评估；失败不调tau或续训救援。

- [计算前协议](PROTOCOL_ZH.md)
- [设计、数学含义与证据边界](docs/01_设计与证据.md)
- [运行与恢复指令](docs/02_运行指令.md)
- [full前核验报告](results/pre_full_review.md)
- [机制诊断](results/stability.json)
- [能力与显存](results/capacity.json)
- [最终核验](results/final_verification.json)

旧代码、协议和checkpoint保留，本包源码/协议/full.ps1哈希在首次full后冻结。用户不用自行做smoke，也不需要启动其他分支。
