# 用户传入的接续摘要（原文保存）

以下是用户在本轮提供的前模型接续摘要原文。其live状态和“尚未”措辞均指传入时点，不能覆盖本轮后续真实结果。

## 目标与约束

目标 **active，未达成**：持续读论文、探索和验证，直到获得可发表且独立确认的 claim。不能将软件复核通过或阶段完成当目标完成。

- 工作区 `D:\MRI`，PowerShell；Python `D:\conda\envs\MRI\python.exe`。
- 全部新增内容保存到 `D:\MRI\innovation`。
- **不用 GPU，不操作用户终端训练，不读 locked IXI test，不改根环境或 `.gitignore`，不新建/委派代理。**
- Python 用 `-X utf8 -B`；CPU 单线程、仅自己低优先级，既有 resource gate 为磁盘 ≥15 GB、可用内存 ≥8 GB。
- 必须实际 poll 判断进程状态；观察超时不是终止，不能据此重启。
- 本次用户要求 checkpoint compaction，不是停止目标。

## 正在运行：先实际 poll session 20644

```powershell
D:\conda\envs\MRI\python.exe -X utf8 -B innovation\experiments\vs_seg_post_resize_task_cpu.py
```

**最后实际返回仍 live：24/45 已完成并逐人通过独立保存预测复核。** 最近完成 VS-SEG-228；没有终止 exit code。

- 固定45已见 CISS，唯一新条件 `post_resize_pchip`。
- 原网格 PCHIP → observed-only 归一化 → 缩256 → 恢复原网格；真实 anchors/tail 保留。
- 相同官方冻结分割模型，一次 CPU forward/人；不重跑旧七条件。
- **不要编辑运行脚本、计划、verifier 或 run_contract 绑定的依赖。**
- 完成应为全45、18任务端点，以及 `independent_all_tasks_and_estimates.json`，最后实际 exit0。
- **尚未读取动态子集 Dice，不可提前分析新任务效应。**

文件：

- `VS_SEG_POST_RESIZE_TASK_CPU_PLAN_2026-10-03.md`
- `experiments/vs_seg_post_resize_task_cpu.py`
- `experiments/verify_vs_seg_post_resize_task_cpu.py`
- `experiments/vs_seg_post_resize_task_cpu/run_contract.json`
- 同目录 `attempt_01.json`、各患者 JSON/NPZ、`verification_<patient>.json`、`stdout.jsonl`。

18端点：两标签 × full/slab/排除参考1mm边界 × post−pipeline/post−raw/pipeline−raw；seed20261101、5000draw，描述性、未 familywise 校正。full/slab固定45；参考core为空时保留配对 undefined 名单，不填零。程序已包含逐患者独立混淆计数/完整网格物理边界复核和最终独立标量 bootstrap。

## 本次新探索：producer 已完成，独立 verifier 尚未启动

**session 34708 实际 exit0。**

```powershell
D:\conda\envs\MRI\python.exe -X utf8 -B innovation\experiments\observable_order_risk_cpu.py
```

新问题：仅由观测层构造的 PCHIP 顺序差，能否预测旧 pipeline 相对 raw 的任务损害。

文件：

- `OBSERVABLE_ORDER_RISK_CPU_PLAN_2026-10-03.md`
- `experiments/observable_order_risk_cpu.py`
- `experiments/verify_observable_order_risk_cpu.py` **已经写好，尚未运行**
- 输出 `experiments/observable_order_risk_cpu/`，合同、`attempt_01.json`、45患者 JSON。

固定规则：

- 全45均已见，纯开发诊断，科学独立确认0。
- 主候选 `order_rms`；次要 `order_max`，不能替换失败主候选。
- 三强比较：`raw_pipeline_rms`、`anchor_roundtrip_rms`、`pchip_linear_rms`。
- 各规则选信号最低15人使用 pipeline，其余使用 raw；平局按原名单，不调方向/预算。
- 评分使用旧 full Dice pipeline−raw，两标签；特征不使用缺层真值或标签。
- oracle按两标签效用较小值降序选15，仅作不可部署上界。
- 5000次无放回随机同预算，seed20261102。
- 主开发门槛：选中15人的双标签 Dice 均 ≥raw−.01；双标签均值均严格优于三个简单比较和随机97.5分位。
- producer最后输出：`main_candidate_development_gate_passed=false`，双标签guard合格患者 **16/45**。**尚未独立核验，尚未详细核读结果。**
- producer实际重放3条件×45=135旧体积；计划写180。新 verifier 已写为4条件×45=180（补 `pipeline_linear`），可完成计划覆盖；不要修改已冻结producer/计划挽救记录。
- verifier重算真实ROI dot-product、独立anchor归一化/roundtrip、fresh pipeline/post差、手写平均秩相关、固定排名/guard、随机分位；共享decoder/resize/RNG，限制写明；0神经推断。
- 下一步立即运行 verifier，保留首失败，不提前宣布科学结论。

## 上一阶段完成，勿重跑

解析处理顺序：

- session5040 producer、68788独立verifier均实际 exit0。
- 45 CISS、2,565缺层；180旧解析输出逐位重放、90新post输出另一构造SHA一致；36端点/ROI/标量bootstrap全通过。
- 显式clip四组合均0像素。
- linear最大归一化顺序差 <1e-6；PCHIP45/45超过，患者全图max差的 min/median/max 为 .00912657/.01387840/.01976109。
- PCHIP support pipeline−post NMSE `−1.21248932e−6`，CI `[−1.35359973e−6, −1.08947167e−6]`；pipeline−raw `−.000144102991`，均值比约 **.8414%**，仅描述分解，非因果比例。
- 双病灶两权重的平均顺序效应CI全部跨0。
- roundtrip使support NMSE45/45降低，但旧raw/pipeline PCHIP Dice .7445975/.6547615；不能只凭NMSE判断结构保护。

文献新增3篇正文、88实际重点锚点，41索引条目/39不同题名，PDF0：

- VINNA DOI `10.1162/imag_a_00180`：原网格特征旁路/latent插值/native分割已有直接先例。
- MR-Linac DOI `10.21037/qims-2025-aw-2151`：两同型系统ACR模体，非患者多厂商验证。
- Stability Atlas DOI `10.3390/jimaging12080392`：合成图像域研究，相关噪声/共变校准失败不能代替患者确认。
- 神经母细胞瘤 DOI `10.1148/ryai.230208` EFetch仅metadata/abstract，publisher禁止XML全文，未取得body；失败保存，不计第四篇，不重复受限路径。

上一阶段归档已完成：

- 30项静态同步＋补记后4项检查均 exit0。
- 新阶段manifest758文件；全局29 PDF、1929来源证据、2238本地链接，errors=[]。
- 第一张图legend重叠，首图/首代码SHA快照保留；第二版实际查看通过。
- 入口及公开对话已更新，但**本次 goal continuation 的新增内容还没有最终归档**。

入口：

- `README.md`
- `VS_SEG_RESAMPLING_ORDER_CPU_RESULT_2026-10-03.md`
- `INNOVATION_DECISION_AFTER_RESAMPLING_ORDER_2026-10-03.md`
- `RESAMPLING_ORDER_NEXT_VALIDATION_PREPARATION_2026-10-03.md`
- `literature/2026-10-03_resampling_order_fulltext_reading.md`
- `SESSION_HANDOFF_RESAMPLING_ORDER_TASK_QUEUE_ACTIVE_2026-10-03.md`
- `SESSION_ARCHIVE_VERIFICATION_RESAMPLING_ORDER_2026-10-03.json`
- `SESSION_ARCHIVE_FINAL_SYNC_RESAMPLING_ORDER_2026-10-03.json`

## 旧关键反证，必须保持

原合同SHA：
`061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5`

原完整83910/56604及残差85839/96195均已完成，勿重启。

- 原 HAT−pipeline PCHIP 主负向假设被反证：NMSE降低45/45，Dice平均 `+.036381704`、CI全正。**停止原负向claim，不能换基线/模型/标签/子组救它。**
- 固定残差相加仅2/6通过，停止该配置。
- MC-RC native/QDA/岭等旧失败保留；native完整16系列/8开发人，平均full Dice仅 .0678，11/16零TP，不能假定此冻结评估器能定位外部来源病灶。
- 45 CISS全已见，不能再当未来方法全新独立确认患者。

## 尚未执行的新想法

本次内部考虑了“空间带宽不一致”因素：保留的native anchors较锐利，插入层经down/up变平滑，可能形成沿z周期性纹理，影响2.5D冻结分割器。可用**只在诊断对照中也处理anchors**、保持所有缺层数组不变的控制区分它。

**尚无计划文件、脚本或实验，不得写成已验证结果。** 这种条件会改变观测层，只能是解释性干预，不能包装为满足原observed-preserving合同的新SR方法。先看全45post任务结果再判断值得执行与否。

## 明确下一步

1. 实际poll20644；继续等待全45，不能提前读新Dice动态子组。
2. 执行 `verify_observable_order_risk_cpu.py`，随后核读主候选、全部强比较/随机/oracle，保留失败并停止固定失败候选。
3. 全45post任务实际完成与18proof通过后，生成任务报告/CSV，判断顺序是否解释任务变化；保留两标签及全部反例。
4. 继续直接查新与可区分控制/真实未见来源准备，目标仍是可发表且独立确认claim，不满足于诊断或软件通过。
5. 本次新增实验、公开消息、进程实际状态、失败、接续、入口与manifest写入innovation。

本次尚需归档的两条公开助手消息：

1. “上一轮取得了实质进展：解析顺序实验完成并通过独立复核，新的 CPU 分割对照已启动。我会先核查该队列的实际状态，再继续查新和准备能区分原因的实验；新增内容继续归档到 `innovation`。”
2. “分割队列仍在运行，已完成 18/45 人。等待期间，我会验证一个仅用观测层可计算的候选信号：PCHIP 顺序差能否预测哪些患者会因处理而损失 Dice。它会与简单差异指标和同预算随机选择比较；这仍是已见患者上的开发探索。”
