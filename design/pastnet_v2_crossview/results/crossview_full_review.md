# LACV E1 full 复核：小幅改善，未晋级

2026-09-15，seed3407，80轮正常完成，best epoch80。源码、协议、recipe、数据manifest、best checkpoint SHA及23名validation患者完整性核验通过。仅validation选型，没有新test结果。

| 指标 | 同预算control | LACV E1 | 配对差值 |
|---|---:|---:|---:|
| PSNR / dB | 25.562011 | 25.576666 | +.014654 |
| SSIM | .83508836 | .83551097 | +.00042261 |
| MAE | .02462836 | .02458643 | −.00004193 |
| MSE | .00309915 | .00309075 | −.00000839 |
| NCC | .93954877 | .93973500 | +.00018623 |
| Dice intensity proxy | .97718878 | .97725100 | +.00006222 |
| HD95 intensity proxy | 5.402722 | 5.311503 | −.091219 |
| tail10 MSE | .02696749 | .02689646 | −.00007103 |

PSNR患者配对bootstrap95%CI为[.009460,.020979]，22/23患者改善，control最差四分位平均+.011116 dB。PSNR效应仅为预设+.10 dB的14.65%；效应guard失败，其他六项guard通过。上述CI只覆盖当前seed的患者重采样，不包含跨seed不确定性，也不消除多轮validation开发适应性。Dice/HD95为强度阈值proxy，不是分割标注下的临床质量结论。

参数1,032,779，forward49.9073 ms/缺失层，相对control1.04641倍；forward峰值.858902 GiB。部分Conv/Linear FLOPs为448.853G/三层区间，不含所有FFT等算子。训练实际峰值19.2569 GiB allocated /19.4141 GiB reserved，循环耗时59,408.97秒（16.5025小时），约20GB预算满足。

最后10轮（epoch70→80）仅增加.000979 dB。best位于末轮本身不证明完全收敛，但不能据此绕过已登记的80轮预算与停止门槛。不得继续延长训练、调整学习率或叠加loss救援。

## 执行决定

E1失败，停止LACV；不运行同容量 `per_anchor` full、不补三seeds、不测IXI/NingXia。这个结果证明当前配置的小幅净改善，尚不能归因于跨锚点机制，也未构成SOTA候选。失败不证明所有跨平面模型均无效。

后续独立低成本诊断位于 `design/pastnet_decoder_audit`：冻结原control，仅检查train上的实际解码幅度限制与原loss输出梯度。诊断不改变任何已有模型，不自动准入full。

- [正式配对gate](gate_crossview_seed3407.json)
- [运行复核JSON](crossview_full_review.json)
- [原预登记协议](../PROTOCOL_ZH.md)
