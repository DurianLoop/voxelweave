# 位置通道单独替换：两公开来源 CPU 探索诊断

**结果后探索，不是独立验证或物理采集因果实验。** [运行前冻结方案](POSITION_CHANNEL_ONLY_PILOT_PLAN_2026-10-01.md)固定 MSValid P1–P3 与 ReMIND-003/-007/-009，逐个使用原已登记目标。实验保持 phase-0 HAT 参考、SwinIR 左右邻片、第三通道线性粗图、归一化、输出残差所加粗图、真值和 acquired-only 支撑，仅把 SwinIR 第四通道的相对位置常数 `rel0` 换为同一目标在 phase-2 的 `rel2`。原 phase-2 全邻片切换同时复算作参照。

| 患者等权（患者内 residue 等权） | MSValid | TCIA ReMIND |
|---|---:|---:|
| 固定患者 / 成功；目标 | 3/3；23 | 3/3；12 |
| 共享 `O` | 1.0544% | 1.0974% |
| 只换位置图 `O` | 4.9726% | 4.1640% |
| 全邻片切换 `O` | 26.5560% | 25.0763% |
| **`O_map - O_shared`** | **+3.9182 个百分点** | **+3.0666 个百分点** |
| `O_disjoint - O_shared` | +25.5017 个百分点 | +23.9789 个百分点 |
| SwinIR MAE：共享 / 只换图 / 全切换 | 81.00 / 90.06 / 80.65 | 126.59 / 135.00 / 120.22 |

六名患者、35 个目标的 `O_map-O_shared` 均为正；无患者、像素或推理失败。患者均值之比约 15.4%/12.8%，只是两个不同干预幅度的描述性比值，**不是**“位置编码解释了全效应的 15%/13%”的因果分解。只换位置图时 MAE 分别增加约 9.06/8.41 原始强度单位，而完整切换没有类似恶化；`O` 的伙伴相关分母也随之变动。因此它表明冻结 SwinIR 对第四通道的错配敏感，不足以判明邻片内容、位置、强度归一化各自的可加贡献。尤其该输入把相位 0 的图像与相位 2 的位置标签拼在一起，偏离训练合同。

[CPU 脚本](experiments/position_channel_only_pilot.py)使用两线程、原 IXI 权重哈希、来源哈希、原评分支撑；每个目标的共享/全切换 `O`、HAT MAE、支撑像素数先与既有冻结 CSV 核对。输出为[逐目标](experiments/position_channel_only_pilot/per_target.csv)、[逐患者](experiments/position_channel_only_pilot/per_patient.csv)与[摘要](experiments/position_channel_only_pilot/summary.json)。[独立只读复核器](experiments/verify_position_channel_only_pilot.py)重新检查固定六人、35 个唯一目标、原指标、差值、比例、患者内 residue 等权和两来源汇总，结果 `PASS`。

可复查 SHA-256：方案 `45ec187e44b32dc2bc8ee1c5ee8ec363d2cc6f558587ee264678c2cec9fdf6c5`；推理脚本 `ebcfdaf4cea82ab714437c0a7510f3b69a0f8ee7ff4f17bcb33a31cb4a044463`；逐目标 `d35a4ea2a2dcdf1395f283eef11cfef5d15842c8486bcd66c6aa90784035a1e5`；逐患者 `74acfcf8f2a56d675a5a0f0b51420cc752f3405b4e312af374054e21b4481c8d`；摘要 `d30977a0bdcc9b3b4f5d81ac60bb019c1dff89e4e11f1fdb097f3ba561706286`。运行时长 96.3 秒，CPU float32，没有读取锁定测试集或占用 CUDA。

**下一步判断：** 本消融找到了一个非零编码敏感性，但在六名事后选择患者上不能改变主稿的发布层上下文审计定位。若需要全量估计，应事前写下对 84/62 人、全部 727 原目标、失败记录和与共同分母的双指标规则，再用相同 CPU 权重运行；它仍只会增强敏感性描述，不会取得纯采集身份结论。更高优先级是取得可核实独立采集/发布来源，或在训练内已知 profile 的因素实验中检验留出观测能否预测缺层损害。
