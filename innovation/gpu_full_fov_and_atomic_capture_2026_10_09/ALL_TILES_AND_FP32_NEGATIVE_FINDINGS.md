# 全tile定位完成，两个FP32算术方案均失败

全192tile定位session58242 actual888551真实exit0，无session_id；elapsed1171.8308秒。独立分母/身份/最大值审核actual6f2b47 exit0：96batch×49field=4704；192不同tile、CPU/GPU各384实际tile forwards，每设备49字段重复逐位同。审核不冒称第二次逐像素重算；原runner重建完整FOV并执行原CPU/GPU SHA相等断言。

全tile首卷积最大误差0，首InstanceNorm3.0517578125e-5；tile概率最大2.104043960571289e-5。完整原FOV差仍5.334615707397461e-6，坐标7.105427357601002e-15，二值零差；完整概率gate仍失败。最大logit差位于heads.2，2.346038818359375e-4。不能把不同层误差相加，不能把最早差异认作唯一原因，也不能把hook/重复/比较费用当纯GPU部署成本。

基于此，预先冻定两个只改14处InstanceNorm算术的全FP32候选。session28213 actual16133a真实exit0，无session_id；独立身份/重复/gate审核actual8c5479 exit0。5个完整FOV runs共960实际GPUtile forwards；每候选2次完整FOV各自逐位同；原CPU/GPU native SHA均重现，GT0、训练更新0。

| 形式 | 完整FOV最大概率差 | 二值差 | 完整流水线秒 | 原3e-6 gate |
|---|---:|---:|---|---|
| native | 5.334615707397461e-6 | 0 | 5.29688 | 失败 |
| FP32 var_mean centered | 5.7220458984375e-6 | 0 | 7.95157 / 8.01200 | 失败 |
| FP32 affine addcmul | 5.364418029785156e-6 | 0 | 7.84949 / 7.89528 | 失败 |

两候选既未达到门槛也未改善速度，停止作为当前部署修复。没有生成新的full38资格、没有接入正式训练。参数SHA、CPU参考、eps、阈值、native mapping和所有医学gate均保留。峰reserved约1.1702GB；只操作本进程，用户原终端训练和其他PID未操作。

下一定位应在固定CPU层输入上，对每个叶算子分别执行CPU/GPU，区分相同输入的本地算术差异和前层传播误差；不重新尝试channels_last/全CPU norm/这两个全norm形式。协议另冻在MATCHED_INPUT_OPERATOR_PROTOCOL.md。即使某算子形式通过局部诊断，也必须重新完整38/atomic/费用/实际terminal/独立审核后才能成为部署资格。

完整35904 session44317仍live，不能用当前4704逐层字段、选择性456patch字段、GIN24合成例或二值一致替代。正式六臂预检ready=false；目前没有独立确认可发表claim，goal active。
