# 持续研究阶段记录：可见特征联合诊断与收益坐标等价

用户持续目标：“一直研究探索验证下去，直到达成一个可发表的claim，注意不要动我现在终端训练的进程”。之前GPU繁忙、CPU可验证探索、不可验证准备及全部内容存innovation的约束继续适用。上一目标turn分类为progress：五人约束/常数实际CPU与独立复核改变下一步。此轮也是progress：实际拟合和独立像素/监督证据否定固定可见政策与标签改名贡献，不是状态重述。科学goal active，尚未完成。

## 实际完成与决定

1. 原session83910多次实际poll仍live，不重启/终止。[15:44:09 UTC历史快照](literature/source_cache/mc_rc_visible_queue_observation_2026-10-02.json)41/45主患者、287conditions、inference；不算动态效果。45 CISS+1 TSE、七条件/322计划、335文件引用合同061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5维持冻结。
2. 在新[事后开发合同](MC_RC_VISIBLE_JOINT_DEVELOPMENT_DIAGNOSTIC_PLAN_2026-10-02.md)下实际完成五开发患者的30项可见特征、分开的监督包和五折患者LOPO，固定λ=.01/五alpha网格；每折只有四训练患者进入标准化和拟合。没有HAT/分割网络训练或新网络推断，没有GPU。
3. [完整结果](MC_RC_VISIBLE_JOINT_DEVELOPMENT_DIAGNOSTIC_RESULT_2026-10-02.md)中13政策全部固定缺层评分。联合gain−.066440/.039271/.493958/−.031182/.367433dB，仅004/006过完整門槛；001/005两病灶guard失败，002gain不足。联合平均还劣于固定.5。按合同停止这套固定特征/回归/grid政策，未事后调参或换gate。
4. 同容量10头的绝对误差/收益坐标最大预测差≤6.085e-16，支持/联合决策逐tile一致。固定线性算子下普通目标线性变换不能创造新信息，因此收益监督改名不能成为贡献；不外推所有神经模型等价，也不称新定理。
5. 独立最终[proof](experiments/mc_rc_visible_joint_development_diagnostic/independent_refit_and_pixel_verification.json)以增广lstsq重拟合20组fold/model；独立Hermite和新实际像素核240目标×13政策、34,872tiles×10监督，共348,720标量监督；全部支持/病灶tile数与可见权重、25行30项特征抽查和信息依赖检查，errors=[]。源decoder复用先前认证helper，未声称新decoder独立性或全部特征独立重建。最大重拟合差约1.16e-15。
6. [后续创新判断](INNOVATION_DECISION_AFTER_VISIBLE_JOINT_2026-10-02.md)保存实际否定与剩余假设；新的病灶可见表征、预测区域/边界和更多开发失败例需另立合同，通用路由/任务指导仍有先例。
7. [下一批来源准备方案](MC_RC_NEXT_DEVELOPER_SOURCE_PREPARATION_PLAN_2026-10-02.md)和[冻结JSON](experiments/mc_rc_visible_joint_development_diagnostic/next_developer_source_preparation.json)已实际从既存标签目录生成007/009/010全部7系列，527 API对象，API FileSize合计261,941,288，包含MPR透明拒绝对象。0网络请求、无新MR/label解码，prepared_not_executed，非原生合格人数或未见确认；全部时间点整体归开发。

## 执行错误与修复均保留

执行首session74482在五特征/监督包、第一fold模型/政策保存后，NumPy bool进度JSON失败exit1；原[失败记录](experiments/mc_rc_visible_joint_development_diagnostic_failed_attempt_01/failure.json)、原源码/合同/全部文件保留。仅布尔序列化改为Python bool后全量session76771exit0；最终stage核原/新所有数组及首fold模型/政策逐位一致，科学设置不改。

独立session65461exit1，只有五项Matched random control differs。原因是复核赋值先求RHS permutation再求LHS choice，颠倒生产固定顺序。原源码/proof与[修复记录](experiments/mc_rc_visible_joint_development_diagnostic/independent_verifier_failure_correction.json)保留；显式positions→permutation后session36961exit0。随后发现验证范围还需覆盖完整监督标签，保留该成功proof/源码后追加全监督复算；session49849最终exit0/errors=[]，没有改生产结果。所有终止handle无需再poll。

本阶段没有新论文获取/正文重读，沿用上轮六篇先例核读和引用来设计控制；不把本轮CPU学习计作新文献。root environment.yml仅只读确认依赖，未修改；.gitignore、根环境、用户终端训练及锁定IXI test未动，没有新代理或对外发布/发送消息。

## 完整归档与下一步

[当前阶段静态核验](literature/verify_mc_rc_visible_stage_archive.py)核输入/输出hash、LOPO/失败、等价政策、完整proof及source-only准备；[全局记录](SESSION_ARCHIVE_VERIFICATION_MC_RC_VISIBLE_2026-10-02.json)按依赖刷新旧八stage、新stage及全局write/read-only。live队列不锁，dependency junction不递归hash，旧文档“未训练”等为历史状态，本轮确实拟合了CPU岭模型。

继续poll唯一原83910。完成推断后自动逐患者再生成/输出核验/原主分析，再跑vs_seg_selection_sensitivity.py。HAT−pipeline PCHIP两个主要方向不变，不挑SwinIR救方向，001/202 Dice改善反证保留；原队列已经用于设计，不能当新方法盲确认。

新一轮优先为007/009/010七系列写实际byte/deadline/no-retry及头/grid/label资源合同并执行来源资格审计；更多数据不是方法贡献，未合格例透明拒绝。新的任务区域/边界可见表征只在另合同下开发，保持普通误差头/风险路由/常数/随机及预算对照；最终完整任务、新未见患者确认仍缺。原raw失败、真值约束空间通过、可见政策失败并存，goal不标complete或blocked。
