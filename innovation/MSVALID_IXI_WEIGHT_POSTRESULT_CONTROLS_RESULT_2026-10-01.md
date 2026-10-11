# MSValid IXI 权重对：共同缩放与反向相位结果

**判定：同一 MSValid 患者的结果后敏感性为正，不是新独立确认。** 在看过[原 IXI 权重次级结果](MSVALID_IXI_WEIGHTS_SECONDARY_RESULT_2026-10-01.md)后，按[固定方案](MSVALID_IXI_WEIGHT_POSTRESULT_CONTROLS_PLAN_2026-10-01.md)重新运行相同 84 名 RRMS 患者、479 个固定目标、同一 IXI HAT/SwinIR checkpoint。CPU float32、两条 torch 线程，全部源 NIfTI 和权重在推理前按现存清单 SHA-256 核对。84 人/479 目标全部完成，无失败，没有打开 IXI 锁定 test 或干预 GPU 训练。

| 患者等权统计 | 原同权重结果 | 两相位共同 min/max，前向 HAT0 | 同一共同 min/max，反向 HAT2 |
|---|---:|---:|---:|
| 共享 `O` | 1.0420% | 1.0435% | 1.0257% |
| 不相交 `O` | 25.2276% | 25.0793% | 25.0938% |
| 不相交减共享 `Delta O` | **+24.1856** 个百分点 | **+24.0358** | **+24.0681** |
| 5,000 次患者 bootstrap 95% 区间 | +23.7150 至 +24.6726 | +23.5813 至 +24.5032 | +23.5902 至 +24.5537 |
| 正向患者 / 目标 | 84/84；479/479 | 84/84；479/479 | 84/84；479/479 |
| 伙伴共享 / 不相交 MAE | 130.33 / 129.46 | 130.28 / 129.18 | 128.41 / 129.48 |

共同缩放前向相对原同权重效应减少 **0.1499 个百分点**；82 人下降、1 人上升、1 人不变，逐患者变化范围约 -0.517 至 +0.00034 点。方案预定的探索性“共同缩放下区间下界 >0 且保留原效应一半”条件通过。反向固定 HAT2 也同向；其评分支撑来自 phase-2 真锚点，不与前向共享同一支撑。合成输入检查中，新的共同缩放准备函数在取相同范围时与原 IXI 推理准备函数最大差为 0；新逐目标计算与原 metrics 的共同字段最大差为 0。

[汇总 JSON](experiments/msvalid_ixi_weight_postresult_controls/summary.json)、[逐患者 CSV](experiments/msvalid_ixi_weight_postresult_controls/per_patient.csv)、[逐目标 CSV](experiments/msvalid_ixi_weight_postresult_controls/per_target.csv) SHA-256 分别为 `8cfc5731bab59c839210581a0c97cbcaa02741d0cbd8b30eda05b058d341c526`、`9c230ec29ca6e9abcfc79ec0d8f224b7b416509b067f866322c55a869cbc5eba`、`6f2b1a1490817da900bbf731e1c1e7d6a9c5caf64a018a529305b7c9555c62a5`。[CPU 脚本](experiments/msvalid_ixi_weight_postresult_controls.py) SHA-256 `b69bdbf97b598a96f05576112bd9b6b05528f1c2bf594b2abab5d37792fbab54`；方案 SHA-256 `bb91ea4aba3293801f1671b8a0457029ca38676862ce8c4f073c784e41ceaf31`。[独立只读复核器](experiments/verify_msvalid_ixi_weight_postresult_controls.py) SHA-256 `4d41e7539c68cffef61facb66461040c955c99837a1ce246277807e34ce2edc0`，输出 `PASS: 84 patients, 479 targets; forward=0.240358, reverse=0.240681, normalization_sensitivity=True`。

共同 min/max 在共享条件中引入不相交锚点的两个极值，仅是结果后机制敏感性，不能代表单条件部署。两方向仍改变完整邻层内容和 signed geometry；此结果没有隔离纯锚点身份。它补齐了[ReMIND 同一 IXI 权重对结果后控制](REMIND_POSTRESULT_CONTROLS_RESULT_2026-10-01.md)的口径，但两来源的效应值不能当疾病差异受控比较。原 MSValid 次级结果与 ReMIND 事前结果及其区间保持不变。
