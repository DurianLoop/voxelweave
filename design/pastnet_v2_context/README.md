# PAST-Net STC：稀疏轨迹上下文实验

当前状态：**E2 `trajectory_extended` full 未通过增量和总体晋级门槛，STC 分支停止。** 不补其他 seeds，不启动 IXI/NingXia 外部训练或测试，不以续训、学习率调整或堆叠模块救援。E1 的容量对照健康通过不代表 E2 晋级。旧 geometry 和 correspondence-only 也保持停止。本包独立于两份已冻结源码，不覆盖旧 checkpoint。

这次检验的是：**局部窗口遗漏的真实观测，能否通过查询位置上的特征趋势/曲率改善缺失层预测？** 不将新增参数、多尺度或二次拟合本身称为已经成立的论文创新。

```mermaid
flowchart LR
    A[真实稀疏六槽及有效掩码] --> B[1/4 与 1/8 共享特征]
    Q[查询 phase 与相对索引] --> C[有掩码的二次轨迹拟合]
    B --> C
    C --> D[值偏差 / 斜率 / 二次项]
    D --> E[上下文投影]
    L[原四锚点与 linear coarse] --> F[原锚点融合]
    F --> G[宽 MA3 与多尺度 latent]
    E --> G
    G --> H[原有有界解码与双域残差]
```

- [证据与设计依据](docs/01_证据与设计依据.md)
- [冻结前登记的实验协议](PROTOCOL_ZH.md)
- [分开的运行指令与显存实测](docs/02_运行指令.md)
- [训练内信息探针](results/train_information_probe/summary.json)
- [原 control 的 validation 分层误差](results/control_validation_error_strata.csv)
- [validation 真实上下文覆盖](results/validation_context_coverage.csv)
- [最终 smoke、恢复、效率和旧源码完整性核验](results/final_verification.json)

实测新增42,096参数，总计1,034,275；开发阶段两臂 smoke 峰值约19.73 GiB allocated / 20.40 GiB reserved。两个正式入口1轮smoke、局部臂resume均通过。E1 full 实测峰值19.74/20.46 GiB，forward 49.56 ms每缺失层（仅计算、不含IO）。

E1 seed3407：71轮早停，best epoch56，validation23患者 PSNR25.566130，较原 control +.004119 dB，配对95%CI [.000872,.006842]，20/23患者改善。forward 时间/显存各为原 control 的1.0392/1.0373倍，符合容量对照健康条件；不能把这个小收益解释为创新成立。

E2 seed3407：71轮早停、best epoch56，PSNR25.567219。相对 local 仅+.001089 dB，95%CI[-.001338,.003866]，10/23患者改善；最差四分位-.001628 dB，Dice/HD95 proxy 均值方向略退。对原 control 总增益+.005208 dB，远低于+.15门槛。效率满足要求，但不能抵消质量/效应门槛失败。

已补充不训练的同checkpoint诊断：急性屏蔽远端槽后 PSNR25.565443，active-minus-masked仅+.001776 dB，95%CI[-.001269,.005005]；中央区间变化严格为零。该模型对远端输入的可测收益仍很弱。此诊断不是重训消融或信息论上限，也不会修改原gate。当前没有需要用户启动的下一条 STC full。

- [E1 健康判定](results/local_health_seed3407_20260912.json)
- [E1 完整复核](results/local_full_review_20260912.md)
- [E2 正式晋级判定](results/gate_extended_seed3407.json)
- [E2 完整复核与停止结论](results/extended_full_review.md)
- [同 checkpoint 远端屏蔽诊断](results/extended_far_mask_diagnosis/diagnosis.json)
