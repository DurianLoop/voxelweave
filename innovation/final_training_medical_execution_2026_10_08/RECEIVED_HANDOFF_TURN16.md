以下为本轮用户提供的模型交接摘要原文；其中的执行结果是先前阶段观察，不是本轮重新执行。交接中未展示的历史对话不能由摘要恢复成逐字原文。

任务仍 **active**：用户要求持续读论文、结合既有 MRI 工作找创新并验证，直到得到可发表 claim；目前没有达到。用户已授权 GPU，要求不干预其终端训练，所有资料和对话放在 `D:\MRI\innovation`。本次用户要求上下文交接，**没有取消研究任务**。

- **接续第一步实际 poll session `70619`，不要重启。** 它正在执行全部 56 FOV 的坐标精度修复核验；最近实际输出已经完成 native 28/28、raw 2/28，均严格通过、旧二值预测变化为 0。之后做其他工作约 3 分钟，可能已有更多输出，尚无真实退出。
- 本轮网络 session `92853` 已真实退出 1，原因是批次内 Crossref HTTP500；两篇正文实际成功取得。没有其他观察 cell 或新训练在运行。不要委派代理或操作其他 PID。

当前目录：`D:\MRI\innovation\final_training_medical_execution_2026_10_08`。Python 使用：

```powershell
& 'D:\conda\envs\MRI\python.exe' -X utf8 -B '<脚本路径>'
```

**此前已经结束的正式工作（不要重跑）**

- 原训练 session99542 真实 exit0：native/raw 各19998更新，总39996，累计84978.77890689997秒。捕获及冻结来源已完成。
- V3 主评价 session76250 exit0，但医学能力门槛失败：
  - 开发患者均值 full Dice：native `.890639`，raw `.859645`。
  - 已见验证4患者/9series full Dice：`.506632` / `.445159`。
  - missing Dice：`.507568` / `.445335`；recall：`.462613` / `.372408`。
  - absRVE：`.474591` / `.571475`；raw有一个空预测/整series零TP。
- V3 全56独立重放 session14716 真实 exit1：全部预测、hash、计数和患者聚合核验完成，但22/56不满足严格概率误差3e-6，最大2.3365020751953125e-05。全部二值差异0、float64坐标门槛56/56通过。
- 旧结果及源码均保留，不能修改、降门槛、删困难病例、挑中间checkpoint。

**本轮数值诊断及正在执行的修复**

1. 接续时 poll session1297，真实 `18c022=0`。
   - 第一条开发失败病例：native、VS-MC-RC-002。
   - 插值前 production/functional 物理概率场完全一致。
   - 旧float32映射误差3.039836883544922e-6，二值差异0。
   - 同场 Torch float64 映射后转float32，与独立实现误差4.547473508864641e-13。
   - 只证明单病例误差原因，不代表全队列或医学成功。
   - 结果：`PROBABILITY_MAPPING_STAGE_DIAGNOSIS.json`。

2. 新建、已执行，不能回改：
   - `PRECISION_REPAIR_V4_PROTOCOL.md`
   - `production_probability_mapping_v4.py`
   - `verify_precision_repair_all56_v4.py`
   - 输出：`precision_v4_attempt01/receipt.json`，56个压缩二值预测。
   - 静态AST核对 `e4c30f=0`：仅最终native概率插值输入float64、输出明确float32；网络/输入MR重采样/窗口融合等保持。
   - 启动 `f6ccc5` → **session70619**，08:33:58 UTC开始。
   - 同一个入口逐病例执行新生产完整FOV、独立functional完整FOV/八角坐标、跨reader压缩重读、独立计数/分数患者聚合；**不是第三次跨进程独立重跑**。
   - CPU4/interop1、below-normal、wall3600秒、整个新目录保存10MB上限，RAM/磁盘各十进制8GB。
   - 不初始化CUDA，不重训，不读确认患者。严格门槛3e-6/3e-12/零二值差异不变。
   - 目前 native完整通过，最大已见概率误差5.960464477539063e-8；医学门槛预计仍失败，但必须以最终结果判断。

**新的标签来源与纵向实测**

- 旧物理体积审计：`PHYSICAL_VOLUME_METADATA_AUDIT.json`，28series元数据。
- 新脚本：
  - `audit_allowed_label_timepoints.py` 首次真实 `a9e533=1`，StopIteration，源schema不同；失败JSON保留。
  - `audit_allowed_label_timepoints_v2.py` 真实 **`26d20a=0`**。
  - 结果：`ALLOWED_LABEL_TIMEPOINT_SOURCE_AUDIT_V2.json`。
- 全28允许series：官方CSV、官方标签ZIP路径、首尾56个实际DICOM header的patient/study/series UID及StudyDate全部一致；没有加载MR/GT数组。原生grid来源核查通过。
- 同患者体积差对应**不同纵向时间点**，不能要求相等、视作同次重复扫描，也不能据此证明错标或治疗：
  - 010：1993-09-07 `10.206825 ml` → 1998-04-08 `.083588` → 1999-03-30 `.164109`，122.1倍。
  - 022：1993 `4.114176` → 1996 `.653375` → 1999 `.209929`，19.6倍。
  - 025：1991 `.332573` → 1994 `2.067735` → 1996 `3.592721`，10.8倍。
  - 日期是发布去标识日期，不当真实日历治疗记录。
- V1修复原因：`geometry_availability_attempt_01.json`用`uid`且只有refined grid；V2从绑定的`label_grid_attempt_01.json`取标签字段，并用`grid_with_fitted_affine`。其他源用`series_uid`。
- 新数学纵向终点：
  - `audit_longitudinal_volume_direction.py`，真实 **`678ec2=0`**。
  - `LONGITUDINAL_VOLUME_DIRECTION_DIAGNOSTIC.json`。
  - 仅从已评分计数与日期计算相邻时间点物理体积变化方向，无新数组/推断。
  - 开发：6患者/8区间，两臂方向错误均0。
  - 已见验证：3患者/5区间，两臂均2区间方向错误，均涉及2患者；患者先均值错误比例均`.5`。
  - **这是事后描述诊断，不是临床增长/复发判断、独立确认或SR因果证据。** native同样失败，不能归因PCHIP。
- 最差病例也有4.1ml和1.2ml，不要把失败只归因极小残余。anchors与missing均差、主要FN及低估体积。

**本轮论文资料与实际阅读**

新公开来源在 `adaptation_sources_attempt01/`，没有安装依赖、没有执行作者代码/下载权重或视觉审图。新PDF为0，未实际应用PDF技能（虽已读其SKILL.md，不需声称使用）。

新增4篇不同论文的原文文字核读；范围不同，不能统称4篇完整复现：

1. **Models Genesis**，DOI `10.1016/j.media.2020.101840`，PMC7726094。
   - `genesis2021_bioc.xml` / `_blocks.json`，247块。
   - 重点方法/数据/结果/讨论/附录及主表核读。
   - 实际重点索引：
     `0,1,14,16,17,20,22,24,25,30,32,34,37–40,42,44,46,48,50,52,54–56,60,61,63–67,69–71,73,74,76,77,80,82,83,85–88,90,108,136,142,147,148,151,153,155–157,221–238`（部分区间主要图注/表/脚注）。
   - 623未标注Chest CT预训练，明确排除test-image leakage，目标全部层fine-tune。MRI目标为FLAIR BraTS，不是CISS。
   - Table3 BMS **IoU**：MSRA63.00±1.73、Genesis67.96±1.29；不是Dice。
   - 作者认可公开模型对比架构/参数/平台不对称，不能借此当同容量证明。恢复MSE低不等于表示好，identity mapping可差。
   - 索引PubMed卷期2021、BioC front year2022有冲突，按DOI认证，不自行统一。
2. **Head and Neck Tumor Segmentation…Pre-trained STU-Net Models**，DOI `10.1007/978-3-031-83274-1_4`，PMC11983000，2025。
   - `stu_mri2025_jats.xml` / `_blocks.json`，**0–65全部提取文字读完**，包括重复段/refs；未视觉看图。
   - 120训练/30内部验证，单split；Table3 DSCagg `.77` nnU-Net、`.81` STU-B scratch、`.83` pretrained B；最终challenge `.81`。DSCagg不同于患者均值。
   - 文本把`.77→.74`称improved，与表矛盾。
   - 文本提STU有transformer，原始STU论文显示残差CNN；不能把这个解释当结构事实。
3. **STU-Net: Scalable and Transferable…**，arXiv `2304.06716v1`。
   - 原始HTML已成功取得，`stu_original_arxiv_html.html`。
   - `extract_stu_original_html.py`首次assert无顶层table失败（tables在figure里），不改旧脚本；V2成功 **`ecb20a=0`**。
   - `stu_original_arxiv_blocks_v2.json` 160块，9个HTML tables，包含于figure。
   - 重点完整读 **22–43、48、50–52、54–74、81–84、141、142、158、159**。
   - 残差CNN、六级、nearest+1×1×1上采样，非Transformer。
   - TotalSegmentator CT预训练，新增MRI/病灶标签需替换head并适配，不能直接zero-shot VS。
   - Table5 AMOS-MR STU-B scratch86.92→ft87.49，nnU-Net87.39；不是巨大/普遍增益。
   - 原始预训练4000epochs×250，fine-tune默认1000×250；A10080GB，不能外推本机。
   - direct inference通过合并GT器官/肿瘤标签对齐，不能用它证明独立肿瘤保持。
4. **Colormap augmentation: a novel method for cross-modality domain generalization**，DOI `10.1007/s11548-025-03559-y`，PMC13035743。
   - `colormap_jats.xml` / `_blocks.json` 98块。
   - **0–60正文、方法、表、讨论读完**；某些首次输出截断，13–26已重新完整读取（实际`322eac=0`），仅去重复LaTeX document-template，不改原文件；refs只看相关BigAug。
   - 2D肝脏CT↔MRI；Cmap全部训练/验证/测试转3通道，与当前单通道合同不同。
   - T2 Table4单Cmap `.5%`，BigAug72.2、BigAug+Style78.5、ExAug+Cmap41.0；不能称普遍提升。
   - block31选择固定gnuplot2时提到逐map测试及最佳83.1，与target完全未见叙述需澄清，不能借用严格独立选择证明。
   - 仅colormap变换不用GPU，不等于神经分割不需GPU或整体免费。
- 另复读MC-RC作者论文PMC11111906，旧缓存，不算新论文。其25万更新/五fold/丰富增强并非当前11人2万步配方。
- 检索失败保留：
  - 错记BigAug题名“Deep stacked transformation…”导致exact zero hit、Crossref500。
  - 后由Colormap ref13纠正：**Generalizing deep learning for medical image segmentation to unseen domains via deep stacked transformation**，DOI `10.1109/TMI.2020.2973595`，PMC7393676。
  - NCBI获取BigAug正文429，`bigaug_receipt.json` completefalse，提取空；**不能算读过BigAug原文**。不要频繁重试。
  - STU Crossref匹配无关论文，保留，不当身份认证；arXiv原始HTML已实际认证。
- 正文获取/提取脚本已执行，不修改；有问题另建版本。
- **阅读笔记/READING_PROVENANCE、创新决策及下一实验准备尚未写！**

**资源与下一步决策**

- `check_next_experiment_resources.py` 实际 **`68741c=0`**。
- `NEXT_EXPERIMENT_RESOURCE_READINESS.json`，08:56:18 UTC：
  - GPU总24455MiB、free1394MiB，未满足原8192MiB启动条件；授权仍有效。
  - 磁盘free8,090,775,552 bytes，8GB储备外90,775,552。
  - RAM可用102.8GB。
  - 同容量短增强pilot保存20MB预测可行，但不能证明医学能力。
  - 按论文参数FP32两份权重估算：STU-S116.8MB、Genesis130.56MB，超过当前储备外空间；还未算optimizer/history/下载。是预测，未实际测checkpoint大小。
- 尚未启动新训练。优先准备同容量、相同初始化/患者与预算的增强对照，再考虑有独立训练身份的预训练；不能把预训练/3D/增强/ROI或收益头本身作为新意。
- 原主候选仍：充分任务适配后，同合法observed输入下，预测具体缺层修正的真实病灶净收益，完整成本超过强raw/直接任务/两路径error-cost/defer/随机/static等匹配控制。
- 可增加纵向体积变化误差为后续终点，**不能要求不同真实时间点体积相等**。当前泛化失败不支持正claim。
- 8未见确认患者/12series、locked IXI继续关闭；4/9验证已见。新文件只innovation，勿改环境、删历史、枚举/干预其他PID。

**归档与明确待办**

1. 实际poll70619到真正退出，记录全部56结果、数值与医学门槛分别判断；失败也保留。记录actual exit receipt，绑定新结果/source SHA。单入口核验的边界如上，不冒充跨进程重跑。
2. 完成4篇阅读笔记、精确provenance、相对既有prior-art的创新决定、下一增强/预训练实验准备（资源未够不假装已跑）。
3. 全阶段公开对话、用户交接摘要、结果说明和新工具记录尚未完整归档。可见原文不能恢复时注明摘要，不伪造逐字。
4. 已通过functions.store恢复并写入 **`RECOVERED_TURN15_TOOL_RECORDS.json`**：
   - watch_turn15_initial、watch_turn15_loop（39观察）、main/strict summary、diagnostic launch；
   - final_evaluation_poll01–14、strict_replay_poll01–19，全部恢复无缺。
5. 本轮functions.store大量`turn16_*`仍可load，需落盘。可从以下名称恢复：
   - initial_probability_diagnosis_poll、initial_inspection、contract_and_resources、
     repair_source_reads、resource_metadata_schema、precision_v4_static_verification、
     precision_v4_launch、label_provenance_and_reading_selection、
     provenance_paths_and_v4_poll01、mc_rc_official_source_reads、
     clinical_metadata_and_v4_poll02、official_dates_and_primary_metadata、
     allowed_timepoint_audit、source_schema_failure_and_primary_blocks_a、
     allowed_timepoint_audit_v2、primary_blocks_b_and_v4_poll03、
     adaptation_primary_index_launch、adaptation_fulltext_launch、
     adaptation_source_and_v4_poll04、stu_first_read_and_identity_addendum、
     stu_remaining_fulltext_and_genesis_catalog、genesis_methods_and_colormap_identity、
     genesis_results_and_bigaug_correct_identity、turn15_tools_recovery、
     genesis_table_colormap_methods_and_stu_primary、
     genesis_table_and_colormap_results_clean_read、stu_original_extraction、
     stu_original_extraction_v2、stu_original_methods_and_results_read、
     longitudinal_direction_audit、colormap_first_clean_and_v4_poll11、
     colormap_template_cleanup_read、next_experiment_resource_readiness。
   - 名称都加`turn16_`前缀。
   - static verification store是根据实际可见e4c30f返回重构，注明过一次store(undefined)失败，不能假装新的执行。
   - template_cleanup_read只存范围说明，真实322eac响应没存对象；可见本摘要记录，不伪造完整输出。
6. 完成后做delta归档，核验旧5535证据，不复制巨大manifest：
   - base5430 `lossless_final_evaluation_entry_2026_10_08/ARCHIVE_MANIFEST.json`
     SHA `d6481cf77e2e46303c4433969ac37804034ba0f70fbfa487570378abb696658e`
   - TADT delta30 `task_routing_author_source_2026_10_08/APPEND_INDEX.json`
     SHA `274c0f1c5713e45f38d3e57a3b4b2d19bb9ffb90b3a121d6f81c6acf60ca7d39`
   - MoEDiff delta75 `moediff_full_scope_and_author_2026_10_08/APPEND_INDEX_V2.json`
     SHA `056f2b0e7b105cf5e628293af3446a340640b81b4f90b0b9f15728a75d4d9bc4`
   - 下一delta要纳入watch9–14、MoEDiff四post、真正结束的训练/主评价/strict及新阶段文件。
   - 当前V4仍live，**不能冻结正在变的receipt**。之前原训练rolling文件现已真正结束，可冻结。
7. 可参考MoEDiff `record_and_append_v2.py`的delta方式，防止重复document字段冲突。
8. 最终汇报诚实说明医学能力失败、科研目标未完成；不标goal complete/blocked，除非用户改变目标。
