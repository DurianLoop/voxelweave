# correspondence-only：full 已完成，未晋级

更新时间：2026-09-10。此分支停止，不继续增加轮数、不补另外两seed、不进入IXI/NingXia测试。原预注册协议及源码保持不变，便于核验已完成run。

| 指标 | control | correspondence-only | 差值 |
|---|---:|---:|---:|
| validation PSNR | 25.562011 | 25.564482 | +.002471 dB |
| SSIM | .83508836 | .83514726 | +.00005891 |
| MAE | .02462836 | .02462268 | −.00000568 |
| MSE | .003099146 | .003097662 | −.000001483 |
| forward延迟/生成层 | 47.6936 ms | 50.5223 ms | +5.93% |

best epoch52，67轮早停，完整训练约13.73小时，峰值allocated18.283 GiB、reserved19.451 GiB。训练与checkpoint/源码/recipe哈希检查通过，未使用test选型。

23名validation患者配对bootstrap（10,000次）PSNR区间：[+.001158,+.003992] dB，18/23胜。其他均值质量与成本guard通过，但效应远低于预设+.10 dB，故总判定 **promoted=false**。病例配对方向稳定不等于具有足够研究价值，也不代表已具备三seed复现证据。

原始证据：[晋级判定](results/gate_correspondence_only.json)、[full核验记录](results/full_review_20260910.json)、[逐患者指标](runs/full_correspondence_only_seed3407_vram20/validation/per_patient.csv)。

## 无需训练的模块关闭诊断

同一已训练checkpoint，仅将新增模块末层weight/bias临时置零；不改磁盘checkpoint，不生成新候选，不重新训练。仍只看干净validation23。

| 已训练网络 | 正常PSNR | 新模块置零后的PSNR | 模块开启−关闭 |
|---|---:|---:|---:|
| geometry | 25.564138 | 25.560495 | +.003642 |
| correspondence-only | 25.564482 | 25.549416 | +.015067 |

对应模块开启−关闭的配对95%区间为[+.007967,+.024162]、20/23胜，投影权重L2范数.5662：模块并非未更新或完全无作用。但它关闭后的共同主干比独立control低.012596 dB，说明在共同适应后的网络中模块贡献与其他参数变化不可简单相加为结构净收益。最终净收益仍只有+.002471 dB。该诊断是急性移除，不等价于重新训练的因果消融，不能据此决定继续加权或增大模块。

原始诊断：[summary.json](results/acute_adapter_diagnosis_20260910/summary.json)，并保留各配置逐slice/series/patient CSV。geometry关闭后的区间跨零；两条独立结构路线均没有达到预设净收益门槛。

本次没有启动新的full，也没有用已失败模型叠加频率或风险损失。后续若重新开展研究，需要另行明确有效信息/训练任务的改变及协议，而不是把本轮未晋级称为继续累加的依据。
