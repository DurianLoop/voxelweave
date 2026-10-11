# 真实旧任务配对标签：资格结果

9对series、4患者的真实已冻结PCHIP/linear完整FOV结果成功连接；[生产资格](qualification_attempt01/receipt.json)与[独立精确重算](independent_attempt01/receipt.json)均实际exit0。本轮没有新增MRIforward、任务训练或head拟合，也没有确认可发表claim。

固定Q为full Dice、ΔQ=linear−PCHIP。患者内series等权，再患者等权：PCHIP均值0.22220312970617495，linear均值0.21844606054481186，ΔQ=−0.003757069161363086。series正2/负4/零3/undefined0，患者正2/负2，全部保留；错误series等权−0.004848830081517072仅展示分母差异，不能改为新主要端点。

| 患者 | series数 | linear−PCHIP |
|---|---:|---:|
| VS-MC-RC-020 | 1 | +0.007702119853609549 |
| VS-MC-RC-022 | 3 | +0.005774463563570235 |
| VS-MC-RC-024 | 2 | −0.01684959890992249 |
| VS-MC-RC-025 | 3 | −0.01165526115270964 |

来源是2026-10-03同一旧20000 task checkpoint，在已见验证4/9上评价过18路径。其原capability_gate_passed=false保持。来源JSON还含开发19 metadata，本轮只导出validation18，未冒称物理来源只含18行；MRI/GT/预测/权重数组均未加载。独立程序不导入生产adapter，另以精确precision/recall的harmonic mean重算Dice，9pairs/72个四域count records与原独立proof一致。

13个真实metadata注入拒绝实际执行，包括missing/duplicate series、错来源/标签/checkpoint/input、缺native plane、GT进入推断、统计/scalar-count不符、虚构fullcost、用弱已见label拟合head及错接开发17特征表。独立verifier核对这些记录但未重新执行13个异常分支。另一次metadata失败注入保留全9series/4患者，患者及队列utility转为null；它不是实际MRI失败，不混进真实结果。

完整动作cost全部null；旧inference_elapsed_seconds只标原infer_native interval，未扩称九相位或患者完整费用。开发11/19的17特征表与这9验证label的patient/UID完全不相交，拒绝把两表拼成训练数据。[paired_outcome_adapter.py](paired_outcome_adapter.py)仅资格化已见旧数据提取；require_fit_ready始终拒绝，尚不是新正式动作label/cost/head生产入口。

[后续正式label与费用连接准备](POSTFIT_EXECUTION_BRIDGE.md)保留原训练→56FOV→六gates→strict→同信息强适配→真实动作余量与全成本→head/强控制→冻结未见确认的顺序。[新增任务适配与计算选择原文](../task_adaptation_compute_prior_art_2026_10_08/PRIMARY_READING.md)又核读两篇：29完整文字页、9视觉页，与本阶段旧label资格分别计数。

公开请求/进度、用户交接和实际tool状态见[可见对话](VISIBLE_DIALOGUE.md)、[用户交接](USER_PROVIDED_HANDOFF.md)、[执行账本](EXECUTION_LEDGER.json)。累计证据由ARCHIVE_MANIFEST.json和ARCHIVE_PROOF.json追加冻结；原文件、根环境和终端训练保持。长期goal继续active。
