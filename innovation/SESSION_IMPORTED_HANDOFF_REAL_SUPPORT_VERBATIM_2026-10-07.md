# 用户提供的接续摘要原文

以下为本轮可见用户消息中的摘要，保留作为交接输入；摘要中的进度时间是当时记录，不作为当前实时状态。不是助手隐藏推理或不可见历史的导出。

## 目标与约束

- 持续研究直到得到并验证可发表的新 claim；goal **active**，尚未完成。
- GPU 已获授权，但不得操作、重启或迁移用户终端训练，也不枚举/修改其他 PID。
- 新文件仅写 `D:\MRI\innovation`；不改既有冻结证据、根环境或 `.gitignore`；不委派代理。
- PowerShell，Python：`D:\conda\envs\MRI\python.exe -X utf8 -B`。执行脚本后 `exit $LASTEXITCODE`，记录真实工具退出。
- 11 开发患者/19 series；4 已见验证患者/9 series；8 确认患者/12 series及 locked IXI test 关闭。
- 新独立 calibration 仅是正式风险保证的条件，**不要将其变成经验 MRI 效益论文的额外硬门槛**。
- 旧 MIRA 有 MSValid84 人确认；“确认0”仅指当前病灶线。

## 训练必须接续

**首先 poll 同一 session `99542`，不要重启。**

最后有更新的实际 poll：chunk `0bc35c`，native **9504**，invocation02新增 **9405**，累计 **20966.394249100005 秒**，仍 live。当前新轮首次 poll `ca209d` 返回同 session，输出为空，**不是 terminal**。

GPU 最近实际查询 `ad347c`：**2026/10/07 21:42:47.783**，free **1394 MiB** / total24455 MiB / util83%，不满足新 GPU 8GB 启动门槛。

两臂各19998/总39996；CPU4/interop1、float32、共同初始化/监督/增强、AdamW LR/WD `.0001`；30h、8GB余量、250MB限制不变。不看中间 MRI 效益。PCHIP99只是历史。

真实训练 exit0且两臂 last19998冻结后，才记录正式退出，执行原56FOV、4验证患者全部6能力gates、独立strict和真实退出 receipts。旧 direct 理想坐标 absolute gate失败保留；float解释器通过不能覆盖它。

## 上一轮已完成并归档：实质 progress

入口：

```text
innovation/SESSION_RESULT_PATIENT_BASELINE_2026-10-07.md
innovation/SESSION_CHECKPOINT_RECEIPT_PATIENT_BASELINE_2026-10-07.json
innovation/literature/patient_baseline_stage_manifest_2026-10-07.json
```

archive `87369e`真实exit0：**39新stage文件，1431累计证据，380708bytes**；前1386 SHA不变、最终全部hash核验通过。finalize `143899`exit0。后置追加文件未纳本manifest，下阶段需纳入：

```text
SESSION_POST_ARCHIVE_PATIENT_BASELINE_UPDATE_2026-10-07.md
SESSION_FINAL_REPLY_PATIENT_BASELINE_ACTUAL_2026-10-07.md
SESSION_CHECKPOINT_RECEIPT_PATIENT_BASELINE_2026-10-07.json
experiments/finalize_patient_baseline_checkpoint_2026_10_07.py
```

实际实现：

- `patient_risk_cost_baseline_executor_2026_10_07.py`
  - Bonferroni、SplitFST、Pareto。
  - binary exact BinCDF；continuous bounded HB；多risk取max p。
  - weak Pareto默认，all-strict变体；FST严格p<delta；Bonf p<=delta/N。
  - 80位Decimal，binaryCDF向上舍入，Bonf门槛向下舍入，HB额外1e-60。
  - 9个选择场景、104个risk值由独立Fraction/120位entropy公式核验。
- `patient_complete_series_panel_2026_10_07.py`
  - 全(patient,UID,policy)覆盖；患者内series等权、患者间等权。
  - total cost求和全部series，再加一次explicit shared。
  - 9项费用必须显式：observed_load、warmup_cache、sr、candidate_exploration、feature、gate、transfer、inference、postprocess。
  - exact Fraction先判binary harm/RVE，再连续loss30位向上舍入。
  - 不等series合成例MID患者Dice **.575**，错误series平均 **.633333…**；BASE为.5/.6。
  - 独立核验3个面板、8患者策略行及三分之一边界。

真实退出：

```text
1f423b risk qualification exit0
22c400 risk independent exit0
d47af1 complete-series qualification exit0
cbbf85 recurring-thirds qualification exit0
5e0378 complete-series independent exit0
20138e metadata recording exit0
```

三个资格保留各4份source_snapshot。**不能静默修改已执行源码**；修正建新版本/attempt。非法输入拒绝分支的独立核验只核记录，不冒称重新执行异常分支。本轮均合成、MRI/GT读取、模型/GPUforward和训练更新0；论文新增0。库资格不是新MRI claim。

重要准备：

```text
PATIENT_RISK_COST_BASELINE_EXECUTOR_PROTOCOL_2026-10-07.md
PATIENT_RISK_COST_BASELINE_NUMERICAL_AMENDMENT_2026-10-07.md
PATIENT_COMPLETE_SERIES_PANEL_PROTOCOL_2026-10-07.md
PATIENT_RISK_COST_REAL_INPUT_TEMPLATE_2026-10-07.json
RISK_COST_BASELINE_AND_CLAIM_SCOPE_FOLLOWUP_2026-10-07.md
SESSION_HANDOFF_PATIENT_BASELINE_LIVE_2026-10-07.md
```

## 当前新轮：刚开始，只有读取，尚无新文件/实验

已公开说：

> 上一轮补齐了强对照执行器和患者汇总。这轮我会继续核对原训练，并检查开发集是否还能提供有用的 MRI 证据，优先验证与候选创新有关的问题；所有新增材料仍保存到 innovation。

当前意图：不要无限追加合成资格，优先找能改变真实MRI下一步行动的开发证据。考虑过**annotation-only的局部支持/缓存成本诊断**，但**尚未写协议或执行**。只可读取19开发标签，不能读未观测native MR、验证/确认像素或训练中间效果；真实资源资格仍待原gates。

刚发现已有 **label anchor visibility** 审计，必须先检查，避免重复：

```text
innovation/experiments/verify_mc_rc_label_anchor_visibility.py
```

`rg`命中其既有四phase、6/26 connectivity分析。需定位生产脚本、结果、病例范围，确认是否已覆盖这19系列。不要重新声称发现了病灶可见性。

## 刚读取的关键实际源

```text
experiments/mc_rc_current_development_input_preparation/attempt_01.json
experiments/mc_rc_development_training_input_cpu/attempt_01.json
experiments/mc_rc_3d_direct_observed_qualification_2026_10_07/attempt01.json
experiments/mc_rc_observed_only_training_input.py
experiments/plan_mc_rc_3d_local_edit_cache_development_cost_2026_10_07.py
experiments/mc_rc_3d_local_edit_cache_2026_10_07/development_metadata_cost_attempt01.json
```

冻结 loader：

- `DEVELOPERS={'VS-MC-RC-'+x for x in ('001','002','004','005','006','007','009','010','011','012','013')}`
- import只对自身设CUDA_VISIBLE_DEVICES=-1及CPU线程环境。
- `read_supervised_label(case)`：
  - require_developer；
  - 检查label文件SHA；
  - nibabel每4层读取，二值/finite；
  - `dicom_rcz_from_label_xyz`整数变换到native RCZ；
  - 检查foreground等于case.expected_label_foreground_voxels。
- `support_domains(observed)`：anchors z%4==0；missing为非anchor且z<last observed；tail z>last。
- `array_sha`绑定shape/dtype/bytes。

001首series例：

```text
shape [256,256,30]
label_array_sha256 1f7fd497f7f5be4fd312014ce03d1542d9497ffc346339c94f44f8ef3575cc4d
foreground1011
grid unpadded ZRC [42,270,270]
padding [[11,11],[0,0],[0,0]]
```

`physical_mr`是native RCZ→ZRC、trilinear align_corners=False、padding；`physical_label`用nearest-exact。如做support成本，需明确哪种映射，不能把GT oracle支持当GT-free动作或实测速度。

既有成本准备仅用了**中央合成单缺层ROI宽7/32/64**，19series的tile/batch counts；没有真实病灶支持、速度、效益。可能剩余有价值的诊断：真实开发标签支持下的受影响tile/union成本范围，明确只是oracle几何可行性、不是部署策略/任务收益。先检查已有审计，判断是否值得运行。

当前读取命令 `8a5bee`中 `Select-Object *label*,*foreground*`因重复匹配属性报PS错误，终退出0但有error stream；读取已取得需要的label字段。后续用明确属性列表。宽rg输出被截断且扫入vendor，后续限制 `innovation/experiments`和root md，排除tools/source_cache。

## 科学路线和下一步

1. poll99542；保留live handle。
2. 查已有anchor-visibility审计和真实局部支持诊断，避免重复。
3. 若确有未覆盖且能影响下一步的annotation-only实验，先写协议、限定19开发标签、资源/IO审计；独立核验；oracle范围说明清楚。否则转向实际缺口，别用容易通过的合成工作替代MRI目标。
4. 原训练结束后严格完成原56FOV/6gates/strict/exit receipts，再真实资源资格和充分适配dense/direct/SR。
5. 有真实余量才研究observed-only收益预测与联合策略，扣Dice分式/overlap影响，计全部成本，强cost/defer、union-greedy/random、LTT/Pareto比较，冻结后8确认及第二任务模型。
6. 保存当前公开对话、目标续作输入、结果/台账；新阶段归档验证前1431 SHA，纳上一post appendices，排除live invocation/history/resume。

有限非单调risk控制、Pareto成本优化、参考IN、cache、联合greedy等都有先例。当前真正待证的是**充分适配后仍存在MRI特有、合法可预测、同真实预算下超强控制且未见确认复现的收益**。新claim未确认；上一goal turn为progress，当前续作尚只有读取，不标complete/blocked。 
