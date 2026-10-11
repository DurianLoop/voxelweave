# 本轮工作记录：动作选择直接先例与新VS来源

用户要求接着已有MRI工作批量读论文、避开被占用GPU，能验证就CPU探索，未能验证的记录并准备，把本轮内容放在D:/MRI/innovation。接续用户提供交接摘要，没有重启科研或新建代理。

本阶段取得crossMoDA2026机构作者PDF、COBRAI2025和Kujawa2024经DOI认证JATS正文。重点核方法/数据/评价/限制，不把提取全文算完全核读。两批关键词搜索存在无关高引用与终端截断，未据此做无先例/首创声明。新增作者PDF在source_cache，主注册库29不含此新增。见[阅读记录](literature/2026-10-02_cobrai_crossmoda_mc_rc_reading.md)。

关键方法结论：COBRAI需要完整参考，是结构残差指标；ACS留出k-space MSE才是该文不需完整参考的选择路径。相对动作收益方案须与既有选择和同容量误差预测比较，不能只改名。见[本轮创新判断](INNOVATION_DECISION_AFTER_COBRAI_CROSSMODA_2026-10-02.md)。

关键来源进展：实际认证TCIA MC-RC Version2，2026-06-04新增133series/126timepoints。CPU核完整487series/427studies/160人，API与manifest完全相同。全部58共享患者排除后，102官方ID候选、100有T2描述患者/238序列；没有新native geometry/标签空间/患者性能验证。见[来源结果](MC_RC_V2_NONPIXEL_IDENTITY_RESULT_2026-10-02.md)。

失败保留：原完整crosswalk审计exit1，8个MC-RC UID均可联上，8个旧VS-SEG UID都未在旧目录找到。SQLite独立目录算术复核exit0只认证数量和失败现象，完整来源仍pending。2021Data和2022dataset页面403原响应保留；Synapse只读公开Project metadata200，未证明文件权限。Zenodo2022 license字段与description/论文冲突，未自动放行。一次PowerShell python-c引号丢失导致SyntaxError，无科研结果输出；改用here-string stdin后读取成功。几次长输出截断未当全部阅读，关键段另分块读取。MiKTeX日志写入stderr仍保留，新渲染实际subprocess returncode0；没有请求配置权限或改用户配置。

后续已固定前三名非重合候选及全部9条T2描述序列，未执行新头/标签读取。[准备](MC_RC_NATIVE_T2_LABEL_FOLLOWUP_PREPARATION_2026-10-02.md)列原生DICOM、label pathname/grid、患者级分组和任务模型训练身份；没有训练收益头或下载模型权重。

唯一CPU长任务仍session83910：本阶段实际poll两次live；12:44:34 UTC保存观察22/45人完成七条件，VS-SEG-226继续推断。观察快照见[live状态](literature/source_cache/action_crossmoda_queue_observation_2026-10-02.json)。不能把快照当最终状态。45CISS+1TSE、335引用合同SHA256061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5未改变；无动态子集性能统计。全推断后自动regenerate、完整主分析，再跑既有selection sensitivity。001/202的HAT Dice改善仍是反证，不改挑SwinIR。

所有新增请求、脚本、raw响应、正文、渲染、metadata、CPU失败/复核、研究判断与后续准备都位于innovation；公开消息见[对话](SESSION_VISIBLE_DIALOGUE_ACTION_CROSSMODA_2026-10-02.md)，用户交接原文见[保存件](USER_PROVIDED_HANDOFF_ACTION_CROSSMODA_2026-10-02.md)。没有使用GPU或干预用户训练、没有读取IXI锁定test、没有改根环境/.gitignore、没有发信或注册。科学goal仍active，本阶段progress，未达成可发表claim。

归档检查：本阶段静态脚本检查24请求、30阅读anchors、189主冻结代码/协议；八行完整来源失败预期保留。README更新涉及此前四个静态manifest，统一依次write/read-only，再核本阶段和全局；原始stdout/stderr/退出码见[核验记录](SESSION_ARCHIVE_VERIFICATION_ACTION_CROSSMODA_2026-10-02.json)。不刷新运行中VS-SEG完整stage，不重跑已通过CPU算术或来源请求。

首次全局write发现上述核验记录的链接先于文件生成而暂时不存在，exit1；此前四静态stage及本stage的write/read-only都已通过。已将完整失败核验记录保存为[attempt01](SESSION_ARCHIVE_VERIFICATION_ACTION_CROSSMODA_2026-10-02_attempt_01.json)，修正驱动器先生成pending记录再查链接，随后只重核有修改的本stage和全局；不重复此前已通过静态stage或CPU算术。
