# 用户提供的接续摘要（原文）

目标仍 **active**：继续研究至可发表且独立确认的 claim，目前未达到。上一轮和本轮都有实质进展，不是停止研究；不要把软件核验或来源资格当科学确认。

### 约束

- 所有新增内容写 `D:\MRI\innovation`。
- Python：`D:\conda\envs\MRI\python.exe -X utf8 -B`。
- 不用 GPU、不操作用户终端训练、不读 locked IXI test、不改根环境或 `.gitignore`，不创建/委派代理。
- 数值任务 CPU 单线程、自身低优先级，磁盘 ≥15 GB、可用内存 ≥8 GB。本轮开始磁盘约17.65 GB。
- 旧45 CISS、旧8 MC-RC患者只能开发；新增患者角色不得根据效果调整。科学确认仍0。
- 不重启已完成或仍 live 的队列。

### 上轮已完成，不重跑

入口：

- `SESSION_HANDOFF_DIRECT_ADAPTATION_AND_IDENTITY_2026-10-03.md`
- `TASK_ADAPTATION_NEXT_TRIAL_PREPARATION_2026-10-03.md`

三篇正文 TumorSynth、FGAS肌瘤、组织学辅助斑块已读152定向块；新12人25系列完成1,475头/25标签及独立重读，21合格，4阴性保留。身份审计、事前角色候选和归档验收均完成。首验收字段错误与修复记录保留，最终同步四检查exit0。

### 本轮关键修正：合格数应为40，不是39

发现上轮角色生成器错误使用旧15条 label visibility 清单，漏掉已通过最新独立几何证明的002另一FIESTA时点：

`1.3.6.1.4.1.14519.5.2.1.213711595575218613093188251544325434833`

最新 `mc_rc_source_denominator_correction/attempt_01.json` 明确旧8人 **16** 合格系列，旧native能力队列也实际使用该序列。上轮CSV错误标记为 `source_rejected_in_prior_preflight`。

本轮已追加修正，不覆盖旧记录、不改患者角色：

- `MC_RC_DEVELOPMENT_INPUT_CPU_PLAN_2026-10-03.md`
- `experiments/prepare_mc_rc_current_development_cases_2026_10_03.py` 已exit0。
- `experiments/mc_rc_current_development_input_preparation/attempt_01.json`
- 同目录 `all159_current_patient_roles.csv`

当前分母：

- 开发11人，26候选系列，**19合格**。
- 验证4人：020/022/025/024，9系列全部合格。
- 确认保留8人：030/029/019/028/031/026/027/015，16候选、12合格。
- 合计23分配候选人、**40合格系列**；科学split仍未启用。
- 开发11人：001/002/004/005/006/007/009/010/011/012/013。
- 所有同人时点同角色，58共享VS-SEG整人排除。

### 新的真实CPU输入流水线

已新增：

- `experiments/mc_rc_observed_only_training_input.py`
- `experiments/audit_mc_rc_development_training_input_cpu.py`
- `experiments/verify_mc_rc_development_training_input_cpu.py`

生产 **session81078已实际exit0**，不要重跑：

- 19系列/11开发患者全部完成。
- 仅解码phase0、stride4的真实observed DICOM层；未解码missing MR。
- 新011/012/013首次仅解码开发角色的observed像素；没有模型效果。
- `ObservedMRI`与标签读取分离；重建/归一化接口无label/native参数。
- raw linear、既有four-neighbor raw PCHIP；边缘不足四邻时linear，tail复制最后anchor。
- 两统计合同：`observed_shared`与`full_own`，float64 mean/population std，输出float32。
- MR、标签同一RAS signed permutation，不插值、不用真值ROI/crop。
- 旧16的observed数组及raw PCHIP输入与旧保存hash逐字节一致。
- 19个observed-only包累计 **116,973,848字节**：
  `data/mc_rc_development_observed_only/*.npz`
- 非有限隐藏值反事实不影响稀疏输入检查通过。
- torch未导入，神经前向0、GPU0、科学确认0。
- 结果：`experiments/mc_rc_development_training_input_cpu/attempt_01.json`

**当前必须先接续 live session1480**：

独立复核脚本正在从原始MR ZIP重读observed层，独立Hermite+harmonic slope公式重算PCHIP、手工统计、标签transpose/flip与RAS变换，核全部19×4=76输入。最后实际观察仍live，仅输出前2系列成功、两插值最大差0。

- 下一步先poll1480，不因观察超时重启。
- 输出目标：
  `experiments/mc_rc_development_training_input_cpu/independent_all19_observed_inputs_and_label_axes_attempt_01.json`
- 尚未确认终态。
- 独立脚本会调用生产reconstruct作实际数组比较，但插值计算和label轴映射有独立实现；不能描述为完全不引用生产代码。

### 新论文检索与正文

已完成四PMC查询，5+12+12+2=**31题名行含重复**，总命中5/52/15/2：

- `literature/search_sparse_task_joint_2026_10_03.py` 已exit0。
- 原始响应：
  `literature/source_cache/sparse_task_joint_search_2026-10-03/attempt_01.json`
- 方案/选择：
  `2026-10-03_sparse_task_joint_search_plan.md`
  `2026-10-03_sparse_task_joint_selection.md`

三篇新JATS body全部获取成功，但**阅读报告和登记尚未写**：

目录：
`literature/source_cache/sparse_task_joint_fulltexts_2026-10-03/`

1. `joint_scar`，PMC10959501，DOI `10.1109/isbi53787.2023.10230541`，39块。
   - 已实际读全部0–38。
   - **不是SR+分割**，而是心肌分割与瘢痕分割两个网络，预测概率mask乘MRI、message passing、联合梯度。
   - 168患者，140训练/28测试；TransUNet，共用backbone但容量/预算是否完全一致未证明。
   - two-step训练用人工心肌mask，测试用预测mask，存在曝光差异。
   - 心肌Dice two-step/MTL/JDL=.894/.900/.891，不能说所有任务都改善。
   - 段30对precision/recall的文字解释与公式方向颠倒；我们的指标须按TP/(TP+FP)、TP/(TP+FN)解释。
   - 原选择里“联合SR/分割”只是检索意图，报告必须纠正。

2. `soft_spinal`，PMC13110827，DOI `10.1016/j.media.2025.103473`，160块。
   - 已读0–19的大部分与**19–65完整**；初次输出截断，20–25已重新读。
   - 243人、6模态，145/49/49患者train/val/test。
   - 6模态hard masks配准到T2后按FOV平均成soft GT，再逆变换；这并非物理组织占比gold standard。
   - 1mm resampling，中心crop64×192×320；大量augmentation、low-resolution模拟、z-score。
   - 3D nnUNet模板、NormReLU、adaptive wing loss；soft/hard GT、单/多模态、DiceCE/AWing对照。
   - nnUNet对照1000epochs，主模型200epochs，不能假定同预算。
   - 尚需读结果与讨论 **66–159** 的相关块；不要把全部160块计已读。

3. `drips`，PMC12633610，DOI `10.1101/2025.10.22.25337423`，113块，**预印本**。
   - 已读 **0–54**（0–17首次可见，18–54完整）。
   - 840 atlas，合成弯曲PVS管状结构；0.5–4mm随机voxel size、形变、k-space motion、Rician noise、bias field。
   - 3D UNet，50×5000updates，12天A100训练。
   - 165评估患者、5队列；训练atlas与评估都有ADNI，需核身份独立性，不能自动称全未见。
   - 段46：在评估PR曲线上挑最大Dice阈值；这是test-selected operating point，不能抄为我们的冻结确认阈值。
   - contrast agnostic会误认其他管状结构，另用Laplacian后处理。
   - 尚需读 **55–112** 结果/讨论/限制。

打印指定块工具：

`literature/show_sparse_task_joint_blocks_2026_10_03.py <stem> <begin> <end>`

### 第四篇直接LGE SR：获取失败保留

为了避免把joint_scar误认为SR，追加查：

- PMC10206514
- DOI `10.1117/1.JMI.10.5.051808`
- *Deep learning architecture for 3D image super-resolution of late gadolinium enhanced cardiac MRI*

既有Markdown/reading_provenance精确DOI检索无命中。新脚本：

`literature/fetch_lge_superresolution_extra_2026_10_03.py`

实际exit0，但请求得到10467字节XML、`AssertionError`，`fulltext_acquired=false`：

- `lge_sr_attempt_01.xml`
- `lge_sr_extra_attempt_01.json`

尚未诊断是body缺失还是DOI问题；不能计正文已读。可先检查raw XML；若只是front，可普通公开PMC HTML访问并用标准库解析。不要安装bs4；上一轮已有标准库解析范例：
`extract_tumorsynth_saved_html_attempt_03_2026_10_03.py`。
若读PDF，须应用PDF skill。

### 下一步

1. **poll1480确认独立19输入复核终态**；失败则保留proof/脚本快照，修复后追加attempt，不能重跑生产冒充新验证。
2. 完成soft_spinal、DRIPS结果/限制核读；诊断LGE XML获取失败，有效获取后再读。
3. 写本轮论文阅读报告及实际块登记，明确joint_scar不是SR、DRIPS测试阈值选择与预算限制。
4. 写角色资格修正、19真实输入结果报告，更新最新README/queue入口；旧39/18只是历史错误记录，新入口明确40/19。
5. 科学下一步要落实真实任务模型训练与能力验证，不能继续仅资格/归档充数。GPU仍不用；可考虑CPU从头训练能力pilot，但**尚未写训练协议/实现、尚未启动训练**。先事前冻结architecture、预算、patient weighting、augmentation、阈值及checkpoint规则；4验证可用于选择，8确认不能用于调参。原6×5矩阵仍未执行。
6. 本轮公开消息、用户compaction请求、失败及新SESSION记录 **尚未归档**；本轮末再做新stage和全局manifest同步。旧验收不覆盖新增文件。

本轮已有三个公开更新：开始说明推进CPU流水线；修正39→40/18→19；说明19生产完成、独立复核live和新先例检索。另刚发checkpoint整理消息。原goal保持active，不mark complete或blocked。

---

以上是接续时用户给出的历史快照。当前完成状态见 [新接续](SESSION_HANDOFF_SPARSE_TASK_TRAINING_2026-10-03.md)，其中live/未读/未训练已被实际结果更新；本原文不改写为最新事实。
