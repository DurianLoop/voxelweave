## 目标与约束

- 持续目标仍 **active**：研究、探索、验证直到形成可发表 MRI claim；**尚未达成**。不能把输入资格、合成例子、论文阅读或特征成本当病灶收益。
- GPU 已授权；**不动用户终端训练进程**，不重启／迁移原训练、不枚举／控制其他 PID、不委派代理。
- 所有新增文件仅写 `D:\MRI\innovation`。根 `.gitignore`、`environment.yml` 不改。
- **已执行／已绑定／已冻结文件不得覆盖**；修复另存 version/attempt。
- PowerShell；Python `D:\conda\envs\MRI\python.exe -X utf8 -B`，脚本命令末尾 `exit $LASTEXITCODE`。
- 开发11患者／19series；已见验证4／9，确认8／12、locked IXI关闭；旧MIRA/MSValid84保留。fresh calibration只约束正式风险保证。
- PDF技能已读／使用；portable阅读器可用。无自动审批拒绝。

## 首先接续原训练

**先 poll 原 live session `99542`，不要重启。**

最新直接观察 **`391f13`**：

- native **18612**
- invocation02 new **18513**
- cumulative **42369.654485999956s**
- 仍返回同 live session，无 terminal exit。

GPU最新 **`beb3d9=0`**：

- `2026/10/08 03:33:14.857`
- free **1394 MiB**／total24455／util85%
- 未满足新增GPU作业8GB预留。

原训练仍native顺序进行，另一raw-PCHIP臂尚待。各19998／总39996、CPU4／interop1、float32、共同初始化／监督／增强、AdamW lr/wd=.0001、30h／8GB储备／250MB合同不变。**真实两臂final exit0且最终冻结后**，才退出receipt→原56完整FOV→全部6能力gates→独立strict。不能用中间loss或新输入资格跳过；旧direct absolute失败不以浮点解释覆盖。

## 已完成并归档，勿重复执行

### 1. 共同投影阶段

入口 `SESSION_RESULT_COMMON_PROJECTED_2026-10-08.md`。

- 19series共同投影资格／独立v2通过。
- 新direct与旧direct完整输入 **19/19逐位相同**；availability相同。
- 新增控制为common projected dense-PCHIP，direct训练臂去重。
- 原理想float64坐标独立失败保留；v2明确float32坐标、未放宽容差。
- 42 observed加载事件；神经／GPUforward／训练更新0。
- 原累计3409冻结证据已经后续归档核过。

模块：
`experiments/mc_rc_common_projected_observed_2026_10_08.py`

### 2. 观测留出阶段

入口 `SESSION_RESULT_OBSERVED_HOLDOUT_2026-10-08.md`。
archive **`d3d033=0`**，270阶段文件，新增278，累计 **3687**；后续已核SHA不变。

- 固定两fold，首末保留，内部奇偶层各留出一次。
- **先mask，再retained统计／投影／预测**；reference预测之后才进入评分。
- 19series／38真实fold；生产38和独立v2的38 counterfactual通过。
- 改heldout值+10000，source／完整预测SHA不变，reference／score变。
- 总observed加载 **41=19+3+19**；检查事件81，唯一fold只有38。
- 原独立 **`628031=1`**：2完整series／5fold／3包，第3series fold1统计exact失败。
- 原因是C-order copy与fancy-index布局归约次序；另存布局v2，**`3a3097=0`**。C-copy后exact，独立中心矩1e-12；插值容差3e-5不变。
- 独立bilinear样点最大误差 `1.0306754507638516e-06`；完整linear／PCHIP预测数学误差约 `4.7683716e-07`。
- **18/19series、10/11患者 PCHIP留出MSE较高**。
- 患者内series等权、患者等权：
  - linear `0.2847022968272982`
  - PCHIP `0.2865475078664227`
  - 差 `0.0018452110391244947`，**+0.6481194776745369%**
  - 唯一负差VS-MC-RC-007：`-0.0003414936597077589`
- 不选择winner；留出改变层距／输入量，评分含背景，不能推出x4缺层或病灶收益。原部署全部合法observed统计本来合法。

重要文件：

- `OBSERVED_HOLDOUT_FEATURE_RESULT_2026-10-08.md`
- `OBSERVED_FEATURE_TO_ACTION_UTILITY_PREPARATION_2026-10-08.md`
- `experiments/observed_holdout_feature_table_2026_10_08.json`
  - 19行、**17个有限数值特征**
  - MRI任务标签、action utility、full action cost均 **null**
- `experiments/observed_holdout_feature_summary_2026_10_08.json`
- 原production、失败、layout-v2各attempt01 JSON与源均保留。

Noise2Void／Noise2Same主文阅读：

- N2V arXiv1811.10980v2：文字1–8、视觉5／8；第9页未读。
- N2Same官方Paper：11页文字全读，视觉2／5／7。
- 本阶段相关新论文2、文字19页、视觉5页。
- 错误ID2010.12062为28页铁电晶体管论文，只看首页排除；获取失败等留存。
- 单独Supplemental当时未读，已在下一阶段补完，**不要回改历史receipt**。

### 3. 最新：真实特征成本与直接先例补读

入口 **`SESSION_RESULT_DEPLOYMENT_FEATURE_COST_2026-10-08.md`**。

- record **`121a19=0`**
- archive **`0af306=0`**
  - 62 stage文件／**4,696,633bytes**
  - 新绑定72／**5,806,235bytes**
  - 累计 **3759**冻结证据
  - 前3687 SHA不变，链接／source bindings通过。
- finalize **`61db12=0`**
- receipt：
  `SESSION_CHECKPOINT_RECEIPT_DEPLOYMENT_FEATURE_COST_2026-10-08.json`
  - 3831bytes
  - SHA `24dd2e3a0780faeb01a92f955baab23fb034acc405b2ab11f25346b56fdd4bc6`

manifest：
`literature/deployment_feature_cost_stage_manifest_2026-10-08.json`

proof：
`SESSION_ARCHIVE_VERIFICATION_DEPLOYMENT_FEATURE_COST_2026-10-08.json`

#### 实际成本作业

- launch **`70e946`** session90875，terminal **`3a6af2=0`**，已经结束，不重跑。
- 一次19observed包、38fold；CPU1／interop1／BLAS1、CUDA不可见、below-normal。
- 无warmup／重复／counterfactual／重复Hermite。
- 全17特征、完整fold scores／统计 **19/19与冻结结果exact**。
- **cold child启动→imports→全部输出→退出：23.848797200014815s**
- 显式生产相位子集：**19.37797900068108s**
- series含资格／GC／审计合计：21.491694600554183s
- 患者合并series后等权生产相位均值：**1.761634454607371s**
- 患者相位范围：0.18639640044420958–6.635758099844679s。
- 两预测相位11.8612292s；source2.4882751s；评分2.5775016s；reference1.2885255s；IO1.1612208s。
- 19.378s只是显式子集，未分配开销含少量生产和资格工作；不能当完整端到端cost。
- 23.85s含资格检查，缓存状态未控制、原系统负载存在；不是GPU速度或全动作／task费用。
- 原108.467s是旧资格三作业总时，不作为部署成本。

文件：

- `DEPLOYMENT_FEATURE_COST_RESULT_2026-10-08.md`
- `experiments/deployment_feature_cost_summary_2026_10_08.json`
- `experiments/measure_deployment_observed_feature_cost_2026_10_08.py`
- `experiments/launch_deployment_observed_feature_cost_2026_10_08.py`
- 各 `deployment_observed_feature_cost.../attempt01.json`／launch receipt
- metadata独立核验 **`e07897=0`**，仅重核JSON、17特征、时间边界和fsum患者聚合，**不是第二次墙时或独立MRI插值**。
- 本阶段医学加载19，神经／GPUforward／训练更新0。

#### 新原文与已有方法碰撞

文件：

- `literature/2026-10-08_downstream_segmentation_and_proof_reading.md`
- `literature/2026-10-08_relative_utility_collision_recheck.md`
- `literature/deployment_feature_cost_reading_provenance_2026-10-08.json`
- 缓存 `literature/source_cache/downstream_feature_cost_primary_2026-10-08/`

获取：

- **`cfa74c=0`**：Crossref精确题名、EuropePMC（0命中不代表不存在）、官方N2Same Supplemental。
- **`0ed60a=0`**：arXiv精确title Atom找到 **1911.12239v3**，不是猜ID。
- Prakash *Leveraging Self-supervised Denoising for Image Segmentation*
  - DOI **10.1109/ISBI45749.2020.9098559**
  - v3，2020-03-19，5页全部文字，视觉1／3。
  - 已有denoise→适配seg、N2V权重finetune、finetune sequential。
  - microscopy／Gaussian／AP和SEG，无MRI。
  - 表有部分高标注量格不占优，不能照摘要说所有格改善。
  - 阈值在哪个split优化未清楚，不指控测试泄漏也不当本项目确认规则。
- N2Same官方Supplemental：4页全文字、视觉1／2；Figure5第4页只文字／图注，未视觉；不重计新论文。
  - AppendixA Eq16→17使用 `Var(X|Y)≤Var(X)=1` 点态推断，边际归一化不能一般推出。
  - Fraction诊断 **`f45139=0`**：
    - Y=0概率19/20，Y=1概率1/20
    - ε|Y0=0；ε|Y1对称±sqrt(381/20)
    - X=Y−1/20+ε
    - VarX=1；平均条件方差381/400=.9525
    - 条件均值方差19/400=.0475
    - Var(X|Y1)=381/20=19.05
  - **只否定这个一般推断，未证明完整Theorem1错误，不是新定理或MRI证书。**
  - BSD68 λinv实际改0.95而非默认2。
- 当前新增独立论文 **1**，Supplemental **1**，新文字页 **9**，视觉 **4**。

已有原文有限复读，不重计新论文：

- **`88e05b=0`**：
  - Madras *Predict Responsibly*，physical3 Eq3：gate预测双方谁loss低，直接覆盖相对收益动机。
  - Mozannar／Sontag *Consistent Estimators for Learning to Defer*，physical2 Eq1：一般classifier/expert成本。
- **`90d225=0`** SafeRestore TXT 1-based347–401、1265–1277：
  - 六deployment可见特征包括entropy、回投影MSE、raw/action detector差异等。
  - 全候选／detector输出先生成，明确不假设效率或latency／energy优势。
- 4862a1、f08ac7输出截断只用于定位，不计完整MoEDiff原文复读。
- 方法结论：`G_a=C_0−C_a`，最大条件期望收益与最小条件成本等价，**已有cost-sensitive/defer**。收益头本身不能作为算法首创。

## 当前科学决策

最新准备：

`TASK_ADAPTED_ACTION_UTILITY_NEXT_PREPARATION_2026-10-08.md`

- 强对照必须加入**两路径条件成本／错误率头及cost-sensitive／learning-to-defer**，不能只胜过baseline-only uncertainty。
- Same observed、总head容量、监督、整患者split、动作集合和全部实测成本。
- SafeRestore六特征双风险排名也需实质对照，探索／所有候选费用计入。
- 连续E[ΔQ]回归与`gain>0`分类不同，要事前定义。
- **head-only LOPO不等于整个pipeline患者外**：若task checkpoint训练见过全部11开发患者，label应标开发内。完整pipeline患者外需fold-specific任务训练及其成本；尚未执行。
- 候选定位为待验证MRI机制／应用结果，非新收益头算法。需强适配后真实净收益、完整成本和冻结确认；无余量则保留负结果。
- 现阶段没有任务label／效应量／完整动作cost／确认。

## 当前新阶段：只开始，尚未写新文件

最新用户自动要求继续goal，本轮公开进度：

> 我会继续补齐正式实验的准备，先确认原训练状态。这一阶段重点检查：两路径成本预测与收益头如何用同一份患者配对标签公平比较，以及哪些标签能算真正的患者外结果；能在 CPU 上核验的接口和分组规则先落地。

已经poll／读取最新准备、旧三臂矩阵、文件列表。**下一步先检查已有执行器，避免重复实现或重复合成检验**：

- `experiments/patient_risk_cost_baseline_executor_2026_10_07.py`
- `experiments/qualify_patient_risk_cost_baseline_executor_2026_10_07.py`
- `experiments/verify_patient_risk_cost_baseline_executor_2026_10_07.py`
- 已有输出：
  - `patient_risk_cost_baseline_executor_qualification_2026_10_07/`
  - `patient_complete_series_panel_qualification_2026_10_07/`
  - `patient_complete_series_panel_rounding_qualification_2026_10_07/`
- `experiments/task_gain_target_cpu_2026_10_07/independent_boolean_cost_replay_attempt01.json`
- 搜索相关既有target／cross-fitting／label接口源码，再决定真实缺口。

可推进方向：将未来真实患者配对标签连接、task checkpoint训练患者role、整患者分组、同信息两路径cost vs gain对照做成可审查接口／必要的有意义核验。**不能制造MRI收益标签，也不能重复既有合成证明充作新进展。** 若更必要的准备缺口存在，优先它；原强模型final依赖不跳过。

## 下一次归档要纳入最新post appendices

3759主manifest之外，以下已创建／真实退出，应下一阶段一并绑定：

- `SESSION_FINAL_TOOL_OBSERVATIONS_DEPLOYMENT_FEATURE_COST_2026-10-08.json`
- `SESSION_POST_ARCHIVE_DEPLOYMENT_FEATURE_COST_UPDATE_2026-10-08.md`
- `SESSION_CHECKPOINT_RECEIPT_DEPLOYMENT_FEATURE_COST_2026-10-08.json`
- `SESSION_OBSERVED_EXITS_FINALIZE_DEPLOYMENT_FEATURE_COST_2026-10-08.json`
- `SESSION_DELIVERY_DEPLOYMENT_FEATURE_COST_2026-10-08.md`
- `SESSION_PREPARED_FINAL_REPLY_DEPLOYMENT_FEATURE_COST_2026-10-08.md`
- `experiments/finalize_deployment_feature_cost_checkpoint_2026_10_08.py`
- 前manifest／proof。

prepared reply与delivery SHA相同：
`b65686673f4356b9345879149011fd3db2ea63af9cde62941dae81516e9891df`

## 阅读器、网络与根SHA

- 可用portable runtime：
  `innovation/tools/blindspot_pdf_reader_v3_2026_10_08/site_packages`
  - pypdf **6.19.0**
  - pypdfium2 **5.14.0**
  - 官方wheel SHA核过，文件已在旧冻结链。
- 无需安装／复制runtime、不改MRI环境。
- 默认沙箱Schannel出现SEC_E_NO_CREDENTIALS；公开GET已用 `require_escalated` 自动审批成功，无拒绝，TLS验证未关闭。
- GET用Windows curl Schannel、`--noproxy *`、bounded time/bytes，新attempt保留失败；不重试OpenAlex429／旧MiKTeX AppData路线。

根不变：

- `.gitignore` `7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524`
- `environment.yml` `dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257`

医学作业通常CPU1／interop1／BLAS1、CUDA不可见、below-normal、1200s、8GB RAM／disk余量、≤20MB输出。上次实际disk约8.45GB（余量较紧，勿删旧证据或用户文件）。当前阶段预算尚未另定。goal保持active；前两轮都是实质progress。
