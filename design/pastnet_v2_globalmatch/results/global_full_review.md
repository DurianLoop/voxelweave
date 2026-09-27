# QGCR E1复核：停止

2026-09-16，seed3407，79轮早停、best epoch64。源码、recipe、数据manifest、checkpoint SHA及23名validation患者完整配对核验通过。无新test结果。

| 指标 | 同预算control | QGCR global | 差值 |
|---|---:|---:|---:|
| PSNR / dB | 25.562011 | 25.571022 | +.009011 |
| SSIM | .83508836 | .83531406 | +.00022570 |
| MAE | .02462836 | .02460467 | −.00002368 |
| MSE | .00309915 | .00309392 | −.00000522 |
| NCC | .93954877 | .93966459 | +.00011582 |
| Dice intensity proxy | .97718878 | .97720597 | +.00001719 |
| HD95 intensity proxy | 5.402722 | 5.342826 | −.059897 |
| tail10 MSE | .02696749 | .02692128 | −.00004622 |

PSNR配对患者bootstrap95%CI[.005672,.012529]，21/23患者改善，control最差四分位+.005891 dB。效应仅为+.10门槛的9.01%，因此停止；其余六项guard通过。单seed患者CI不包含seed不确定性，也不能消除多轮validation开发适应性。Dice/HD95 proxy的CI均跨零，仅均值方向通过guard，不作真实分割质量主张。

模型1,048,019参数；训练循环14.2042小时，峰值20.6409 GiB allocated /20.7598 GiB reserved。forward49.2723ms/缺失层，相对control1.03310倍；forward峰值.870795GiB，相对1.01403倍。部分算子448.64264G FLOPs/三层区间，非总FLOPs。

这说明当前global模块带来很小的净改善，不能证明全图对应机制有效；未运行相同容量local对照，也不能由此排除所有远距离对应方法。固定4区间MSE下降15.32%的能力检查没有预测到实质validation收益，后续仍需区分过拟合能力与泛化。

按注册规则停止QGCR，不运行local、不加seed、不续训或调学习率、不测试IXI/NingXia。后续独立 `pastnet_softtail` 只改变原control训练目标中的hard tail项，不使用QGCR权重、不叠加本模块、不修改本分支门槛。

- [完整正式gate](gate_global_seed3407.json)
- [运行核验JSON](global_full_review.json)
- [原协议](../PROTOCOL_ZH.md)
