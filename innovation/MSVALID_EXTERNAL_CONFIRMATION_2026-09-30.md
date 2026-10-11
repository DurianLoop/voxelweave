# MSValid 外部确认：MIRA 的共享锚点失明现象

## 预设主结果

本轮在打开 MSValid 目标像素前固定了[协议](MSVALID_CONFIRMATION_PROTOCOL_2026-09-30.md)、[84 人几何名单](literature/msvalid_geometry_qualification.json)、fastMRI HAT/SwinIR 权重、双相位真实锚点、acquired-only 评分支撑及患者 bootstrap 规则。公开数据为 [MSValid，Zenodo 10875606](https://zenodo.org/records/10875606)：84 名复发缓解型多发性硬化症患者的脑 T2；每人仅取 ZIP 字典序第一份 T2。84 份影像均通过[CRC、gzip、NIfTI 与有限值审计](literature/msvalid_integrity_audit.json)，84 个文件 SHA-256 互异。轴向代码全为 LAS，84/84 affine 非奇异。原生 z 间距 3–6 mm，其中 63 人约 6 mm。本试验再次 x4 抽取原生层，不是厚层到薄层的真实超分辨实验。

单一主对照固定 HAT phase-0 预测和目标，伙伴分别为 SwinIR phase-0（共享真实锚点）与 SwinIR phase-2（不相交真实锚点）。两种伙伴各自使用全部真实相位锚点和仓库原 `interpolate_volume` 的 observed-only min/max 归一化。目标限 residue 1/3 且两相位每侧各至少两张真锚点；共 479 层。评分 mask 是 phase-0 最近两真锚点各自 1% 最大绝对强度阈值的并集，未读目标确定支撑。单层 CPU 输出与原模型 `interpolate_volume` 的合成输入检查最大绝对差均为 0。主估计量为先在患者内分别平均 residue 1/3，再两 residue 等权，最后 84 患者等权的 `O_disjoint-O_shared`，其中 `O=mean(((a-b)/2)^2)/T`、`T=(MSE(a,y)+MSE(b,y))/2`。

| 预定端点或描述 | 结果 |
|---|---:|
| 完整计分患者 / 几何合格目标 / 失败 | 84 / 479 / 0 |
| 患者等权共享 `O` | 2.8428% |
| 患者等权不相交 `O` | 22.5993% |
| 主端点 `ΔO` | **+19.7565 个百分点** |
| 5,000 次患者配对 bootstrap 95% CI，种子 20260930 | **+19.3276 至 +20.1605 个百分点** |
| 正 / 负患者；正 / 负目标（后者非独立样本） | 84 / 0；479 / 0 |
| residue 1 / residue 3 的患者等权 `ΔO` | +18.6878 / +20.8253 个百分点 |

预设成功规则为至少 70 人完整计分且主 CI 下界大于零；本次满足。逐患者效应范围为 +13.47 至 +23.63 个百分点。这个正结果在事前固定的单一 HAT→SwinIR 对照和 MSValid 疾病域成立，不是 20 对模型的外部重复，也不更新已失败的部署评分 claim。原 fastMRI 与 IXI 的 acquired-only HAT→SwinIR 历史效果约 +15.88 与 +28.42 个百分点，数值仅供描述，目标几何和队列不同，不作受控跨队列相减。

## 反解释与限制

主效应并非由 phase-2 SwinIR 在整体上更差而显然产生：患者等权 SwinIR MAE 共享为 141.68、phase-2 为 139.06 个**原始强度单位**，61/84 人 phase-2 较低；不相交/共享成对 MSE 的患者平均比值约 0.989。数值单位随扫描强度而异，只适合同患者配对解读。acquired-only 支撑占原始面内网格比例的中位数约 49.5%，范围 33.2%–87.1%；支撑不是目标 mask。HAT 的原预测在每一对中完全相同，因此 `O` 变化源于伙伴与其误差/协方差变化，而不是参考被换掉。原始逐层和逐患者结果见[结果目录](experiments/msvalid_mira_confirmation/summary.json)；[提取清单](literature/msvalid_extraction_manifest.json)记录文件哈希。

仍不能把 `ΔO` 解释为纯锚点身份因果效应：phase-2 同时改变 SwinIR 的完整上下文、相对位置和 observed-only 归一化。两个模型在 fastMRI 上训练；疾病组织、线圈/预处理和 3–6 mm 原生层距共同改变。`O` 在回顾性分析中需要目标像素，无法直接部署成单例正确性分数。MSValid 是与既有 NYU/IXI 数据来源不同的公开队列，但匿名 ID 不能严格排除跨库同人；第一份 T2 的固定选取避免了同一患者多时间点充当独立样本。此结果没有真实薄层真值、解剖分割安全性或临床效益证据。

## 对创新与下一步的影响

最稳妥的论文主张现在可以收窄为：**在一个事前冻结、不同医院的 RRMS 患者 T2 队列中，共享真实锚点时两个冻结重建器的低分歧仍会遮蔽共同误差；不相交锚点的同目标比较显著提高局部误差可观测比例，而且伙伴整体误差未变差。** 这增强现有 MIRA 机制论文的外部证据，不产生一个新的重建方法；“共同错误存在”与代数分解均已有先例，创新仍需落在可审计的测量身份干预、响应影响与失败边界。当前未对病灶位置或病灶层面收益单独验证。当前 CVPR 稿件若要使用新结果，需更新主文、方法合同、伦理/数据许可引用和全部相应复核，不可只追加一行显著性数字。

下一步优先做两类明确标成**已看过 MSValid 结果后的探索**：在同数据上反转 A/B 相位或用匹配位置的对照量化 signed geometry/归一化贡献；在另一个未触及队列重复事前固定主对照。部署 guard、真实 slice-response 去模糊和局部修正收益预测仍是不同问题，不能由本结果自动升级。

可复核材料：[主结果 JSON](experiments/msvalid_mira_confirmation/summary.json)、[逐患者 CSV](experiments/msvalid_mira_confirmation/per_patient.csv)、[逐目标 CSV](experiments/msvalid_mira_confirmation/per_target.csv)、[CPU 推理脚本](experiments/msvalid_mira_confirmation.py)、[完整性审计脚本](literature/msvalid_integrity_audit.py)及[只读结果复核器](experiments/verify_msvalid_confirmation.py)。复核器已从 CSV 重建全部患者/目标配对、两 residue 等权主端点及同种子 bootstrap，并与主 JSON 精确对上。主结果内记录协议、脚本、几何快照和模型权重 SHA-256；本轮未使用 GPU 或 IXI 锁定 test。
