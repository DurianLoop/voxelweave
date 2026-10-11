# 用户提供的接续交接原文

以下为本次接续时用户提供的前一模型摘要；是交接材料，具体完成情况仍以实际工具和文件为准。

任务仍 **active**，没有可发表且独立确认的 claim。用户要求一直研究、探索和验证；允许 GPU，但不得干预其终端训练或其他 PID。所有研究材料和公开对话写入 `D:\MRI\innovation`。本次仅上下文交接，没有暂停目标。

### 接续第一步

**实际 poll 原训练 session `29823`，不要重启。**

最后真实返回 `336ae1` 仍包含 `session_id`，首分支 `native_reference_intensity`：

- 1430 → **1540/2992 更新**
- median step `2.0717198500060476 秒`
- 累计 `3248.296109099989 秒`
- 最新 loss `.1473725587129593`，只作进度，不选 checkpoint。

其余三分支尚无实际完成记录。四分支各2992、总11968更新；CPU4/interop1/below-normal，wall27000秒、整个实验目录45MB、磁盘/RAM各8GB储备。冻结训练源、配方、滚动 receipt/journal 不改、不冻结 live 文件哈希；没有 optimizer 恢复支持。

训练入口：
`innovation/spatial_adaptation_matched_2026_10_08/run_matched_adaptation.py`

Python：
`D:\conda\envs\MRI\python.exe -X utf8 -B`

GPU授权持续有效；最近上一轮 totals `f00315` 为24455MiB总量、1394MiB空闲，未满足8192MiB启动门槛。本轮未重新查GPU，也未枚举/操作其他PID。

### 上一轮已完成，不重跑

上一 goal turn 是 **progress**：

- 原native/raw各19998、共39996更新真实结束。
- V4全部56生产/functional完整FOV严格通过，旧二值和医学结果变化0。
- 99步四分支pilot396 CPU更新、36生产+36functional FOV评价真实结束；均未过原六医学门槛。
- BigAug、SynthSeg+主文阅读、两项CPU表格审计、五个2992步最终评价入口完成。
- archive session62551真正 `682bea exit0`：原5907 SHA保持、新69，累计 **5976**。

最新有效归档：

- `augmentation_primary_followup_2026_10_08/APPEND_INDEX.json`
- SHA `232e41ed93e57e988790c654318b3360b7851fccbd06eb693886dbf61532e623`
- `APPEND_PROOF.json` SHA `4537283ba48a9fc58715b9f64422088bcbefd702d68284133bb0cf133635f23b`

同目录 `LAST_POST_ARCHIVE_HANDOFF.md`、`POST_ARCHIVE_ACTUAL_TOOL_OBSERVATIONS.json`、`VISIBLE_DIALOGUE_TURN19_PART02.md`、`POST_ARCHIVE_FINAL_METADATA.json` 是 index 后附，下一delta纳入。它们最新990更新是历史时点，已由本轮1540实际poll更新。

五评价入口在 `spatial_adaptation_matched_2026_10_08`：

1. `capture_training_terminal.py`
2. `evaluate_matched.py`
3. `capture_evaluation_terminal.py`
4. `summarize_matched.py`
5. `check_prepared_entry.py`

`ENTRY_PREPARATION_CHECK.json` 的 `0dddb3 exit0` 只证明语法/冻结来源资格。**四分支真正exit0、四state与11968日志核验之前，不运行验证评价。**

### 本轮 turn20 新进展，尚未归档

新目录：
`innovation/tumor_qc_strength_followup_2026_10_08`

完成一篇更直接的脑肿瘤QC原文与作者静态代码审计：

**QCResUNet: Joint subject-level and voxel-level segmentation quality prediction**

- DOI `10.1016/j.media.2025.103718`
- PMID40945175，first online2025-08-27、卷期2026。
- 作者预印本 **arXiv `2412.07156v2`**，更新2025-07-04；不宣称与journal版逐位一致。
- HTML `primary_sources_attempt01/qcresunet_arxiv_v2.html`
- SHA `8cc2f419bbc8e87e84769dd9e875b28d144556e3a3733263ef28ad901bdd0508`
- 实际正文获取 `216fb4=0`，标准库提取 `ecd33f=0`。
- `extraction_attempt01/blocks.json` 200块，另有结构化 `tables.json`、`maths.json`。
- **主文0–107完整核读；同HTML附录172–199完整核读。**
- 109–171 references未完整读；没有视觉审图、PDF或作者网络执行。

公开索引两个query各最多8条，真实 `1e0fb6=0`。初次输出截断，`621399`已完整重读16题名/DOI/日期及QCResUNet摘要；不计16篇已读。原索引125/109总命中，不是系统综述。确切DOI与arXiv题名/全部5作者身份匹配 `ad1ec0=0`。已有SynthSeg/BigAug/TumorSynth不重复计数。

关键原文事实与决策：

- ResNet34+decoder+attention同时预测 **绝对DSC、NSD、逐区域SEM**；已有“定位错误区域”的直接先例，不能作宽泛新意。
- 验证的是QC/错误定位；实际修正收益仅作为后续人机反馈潜力，**没有本项目具体缺层动作净收益证据**。此前defer/cost-sensitive/SafeRestore/MoEDiff先例仍排除“收益头本身创新”。
- BraTS1251，固定内部测试251，剩余667/333训练验证，三次划分/ensemble；不要自动称标准轮换三折测试。
- 用nnUNet/nnFormer、弱/强中间state、多模态组合、人工SegGen制造大量不同质量segmentations；DeepMedic另作未见方法测试。
- **训练和测试按真实DSC十个bin重采样**。测试样本4753/1204/2693不是独立患者数，自然患者分布部署收益不能由此直接推断。
- 4模态输入；T2-only附录的DSC预测r：BraTS `.581`、SSA `.635`、WUSM `.538`，SEM Dice `.429/.363/.349`；四模态分别r `.968/.964/.912`、SEM `.769/.702/.684`。不能直接移植到本项目单observed T2。
- A100、100epochs、batch4、AMP；报告QCResUNet16.59M参数/296.64G FLOPs是单模型，主结果三模型ensemble，另有基础分割、样本生成、调参费用；未取得实际完整pipeline时间。
- 原文歧义待笔记记录：Appendix A176把正确background称FP；UMap公式写50次softmax概率平均而非明确variance/entropy；Dice loss写1/V归一化、CE只列正项；MAE“比MSE更敏感outliers”的解释可疑；超参range最高2e-4而table3最优2.1e-4。不要静默修正、也不要据此判全篇结果无效。
- Appendix D把WT/TC/ET错误图按解剖嵌套方式转可视化类别；错误图本身不必嵌套，下述CPU已核。

### 作者公开代码：读取与失败均保留

作者repo `sotiraslab/QCResUNet`：

- repo API成功，commit API403 rate limit，`2efe53 exit1`，不重试API。
- 单次普通公开GitHub HTML已下载，V1误取payload.repo导致 `36f23d exit1`；失败文件 `AUTHOR_WEB_ATTEMPT01_FAILURE.json`。
- **V2只解析已有HTML，无新增GET**，`a53382=0`，从layout repo/refInfo核实固定commit：
  `e9ddc2418c72cc1c20b69bd3074b7f96b8b5f408`
- 身份：`author_web_attempt01/receipt_v2.json`
- 四份raw文本获取 `50474a=0`，均存 `author_root_sources_attempt01/*.source.txt`，全文实际读：
  - README `da8216=0`，5156bytes
  - utils `7e95fb=0`，6810bytes
  - dataloading `2be2a8=0`，5022bytes
  - main `7c007b=0`，15332bytes
- 没有clone、安装、import/执行作者代码或下载权重。只读四文件，**不称已审全repo**；最多六文件预算还有两份，但无需为数量继续抓。
- 已读root清单没有 `losses.py`；main从其导入DC_and_BCE_loss/PearsonCorrLoss，实际loss/指标生成CSV仍未核，不推断整个环境必然缺该模块。
- README描述refinement并提供qcresunet34/50命令；已读main实际是单CSV scalar质量目标+单二值label-mismatch SEM，不能称完整重现论文DSC+NSD+多区域版本。

**非医学CPU审计已真实完成 `2b1bbc exit0`：**

脚本：
`audit_static_and_error_semantics.py`

结果：
`static_semantics_attempt01/receipt.json`

- 三py仅AST parse/compile，不执行。
- `inspect.Signature.bind`独立审计main74/75两个RegDataLoaderV1调用：定义需6个必需参数，调用5个，均缺 `batch_size`。这是静态绑定证据，不是执行作者程序或判论文运行失败。
- README示例 `qcresunet34/qcresunet50` 均不在当前main argparse choices。
- 穷举4解剖标签的16个GT/query组合：**6个区域XOR错误图不嵌套**；Appendix D按解剖方式重新解码不等价。只影响该可视化代数解释，**不据此否定原逐channel SEM评价**。
- 穷举4个binary组合：`E=P XOR GT`；`FP=E AND P`、`FN=E AND NOT P`均精确。单二值VS任务的signed error方向可从query+error导出，signed-error head本身不当创新。
- MRI/GT/model数组0、神经forward0、CUDAfalse，用时`.0123569`秒。
- 预写协议 `STATIC_AND_SEMANTIC_AUDIT_PROTOCOL.md`。
- 当前训练末次poll同call返回1430/1540，仍live。

### 下一步

1. 实际poll29823，继续原训练，不重启、不动其他PID。
2. 完成本轮QCResUNet **阅读笔记、来源登记、作者代码局限、对候选创新/强对照的影响**。可补读选定refs（MICCAI2023前版本、Jungo2020等），不把预览当全文已读。
3. 保存本轮公开commentary、实际工具与所有失败。大量turn20 observations还在 `functions.store`，需要落盘；注意有些值是 `{status:"fulfilled",value:tool_result}` 包装，别重犯上一轮registrar的exit_code KeyError。
4. 新stage归档接**5976**并纳入turn19后附，live训练folder除frozen_config继续全部排除。不修改旧index、已执行/绑定脚本或根状态文件；新状态另写。
5. 四训练分支真正结束后才保存实际terminal返回（标 `observed_unified_exec_session=29823`）、运行terminal审计→36FOV完整评价→实际评价exit审计→matched summary。匹配比较spatial2992−intensity2992，不能用99步旧control归因。
6. 科学目标未达，不标complete/blocked。若能力不合格继续普通强基线；若合格才实际验证动作余量、全成本及强控制，再冻结后开8未见确认一次。

可恢复store主要keys：

- `turn20_initial_actual`
- `turn20_task_QC_local_search`
- `turn20_current_foundations`
- `turn20_fixed_index_actual`
- `turn20_complete_index_catalog`
- `turn20_QCResUNet_local_dedup_and_effective_model`
- `turn20_QCResUNet_identity_actual`
- `turn20_QCResUNet_html_actual`
- `turn20_QCResUNet_extraction_actual`
- `turn20_qcresunet_read_0_17`
- `turn20_qcresunet_read_18_30`
- `turn20_qcresunet_read_31_53`
- `turn20_qcresunet_read_54_74`
- `turn20_qcresunet_read_75_95`
- `turn20_qcresunet_read_96_108`
- `turn20_qcresunet_appendix_read172_199`
- `turn20_error_benefit_existing_audit_search`
- `turn20_author_identity_actual`
- `turn20_author_web_identity_actual`
- `turn20_author_web_v2_actual`
- `turn20_author_root_fetch_actual`
- `turn20_author_read_README_md`
- `turn20_author_read_utils_py`
- `turn20_author_read_dataloading_py`
- `turn20_author_read_main_py`
- `turn20_static_semantics_actual`

### 固定边界

全队列异质T2，不能统称CISS。开发11患者/19series；已见验证4患者/9series；**8未见确认患者/12series与locked IXI关闭**。不挑中间state、不降六医学门槛、不删除困难病例、不将accepted子集替代全患者分母。普通augmentation、3D、预训练、QC/error maps、metadata、收益头本身均已有先例。不得委派代理、安装依赖、改根environment/.gitignore、枚举/干预其他PID；所有新增只innovation。
