# MSValid 共同 min/max 敏感性结果（结果后探索）

这是已看到[事前主结果](MSVALID_EXTERNAL_CONFIRMATION_2026-09-30.md)后制定的[控制方案](MSVALID_COMMON_NORM_PLAN_2026-09-30.md)，**不是第二次独立确认**。保持原首份 T2 的 84 人、479 个 residue 1/3 目标、HAT phase-0 固定参考、SwinIR phase-0/phase-2 伙伴、原 phase-0 acquired-only 评分 mask、CPU float32、原 checkpoint 和患者内 residue 等权。唯一输入处理变动是两相位真实锚点共用其并集 min/max。完整逐目标、逐患者及运行哈希见[结果 JSON](experiments/msvalid_common_norm/summary.json)，[只读复核脚本](experiments/verify_msvalid_common_norm.py)从 CSV 重算所有患者均值、总均值、正负人数及同种子 bootstrap，全部通过。

| 口径 | 共享 `O` | 不相交 `O` | `delta O` | 患者 95% CI | 正/负患者 | 伙伴 MAE（共享/不相交） |
|---|---:|---:|---:|---:|---:|---:|
| 原各相位 observed-only min/max，事前主结果 | 2.8428% | 22.5993% | **+19.7565** 个百分点 | +19.3276 至 +20.1605 个百分点 | 84/0 | 141.68 / 139.06 |
| 两相位锚点并集共同 min/max，结果后控制 | 2.8426% | 22.3197% | **+19.4771** 个百分点 | +19.0337 至 +19.9065 个百分点（探索性） | 84/0 | 141.61 / 138.66 |

相对原端点，患者等权 `delta O` 平均减少 **0.2794 个百分点**；79 人减少、4 人增加、1 人不变。控制后各患者 `delta O` 范围为 +11.7061 至 +23.6346 个百分点。原样本的两相位归一化上限差中位数为联合动态范围的 8.82%。因此**独立 min/max 差异不是正效应的唯一解释**。这不证明归一化零贡献，亦不证明共享锚点身份的纯因果效应：phase-2 仍替换全部真实邻层及其几何/内容，模型接收的相对位置也改变。

并集 min/max 让共享组使用了来自 disjoint phase-2 锚点的极值，因此这一处理不代表真实“只看 phase-0 锚点”的部署输入。报告其结果仅为机制敏感性。伙伴 MAE 为各 MRI 体积的原始强度单位，不可当作跨设备统一临床量纲。主结果的事前 CI 不因本轮探索而更新，旧 acquired-only guard 的失败也不受此结果改变。下一步的[外部响应影响实验](MSVALID_INFLUENCE_FUTURE_PROTOCOL_2026-09-30.md)尚未运行；其几何可行性已有[纯元数据检查](experiments/msvalid_influence_geometry.json)。
