# 当前接续用户摘要（原文保存）

用户说明原文：

> Another language model started to solve this problem and produced a summary of its thinking process. You also have access to the state of the tools that were used by that language model. Use this to build on the work that has already been done and avoid duplicating work. Here is the summary produced by the other language model, use the information in this summary to assist with your own analysis:

以下原样保存用户提供的摘要。它是用户公开输入，不是当前模型内部推理。其“尚未完成”等状态指交接时点；本次完成项以实际结果和阶段记录为准。

目标仍为 **active**：继续研究直到得到可发表且独立确认的 claim。当前尚未达成；用户本次只要求 compaction，不是停止研究。

### 约束

- 工作区 `D:\MRI`；PowerShell；Python `D:\conda\envs\MRI\python.exe`。
- 新增内容全部放 `D:\MRI\innovation`。
- 不使用 GPU、不动用户终端训练、不读 locked IXI test、不改根环境或 `.gitignore`、不新建/委派代理。
- Python 使用 `-X utf8 -B`；CPU 单线程、自身低优先级；磁盘 ≥15 GB、可用内存 ≥8 GB。
- 所有本轮 CPU 队列现在均已实际结束，**没有需要重启或继续等待的本轮进程**。
- 原45 CISS全已见，科学独立确认患者仍为0。软件复核不等于科学确认。

### 已完成，勿重跑

1. **post 任务队列 session20644：实际 exit0。**
   - 全45人、45新前向、18端点、保存预测独立复核完成。
   - `experiments/vs_seg_post_resize_task_cpu/independent_all_tasks_and_estimates.json`
   - 已生成 `VS_SEG_POST_RESIZE_TASK_CPU_RESULT_2026-10-03.md`、45人/18端点CSV。
   - JSON full Dice：raw `.74459750`、pipeline `.65476150`、post `.65284400`。
   - post−pipeline：`−.00191750`，描述性CI `[−.00483038, −.00015858]`。
   - post−raw：`−.09175350`，CI `[−.14691696, −.04704404]`。
   - RTSTRUCT方向相同。JSON去1mm边界的顺序差CI跨0；不能声称所有域显著或等效。
   - 改变处理顺序没有消除缩放流程相对raw的较大任务差距。

2. **observable_order_risk：producer34708、verifier35552均 exit0。**
   - 主候选失败停止，不改排名方向/预算、不换次要max挽救。
   - 最低order_rms的15人平均ΔDice：JSON `−.11545667`、RT `−.11569908`；guard失败，劣于简单比较。
   - 全45仅16人满足双标签−.01 guard。
   - producer重放135旧体积；verifier补pipeline_linear，覆盖180，历史差异完整披露。
   - 报告：`OBSERVABLE_ORDER_RISK_CPU_RESULT_2026-10-03.md`。
   - proof：`experiments/observable_order_risk_cpu/independent_observables_and_rankings.json`。

3. **anchor bandwidth解析：44318/15909均 exit0。**
   - 45人、855完整间隔、2565缺层、90旧raw/post数组重放；四条件及梯度独立复算通过。
   - 指标 `L=log(Eanchor/mean(Einserted))` 的患者均值：
     - raw `.32422887`
     - mixed_post `1.26286697`
     - slab_roundtrip `.29622220`
     - raw_anchor_roundtrip `−.64241590`
   - mixed−raw全45升高，平均 `+.93863810`；同时处理anchors后全45降低。
   - **这只证实所测相位梯度能量变化，不证明Dice恢复或解剖伤害。**
   - 改anchors的条件违反observed-preserving合同，仅解释性干预。
   - log指标可分离，重复的配对差不是独立机制发现。
   - 报告：`ANCHOR_BANDWIDTH_DIAGNOSTIC_CPU_RESULT_2026-10-03.md`。

4. **归一化技术预检：51036 exit1；90226修正版 exit0。**
   - 固定202/203/204，两baseline共6对。
   - 改anchors、原missing数组相同，但own全volume mean/std使所有missing网络输入改变；fixed baseline stats使missing/tail逐位不变。
   - 首失败是最后错误断言torch未导入；共享重建模块间接导入torch。首结果静态 `torch_imported=false`不可信，原文件保留。
   - 修正版真实 `torch_imported=true`、`cuda_initialized=false`，无模型/前向。
   - 使用authenticated MONAI类源码隔离执行，Transform替换object；不是完整MONAI栈复现或独立第二实现。
   - 报告：`ANCHOR_NORMALIZATION_CONTROL_CPU_RESULT_2026-10-03.md`；修正说明与两个输出目录均保留。

5. **新三人anchors任务pilot：55424 exit0；最终verifier11226 exit0。**
   - 固定202/203/204，各4条件，共12新CPU前向。
   - own/fixed × raw/post anchors roundtrip；缺层原数组不变。
   - 12保存预测指标复核、12完整网络输入SHA重放、6fixed missing身份、36配对端点全部通过。
   - 输出：`experiments/anchor_bandwidth_task_cpu_pilot/`
   - proof：`independent_inputs_and_all36_estimates.json`
   - **刚完成完整结果核读，正式报告尚未生成。**
   - JSON full `post_anchor_fixed−post`：
     - 202 `−.00149780`
     - 203 `−.02975063`
     - 204 `+.01608354`
     - 均值 `−.00505496`；RT均值 `−.00507443`。
   - own post均值 JSON `−.00813223`、RT `−.00816166`。
   - raw_anchor_fixed−raw均值 JSON `+.00958135`、RT `+.00944103`，但202变差。
   - **不支持“平衡anchors带宽就能恢复post任务表现”的固定恢复解释。不能换raw/子组挽救。**
   - 重要反例：post_fixed在JSON去1mm边界均值 `+.02011658`，与full负向不同；全部域必须保留，不挑core代替full。
   - n=3开发诊断，无bootstrap/科学确认。

### 文献与图

本阶段新增 **5篇公开JATS正文、221重点证据块、PDF0**：

- Lazy Resampling：`10.1016/j.cmpb.2024.108422`
- 真实配对MRI形态学：`10.1162/imag.a.997`
- 动态声道SR：`10.3390/jimaging9100233`
- dStripe：`10.1016/j.media.2021.102255`
- STRESS：`10.1007/978-3-030-87234-2_19`

阅读报告：

- `literature/2026-10-03_bandwidth_consistency_fulltext_reading.md`
- `literature/2026-10-03_phase_direct_neighbour_fulltext_reading.md`

均有XML、blocks、正文和reading_provenance。作者实验未复现、图像/supplement未核读。8查询共42题名条目，不等于42全文；版本重复不计独立研究。

新意收窄：重复重采样损失、频率约束、slice一致性、交错SSR、冻结下游任务评价都有直接先例。dStripe实际SURE-based loss的条件不能直接当本项目无偏保证；STRESS实际有pretrained keypoint/PCK评价。

图 `experiments/vs_seg_post_resize_task_cpu/post_task_and_bandwidth_diagnostic_attempt_02.png/.svg` 已实际查看通过。首图均值标注挤到y刻度，首图、首代码快照和失败QA均保留。

### 尚未完成的归档与明确下一步

1. **生成pilot正式报告和CSV。**
   - 建议创建 `experiments/report_anchor_bandwidth_task_cpu_pilot.py`。
   - 输出名已被待执行archive checker引用：
     - `ANCHOR_BANDWIDTH_TASK_CPU_PILOT_RESULT_2026-10-03.md`
     - pilot目录 `report_provenance.json`，需有 `script_sha256`及`outputs[{path,sha256}]`。
   - 全36端点/逐人反例保留，主full恢复解释停止；不要仅报告raw正均值或core正均值。

2. 写/更新：
   - `INNOVATION_DECISION_AFTER_POST_TASK_AND_PHASE_2026-10-03.md` **尚不存在**。
   - `SESSION_UPDATE_ORDER_RISK_AND_PHASE_2026-10-03.md` **尚不存在**。
   - `SESSION_HANDOFF_ORDER_RISK_AND_PHASE_2026-10-03.md` **尚不存在**。
   - 已有 `POST_TASK_AND_PHASE_NEXT_VALIDATION_PREPARATION_2026-10-03.md` 仍写pilot正在运行，需追加完整失败结果和新决策。
   - 不盲目扩展失败anchors恢复干预到全45；继续寻找可区分因素、评估器曝光和真正未见来源。GPU训练准备仍未执行。

3. 修复入口并保存修改前快照：
   - `innovation/README.md`与`EXPERIMENT_QUEUE.md`首段存在**实际字面“????”**，不是显示问题；本轮尚未修复。
   - 已确认两文件不被新pilot合同绑定。
   - 待建快照目录：`literature/source_cache/order_risk_and_phase_entry_snapshot_2026-10-03/`。
   - 最新入口应覆盖完整post、风险失败、phase诊断及pilot反证。

4. 完成本轮静态归档：
   - 已写 `literature/verify_order_risk_and_phase_stage_archive_2026_10_03.py`，**尚未执行**。
   - 它要求上述缺失报告/记录/快照存在，绑定完整pilot proof及5正文。
   - 修改README/EXPERIMENT_QUEUE后需同步历史stage manifests；可参考 `verify_resampling_order_all_archives_2026_10_03.py` 的SCRIPTS组合，但使用新audit输出，不能覆盖首历史audit。
   - 最后更新并只读复核全局 `innovation/verify_archive.py --write` / 无参数。
   - 不重跑已完成科学实验，仅做静态SHA/链接/记录核验。

5. 对话归档：
   - 已保存 `SESSION_VISIBLE_DIALOGUE_ORDER_RISK_AND_PHASE_2026-10-03.md`，包含用户请求、摘要中两条旧公开消息和本轮前11条公开回复。
   - 已保存要点 `SESSION_IMPORTED_CHECKPOINT_ORDER_RISK_AND_PHASE_2026-10-03.md`。
   - 已保存用户传入摘要原文 `SESSION_USER_PROVIDED_SUMMARY_ORDER_RISK_AND_PHASE_2026-10-03.md`。
   - **尚需追加**之后两条公开消息：
     - “三人预检的 12 个条件已全部完成，保存的预测均通过指标复核。现在正在重新构造网络输入，并核对 36 个配对端点；完成后会把结果、反例、论文查新和后续准备一起整理进 `innovation`。”
     - “我会把接续状态写入 `innovation`。所有 CPU 队列都已结束；最新三人结果不支持‘同时处理 anchors 就能恢复 post 分割表现’。尚未完成的是这项结果的正式报告、创新判断和本轮归档清单同步。”
   - 同时保存本次用户compaction请求和本handoff。

原HAT−pipelinePCHIP负向claim仍被旧完整45结果反证；旧残差相加、MC-RC native/QDA/岭失败继续保留。原合同SHA：
`061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5`。所有旧队列和本轮队列均勿重启。
