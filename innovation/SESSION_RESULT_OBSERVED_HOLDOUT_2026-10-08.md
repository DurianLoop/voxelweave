# 本阶段入口：合法观测留出特征、原文补读与收益实验准备

完成11开发患者／19系列／38真实fold的先mask观测特征，并通过独立布局v2复核。生产、原失败、v2累计加载41个observed包（唯一19个），81次counterfactual检查事件（唯一38fold），新增神经／GPUforward／训练更新0。原独立失败和source保留；v2明确C-order统计，未放宽容差。

患者等权normalized observed MSE：linear0.284702296827、PCHIP0.286547507866，PCHIP−linear=0.00184521103912（+0.648119%）；18/19系列、10/11患者为正。它是留出诊断，改变间距／输入量且含背景，不推病灶收益，不据此选部署winner。

- [真实MRI特征结果与11患者表](OBSERVED_HOLDOUT_FEATURE_RESULT_2026-10-08.md)
- [19行可观测特征表；任务收益／成本仍null](experiments/observed_holdout_feature_table_2026_10_08.json)
- [Noise2Void／Noise2Same原文核读：19文字页、5视觉页](literature/2026-10-08_blindspot_dependence_primary_reading.md)
- [动作收益候选、可执行依赖、强控制和补读队列](OBSERVED_FEATURE_TO_ACTION_UTILITY_PREPARATION_2026-10-08.md)
- [可见对话](SESSION_VISIBLE_DIALOGUE_OBSERVED_HOLDOUT_2026-10-08.md)、[交接事实](SESSION_IMPORTED_HANDOFF_OBSERVED_HOLDOUT_2026-10-08.md)、[工具／资源账本](SESSION_EXECUTION_LEDGER_OBSERVED_HOLDOUT_2026-10-08.json)、[冻结清单](literature/observed_holdout_stage_manifest_2026-10-08.json)

Noise2Same官方主PDF11页实际文字全部核读，单独Supplemental／AuthorFeedback未取未读；Noise2Void主PDF1–8文字、5／8视觉，第9页未读。错误ID28页晶体管论文排除，429、cap、MiKTeX、TLS、旧summary元数据字段失败都保留。portable PDF reader仅在innovation/tools，不改MRI环境或根文件；没有automatic approval rejection、其他进程控制或新代理。

原live99542继续，最近本阶段poll为native17028／new16929／累计38635.90585660003s，无terminal exit。新增GPU作业需8GB余量，最近1394MiB尚不满足；用户GPU授权持续有效。两臂最终退出／冻结后才原56FOV→6gates→strict；本阶段没有任务效益、确认、验证或lockedIXI读取。

尚未达成可发表MRI收益claim，goal active。本轮实质进展为真实留出特征及独立核验；后续路线是配对真实任务收益与完整成本，而不是将自监督／插值诊断包装成效益。
