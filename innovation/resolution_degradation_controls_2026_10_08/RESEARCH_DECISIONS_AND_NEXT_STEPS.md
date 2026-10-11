# 从已有工作和文献保留的研究判断

新增paper maintext数量为0：本轮复核的是已实际完成的阅读笔记和原生产增强接口，不将复读或源码算新论文。项目仍处于任务强基线资格阶段，不用数值一致性替代临床收益。

| 已有先例/证据 | 对当前创新判断的影响 | 准备的实证差异 |
|---|---|---|
| VINN内部feature尺度转换、native skip、内部SF扰动；FastSurfer固定版本支持image-only anisotropy分支 | 标签不变、尺度扰动、分辨率增强均已有先例；不能把本3D降质称作者精确复现 | 普通充分任务增强控制，真实整数spacing和全费用资格 |
| 强QC的error map、radiomics/RF、ensemble/MC等 | 绝对QC、形状分数、错误方向或简单置信度不是独立新意 | 同容量/同监督/同合法信息/同患者fold的QC-error-cost-defer控制 |
| 2026病灶级ensemble/cluster/CC阈值和label重定义 | 静态模型排名、病灶后处理、按cluster选策略已有明确近邻 | 具体动作前后真实病灶损害差，显式合法采集可见性与全费用 |
| 旧whole-target policy仅272/1785 active可执行，5患者9series零事件 | 保留全部监督分母仍不能保证增强充分；这候选不作强基线 | 三轴普通降质完整metadata每患者/series都有事件，真实MRI/强度全分布检查进行中 |
| InstanceNorm合成反例：局部卷积相同而归一化输出差3.8565 | 输入support mask不认证整个网络输出安全 | 完整FOV医学评价；padding变化和归一化费用/效果必须实测 |

阅读依据：既有[原文核读](../full_support_oracle_and_vinn_followup_2026_10_08/PRIMARY_READING_AND_PROJECT_DECISIONS.md)、[固定作者训练链](../real_context_and_author_code_followup_2026_10_08/AUTHOR_TRAINING_CHAIN_FINDINGS.md)、[肿瘤QC强控制](../tumor_qc_strength_followup_2026_10_08/STRONG_QC_AND_ACTION_PREPARATION.md)及[QC与动作准备](../augmentation_primary_followup_2026_10_08/QC_AND_ACTION_NEXT_TRIAL_PREPARATION.md)。本轮没有核读其所引更多参考文献，也没有执行作者实现。

保留的待证伪假设：在充分任务模型及真实可修正余量成立后，合法采集可见性/支持范围/预测信息，能否比强QC-error-cost-defer更好地决定某个具体动作，改善完整患者分母的病灶损害并节约总费用。仅有更准QC、较高PSNR、较漂亮mask或accepted子集Dice不足以支撑此claim。

具体接续：

1. 首先真实poll74234和29823。新完整管线失败即保留failed_field和terminal，不降低门槛或从患者/轴/patch中删反例；成功才保存实际terminal，执行已准备audit_full_real_terminal.py核35,904唯一键及全分母。
2. 原四臂真正all-last2992后，原capture_training_terminal→evaluate_matched→capture_evaluation_terminal→summarize_matched。只用D:/conda/envs/MRI/python.exe；先11968journal、每患者272步、四last，再4已见验证9series的36生产+36functional完整FOV。原六医学门槛不降。这项医学评价优先于继续新训练。
3. 若必要输入任务能力不足，完成普通强任务基线及全cache/support/forward/backward/推理实测费用；GPU达到8192MiB起跑储备、磁盘/RAM8GB储备才冻结新训练。当前不为已有CPU训练迁移device，也不把三轴metadata覆盖称医学改善。
4. 能力和动作余量成立后，冻结动作集、病灶损害单位、费用权重、失败/拒绝路径，11患者内严格patient-fold外生成具体动作前后真实结果。全部series按患者同fold，task/localization/QC/收益/校准均不见外折；包含全11GT的19998parent不能作独立折外warm start。
5. 比较raw保留、always/static best、费用匹配random、强QC-error-cost-defer、同容量收益头及去采集可见性控制；若先执行两路径才能估计收益，两路径成本都算。联合动作实际运行，不能相加单动作标签；accepted/rejected均列完整患者和费用。
6. 没有真实可修正余量或增益胜不过强控制，则保存负结果，不改任务为只追求软件通过。完整选择协议冻结后才一次打开8未见确认12series；独立任务实现/任务网与全患者分母复核。lockedIXI仍关闭。

尚不能验证的内容已具备上述条件、控制及拒绝标准；收益头/新模型训练、完整动作标签生成和未见确认均未执行。完整MRI数值资格是进入这些步骤的前置条件，发表目标尚未完成。
