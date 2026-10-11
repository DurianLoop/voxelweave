# 本阶段：第二批来源完整核验与三开发患者动作试验

上一轮分类为progress（真实来源、几何证据和归档），本轮亦为progress：完成下一批实际读取，修复资源门槛导致的未读状态，执行三患者CPU HAT/动作oracle并独立复核，得到改变下一步决策的主方向失败证据。科学goal仍active，尚无可发表且独立验证claim；GPU、用户终端训练、锁定IXI test、根环境/.gitignore未干预，没有新建/委派代理。

## 实际结果

1. 原CPU session83910实际poll live，仍原45 CISS+1TSE合同；本阶段不重启/终止、不统计动态效果。最新保存快照见 [队列观察](literature/source_cache/mc_rc_action_batch_queue_observation_2026-10-02.json)。全部推断后仍由驱动器自动regenerate/完整主分析，再运行selection sensitivity。001/202 HAT Dice改善反证保留。
2. [第二批原生头/标签结果](MC_RC_004_006_NATIVE_LABEL_RESULT_2026-10-02.md)：004/005/006全八既定T2，实际133,512,951 bytes、701头。六条头资格，八标签实际处理完成，六条头+grid/三人通过，两个004派生/MPR不放行。
3. 标签首跑exit1保留：float64导致五标签超过预写100MB/300MB名义数组上限，非missing/grid失败。追加资源合同采用单数组400MB/全部2GB、≤32MB slab；只补读五标签，复用三已读。独立701头+全部八标签/lstsq/逆整数grid复核exit0/errors=[]。
4. [三患者动作结果](MC_RC_THREE_DEVELOPMENT_ACTION_ORACLE_RESULT_2026-10-02.md)：每人固定最早合格时间点，实际解码三MR，CPU已有IXI HAT，无训练/新权重。195内部缺层、主tile32，固定pipeline和raw两动作及五常数/volume/slice对照。
5. 主pipeline支持域增益0.1476/0.1776/0.2404dB，但004病灶目标等权、006像素加权守卫失败，只有005通过；预写三人全部满足门槛未达，停止该固定主动作/粒度的收益头训练。raw次要三人均过守卫；相对端点0.409–0.819dB，但相对逐患者最佳五常数的描述性增量仅0.225–0.260dB，仍是target-assisted上限，不可部署。
6. 动作独立复核重新MR解码/标签坐标、Hermite PCHIP/向量化投影，195目标、54,768 tiles/全部策略层误差；每患者首中末共九HAT层直接前向逐位一致，实际exit0/errors=[]。只九层再前向，非全HAT体积独立再生成；三人仍development，未做Dice/任务临床评价或患者确认CI。
7. [raw分支准备](MC_RC_RAW_ACTION_FOLLOWUP_PREPARATION_2026-10-02.md)明确事后选择，保留主失败；只联结首批已有001/002最早合格系列，prepared_not_executed、无新MR解码/网络请求。真正执行前另冻观测/动作/预算/资源合同；若任一开发复核失败不启动raw头。当前不训练收益头。

## 代码与事实材料

- [下载/v2头脚本](literature/download_mc_rc_004_006_native_headers_2026_10_02.py)、[几何v2](experiments/mc_rc_native_header_geometry_v2.py)、[执行前合同](MC_RC_004_006_NATIVE_AND_LABEL_EXECUTION_PLAN_2026-10-02.md)与 [八请求ledger](literature/source_cache/mc_rc_004_006_native_headers_2026-10-02/attempt_01.json)。真实MR ZIP在 [data目录](data/mc_rc_004_006_native_header_gate)。
- [标签首跑脚本](experiments/audit_mc_rc_004_006_label_grid.py)、[资源修订合同](MC_RC_004_006_LABEL_RESOURCE_FOLLOWUP_PLAN_2026-10-02.md)、[追加脚本](experiments/complete_mc_rc_004_006_label_resource_followup.py)、[来源独立脚本](experiments/verify_mc_rc_004_006_native_label_preflight.py)。失败/追加/proof在 [标签gate目录](experiments/mc_rc_004_006_native_label_gate)，实际八标签在 [data目录](data/mc_rc_004_006_label_grid)。
- [开发合同](MC_RC_THREE_DEVELOPMENT_ACTION_ORACLE_PLAN_2026-10-02.md)、[CPU动作脚本](experiments/mc_rc_three_development_action_oracle.py)、[独立动作复核](experiments/verify_mc_rc_three_development_action_oracle.py)、[常数对照/后续准备算术](experiments/summarize_mc_rc_action_oracle_followup.py)。输入冻结、HAT数组、tile CSV、层策略误差/guards与proof在 [实验目录](experiments/mc_rc_three_development_action_oracle)。

本阶段新增0份论文PDF，未重复上一轮重点正文下载或原来源已通过复算；主要进展是方法可行性的患者开发证据。此前COBRAI/crossMoDA/ENSURE等新意边界继续适用，不声称已经排除所有routing/收益预测直接先例。

## 归档与后续

本轮用户目标/公开消息见 [对话归档](SESSION_VISIBLE_DIALOGUE_MC_RC_ACTION_BATCH_2026-10-02.md)。[阶段静态核验](literature/verify_mc_rc_action_batch_stage_archive.py)包含八原MR ZIP/八标签、全部源码/合同/失败、三HAT数组/数值/九直接前向proof、常数对照与后续未执行属性，排除实时原队列及bundled依赖junction。README更新后刷新六个旧静态stage、本stage和全局write/read-only，实际结果见 [核验记录](SESSION_ARCHIVE_VERIFICATION_MC_RC_ACTION_BATCH_2026-10-02.json)。核验通过不等于发表claim。

下一轮从 [接续入口](SESSION_HANDOFF_MC_RC_ACTION_BATCH_QUEUE_ACTIVE_2026-10-02.md)继续同一83910、001/002 raw开发复核及独立来源/任务确认条件。原45+1完全结束前不统计动态子集；主比较不改，原标签覆盖和legacy UID缺口不清除。
