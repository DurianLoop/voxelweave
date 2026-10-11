# 单012全视野、同预算loss配方诊断完整结果

两臂同981,602参数/初权重/4000updates/全部4000真实输入与augmentation draws；独立重生成每个draw摘要、核两套最后checkpoint、全部原生指标和6个完整plane重放通过。单开发患者训练内诊断，不是未见验证或loss泛化效果。

| loss配方 | full Dice | missing Dice | recall | precision | absRVE | ASSD mm | HD95 mm | fit gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| bce_batch_dice | 0.865312 | 0.865501 | 0.917088 | 0.819070 | 0.119669 | 2.364254 | 17.660134 | False |
| asymmetric_unified_focal | 0.823786 | 0.840950 | 0.955726 | 0.723855 | 0.320328 | 3.855615 | 25.185642 | False |

预写fit gate为full/missing Dice和full recall≥.90且absRVE≤.10；各臂门槛逐项如下：

bce_batch_dice: {"full_dice": false, "missing_dice": false, "full_recall": true, "full_absRVE": false}
asymmetric_unified_focal: {"full_dice": false, "missing_dice": false, "full_recall": true, "full_absRVE": false}

| 配方/域 | TP | FP | FN | Dice | precision | recall | signed RVE | absRVE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| bce_batch_dice/full | 177395 | 39186 | 16038 | 0.865312 | 0.819070 | 0.917088 | 0.119669 | 0.119669 |
| bce_batch_dice/missing | 132731 | 28759 | 12494 | 0.865501 | 0.821915 | 0.913968 | 0.111999 | 0.111999 |
| bce_batch_dice/anchors | 44664 | 10427 | 3544 | 0.864752 | 0.810731 | 0.926485 | 0.142777 | 0.142777 |
| bce_batch_dice/tail | 0 | 0 | 0 | undefined | undefined | undefined | undefined | undefined |
| asymmetric_unified_focal/full | 184869 | 70526 | 8564 | 0.823786 | 0.723855 | 0.955726 | 0.320328 | 0.320328 |
| asymmetric_unified_focal/missing | 138420 | 45554 | 6805 | 0.840950 | 0.752389 | 0.953142 | 0.266820 | 0.266820 |
| asymmetric_unified_focal/anchors | 46449 | 18662 | 1759 | 0.819792 | 0.713382 | 0.963512 | 0.350626 | 0.350626 |
| asymmetric_unified_focal/tail | 0 | 6310 | 0 | 0.000000 | 0.000000 | undefined | undefined | undefined |

Unified配方−BCE+Dice（同一训练病例、单seed）full差值：{"dice": -0.041526412600263796, "recall": 0.038638701772706785, "absolute_relative_volume_error": 0.20065862598419093}。这些是loss配方的整体差值：同时改变pixel项、区域项和per-image/class归约，不能归因于focal本身；loss数值尺度不同，不能用曲线高低比较优劣。

通过fit gate的配方：无。固定4000步两配方均未证明完整可拟合性；不得事后加步或调门槛将本轮改写为通过。可另写固定slice/曝光与容量诊断协议。

真实训练总updates8000；合成preflight另20updates、无真实MR。生产global/local调用8164/8596，独立重放6/24。CPU单线程、自身below-normal；GPU初始化false，验证/确认患者未加载，隐藏MR不解码。两套训练权重是同一架构/同一病例loss对照，不是第二独立泛化任务网络。

[协议](MC_RC_GLOBAL_LOCAL_SINGLE_CASE_LOSS_CPU_PROTOCOL_2026-10-03.md)、[两臂原始结果](experiments/mc_rc_global_local_single_case_loss_cpu/attempt_01.json)、[draw/指标/完整plane核验](experiments/mc_rc_global_local_single_case_loss_cpu/independent_metrics_draws_and_checkpoint_attempt_01.json)、[两篇新原始文献](literature/2026-10-03_loss_sampling_bias_fulltext_reading.md)。科学确认0，新发表claim未达到，goal active。
