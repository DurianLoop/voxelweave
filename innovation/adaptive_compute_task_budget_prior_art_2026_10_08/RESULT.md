# 本轮结果

新增精读原文2篇，完整文字32页、实际视觉19页；CPU核对39行公开表成功，并完成ACT费用敏感性、非线性收敛前提反例、hard-router公式诊断。四次作者repo检索返回9条metadata，无已认证作者实现，未读README/源码。论文查新范围限定，不宣称完成系统综述或已排除所有相同工作。

- RD-ViT MoE参数约基线53.26%，训练时间1.94924倍；没有给出可核推理加速。保留attention的ACT不能按8/1.4直接外推全部模型5.7倍加速。
- HiFi-MambaV2同patch P1/P2 FLOPs约前代2.54倍；M4Raw P1 AF8的PSNR/SSIM/NMSE均略退化。原文存在多处表/文字和数据分母不一致，已记录定位。
- scalar数学例验证：稳定A和bounded nonlinear f不足以保证全映射contraction；接近均匀soft probabilities也可能hard路由100%集中。这些没有测试作者网络或MRI效果。

结合已有19series实际证据，保留“充分适配后的真实病灶action收益 + 完整成本分配”候选；先测有无可恢复余量，再测policy相对强静态/risk/defer/cost。细节、失败分支、控制与医学执行依赖见 [后续准备](ACTION_VALUE_AND_ACTUAL_COMPUTE_CONTROLS.md)，论文定位见 [原文笔记](PRIMARY_READING.md)，可复算结果见 [CPU receipt](cpu_audit_attempt01/receipt.json)。

原训练最后实际poll5927d4仍返回live session99542，raw arm6732、invocation新增累计26532、累计wall61323.13734419993秒；这些不是本轮新医学训练结果。最新GPU344a32 free1394MiB；RAM/disk reserve通过，根.gitignore/environment.yml SHA未变。未控制其它PID，未启新代理，未改环境，未删历史。未加载新MRI/标签/权重，0神经/GPUforward、0新增训练/head/action labels，未见确认与locked IXI未开。

经验证可发表MRI claim仍未达成，goal active；论文与算术进展不能替代原训练结束后的医学验证。
