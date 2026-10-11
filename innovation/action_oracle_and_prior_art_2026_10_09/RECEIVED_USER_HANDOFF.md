用户提供的接续摘要，保留为继承来源；以下不是本次重新执行结果。

## 目标与约束

科研目标仍 **active**：持续研究、探索、验证，直到得到可发表且独立确认的 claim。用户允许 GPU，所有新增只写 `D:\MRI\innovation`。

- 不动用户原终端训练，不枚举/操作其他 PID，不安装、不委派、不删除历史。
- PowerShell；Python：`D:\conda\envs\MRI\python.exe -B -X utf8`。
- CPU1线程/below-normal；RAM和磁盘各保留十进制8GB，既有stage allowance不降低。
- GPU启动空闲至少8192MiB；此前本进程10%allocator、peak reserved≤2.5GB，执行中free≥4GB。
- 强度/概率3e-6、坐标3e-12、二值零差，原六医学gate不降。
- 11开发患者/19series；4已见验证患者/9series。8未见确认患者/12series及lockedIXI保持关闭。
- 含全部11开发GT的19998parent只能用于开发能力诊断，严禁严格LOPO外折warm-start。
- 已绑定或执行的代码/旧归档不编辑；修复另版本。
- 无适用AGENTS.md；当前没有使用新skill。
- PowerShell传`python -c`中的双引号会丢失；用单引号here-string经stdin，或正式.py文件。

## 上一轮已完成、归档为7180

目录：`acquisition_action_generalization_author_2026_10_09`

- 优化参考完整542实际session31883→`4eaf2e exit0`，独立审核`59e97f exit0`。
- 图像逐位一致、全部强度误差0、坐标最大`1.1368683772161603e-13`。
- GPU checkpointed六分支：
  - v1 CUDA_VISIBLE_DEVICES被CPU工具改为-1，初始化前失败。
  - v2恢复GPU后触及10%allocator而OOM，未完成forward/backward。
  - v3实际session42442→`9897da exit0`，独立`09b462 exit0`。
  - 6forward/6backward、12完整million-voxel patch，固定一开发病例step2；peak reserved`2,334,130,176`bytes；optimizer更新0，权重不变。
  - 固定CPU synthetic原图与checkpointed图输出/loss/全部梯度逐位相同。
  - **未资格AdamW、正式训练、完整FOV推理或临床收益。**
- 已核旧6997全部SHA/bytes，追加183，冻结链7180。
  - `APPEND_INDEX.json` SHA `8cfc6bc2738b05f1a530ea42af3f502c2ea9d100a54776d53d03b6a864332f52`
  - `APPEND_PROOF.json` SHA `806dfe4a81ea42c1727cf482d4abc2cf504bcdc3c284596c07abee4801f6e018`
  - actual archive session28101→`1192c5 exit0`。
- 123个实际可用tool buffers已导出`ACTUAL_AVAILABLE_TOOL_RETURNS.json.gz`，264151压缩bytes。归档后工具、handoff等静态文件另存，下一增量需绑定。
- 入口：
  - `ROUND_UPDATE_2026_10_09_GPU.md`
  - `PROJECT_EVIDENCE_AND_NARROW_CLAIM.md`
  - `POST_ARCHIVE_HANDOFF.md`
- 末次整轮磁盘forecast短缺14,324,295bytes（GPU新增1MB已计），未启动正式新训练。

## 当前唯一长时间live

**session44317**，运行：

`full_certified_schedule_2026_10_09/qualify_full_real_pipeline.py`

从头完整35904字段，原2992schedule/5984geometries，两输入×三模式，不继承失败prefix。预算64800秒，forecast42538.72秒。

本轮开头已重新poll确认live。最新实际观察：

- tool chunk **e7abe6**
- 2880/35904，elapsed1595.48秒。
- 全强度误差0、坐标`5.684341886080802e-14`。
- 返回仍有session_id；**不是终态**。当前可能已进一步推进，先poll44317。
- live `full_real_pipeline_attempt01`全排除冻结归档。

终态后：

1. 保存`ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json`，附`observed_unified_exec_session=44317`。
2. 只有实际exit0且无session_id，执行 **`audit_full_real_terminal_v2.py`**。
3. v1 auditor错误期待启动字段`actual_unified_exec_session`；实际启动文件字段为`observed_unified_exec_session`。已准备独立v2，只改该key，原文件未改。准备实际`c1126d exit0`，尚未执行audit。
4. 不再poll早已结束31883/42442/65500/28101及更旧sessions。

## 本轮新目录与实质进展

目录：**`action_oracle_and_prior_art_2026_10_09`**，stage2MB，保留其他allowance16.8MB（guard总18.8MB）。

### 1. 现有两部署流程的精确oracle上界已完成并独立审核

源码：

- `diagnose_existing_action_oracle.py`
- `audit_oracle_upper_bound.py`
- `PROTOCOL.md`

实际：

- `abe05f exit0`，`existing_action_oracle_attempt01/receipt.json`
- 独立`206892 exit0`，`oracle_terminal_audit_attempt01/receipt.json`

只读旧完整FOV结果JSON及整数TP/FP/FN/TN，**MRI/GT/probability/model数组0**。

两个合法observed-input、同parent/2992预算动作：

- `raw_pchip_intensity`
- `raw_pchip_spatial`

全部4已见验证患者/9series，患者先均值。Fraction精确计数：

- 穷举16患者一致策略、512逐series策略。
- 哪怕GT逐series选最高Dice：
  - fullDice上界 **0.5545512725845162**
  - exact fraction `329214433836254638369892077542619 / 593659144089477854737724167075920`
  - 原gate0.70不可达。
  - 两种穷举的六gate通过策略都 **0**。
- 开发11患者/19series上界0.8847471928009376，仅训练病例描述。
- 独立审核用整数cross-product选max与75位Decimal求患者均值，误差<1e-70。
- 所有费用乐观置0，只作必要上界；不是净收益实验。
- **只约束这两个现有whole-series流程**，不约束新SR/TTA、局部融合或新模型；不是独立临床确认或可发表claim。
- 原receipt键`all_whole_series_selectors_can_meet_fullDice_gate`语义是feasibility flag，不能解读为“每个策略都能过gate”；独立audit已明确更正。

这改变下一决策：当前选择器救不了现有流程，优先补强普通任务泛化/实际动作集合。

### 2. 公开先例检索已终态

- `search_direct_prior_art.py`
  - session24344→`9673e8 exit0`
  - EuropePMC5组TITLE_ABS查询/pageSize8。
  - adaptive acquisition窄查询0；**不能证明新颖性**。
  - 找到dynamic expert routing及source-free active annotation。
  - `public_index_attempt01/receipt.json`及原responses gzip均保存。
- `search_crossref_direct_ml.py`
  - 实际`ad9f8e exit0`
  - `crossref_index_attempt01`。
  - 检出2015 *A robust adaptive sampling method for faster acquisition of MR images* DOI`10.1016/j.mri.2015.01.008`，及2022adaptive k-space RL DOI`10.58530/2022/2453`等。
  - 仅bibliographic检索，未读这些主文。
- 来源网络：urllib、验证TLS、`ProxyHandler({})`，此前正常；只公开关键词，不上传病例。

### 3. 新两篇正文文本已实际全范围读完，尚未冻结阅读provenance/综合笔记

已获取并核DOI/PMCID，实际`cc26fb exit0`：

1. **Dynamic expert routing with boundary-aware decoding for accurate brain tumor segmentation from incomplete MRI data**
   - DOI`10.1038/s41598-026-48187-x`
   - PMC13230987
   - key`routing`
   - 156提取块、14表、20display formulas。
2. **Source-Free Active Domain Adaptation for Brain Tumor Segmentation via Mamba and Region-Level Uncertainty**
   - DOI`10.3390/brainsci16030300`
   - PMC13023837
   - key`active`
   - 174提取块、8表、24display formulas。

原始XML/blocks/tables/formulas均gzip保存：

`primary_xml_attempt01`

使用`read_primary_ranges.py`，每次最多15000字符，完整输出没有阅读工具截断。范围receipt在`reading_ranges_attempt01`：

- routing：0→30→71→91→115→132→156
- active：0→34→80→120→137→164→174
- 全 **330提取块、22表文本**已实际读。
- 包括abstract、正文、图注、表、声明等，不等于330实验。
- **未读图像像素、外部补充材料。**
- routing20公式是GIF，只抽出编号，inline数学量也经常缺失；已查看原XML确认。**不能称完整公式阅读或填补P/k/T/学习率等符号值。**
- active24公式有MathML，正文flattened公式已读，但没有逐个全XML解读全部24式。
- `PRIMARY_SELECTION.md`解释选择与范围。
- 需要现在生成`READING_PROVENANCE.json`、findings和下一试验更新，别再重复计新主文。

重要读文结论：

**routing**
- 有top-k专家、LoRA、cross-modality KL/contrastive consistency、MC uncertainty decoder、boundary/curriculum的直接组合先例。
- BraTS缺对比模态，非本项目CISS缺层。
- 300epoch课程40%WT、30%WT+TC、30%全。
- 3fold×5seed，报告15配对t-test观测；不是15独立患者。
- Held-out fold兼validation/testing；early stopping描述73/75不一致，不能认证独立确认或内折选择。
- 数字差异要保留：
  - Table3/5 BraTS2019 full`.912/.878/.835`，Table11/abstract`.918/.889/.852`。
  - Table4/5 2020`.918/.884/.842`，Table12/abstract`.924/.894/.861`。
  - 正文92边界数字10.48/6.63/4.42与Table4不同。
  - “best baseline”Table5数值与Table1/2不完全一致。
  - 原文108说配置测试only10 images，与全cohort评价关系未明确。
- Table6 38.2M/191.6G/0.82秒/7.4GB；正文98又说4 stochastic passes、single-pass0.74秒。不能当本项目全费用。
- 未按scanner/field strength分层，134/135承认未核真正异质临床泛化。
- 作者Zenodo代码是教育toy，见下。

**active / RUGS**
- Source-free不等于无标签：主动选目标数据，人工标注5%，MeanTeacher半监督。
- SLIC entropy map400regions、compactness .05，Kmeans K2；高不确定region数量≥βNs，β.1。这约束region数量，**不数学保证真实foreground覆盖**。
- 候选pool=5B，uncertainty+core-set diversity，λ.5；minmax normalization flat-score/tie处理正文未明确。
- 网络2D224²，slice-by-slice重建3D；152/155承认无inter-slice。
- 全4模态，不处理missing modality。
- source7:1:2、300epoch；target20kiter、batch16=4 labeled+12 unlabeled、5fold+earlystop。
- **5%标注预算单位（slice还是patient）及outer fold划分需代码/实际list核验，正文不足；不认证泄漏也不认证严格患者隔离。**
- Table3 RUGS ET58.42，Full fine-tune59.50；不能按正文“highest”称超过全部监督上界。
- Table8 RUA+Core-set WT76.48/recall77.44优于UGCS WT76.23/recall74.87，而UGCS边界/precision等更好；不所有指标同向。
- Table7 inference10.17ms是2D网络，不包含遍历全pool、SLIC/Kmeans、core-set、人工标注、20k适应及完整volume。
- 已有region uncertainty+budgeted selection先例，不把宽泛路由/UQ组合当创新。

### 4. 作者公开源码已下载并完整读文本，未执行

`fetch_author_metadata.py`实际 **4b58ac exit1**，部分失败保留：

- routing Zenodo record18331077成功，DOI`10.5281/zenodo.18331077`。
- active公开GitHub `ZHW11/SFADA-for-brain-tumor-segmentation` **404**，未获得源码，未联系作者，不要假称复现。
- `author_metadata_attempt01/receipt.json`。

routing：

- `fetch_routing_author_code.py`实际 **de1995 exit0**。
- 作者ZIP17555bytes，MD5 **0631d0422de239e7175884dc406c63eb**核对成功。
- ZIP原样保留，未按ZIP路径解压；只将21文本文件另存扁平安全路径。
- `routing_author_code_attempt01/receipt.json`列所有original member与sourceSHA。
- 共21文件、**631行**（含空`__init__`），已通过两次Get-Content完整读所有文本。实际`3ca1d1`、`1ddd0c`，没有截断。
- 首次下载打印members输出被工具截断，保留；后续独立完整源码读取不受影响。
- **没有执行作者源码，没有安装依赖/生成其dummy数据。**

源码重要发现：

- README明确 **Educational reference implementation with a tiny synthetic example**，BraTS2018示意，非已认证2026研究全代码。
- YAML50epoch/batch1，4experts/top2/rank8；这仅toy配置，不能当正文2026精确设置。
- LoRALinear `freeze_main=False`默认；encoder/ExpertFFN未传true；train从随机初始化，无pretrained load。不能称本文冻结预训练LoRA的复现。
- decoder没有MC/dropout/UQ gate；engine loss只有Dice+BCE，没有CMC、surface或entropy load balance。
- MoE每个top-k rank遍历专家，若`mask.any()`则`expert(x)`对整个token batch计算后mask；**不是按选中token稀疏dispatch**。不同tokens覆盖4expert时，每rank都可能计算全4，k2可能8全batch expert calls，不能从top2直接推理费用。
- `avail`从dataset输出，trainer没有传给model；model仅接x。
- toy WT/TC/ET用`y==1/2/3`互斥标签；真实BraTS WT/TC嵌套region不能直接照搬。
- PatchEmbed默认kernel/stride4；first feature实际input/4却叫`s8`，HGD最后`scale_factor=8`，按当前代码输出空间为输入2倍；默认64³将成128³，与64³toy target不匹配。**目前是静态源推导，没有执行验证，不要称实际runtime已失败。**
- `patches.py`range不追加最后start，norm零改1，可能漏tail。也是静态分析，未运行作者函数。
- `infer.py`忽略in-path直接读第一个toy val，不调用slider。
- 这些仅界定公开toy能否作exact reproduction，不证明作者研究没有实现或其结果无效。

## 尚未完成的本轮工作

1. **先poll44317**。仍live则不restart；终态按上述流程存actual并audit v2。
2. 冻结两篇阅读provenance/330blocks/22tables/631行作者源码范围，写结论与创新边界。保存本轮actual工具返回和公开对话。
3. 写现有oracle负结果与scope：上界.5546，512全失败；只两个现有whole-series部署流程，不能扩到新SR/局部融合。
4. **六臂训练runner还没有写！**
   - 仅本轮读了原`spatial_adaptation_matched_2026_10_08/run_matched_adaptation.py`完整180行。
   - 用户公开进度说“补齐训练准备”，需要继续具体完成，不能称已准备。
   - 原入口可参考：
     - common_init imports source/cache/sampler/TaskUNet/loss/state_hash。
     - parent via `SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_2026-10-07.json`，各19998，SHA与state_hash核验。
     - 原2992schedule、11患者各272曝光、AdamW reset lr1e-4/decay1e-4。
     - 现成checkpointed class：`gpu_graph_cost_smoke_2026_10_09/checkpointed_model.py`
     - certified resolution：`certified_resolution_rounding_2026_10_09/certified_resolution.py`
     - intensity：`intensity_precision_failure_diagnosis_2026_10_09/intensity_float64_stats.py`
     - frozen5984 originalgeometry journal：`real_context_and_author_code_followup_2026_10_08/full_schedule_attempt01/geometry.journal.jsonl.gz`
       step/patch primitives/geometry/母GT可配对。
   - 两输入×三模式，各2992，总17952更新，完整母GT保持，强度增强照旧。
   - **正式执行须完整35904 terminal+audit、AdamW/capture/full-inference费用资格与fresh整轮disk/GPU准入。当前这些均未完成。**
   - 新runner要CPU1/interop1、导入CPU工具后恢复本进程CUDA_VISIBLE_DEVICES=0及original_lazy_init，FP32/TF32off/deterministic/10%cap。
   - 后续训练大文件完整预算仍短缺，不能缩小科学scope、删除历史或降低reserve来通过。
5. 作者源码静态问题可以做必要独立短诊断（自写数学/形状/费用推导，不执行作者repo），但不要用更多toy替代医学进展。
6. 本轮**尚未增量archive/新最终回复**。旧7180保持；上一轮post-archive文件及本轮所有结束文件应追加；排除live full attempt。

## 工具缓存与保存

- 当前所有本轮已确认actual返回key在 **`load("turn43_tool_keys")`**。
- 包括初始poll、两个oracle、检索、全文范围读、作者metadata/ZIP/所有源码。
- 最新关键：
  - `turn43_read_primary_f_2`：full live e7abe6
  - `turn43_author_metadata_start`：4b58ac partial exit1
  - `turn43_author_archive_start`：de1995 exit0，原输出截断保留
  - `turn43_author_code_read_0/1`：完整631行
  - `turn43_prepare_read_0`：原matched trainer完整源码
  - `turn43_prepare_read_1`：631行统计及routing GIF/active MathML原XML核查
- `turn42`缓存也仍在；上一轮完整导出之后的新returns已保存到`ACTUAL_POST_EXPORT_AND_ARCHIVE_RETURNS.json`。
- 导出用安全base64，不把JSON.stringify直接插入shell。之前采用ASCII转义Unicode、每chunk15000bytes再base64，55chunks成功。helper已在旧作者目录，若新stage要另复制为新文件/新输出路径，不覆盖旧gzip。

## 本轮公开更新已发送

1. 上一轮是实质progress；确认full当前状态、补六臂准备、核采集动作选择先例，保护原训练。
2. full仍live强度0；找到dynamic expert routing，做GT乐观现有动作上界。
3. 上界.5546<.70、512策略全六gate失败；仅现有两流程，不排除新SR/模型，优先强任务基线。
4. 新两篇有missing expert routing和region-UQ active selection先例；后者用目标GT，不是无标签适应；继续核源码/分母/费用。

研究未获得可发表且独立确认claim，goal继续active。
