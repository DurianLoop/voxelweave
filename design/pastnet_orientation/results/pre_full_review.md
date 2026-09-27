# full前检查：2026-09-21

已通过，可交付用户运行；正式full未启动。

| 检查 | 结果 |
|---|---|
| 训练集机制，112series/111患者 | 非恒等视图MSE比1.738887；方向差平方/原误差0.801081；超过预登记1.1或0.05条件 |
| 八视图平均诊断 | -1.062778 dB，仅训练集；不作为候选，不使用推理集成 |
| 8动作与反动作 | cond/anchors/target逐位还原 |
| physical方向与spacing | 与真实世界坐标网格有限差分逐位一致 |
| 条件与z反转 | coarse正确，平面动作和z反转可交换，原输入未修改 |
| 原模型一致性 | eval输出逐位相同；identity loss相同、参数梯度最大差0 |
| 完整256²所有动作 | 原完整目标函数、AMP反传与AdamW更新全部有限 |
| 随机动作恢复 | 恢复模型/optimizer/scaler/CPU-CUDA RNG后，动作、loss和更新后权重逐位一致 |
| 显存 | 19.657880 GiB allocated /20.330078 GiB reserved；trainer smoke约19.64/20.36 |
| 实际trainer | 2个训练区间、1个validation区间、完整模型完成；非用于选型 |
| checkpoint与指标 | 哈希通过；独立复算最佳smoke的8项指标差值全部0 |
| 完成后resume | 正确跳过，不多训练一轮 |
| 效率 | 同参数992179、同部分Conv/Linear FLOPs；延迟比1.006553、显存比1.0 |
| full脚本 | 实际`-Preflight`确认train1360/val69和冻结源哈希；full目录不存在 |
| 报告隔离 | full晋级报告拒绝smoke；已有control的完整性检查通过 |

诊断checkpoint为既有control best，full初始化仍为原G086，不把已多训的control best当作新初始化。所有方向变换均无需插值；物理信息只是同步维护，control结构仍不读取新增物理条件，因而本轮没有同时引入geometry变量。

科学边界：方向增强是已知方法，不是原创核心架构。大方向差异可能反映学习到的解剖先验，也可能限制泛化；本诊断不能区分二者。正式validation单变量实验会检验在原方向上增强是否有益，达不到+0.10dB或质量守卫则停止。

协议、模型、训练与检查脚本未修改任何既有冻结包；旧checkpoint、I3Net产物和论文test表均保留。
