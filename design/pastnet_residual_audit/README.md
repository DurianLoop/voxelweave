# 成熟 PAST-Net 剩余误差诊断

本轮已完成，**没有探针达到进入 validation 核验的预设门槛，没有新的 full 指令**。未读取 validation/test 图像或标签进行本轮评估，未更新 PAST-Net 权重。geometry、correspondence-only 和 STC 继续保持停止。

基点为同预算 control（G086 系列）的冻结最佳 checkpoint，采用既有观测归一化合同。112个训练series、340个固定稀疏区间，患者划分56名拟合、55名检查。检查患者未参与探针系数拟合，但曾参与历史网络训练，不能称作独立临床泛化测试。

| 探针 | 检查组对基点 PSNR 增益 | 相对前一探针增益 | 对基点 MAE 变化 | 进入 validation |
|---|---:|---:|---:|---|
| 预测自身偏差 self | +.024857 dB | +.024857 dB | +1.34% | 否 |
| 再加入原四锚点 local | +.027663 dB | +.002806 dB | +1.55% | 否 |
| 再加入远端观测 extended | +.028215 dB | +.000552 dB | +1.52% | 否 |

MAE 上升为退步。所有PSNR增益均未达到预先设置的+.05 dB总效应要求；各增量也未达到+.03 dB，且MAE guard失败。不能用统计显著的小增益替代实用门槛。

本轮不同于早期“从linear预测target”的探针：拟合目标是 `target − frozen control prediction`。远端观测对这个成熟模型剩余误差的线性可读信号很弱。预测自身偏差带来大部分改善，却伴随MAE退步，提示后续应审查多指标取舍。**这尚不证明原训练loss是根因，也不证明复杂模型没有更多可用信息。** 不因这个结果直接启动新loss full。

- [结果与研究结论](REPORT_ZH.md)
- [结果产生前登记的协议](PROTOCOL_ZH.md)
- [完整结果JSON](results/train_residual_v1/summary.json)
- [拟合/检查组统计](results/train_residual_v1/group_means.csv)
- [患者与数据/源码核验](results/train_residual_v1/verification.json)
- [输入特征合同检查](results/feature_contracts.json)

代码入口为 `run_probe.py`，不改旧包。已有结果拒绝覆盖；如因环境迁移必须复现，助手应指定新 `--out` 并核对固定协议，不把重复运行当成新seed。
