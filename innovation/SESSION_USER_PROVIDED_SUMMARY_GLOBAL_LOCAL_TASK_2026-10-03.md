# 用户提供的接续摘要原文

以下是用户本次消息中的摘要；它描述此前工作和当时进程状态，不能当作当前新验收。

目标仍 **active**：持续研究、探索、验证直到取得可发表且独立确认的 claim。尚未达到。上一 goal turn 属于 **progress**：完成两个 CPU 训练反例、四篇正文及独立复核；本轮又已启动更强训练并完成验证输入证明。用户现在要求 compaction，**不是暂停或取消研究**。

### 约束

- 所有新增内容写 `D:\MRI\innovation`。
- Python：`D:\conda\envs\MRI\python.exe -X utf8 -B`。
- 不用 GPU，不枚举/操作用户终端训练，不读 locked IXI test，不改根环境或 `.gitignore`，不创建/委派代理。
- 数值进程 CPU 单线程、自身 below-normal priority；磁盘 ≥15 GB、可用内存 ≥8 GB。目前约17.50 GB磁盘、110 GB可用内存。
- 不重启已完成或仍 live 的任务。来源/软件/归档核验不等于科学确认。
- 旧45 CISS和既有开发患者不能用于未见确认；患者角色不得根据效果调整。

### 上轮完成，勿重跑

入口：

- `SESSION_HANDOFF_SPARSE_TASK_TRAINING_2026-10-03.md`
- `SPARSE_TASK_CAPABILITY_AND_MATRIX_NEXT_PREPARATION_2026-10-03.md`

四篇正文/393实际文字块已登记。19开发输入证明完成：354 observed planes、76输入条件、19标签轴，隐藏MR未解码。

两次122,609参数小网络训练各4000updates：
- 10人18系列，013整人留出：012训练内PCHIP full Dice `.010724`，013 Dice `0`。
- 单012重新训练：full `.555150`、missing `.557284`、体积误差1.3602%，但边界/位置失败。
- 全部指标、物理cKDTree距离与15完整plane checkpoint重放通过；两项能力门槛均失败。
- 8000真实updates、13,779总forward调用，科学确认0。
- 上轮107文件stage和全局归档四检查全部exit0。该旧验收**不覆盖本轮新增文件**。

### 本轮最关键：训练 session44473仍 live

**下一步先poll44473，不能重启。**

预写协议：

`MC_RC_GLOBAL_LOCAL_TASK_CPU_PLAN_2026-10-03.md`

实现：

- `experiments/mc_rc_global_local_task_cpu_support.py`
- `experiments/run_mc_rc_global_local_task_training_cpu.py`

真实结果持续更新：

`experiments/mc_rc_global_local_task_training_cpu/attempt_01.json`

最后实际观察：
- live session **44473**
- `updates_completed=4400`
- `complete=false`, `errors=[]`
- 训练开始 `2026-10-03T00:24:18.856471+00:00`
- 第4400步elapsed `653.243s`，最后100步total/local/global loss约 `[1.45037,.94427,1.01219]`
- 981,602参数，RAM cache `1,934,265,736`字节。
- 合成10步预检每步 `.136257s`，通过。
- 当前训练预计总约45–50分钟；**不得依据loss中途改预算、架构或选checkpoint**。

固定训练：
- 全部11开发人19系列，随机初始化，seed20261004。
- 20,000updates，AdamW `.001→.0001` cosine、wd `.0001`。
- raw PCHIP + observed_shared，observed-only，无隐藏/native MR。
- 平面约.5mm重采样；5通道物理z偏移−2/−1/0/1/2mm。
- 全FOV256分支通道8/16/32/64/128；局部128分支16/32/64/128；全FOV8features+1logit作为局部上下文。
- 每update均匀patient、均匀series；z半前景/半全域；同z两个patch（前景/随机）；标签只作训练监督和采样。
- BCE+Dice local + `.5` global辅助loss。
- 最后checkpoint固定阈值.5；全FOV规则tile stride96，概率映回原生后评分。
- 这是既有coarse-to-fine思想的**任务能力基线，不是新方法claim**。
- 无中途验证；验证效果须最后weights冻结后才能开。
- 推断/evaluator/新模型独立复核脚本 **尚未实现**。

### 4验证人9输入：生产和独立证明已完成

固定角色020/022/024/025，9系列，原角色不变。

新增：

- `MC_RC_VALIDATION_OBSERVED_INPUT_CPU_PLAN_2026-10-03.md`
- `experiments/mc_rc_task_roles_input_cpu.py`
- `experiments/prepare_mc_rc_validation_task_cases_cpu.py`
- `experiments/audit_mc_rc_validation_task_input_cpu.py`
- `experiments/prepare_validation_input_verifier_cpu.py`
- `experiments/verify_mc_rc_validation_task_input_cpu.py`

结果：

- `experiments/mc_rc_validation_task_case_preparation/attempt_01.json`
- `experiments/mc_rc_validation_task_input_cpu/attempt_01.json`
- `experiments/mc_rc_validation_task_input_cpu/independent_all9_observed_inputs_and_label_axes_attempt_01.json`

生产session51445已exit0，独立session94766已exit0：
- 145真实observed层、36输入条件、9标签轴全部通过。
- observed-only包累计32,901,121字节：
  `data/mc_rc_validation_observed_only/*.npz`
- raw linear/PCHIP × observed_shared/full_own，RAS/统计/label轴核验。
- 独立PCHIP最大差 `.00048828125`，容差通过。
- 未解码隐藏MR，torch未导入，新前向0，**验证模型效果尚未读取**。
- 独立算法复用旧19证明的Hermite/统计/轴实现，生成来源SHA保存于 `verifier_generation.json`；不要说全新完全独立代码。
- 新IO allowlist只11开发+4验证，确认/未分配拒绝。旧developer-only模块未改。
- 科学split仍未启用，尚须绑定最后checkpoint创建诊断split记录。

### 本轮新论文：两篇已获取，阅读未完成/未登记

检索：

- `literature/2026-10-03_global_local_task_search_plan.md`
- `literature/2026-10-03_global_local_task_selection.md`
- `literature/search_global_local_task_2026_10_03.py`
- 原始 `literature/source_cache/global_local_task_search_2026-10-03/attempt_01.json`
- 三查询各6题名，共18行；总命中10/10/12，**不是18全文**。

两篇JATS正文成功：

`literature/source_cache/global_local_task_fulltexts_2026-10-03/`

打印工具：

`literature/show_global_local_task_blocks_2026_10_03.py <stem> <begin> <end>`

1. **vs_cascade**，PMC11903922，DOI `10.1002/lary.31979`，50块。
   - **已实际读全部0–49**，尚未写阅读报告/登记。
   - 两级CNN，初预测mask与encoderfeatures指导第二级，已有直接VS级联/空间attention先例。
   - 公共242患者155/39/48；内部96患者72/16/8。
   - 关键：内部只取有可见肿瘤切面并按最大GT mask包围框裁剪；公共100×100×50mm box **centered on tumor mass**，不能自动当全FOV无标签部署。
   - 表2公共T2 3D `.81→.82`；内部T2 2D `.55→.51`，HD95 `32.03→32.14mm`，并非所有条件改善。
   - 表3attention有权衡：2D T2 RVE `22.77→27.47%`；2.5D T2 RVE `49.21→51.50%`；2.5D T1 HD95 `5.58→6.49mm`。
   - 参数明显增加；文章段45“over 2°ø”乱码，不擅自还原精确倍数。
   - 不能抄“所有架构模态都改善”的宽结论。

2. **olfactory**，PMC8473894，DOI `10.1016/j.neuroimage.2021.118464`，122块。
   - **已读0–65完整**；需继续66–121，不计全122已读。
   - 357训练/203内部test；12无可见OB、109同session两T2协议稳定性、30外部HCP。
   - 在1.6mm全FOV上学习ROI定位，预测centroid crop .8mm、96³；四组×三视图=12模型集成，不是单模型同容量对照。
   - GT定位监督用人工左右OB centroid，但**推断crop来自预测定位**，与上篇GT crop要区别。
   - focal+Dice，边界加权，40epochs，多视图；输入邻层/强度变换保持邻层一致。
   - 段53明确volume similarity可最高而空间overlap零：**我们上轮“体积接近但空间错误”不能当新规律**。
   - Average Hausdorff Distance定义为两方向平均距离的max，与我们pooled 6-surface ASSD不同；不要直接比较数值。
   - 尚需读结果、稳定性、外部与限制。

### 既有MC-RC原论文补读，不计新论文

DOI `10.3389/fncom.2024.1365727`、PMC11111906 已有旧阅读：

`literature/2026-10-02_cobrai_crossmoda_mc_rc_reading.md`

来源：

`literature/source_cache/cobrai_crossmoda_public_2026-10-02/kujawa_jats_attempt_01_paragraphs.json`

本轮实际补读 **39–50、64–69、74**（19块），未登记补读报告。

关键：
- 作者用 **nnU-Net v2**、nonzero crop、z-score、median-spacing resampling。
- 1000epochs×250 minibatches=250k updates/fold，batch2；5fold/2D+3D集成；不是我们此前失败的SC-GK UNet2d5模型。
- 表2MC-RC T2：MC-RC-trained291训练图/72测试图 meanDice85.0±15.6%；SC-GK-trained196图仅16.5±31.9%；combined85.2±14.1%。
- 表3该SC-GK-on-MCRC T2 medianDice0；作者明报完全漏检和undefined∞。
- 作者训练图/时点数不是独立patient数，不外推我们的11人或20k预算。
- 段69无残留病例单独评价；我们的保留集合只合格正标签，不能虚报无肿瘤检出能力。
- 这是有价值的域/训练预算先例，不能说新基线已达到作者能力。

### 下一步顺序

1. **poll44473并查看最新JSON**，继续原20k训练；不重启/不调参。
2. 完成olfactory66–121阅读，写两篇报告与实际锚点登记；MC-RC19块补读单列为复读。明确GT crop、T2失败、参数/集成/预算和volume先例。
3. 实现更强模型验证evaluator：绑定9输入独立证明、最后20k checkpoint/代码/协议/训练身份；仅4验证患者，两输入共18条件；原生full/anchors/missing/tail和物理边界/漏检/体积全部保留。
4. **避免导入两个设置torch interop线程的支持模块**：新global-local模块和旧 `mc_rc_sparse_task_cpu_pilot_support.py` 都执行 `set_num_interop_threads(1)`，双导入可能报错。将旧counts/surface与独立bincount/cKDTree函数抽取到新的纯CPU/numpy指标模块，保留来源SHA；不要编辑正在运行的support/协议。
5. 独立检验新物理z取样、full→local grid_sample位置/轴、概率回原生与coverage；最后模型每验证输入至少3完整z-plane重放，全部计数和cKDTree距离核验。直接重放仍引用同architecture，不称第二独立模型。
6. 训练实际exit且`complete=true`后才跑验证效果。能力门槛见协议：患者先聚合，4人mean full≥.70/missing≥.65/recall≥.70/absRVE≤.50，无系列全漏检；通过仅放行后续native能力/公平矩阵，失败则保留反例。
7. 保存本轮公开消息、这次compaction请求和新handoff，更新README/queue并新stage/global验收；**本轮这些尚未完成**。上轮archive不覆盖新增。
8. 原6×5/native控制/直接与随机分辨率公平对照/具体可观测修正/8患者最终确认仍未执行。目标不能complete或blocked。

### 固定患者角色

- 开发11人：001/002/004/005/006/007/009/010/011/012/013，19合格系列。
- 验证4人：020/022/025/024，9合格。
- 确认保留8人：030/029/019/028/031/026/027/015，12合格，**禁止开效果**。
- 总40合格/23已分配候选患者；旧39/18是历史生成错误。
- 同患者所有时点同角色，58共享VS-SEG整人排除。
- 科学确认仍0，尚无可发表且独立确认claim。
