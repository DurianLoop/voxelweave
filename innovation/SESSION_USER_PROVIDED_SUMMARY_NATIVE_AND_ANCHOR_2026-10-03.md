# 用户提供的上一模型交接摘要（原内容）

## 目标与约束

目标 **active，未达成**：持续读论文、探索并验证，直到形成可发表且独立确认的 claim。checkpoint 不暂停研究。

- 工作区 `D:\MRI`，PowerShell；Python `D:\conda\envs\MRI\python.exe`。
- 不使用 GPU，不操作用户终端训练，不读锁定 IXI test，不改根 `.gitignore` / 环境。
- 不新建或委派代理。所有研究、代码、证据、公开对话保存在 `innovation`。
- 上一完整阶段属于 **progress**；本次继续已实际 poll 两个仍 live 的任务，是 **verified wait**。

## 当前两个 live 任务：先实际 poll，不重启

1. **session80884**
   ```powershell
   D:\conda\envs\MRI\python.exe -B innovation\experiments\mc_rc_native_competence_queue.py
   ```
   最近实际 poll 仍 live，阶段 `native_diagnostic`。最新日志已完成009第二系列，即约 **13/16系列**；完整结果尚未确认。
   - 状态：`experiments/mc_rc_native_competence_queue/attempt_01.json`
   - 主日志：`.../native_diagnostic_attempt_01.log`
   - 主结果：`experiments/mc_rc_native_competence_cpu/attempt_01.json`
   - 队列自动执行：完整16诊断 → 全部独立模型/区域重放；失败不自动 retry。
   - **完整 native MRI 像素只允许用于此次指定参考对照**，不得输入 sparse 路线。
   - 新合同：`MC_RC_NATIVE_COMPETENCE_CPU_PLAN_2026-10-03.md`
   - 脚本：
     `mc_rc_native_competence_cpu.py`
     `verify_mc_rc_native_competence_cpu.py`
   - 独立 proof 预期：`independent_native_model_and_roi_replay.json`
   - 主运行17次新前向：16 native + 1遗漏系列 sparse；独立复核再17次。
   - 不修改运行中的代码/合同，不提前解释患者平均或称已复核。

2. **session83910**
   ```powershell
   D:\conda\envs\MRI\python.exe -B innovation\experiments\vs_seg_full_volume_queue.py
   ```
   最近实际 poll 仍 live，已完成 `verify_VS-SEG-230`，仍有后续患者核验。
   - 322/322推断条件、45/45 CISS主患者推断完成，**不等于整个队列完成**。
   - 合同 SHA256：
     `061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5`
   - 完整核验/原主分析之后才执行 `vs_seg_selection_sensitivity.py`。
   - HAT−pipeline PCHIP 固定主比较、001/202 Dice改善反证保持，不挑模型救方向。

## 上一阶段已完成的新证据

### 预测区域完整失败，且独立重放通过

- session77501 **实际 poll exit0**，15系列全部执行，errors=[]。
- session29338 **实际 poll exit0**，全部独立复核，errors=[]。均已 terminal，勿重跑。
- 原模型：认证官方冻结 `UNet2d5_Att_Hard_T2_final`，observed-only raw-PCHIP，RAS / NormalizeIntensity / Gaussian 384×384×64滑窗。
- 主 ROI：预测在真实phase0观测层的mask两侧并集 +2mm。
- **0/15系列过预写几何门槛**；停止固定 checkpoint / 主区域配置，不调半径、阈值、crop，不以dense次要ROI救失败。
- 独立验证：1069原DICOM头、268真实anchors、15新CPU前向、759缺层×6策略、原label/整数坐标/physical disk/患者汇总。
- 11系列全体积零真阳性，其中8为空预测。
- 006 SPC384 sparse full Dice `.867673`，但主ROI foreground `.982213`、boundary `.942915`，仍失败。
- 010 FIESTA Hi Res full Dice `.436919`，主ROI foreground `.492393`。
- 不能尚未完成native对照就归因domain shift或抽层。
- 报告：`MC_RC_FROZEN_PREDICTED_REGION_CPU_RESULT_2026-10-03.md`
- proof：
  `experiments/mc_rc_frozen_predicted_region_cpu/independent_observed_input_roi_and_model_replay.json`

### 理想真实观测mask仅为几何上限

原15系列/8开发人/759缺层，union +2mm：
- 15/15几何门槛通过。
- foreground `.9955604883–1`
- boundary `.9921875–1`
- ROI fraction `.0003473618–.0276431129`
- tile fraction `.0022977941–.0500992063`
- tile foreground 全1。
- 原label独立复核 errors=[]；787,030前景体素、全部9策略、packed masks及预算。
- 报告：`MC_RC_OBSERVED_REGION_PROPAGATION_RESULT_2026-10-03.md`
- 真值mask不是部署能力或新方法优势。

### 来源分母错误已更正

当前三批 **24来源中16合格 / 8开发患者，8拒绝或pending**。
旧15名单错误沿用初始资格，漏了已由追加几何审计认证的002第二时点：
`1.3.6.1.4.1.14519.5.2.1.213711595575218613093188251544325434833`

- 该系列7046标签前景体素；仍属于原开发患者002，**不是新独立确认**。
- 旧15合同/输出保留，不能再无条件称“当前全部15”。
- 当前native16合同：旧15 affine/spacing沿用旧配置以可比；遗漏系列用已认证拟合affine/integer grid。
- 脚本实际exit0：
  `experiments/mc_rc_source_denominator_correction.py`
- 结果：
  `experiments/mc_rc_source_denominator_correction/attempt_01.json`
- 报告：
  `MC_RC_SOURCE_DENOMINATOR_CORRECTION_RESULT_2026-10-03.md`

## 新读论文与创新判断

四条 Europe PMC 查询返回41索引记录，新增 **3篇JATS全文**，实际读372相关段落，含方法/结果/讨论/表格/图注；补充文件和新图像未审阅。旧SafeRestore PDF第5页另视觉复看，pdf技能已使用。新增PDF为0。

- SynthSeg 2023，DOI `10.1016/j.media.2023.102789`：
  尺度/contrast域随机化、独立thickness/spacing、label合成训练已有。发布脑结构模型不等于已认证VS检测器。
- 轴位T2脊髓MS分割2025，DOI `10.1162/imag.a.45`：
  2D区域联合监督、多中心及各向异性已有；更多3D上下文/straightening未必改善。582患者，TUM63测试患者的126时点不能称126独立人。
- FGAS2026，DOI `10.1038/s41746-026-02780-6`：
  foundation pseudo-label、跨view一致性、连接/紧致正则组合已有；centroid Gaussian / LCC不保证多病灶拓扑或真值正确。论文存在数据/epoch/分母描述不一致，已记清。

路径：
- 报告：`literature/2026-10-03_predicted_region_fulltext_reading.md`
- 原文与provenance：`literature/source_cache/predicted_region_fulltexts_2026-10-03/`
- 检索原响应：`literature/source_cache/predicted_region_search_2026-10-03/`

窄候选仍是 **仅真实稀疏观测可得的病灶保护局部修正**，尚未成功。
- 旧30特征/λ=.01/五alpha岭失败、线性收益/误差坐标等价保留。
- 需要超过SafeRestore动作风险、普通误差头、固定alpha、旧特征及预算随机强对照。
- 科学独立确认患者仍0。
- 判断：`INNOVATION_DECISION_AFTER_PREDICTED_REGION_2026-10-03.md`
- 后续准备：`MC_RC_NEXT_REPRESENTATION_AND_ACTION_PREPARATION_2026-10-03.md`

## 归档状态与入口

完整阶段24项static write/read-only检查通过；添加最后公开对话/handoff之后，另4项stage/global write/read-only核验也exit0。

- `SESSION_ARCHIVE_VERIFICATION_MC_RC_PREDICTED_REGION_2026-10-03.json`
  含24原检查和4 followup检查。
- 新stage manifest：187文件；
  `literature/mc_rc_predicted_region_stage_archive_manifest_2026-10-03.json`
- 全局验证当时29 PDF、1867 evidence文件、2072 local links，errors=[]。
- **静态核验排除正在运行的native和原队列输出**，不能冒充科学/模型完成。

入口已更新：
- `innovation/README.md`
- `EXPERIMENT_QUEUE.md`
- `SESSION_UPDATE_MC_RC_PREDICTED_REGION_2026-10-03.md`
- `SESSION_VISIBLE_DIALOGUE_MC_RC_PREDICTED_REGION_2026-10-03.md`
- `SESSION_IMPORTED_CHECKPOINT_PREDICTED_REGION_2026-10-03.md`
- `SESSION_HANDOFF_MC_RC_PREDICTED_NATIVE_QUEUE_ACTIVE_2026-10-03.md`

两个文档工具调用格式/匹配错误均发生在写入前，已归档并修正；不是模型失败或审批拒绝。**曾尝试新增native报告脚本，但整次patch事务失败，`report_mc_rc_native_competence_cpu.py`实际不存在。**

## 下一步

1. 实际poll80884、83910；不依据历史文件重启。
2. native16完整且独立17重放proof errors=[]后，核源码/proof覆盖、保存完整结果报告与新的对话/归档。
   - 主端点：患者内系列等权，再8患者等权的缺层Dice(native−sparse)，仅描述性。
   - 并报full/observed/missing任务能力、ROI覆盖/成本、所有失败和遗漏002。
   - native也失败时，不能将sparse失败全归于抽层；差异不自动给出协议因果。
3. 原队列完成后读完整固定主分析，再跑既有筛选敏感性并复核。
4. 根据完整证据选下一项有区分力的CPU假设/新表征合同，保留全部开发失败和真正未见确认需求；不能把已有模块组合、oracle或代码成功称发表claim。
5. 本次继续读了`CLAIM_PUBLICATION_GATE_2026-09-30.md`，它说明旧MIRA候选也未达发表门槛：解析对照已否定深架构特有机制，可行动评分失败；旧发布层审计的阳性事实不能替代新方法/临床优势。当前用户目标仍未完成，保持active。
