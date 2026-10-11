# 接续阶段记录：五开发患者失败与约束动作空间

科学目标继续active，尚未达成可发表且独立验证claim。用户要求接着基于MRI项目批量读论文、GPU忙时先做可验证探索、对其余路线留下记录与准备，全部写入D:\MRI\innovation；本阶段沿用授权，未启动新代理，未操作用户训练、GPU、锁定IXI test、根环境或.gitignore。

## 实际完成

1. 原固定CPU队列session83910真实poll仍live。最终本阶段[进度快照](literature/source_cache/mc_rc_constrained_queue_observation_2026-10-02.json)在15:11:09 UTC记录37/45主患者、259条件，stage=inference，未统计动态子集效果。原45 CISS+1 TSE及335文件合同SHA256 061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5未改。335是合同引用数量，322是七条件×46人的计划数量，两者不同。
2. [001/002 raw开发复核](MC_RC_001_002_RAW_ACTION_ORACLE_RESULT_2026-10-02.md)实际CPU完成，001两病灶守卫失败，002通过；三人pipeline原失败和五人raw无约束失败均保留。执行session82925及独立session38154已exit0，无需再poll。45目标、14,976 tiles、六个直接HAT前向逐位一致，未全部再生成。
3. [五人约束oracle](MC_RC_FIVE_DEVELOPER_CONSTRAINED_ORACLE_RESULT_2026-10-02.md)session34030实际poll exit0，最后005/006及完整结论已读。240内部缺层，约束支持域gain .165081/.404077/.819447/.409169/.659883 dB，全部固定数值认证。独立session76938完整exit0，重新解码/独立PCHIP/逐tile/实际像素/dual-KKT核34,872 tiles，errors=[]；不含任何新网络推断。
4. [常数对照诊断](experiments/mc_rc_constrained_constant_diagnostic/attempt_01.json)实际CPU exit0，五人共同alpha可行区间非空，tile超过最佳病灶可行共同系数约.655/.197/.257/.246/.207dB。001只有10个病灶动作tile改变；此定位使用真值，未验证可见预测。
5. [六篇论文复读](literature/2026-10-02_constrained_oracle_prior_art_recheck.md)和[阅读索引](literature/source_cache/constrained_oracle_reading_2026-10-02/index.json)实际完成，六份bounded摘录、四PDF页Poppler渲染/视觉检查。无新增全文或网络请求。明确通用双守卫/风险路由/区域专家/任务指导/病灶聚合已有先例。
6. [新的后续准备](MC_RC_JOINT_ACTION_FOLLOWUP_PREPARATION_2026-10-02.md)保存待执行可见输入诊断、强对照、完整任务、身份/划分及未见确认条件。原失败收益头不恢复训练，新联合路线prepared_not_executed。

## 失败、资源和边界

独立约束复核首跑在Python解析阶段SyntaxError，无数组结果，改显式循环后成功；常数诊断首跑NumPy bool JSON序列化失败，原脚本/合同/失败记录保留，再跑成功。一次命令行依赖探查因PowerShell传参产生NameError，无环境修改；随后用脚本明确确认PyMuPDF缺失，既有MiKTeX Poppler成功替代，首失败render索引保留。尝试读取一个推测命名的文献笔记以及queue_attempt_01.json不存在，已改查实际目录/文件，未影响实验。部分合并输出超预算，必要段落分块复读，未把截断输出称为完整阅读。

CPU计算均隐藏CUDA、单线程、低优先级；资源gate保持可用RAM8GB和磁盘15GB底线。已进行两新开发MR首次解码，因此不能继续说本阶段没有读取新MR。人工mask和隐藏参考只用于开发监督/oracle/评价，不能叫无真值或部署可见。数值认证不是未见患者、任务/Dice、临床风险certificate或真实厚层验证。没有发布论文/PR或对外发送消息。

[静态阶段核验脚本](literature/verify_mc_rc_constrained_stage_archive.py)与[全局核验记录](SESSION_ARCHIVE_VERIFICATION_MC_RC_CONSTRAINED_2026-10-02.json)管理hash、失败与科学结论一致性。README依赖的旧七阶段先按真实记录refresh，再验证新阶段及全局；live推断产物不纳入静态manifest，tool依赖junction不递归hash。

## 下一步保持连续

继续poll原83910，不重启/终止。完整推断后驱动器自动再生成/输出核验/主分析；全部成功后运行vs_seg_selection_sensitivity.py。HAT−pipeline PCHIP两个主要方向固定，001/202 Dice反证保留，不能挑SwinIR替代主方向。

新方法先另写患者角色/可见特征/相同容量/预算/停止条件的合同，再做CPU低容量开发诊断；尤其仅001的约束活跃，现五人不能支撑泛化病灶安全学习。继续审核更多合格开发/未见来源，所有同患者时间点整体分组，排除58共享身份。旧队列及五人已经用于设计，不再算新方法未见确认。待证候选与不可证条件均见后续准备，科学goal不标complete。
