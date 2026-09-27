# full前核验：2026-09-22

**通过，shared seed3407可交付用户运行；尚未启动full。**

| 检查 | 结果 |
|---|---|
| 初始旧模型映射 | G086全部326个tensor严格映射；shared/plain与原预测逐位一致 |
| 非零权重分支等变性 | 八动作最大绝对差1.8813e-7，低于预登记1e-5 |
| 非空泛对照 | plain非零分支不满足同样等变性；方向平均实际改变非零输出，详见checks.json |
| 信息合同 | 新分支不读target，原输入未修改；直接重复的无效outer像素槽不进入新分支，使用原masked differences |
| 参数 | shared/plain均1,006,163，新增13,984 |
| shared容量 | 固定4个train区间96步，MSE下降35.8237%，MAE 0.0228601→0.0189948，新增分支梯度与响应非零 |
| plain容量 | 同样96步，MSE下降35.8497%，MAE下降；两分支差异不用于选型 |
| 真实完整反传显存 | shared19.8002/20.4883 GiB，plain19.7031/20.4160 GiB allocated/reserved |
| 真实trainer smoke | 两分支均完整256²、原loss、优化器/EMA更新成功；shared峰值19.7793/20.4844 GiB |
| 独立指标复算 | 两个smoke best的八项质量指标差值全部0 |
| 恢复加载 | 在smoke副本中移开completion，实际加载last中的model/EMA/AdamW/scaler/RNG并完成；未追加优化步骤；best/last哈希不变 |
| 推理效率 | 53.5211 ms/缺失层，原control47.6936，延迟比1.1222；显存0.858799 GiB，比1.000063 |
| 部分FLOPs | 450.2194G/三层区间，仅Conv/Linear，不是总FLOPs |
| 脚本入口 | 实际PowerShell `-Preflight`通过，确认train1360/val69、固定recipe与源哈希，full目录不存在 |
| 报告边界 | 完整报告拒绝smoke，旧control完整性核验通过 |

容量测试没有显示shared优于plain；它只证明模型可训练，没有用它选择共享结构的超参数。正式筛选后仍必须执行预登记的plain消融，不能跳过归因检查。

本轮不旋转完整训练图像，不增加新loss，不使用orientation full权重，不运行外部测试。新分支全部八方向成本已计入效率。所有旧源码与checkpoint保留。

完整记录：`checks.json`、`capacity.json`、`efficiency_shared.json`、`full_preflight.json`、`final_verification.json`。当前唯一待运行项为README中的shared seed3407 full。
