# 用户提供的接续摘要（原文归档）

以下为用户本轮提供的接续摘要，历史状态不代表本次最新状态。

## 目标与约束

目标仍 **active、未达成**：继续读论文、探索并验证，直到形成可发表且独立确认的 claim。用户要求所有新增研究、代码、证据、失败和公开对话保存到 `D:\MRI\innovation`。

- 工作区 `D:\MRI`，PowerShell。
- Python：`D:\conda\envs\MRI\python.exe`。
- **不使用 GPU，不操作用户终端训练，不读 locked IXI test，不改根 `.gitignore` 或环境，不新建/委派代理。**
- 依据真实 process poll 判断状态；观察超时不代表终止，不能据此重启。
- 当前续作尚未归档公开消息与阶段总结；不要因 checkpoint 暂停或完成 goal。

## 上一完整阶段：已完成，勿重跑

实际 exit0：

- 原完整队列 **83910**：322/322 条件，45 CISS 主患者＋1 TSE 次要患者；46 人重建独立再生成及保存任务输出指标核验完成。
- 后续队列 **56604**：112 真实筛选端点、5,000 共享患者 bootstrap、组成和四目标恒等式复核，errors=[]。
- 新完整统计复核：**58 条**主终点/固定敏感性，独立标量 bootstrap，errors=[]。
- 残差相加探索 **85839** 与独立复核 **96195**：全部完成。

原合同 SHA256：
`061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5`

**关键科学结果：原负向主假设被反证，必须停止。**

HAT−pipeline PCHIP：

- 支持 NMSE：`−0.0002450110095`，95% CI `[−0.0002752372654, −0.0002170491329]`；45/45 改善。
- 原 JSON 完整体积 Dice：`+0.03638170404`，CI `[+0.007181221983, +0.07198061880]`；26 改善、16 降低、3 相同。
- 原预写判据要求 NMSE 与 Dice 两个 CI 上限均负，因此失败。**不能换 SwinIR、raw 基线、标签或子组挽救主 claim。**

平均 Dice：

| native | raw linear | raw PCHIP | pipeline linear | pipeline PCHIP | HAT | SwinIR |
|---:|---:|---:|---:|---:|---:|---:|
| .90743931 | .70204741 | .74459750 | .56211897 | .65476150 | .69114321 | .63913396 |

HAT−raw PCHIP 次要 Dice `−.053454294`，描述性 CI `[−.099770378, −.015642155]`。基底处理影响比较方向，但不能单独归因缩放、裁剪、抗混叠或冻结评估器响应，也不能升级成原主要确认。1 mm 边界带敏感性 CI 跨0；RT 主 Dice 同正方向。

112 行中13行有点估计反号，包含标签/full/slab重复敏感性；**主 HAT−pipeline PCHIP 两标签没有反号**。区间未 familywise 校正，不能宣布确认排名反转。

固定残差相加：
`raw_PCHIP + (HAT − pipeline_PCHIP)`，alpha1、无新 clip。
旧 MC-RC001/002/004/005/006＋已见训练例 VS-SEG001，共297缺层；仅004/005两项通过≥0.1dB收益＋两病灶误差守卫，**2/6，固定配置停止**。全部另一相加次序 float32 SHA、四条件 ROI/dot-product/math.fsum独立复核通过。无新神经推断或任务 Dice。

上一阶段新增两篇正文、26题名、4重点摘要、139相关块、PDF0：

- Morshuis/Hein/Baumgartner，arXiv **2508.18975v2**，DOI `10.1109/TBME.2026.3679957`：七方法、两膝 MRI 数据集；每重建输入训练对应 segmenter，已有图像/任务分离与强简单基线先例。
- Wu等，DOI `10.1038/s44303-025-00076-0`，PMC11981920：综述，不是独立方法成果。
- Giannakopoulos MRM正式条目为既有预印本重复，不算新正文。
- Küstner DOI `10.1002/mrm.30030` 原正文仍缺；不要重复403/401路径。

旧 native/QDA 两分支均0/16保护ROI、旧岭失败、收益/误差线性等价、MIRA线性伙伴反证均保留。新方法确认患者仍0。45 CISS现已见结果，不能再当未来方法未见确认集。

上一阶段归档 **28项静态检查＋补记后4项同步检查全部exit0**：
1139文件阶段manifest；全局29 PDF、1907 evidence files、2178本地链接，errors=[]。

入口：

- `README.md`
- `INNOVATION_DECISION_AFTER_COMPLETE_COHORT_2026-10-03.md`
- `SESSION_HANDOFF_COMPLETE_COHORT_2026-10-03.md`
- `VS_SEG_COMPLETE_EVIDENCE_RESULT_2026-10-03.md`
- `VS_SEG_SELECTION_SENSITIVITY_REAL_RESULT_2026-10-03.md`
- `RESIDUAL_ADDBACK_CPU_RESULT_2026-10-03.md`
- `literature/2026-10-03_task_utility_fulltext_reading.md`
- `SESSION_ARCHIVE_VERIFICATION_COMPLETE_COHORT_2026-10-03.json`

## 当前续作：新 CPU 实验已启动，先实际 poll

**session 5040**，最后实际工具返回仍 live、无输出：

```powershell
D:\conda\envs\MRI\python.exe -B innovation\experiments\vs_seg_resampling_order_cpu.py
```

**不能重启，不改运行脚本/合同。**

新文件：

- `VS_SEG_RESAMPLING_ORDER_CPU_PLAN_2026-10-03.md`
- `experiments/vs_seg_resampling_order_cpu.py`
- 输出目录 `experiments/vs_seg_resampling_order_cpu/`
- 合同 `run_contract.json`
- 进度/结果 `attempt_01.json`
- 每患者 `<patient>.json`

新问题：解析基线的差异是否包含**实际显式裁剪**及 **PCHIP 与面内重采样顺序**效应。全固定45已见 CISS、全部内部缺层，两标签；结果后开发诊断，不是新确认，不复活原主张。

两插值核各三条件：

1. 既有 raw linear / raw PCHIP。
2. 既有 pipeline linear / pipeline PCHIP：观测层先缩256，再插值，再恢复原网格。
3. 新 post_resize linear / PCHIP：原网格 raw 插值后，按同 observed min/max、`span+1e-8`归一化，缩256、显式clip[0,1]、恢复原网格。真实 anchors 和尾部逐位保留。

四既有解析输出必须匹配旧字段 **`reconstructed_array_sha256`**，180体积逐位重放；90新post体积。只解析处理，**0新神经/任务推断**，CPU一线程、自己below-normal、15GB磁盘/8GB内存门槛。

保存：

- 所有层支持/两病灶 SSE、分母及两加权 NMSE。
- before/post显式clip实际改变像素/层及越界幅度。
- pipeline−post的float64差异、ROI差异NMSE与max。
- 线性解释阈值预写：全患者max归一化order差≤`1e-6`；PCHIP报告超过人数。
- 36描述性端点：两核×三域×两权重×三比较：
  `post−raw`、`pipeline−post`、`pipeline−raw`。
- Bootstrap seed **20261031**，5,000draw，45患者等权；不作familywise成功claim。
- 分解是描述恒等式，不是因果中介分析或新理论。
- 原图像NMSE沿用旧runtime **float32差后float64归一化**；order差单独用float64，两者明确区分。

**新独立 verifier 尚未写、尚未执行。**
计划用既有独立Hermite PCHIP/显式linear、逐层ROI dot-product、math.fsum、另种post构造、标量bootstrap/手写分位复核；共享native解码/网格/resize/RNG，独立性限制要写清。

## 当前续作：新文献查询已完成，但尚未读结果

新查询 session返回 **exit0**，无需重跑：

```powershell
D:\conda\envs\MRI\python.exe -B innovation\literature\search_resampling_order_2026_10_03.py
```

文件：

- `literature/2026-10-03_resampling_order_search_plan.md`
- `literature/search_resampling_order_2026_10_03.py`
- `literature/source_cache/resampling_order_search_2026-10-03/attempt_01.json`
- 三原始 `.response` 文件及hash。

返回题名数 **3＋12＋12＝27**（含可能重复/无关），报告总hit数3/49/32。**还没查看题名或摘要，更没有新正文阅读，勿提前计阅读数量。**

三查询：

- MRI＋interpolation＋partial volume/resampling＋segmentation/lesion。
- MRI＋SR/reconstruction＋preprocessing/resampling＋image quality/segmentation。
- resampling/interpolation＋radiomics＋reproducibility。

每次30秒、索引5MB、公开来源，不重试受限publisher；下一步按直接相关程度选正文，不凑数量。

## 本轮尚需归档的公开助手消息

1. “上一轮有实质进展：完整队列反证了原主假设，新的残差相加对照也已验证失败。我会接着查清输入处理怎样影响任务比较，并寻找能区分原因的下一项实验；所有新记录继续放在 `innovation`，不操作 GPU 或终端训练。”
2. “下一项先做解析对照：对同一缺层图像分别‘先缩到 256 再插值’和‘先在原网格插值再缩放’，同时检查裁剪是否实际改动了像素，并用线性插值作解释对照。它可以帮助判断 PCHIP 的处理顺序是否影响结果；这一轮先不重跑分割网络。”

## 明确下一步

1. **实际 poll session5040**；检查失败/完成，不能凭历史状态重启。
2. 读取新27题名/摘要，查重复，选择直接相关公开正文并实际核读、保存provenance。
3. 写并执行新全45解析顺序独立 verifier；保留任何失败首记录。
4. 全45和proof完成后再核读clip/order及全部36端点；判断是否有足够差异值得另写任务控制或独立来源验证。图像结果不能替代Dice/临床因果。
5. 继续朝可发表且独立确认claim推进；目前没有这样的claim。
6. 本轮报告、公开对话、手交接、入口和静态manifest更新到innovation。上一阶段32检查不用无理由重跑；新入口若改变历史共享README哈希，按已有同步模式更新。
