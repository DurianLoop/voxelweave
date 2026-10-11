# 后续尝试的入口、条件与拒绝标准

第一优先仍是full_real_intensity_v2_2026_10_09的session90446，当前完整35904资格未终态。实际整体exit0且无session_id后保存原目录ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json，加observed_unified_exec_session=90446，执行既有audit_full_real_terminal.py；失败保留terminal/failed_field，不继承旧6216、不降低3e-6/3e-12/二值零差。不重启或改live runner。12652/29823/78123已经完成，禁止再poll。

六个普通分辨率分支明确为2输入×3mode，使用原2992schedule/每人272曝光、相同parent和optimizer reset；native是诊断上界，raw-PCHIP才是部署可用输入。统一gamma v2、label原位不变。新runner、capture/evaluation、完整cache/augmentation/forward/backward/inference费用入口仍要另建版本和独立资格，当前仅文字计划及算子已准备，不能称已有可运行训练入口。全11GT parent只作开发能力/普通增强诊断，不可作严格LOPO外折init。

资源：实际2a103d完成40份冻结文本NTFS压缩，逻辑62,855,339bytes的路径/字节/SHA均保持，API物理节省33,409,195bytes；同步workspace free也受其他写入影响，不把差额当孤立精确节省。081d9c完整forecast：六branch61,356,359bytes，加原allowance9,800,000需71,156,359；当时储备外47,431,680，短缺23,724,679bytes。文献/归档新增后须fresh重算，不能把旧snapshot当起跑准入。GPU仍需fresh>=8192MiB，现1394不足，磁盘/RAM各保留8GB。继续只针对冻结离线文本另事前清单压缩可探索；不能删除/移动历史或处理MRI/model/live来腾空间。

追加的泛化控制准备：global gamma/明确global Bézier、regionwise monotonic hard-mask与明确seam平滑、ordinary resolution、合法support/reliability-map、scanner/domain-unlearning。所有参数只在11开发的内折设定，不按4seen val特调024或阈值。region curves取精确x=t的fixture仅用于实现数值资格；作者随机采样与nonmonotonic inversion未核，不冒充复现。真实3D输入、GT原位、padding/support、强度统计顺序及全费用必须另资格，当前5toy通过不替代任何病人/模型检查。

UQ入口准备：同时保留每个完整MC样本的voxel field identity和总体积/病灶损害，再计算联合sample-wise统计。Borges式82边际percentile-volume作为另一个定义清楚且独立校准的已知baseline，不与joint predictive quantiles混名；baseline/action paired收益应由实际完整结果相减并保留共同样本或明确coupling，不能把两条边际风险当配对GT。任务仍是FN/FP与病灶实际损害，不以低volume variance/低absRVE/窄区间代漏检约束。

严格患者fold需cold init：task/localization/QC/gain/cost、特征变换、任何domain classifier、UQ/校准均不见外折，全部series随patient同fold；含全11GT的parent禁止作为严格外折warm start。部署feature仅来自合法observed input、metadata与固定预测，不用GT体积/ROI/native missingpixels。scanner/site只是合法已知域信息，不自动等同真实PSF或slice-profile。

候选主张一律在实际充分task及paired可修正余量成立后比较：同信息action-conditioned risk差、QC/error-cost-defer、gain head、去采集、metadata-only、strongest static、always-none/always-action、费用匹配random。共同候选探索、失败、fallback、defer、teacher/label生成、校准和两路径推理全费入账，联合动作重跑完整FOV，不相加单动作收益。不删小病灶或accepted外患者改变分母。

主端点/患者聚合/比较family、action集和预算冻结之后才一次打开8确认患者12series；原六医学gate和独立第二任务实现仍必需。无动作余量、强控制消除采集增量、费用匹配后失效或独立患者不复现均作为负结果。数值资格/文献阅读/压缩/CPU反例均不能当目标完成，科研goal保持active。
