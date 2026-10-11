# 后续可执行路线与待取得资源

第一依赖是仍运行的 session29823：四分支last2992、11968条journal与terminal真实exit0齐备后，原 capture_training_terminal→evaluate_matched（36生产/36functionalFOV）→capture_evaluation_terminal→summarize_matched。主比较spatial2992−intensity2992；六医学/严格数值门槛与完整患者分母不变，不拿旧99-step control作长spatial归因。

若能力仍不足，下一普通强基线候选是原位标签的低通/分辨率退化与roundtrip，但先处理已实证的FOV不足。新模块只接受真实上下文，不能直接接当前batch然后把缺失边界补零并称标签/信息安全。至少60/76旧stress plans所需的真实正权重邻居已经越出全FOV，不存在的观测不能补造。

支持策略冻结前需做开发内入口资格：从原物理cache取context，严格处理start/flips与normalized physical coordinate，不加载未观测薄层或GT作影像。选择固定common interior+匹配label裁剪，或固定全部支臂相同的support不足时identity/disabled策略；两者都会改变训练曝露/增强分布，须另立same-parent、same-schedule、same-budget比较，而不是称复现内耳论文。记录所有患者/series的无效增强比例，保留难例，不按label或验证Dice筛病例。若采用有效邻域mask/更紧support stencil，先证明其全目标范围而非32点抽查，区分真实FOV和crop边界。

建议冻结的三种普通control：intensity；intensity+低通/分辨率退化；intensity+support合法roundtrip。保持各自native_reference/raw-PCHIP父last19998、同2992prefix/每患者272曝光、lr1e-4/wd1e-4/AdamW重置、last checkpoint、基础crop/flip一致；GT空间不同策略需明示。保守halo倍数不是时间倍数，另测cache extraction、两resampling、CPU/GPU耗时/内存和storage。GPU未来新阶段用fresh totals≥8192MiB及runtime余量；用户授权已有效。不得中途迁移当前四臂。

合成label-GMM/SynthSeg不能由VS二值label直接忠实复现：背景含多组织，需要合法的稠密解剖标签/概率生成先验、病理解剖覆盖和作者license/依赖/训练成本。当前没有下载/运行外部模型，也不对用户环境安装；先取得作者生成器noise单位/顺序、固定版本与训练语义再决定是否构建低成本近似。GOUHFI关闭downsample、claustrum启用downsample的对立不是处方，应由开发内matched控制解决。

当任务能力和真实动作余量都足够，收益候选才前进：11开发患者内以患者分折，任务/定位/QC/收益训练和校准全部折内，标注实际 actions前后missing病灶损害差；特征限原观测、spacing/support、固定model预测/QC，不用薄层GT或oracle region。控制raw、direct task、充分增强、静态/随机/always action、强QC/error-cost/defer及联合动作相互作用；评价净费用时包含定位/配准/QC/动作/后续分割和失败路径。GOUHFI/claustrum用固定解剖atlas不能替代VS实际损害标签，已有QC的高分也不能当效益证书。

医疗主评价保留完整FOV/全部患者，额外common interior仅作明示的机制诊断，不能缩小主分母。已有4验证患者不拿来调新的support、尺度或损失；方案完全冻结后8未见确认12series仅打开一次，并保留独立任务网复核。异质T2仍不能统称CISS。

未完成资源：FastSurferVINN原文（本轮HTTP500）；2026病灶级集成原文（HTTP500）；claustrum外链Supporting PDF；两作者源码/预训练权重/图像像素。可以更换公开作者版本作新attempt，必须核DOI/题名/版本并保留失败，不以本文讨论引用代读原论文。claustrum供者分折及全18atlas用于CV的边界须核代码；即便源码可取，本项目lockedIXI仍关闭。
