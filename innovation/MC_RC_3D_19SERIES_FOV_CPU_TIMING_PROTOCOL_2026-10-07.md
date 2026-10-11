# 全19开发series完整FOV的无评分CPU计时

前置：低LR两臂所有原拟合gate与独立重放通过；19series CPU资源资格及无更新独立batch核验complete、errors=[]且实际exit0，源JSON/最后checkpoint SHA匹配。仍只加载11开发患者/19series，不加载验证或确认MRI/GT。这个计时不证明19series任务能力。

使用各臂原低LR单001最后模型，不使用资源资格的丢弃后权重。CPU4 intra-op/1interop、below-normal、float32、原完整physicalgrid/PATCH/半patch stride/Gaussian blending/native-coordinate映射，原infer_full_fov原样。每个series分别记录输入构造+hash耗时、整个FOV真实推断+拼接/映回耗时、输出概率hash、完整shape/coverage/tile数、checkpoint不变性；不计算Dice、recall或任何GT端点，不保存概率/预测体积。

19series事前metadata已有1139tile；两臂分别全部覆盖并核总数。新单次进程墙钟<=1800秒、保存<10MB、RAM/磁盘各留8GB、无CUDA。逐series前后检查资源；没有更换推断context、tile对齐或归一化。独立计时核验只重核metadata的tile数和时间聚合/哈希来源，不重复完整网络前向，也不把telemetry当独立MRI复现。

正式训练预算随后基于33步/臂的真实增强采样、cache、此次全FOV成本共同估计；20k/50k仍是情景，不自动开始长训练或声称充分适配。观察到的中位数/最大值都不是未来墙钟保证。若资格或计时失败，保留失败并调整另一个新协议，原门槛不改。
