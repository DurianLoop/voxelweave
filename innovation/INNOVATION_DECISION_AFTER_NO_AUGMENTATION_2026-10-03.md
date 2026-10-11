# 无增强完整任务结果后的创新判断

本轮实质结果是：去掉增强显著提高训练内拟合，但四验证能力进一步失败。旧全增强20k开发/验证full Dice .127947/.127522，新无增强为.686214/.068768；新missing .072294、recall .046885、absRVE1.371381，9验证series中4个TP0、1个全空。所有六项原能力gate失败，不改门槛、不删病例、不换checkpoint。

训练20000draw/40000整patch和最后权重认证、新37预测计数/完整affine边界/111plane独立重放都实际结束。失败不是代码未运行的推测，也不是仅看loss。GPU相同权重六固定完整plane的mask比对0差异，只有一张有预测前景；不把它外推为37体积逐值跨设备复现。单seed、四验证此前已见，不能推断去增强的群体因果或临床结果。

| 想法 | 本轮已有证据/先例 | 当前处理 |
|---|---|---|
| 去增强就是改善MRI重建任务的新方法 | 训练内提高而验证下降；增强是现成基线因素 | 否定宽贡献，继续能力开发 |
| 使用TTA/entropy选择误差区域 | 2019原文已明确TTA逆映射、像素entropy、VVC及error关联；20/40倍推理预算 | 可以作未来候选特征，不能称首创或跨域错误保证 |
| 物理采集增强/先恢复与直接分割 | 2020 k-space运动模拟与直接任务/去伪影已有实验；真实参考主要为clean预测而非manual GT | 必须作为强对照，区别运动模拟与真实隔层观测，不直接移植作者结论 |
| 同信息充分适配后仍存在可观测、可修复缺层病灶残余 | 当前模型连强任务能力尚未通过；已读近邻没有证实本合同的正结果 | 保留可否证问题，尚未验证、更未确认新颖性 |

精确目标仍是：在同observed信息/输入统计/监督/容量/预算、充分任务适配后，能否获得优于强raw PCHIP和直接任务修复的、只由可观测信息驱动的缺层病灶修正。当前数据不能支持最终答案为是。

下一能力研究把几何与强度拆开。两个partial输入已完成19series/608draw/1216完整patch及新输入SHA预检；旧CPU两臂不作为新GPU因素的同设备控制。新协议在已见开发失败后冻结为开发：GPU四臂均从同初权重从头各20k，none/both/geometry_only/intensity_only顺序，总80k；全患者/series外生流、patch支撑、loss/预算/最后权重相同。它可能仍失败，必须逐臂保留；不能选好臂后称未见确认。

新GPU运行器已实现。首session52790实际exit1：10真实更新/梯度均有限，但总80k投影5456.296秒>3600资源gate，按协议停止；[失败结果](experiments/mc_rc_gpu_geometry_intensity_factorial/attempt_01.json)保留。新[全GPU执行协议](MC_RC_GPU_FACTORIAL_ATTEMPT02_RUNTIME_PROTOCOL_2026-10-03.md)不降低3600秒门槛；session33664也已实际exit1：10更新、.04590079秒/步，投影3672.063秒>3600，[attempt02失败](experiments/mc_rc_gpu_geometry_intensity_factorial_attempt02/attempt_01.json)保留。两个网络分支都已回传真实梯度，kernel数值预检也通过；这20更新不是新能力效果。

接着另立[有界单配方20k协议](MC_RC_INTENSITY_ONLY_GPU_CAPABILITY_PROTOCOL_2026-10-03.md)，只研究intensity_only能否改善能力；工作量变为20k，原80k四因素未完成且未放宽其门槛，不作同设备四臂因果claim。新session25991已启动，[动态输出](experiments/mc_rc_intensity_only_gpu_capability/attempt_01.json)状态以实际poll为准。本文件不提前宣称20k或新的37/111完成。新的全量训练verifier与binding/evaluator仍需实现。先解决能力，再原生控制/6×5公平矩阵/同observed直接任务与分辨率随机化，最后才开发具体修正并冻结八确认/第二任务网络。

旧45CISS中HAT相对pipeline PCHIP平均Dice为正的反例、旧addback/QDA/线性政策失败不撤销，不换患者/弱基线挽救旧claim。科学确认0，没有可发表且独立确认的新claim；goal active。证据：[完整结果](MC_RC_NO_AUGMENTATION_FULL_TASK_RESULT_2026-10-03.md)、[新全文报告](literature/2026-10-03_no_augmentation_task_fulltext_reading.md)、[GPU因素协议](MC_RC_GPU_GEOMETRY_INTENSITY_FACTORIAL_PROTOCOL_2026-10-03.md)。
