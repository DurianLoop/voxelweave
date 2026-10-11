## 目标与约束

- 持续探索、验证，直到得到可发表的新 claim；goal **active**，尚未达成。
- GPU 已授权，但不得操作、重启或迁移用户终端训练，不枚举/修改其他 PID。
- 新文件仅写 `D:\MRI\innovation`；不改冻结证据、根环境、`.gitignore`；不委派代理。
- PowerShell；Python：`D:\conda\envs\MRI\python.exe -X utf8 -B`。运行后 `exit $LASTEXITCODE`，记录真实工具退出。
- 11 开发患者/19 series；4 已见验证患者/9 series；8 确认患者/12 series、locked IXI 关闭。
- fresh calibration 只限制正式风险保证，不是经验 MRI 效益论文的额外硬门槛。
- 旧 MIRA/MSValid84 确认保留；“确认0”只指当前病灶线。

## 原训练：必须接续同一 session

**首先 poll `99542`，不要重启。**

- 最新实际 poll：`4ebf02`，返回同一 live session、输出为空，**不是 terminal**。
- 最后含更新的 poll：`d72ada`：
  - native **10395**
  - invocation02 新增 **10296**
  - cumulative **23046.679234499927 秒**
- 最新 GPU 查询：`9fbf6b`，**2026/10/07 22:13:57.195**，free **1394 MiB** / total24455 / util92%，未达新 GPU 8GB 门槛。
- 两臂各19998/总39996；CPU4/interop1、float32、共同初始化/监督/增强、AdamW LR/WD `.0001`；30h/8GB余量/250MB不变。PCHIP99仅历史，不读中间 MRI 效益。
- 真实 training exit0且最后两臂冻结后，才写实际退出 receipt，执行原56FOV、全部6能力 gates、独立 strict。旧 direct 理想坐标 absolute gate 失败不能被 float 解释器覆盖。

## 上一完整轮：已完成，属于实质 progress

入口：

```text
innovation/SESSION_RESULT_REAL_SUPPORT_2026-10-07.md
innovation/SESSION_CHECKPOINT_RECEIPT_REAL_SUPPORT_2026-10-07.json
innovation/literature/real_support_stage_manifest_2026-10-07.json
innovation/REAL_SUPPORT_TO_OBSERVED_TASK_FOLLOWUP_2026-10-07.md
```

实际归档 `cfd61d` exit0：

- **79** 新 stage 文件
- **1516** 累计冻结证据
- **9,484,187 bytes**
- 前1431 SHA不变，全部最终证据 SHA 已核验。
- finalize `d697b8` exit0。
- 根受观察文件 hash 不变。

完成了 annotation-only 的真实支持成本诊断：

```text
experiments/mc_rc_real_support_cache_diagnostic_2026_10_07.py
experiments/verify_mc_rc_real_support_cache_diagnostic_2026_10_07.py
experiments/mc_rc_real_support_cache_diagnostic_2026_10_07/attempt01.json
experiments/mc_rc_real_support_cache_diagnostic_2026_10_07/independent_rational_support_attempt01.json
```

- 19 series/11患者、1139 tiles，生产19+独立19次开发标签读。
- 新MRI、model/GPU forward、训练更新0。
- 两种 GT oracle 支持：missing前景、RC半径2**体素**包络。
- 保留原 physical_mr trilinear 正支持、PATCH64×128×128、原排序/batch2。
- 生产 `7b4755` exit0，44.6145s；独立 `7ad831` exit0，41.3296s。
- 独立采用 transpose/flip 标签、Fraction 中心邻居 Boolean OR、独立 tile/cost；核19 series、38支持、806单层记录全部一致。
- 前景 N总572/k170，患者等权条件forward节省60.68%；包络k175、59.14%。
- 18/19有条件复用，但5个同支持候选含初始化仅17/19严格省：
  - 001第二：8/8失效，比例1.2，永远无法摊销省算。
  - 009一series：24/30，比例1.0，至少6候选才严格省。
  - 001第一：6/8，比例.95，至少5候选才省。
- 001第二包络仅0.0675% native FOV仍全batch失效，面积不能代表成本。
- 单层全部分开3556调用 vs 一次联合175，**不同动作数/输出，不能称20倍速度**。
- GT支持非部署ROI、非效益上下界，未测实际MRI差分、速度或Dice。

新增核读3篇正式会议原文：

```text
literature/2026-10-07_spatial_compute_primary_reading.md
literature/spatial_compute_reading_provenance_2026-10-07.json
literature/source_cache/spatial_compute_primary_2026-10-07/
literature/source_cache/spatial_compute_sbnet_2026-10-07/
```

SACT2017、DynConv2020、SBNet2018；30 PDF页取得、三篇主文1–8全部文字核读、7关键页视觉核看。SACT/DynConv refs9–10已看，SBNet refs9–10未读；补充/作者复现未做。

区域门控、预算loss、预测mask、block/halo及cache已有前例，不单独当创新。SBNet Table7主网33.1ms+PSP3.2ms，Dense88ms，加总约2.424×，主网单项2.66×；只是表格算术非复现。保留其.88×单层减速、AP下降、Figure3 stride/overlap含混；DynConv Table2 caption2-stack/首row4-stack不一致保留。

下一阶段需纳上一轮 post-manifest appendices：

```text
SESSION_FINAL_TOOL_OBSERVATIONS_REAL_SUPPORT_2026-10-07.json
SESSION_POST_ARCHIVE_REAL_SUPPORT_UPDATE_2026-10-07.md
SESSION_CHECKPOINT_RECEIPT_REAL_SUPPORT_2026-10-07.json
SESSION_OBSERVED_EXITS_FINALIZE_REAL_SUPPORT_2026-10-07.json
experiments/finalize_real_support_checkpoint_2026_10_07.py
```

实际最终回复已在79文件内，无需再重复纳。

## 当前轮：方向、已查证事实

已公开更新：

1. 上轮是实质progress，本轮核原训练、查现存真实实验。
2. 查到19series label roundtrip已经完成，**不要重复**。
3. 转向：GT oracle节省可能高估部署空间，检查冻结 observed-only ROI 对当前3D缓存成本。
4. 刚告知用户：新审计在预测数组读取前断言退出，失败保存，旧结果未改；交接标明接续点。

已有 roundtrip 完整结果：

```text
MC_RC_3D_LABEL_ROUNDTRIP_RESULT_2026-10-07.md
experiments/mc_rc_3d_label_roundtrip_v3_2026_10_07/attempt01.json
```

19开发标签、患者Dice .96783554/recall .96388237/absRVE .01734134；生产float32 strict仅14/19，hard全一致；float64解释器通过不覆盖原失败。不要重新做容易的标签往返。

旧 QDA 是 **16 series/8患者**，完全为当前19的子集，011/012/013没有旧预测。不是19：

```text
MC_RC_ANCHOR_QDA_CPU_PLAN_2026-10-03.md
MC_RC_ANCHOR_QDA_CPU_RESULT_2026-10-03.md
experiments/mc_rc_anchor_qda_cpu/run_contract.json
experiments/mc_rc_anchor_qda_cpu/attempt_01.json
experiments/mc_rc_anchor_qda_cpu/independent_anchor_qda_replay.json
```

- 固定方法 joint_QDA（唯一主）、appearance_QDA、coordinates_QDA、joint_LDA。
- observed MR和observed labels训练，整患者剔除7人训练；原posterior=.5、先验/shrinkage不调。
- 全部16的原ROI gates都失败，主joint_QDA前景覆盖0–.285974、边界0–.215342、患者观察Dice .006326948。这是**旧已知失败，不算新发现**，不能推导所有表示不可能。
- 原ROI：每缺层用两侧预测anchor masks并集，native面内物理disk扩张 **2mm**，同间隔3缺层共ROI。
- `roi_summary` 在 `mc_rc_native_competence_cpu.py:50`：
  `distance_transform_edt(~union,sampling=spacing_rc[:2]) <= 2.+1e-12`；union空则全零。
- 每缓存 NPZ 路径从旧 row `prediction_file` 取得，不猜文件名。
- 001首例：
  ```text
  experiments/mc_rc_anchor_qda_cpu/1.3.6.1.4.1.14519.5.2.1.10875952303942319530925289292568369177_anchor_predictions.npz
  file SHA 7b9003065f5bd56347a94800298912110e0afa95da779a25b6de7cfc7f97d91c
  ```
  joint/appearance/coordinates预测array SHA:
  `94350915ce4cbb8b18b3f12cde6fd34b4dc11e9326b278254590e424f0b21f75`
- 旧proof counts：16series、8patients、4methods、1216 fresh anchor classifications、864 missing targets。
- 主001首ROI空、coverage0。空ROI对应no proposed edit，不能当有效动作/无限速度。

MIRA旧机制线已查：

```text
MIRA_PUBLICATION_CLAIM_CANDIDATE_2026-10-01.md
PUBLIC_ONLY_CLAIM_REVIEW_STRESS_TEST_2026-10-01.md
```

有MSValid/ReMIND/UPENN上下文误差对齐证据，但仍未过可发表门槛，缺任务效益/可行动性/强新意；不能用旧候选重命名为本目标已完成。当前不转往简单扩无标签阳性队列。

## 当前新代码与失败：优先处理

已新建并执行，**不可静默修改执行过的源码**：

```text
innovation/MC_RC_OBSERVED_ROI_CACHE_COST_PROTOCOL_2026-10-07.md
innovation/experiments/mc_rc_observed_roi_cache_cost_2026_10_07.py
innovation/experiments/mc_rc_observed_roi_cache_cost_2026_10_07/attempt01.json
```

实际 `e28394` **exit1**，0.2239672s：

```json
{
  "complete": false,
  "errors": ["AssertionError: "],
  "cached_prediction_arrays_loaded": 0,
  "prohibited_access_attempts": []
}
```

**尚未读取失败 JSON 的 traceback，下一步先读它确定失败行。** 不猜原因、不改判成功。新MRI/GT/forward/update0。

该协议固定：
- 旧全部16/8和4方法，3缺失开发series单列not_available，不填0。
- 只读预测NPZ/metadata/旧proof，不读MR/GT/checkpoint，不分类或重训。
- 原2mm ROI映射当前 physical_mr 正支持、原tile/batch2，报告完整N/k、条件节省、5候选初始化、空ROI、原覆盖门槛交集。
- 原coverage只复用已核结果，明确**来源值而非新GT评分**。
- 2mm预测ROI不能与上轮2体素GT包络称同支持受控比较。
- sys audit hook限制workspace读取到显式metadata/predictions，记录prohibited路径；其他root库读允许。
- 计划独立核验：显式physical disk结构元素+binary_dilation代替EDT，Fraction Boolean resampling代替torch，独立成本/Fraction患者均值；coverage只核来源，不假称重跑GT。

**发现待修的源码设计问题（尚未执行修正）：**
`initial[:9]` snapshots按 `p.name+'.source_snapshot'` 保存，PREP与旧QDA结果都叫`attempt_01.json`，会碰撞覆写。新v2/attempt02应采用唯一相对路径编码或索引前缀，并保持失败v1原样。这不是当前断言原因的已证据判断。

源代码还检查：
- old/proof/result/contract SHA。
- 16/8与当前19 subset，8fold整患者排除。
- 当前与旧case的patient/UID/native_shape/spacing/affine/label_sha/map逐项精确相等。
- grid及tile_plan与上一真实支持结果相等。
- NPZ key set必须等于4 methods，数组bool、shape `(R,C,numanchors)`、array SHA。
这些任一断言可能是当前失败；看traceback再适应，不放宽科学合同。

## 下一步

1. poll99542，保留live handle。
2. 读失败attempt01 traceback，定位 assertion。核实际旧输入结构/精度/来源，不用猜测。
3. 保存失败源码/receipt；建新v2或attempt02，修正真实实现问题与snapshot碰撞，不静默改v1，不为通过删病例/改ROI配置。
4. 真正完成冻结 observed ROI 的新3D成本审计；如值得继续，执行独立disk/Boolean/Fraction核验。
5. 科学结论须区分：旧ROI覆盖失败、此次新成本结果、GT理想节省、真实任务收益。不能用廉价空ROI构造成功claim。
6. 当前轮所有公开更新、goal续作输入、失败/真实退出、结果和后续记录到innovation；本轮尚未建立session入口/manifest。
7. 新归档先核前1516 SHA，纳上轮post appendices，排除live invocation/history/resume。
8. 原训练完成后按原流程执行56FOV/6gates/strict，再资源资格、充分适配dense/direct/SR、合法ROI与真实差分/总成本、paired收益+cost/defer/union-greedy/random/LTT/Pareto、冻结后8确认。
9. goal保持active；上一轮progress。本轮已有失败实现与缺口定位，未成功实测，不能标complete或blocked。

## 读取问题记录

当前轮非科学读取错误需如实记录：
- `8ae6d2` exit1：PowerShell `rg innovation\*.md` 不展开，Windows路径错误；前面的handoff读取成功。
- `2260fa` exit1：猜了不存在的`..._predictions_before_label.json`；已通过 `b47576` exit0取得权威prediction_file路径。
- 大输出若截断不能当全文已读；关键QDA协议/结果已有足够范围，必要时小段重读。
