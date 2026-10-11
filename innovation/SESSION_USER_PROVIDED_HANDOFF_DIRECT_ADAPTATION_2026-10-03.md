# 用户提供的接续摘要（原文）

目标仍 **active**：持续研究到可发表且独立确认的 claim；目前未达到。这是用户请求的 compaction，不是停止研究。本次 goal continuation 已有实质进展，新来源下载仍在运行。

### 约束

- 所有新增内容写 `D:\MRI\innovation`。
- Python：`D:\conda\envs\MRI\python.exe -X utf8 -B`。
- 不用 GPU、不操作用户终端训练、不读 locked IXI test、不改根环境或 `.gitignore`、不创建或委派代理。
- CPU 单线程、自身低优先级；磁盘至少 15 GB、可用内存至少 8 GB。
- 本次实测磁盘约 **18 GB**，内存约 110 GB，因此来源下载采用有限批次。
- 旧45 CISS、MC-RC旧8开发患者不能当新方法未见确认；科学确认仍0。
- 不以归档验收、来源资格或软件复核代替科学确认；不重启已完成或仍 live 的队列。

### 上一阶段已完成、无需重跑

入口：

- `SESSION_HANDOFF_STATS_SWAP_AND_SOURCE_2026-10-03.md`
- `INNOVATION_DECISION_AFTER_STATS_SWAP_2026-10-03.md`
- `STATS_SWAP_AND_SOURCE_NEXT_PREPARATION_2026-10-03.md`

成果：

1. 三人202/203/204统计互换6次CPU前向已完成，最终复核79154 exit0。6交叉输入、6对角输入、72采集域计数、30端点一致。
   - 主JSON full ΔDice **+.001410324**，异质且有负反例。
   - 三人原post−raw **+.03335979**，全45 **−.09175350**；不能外推损失归因或恢复。
2. 全45统计审计90旧数组、0新前向完成，独立标量验证通过。
   - post std平均 **−2.4882%**；相同anchors归一化scale **+2.5525%**。
   - scale/RMS与Dice的Spearman近0，不支持风险排序或因果解释。
3. 3篇原始PDF核读、28已读页、3视觉页登记完整：
   - Region Normalization；
   - Partial Convolution；
   - Normalization-Equivariant Networks。
   - 宽归一化/掩膜/argmax不变思路均有直接先例，anchor-only仅保留控制。
4. MC-RC源目录真实 **71人/159 labelled T2 series**，不是继承摘要的81。
   - API全部58共享VS-SEG患者排除。
   - 旧8人21候选series开发；余63人138series仅候选。
5. 固定011/012/013全部5series：230 MR非像素头、5label检查及独立重读完成。
   - 3series通过，013两个2D厚层时点失败保留。
   - 没有MR像素解码或模型效果，3人角色pending。
   - 首独立proof误加1e-4体素容差失败；原脚本与proof保留，按原0.05mm物理门槛修正后attempt02通过。
6. 上阶段静态及全局验收4检查 exit0：
   - `SESSION_ARCHIVE_VERIFICATION_STATS_SWAP_AND_SOURCE_2026-10-03.json`
   - stage627文件，global29主注册PDF、2024证据文件、2410链接，errors=[]。
   - 本次新source_cache已增加，所以 **global清单需本轮结束再同步**；历史验收不覆盖。

旧HAT负claim被+.036381704反证、残差2/6、order_rms、anchors带宽、native/QDA失败继续有效。

### 本次 continuation 新增文件与实际工作

已写方案：

- `MC_RC_NEXT12_IDENTITY_SOURCE_PLAN_2026-10-03.md`
- `literature/2026-10-03_task_adaptation_direct_search_plan.md`

已写并实际运行：

- `literature/download_mc_rc_next12_headers_2026_10_03.py`
- `literature/search_task_adaptation_direct_2026_10_03.py`

**当前必须先接续的 live 进程：session40497。**

- 固定候选去旧8人及已预检011/012/013后，字典序前12人：
  `015,019,020,022,024,025,026,027,028,029,030,031`，完整ID前缀 `VS-MC-RC-`。
- 全部25 labelled T2 series，API1475对象、615,515,656预估字节。
- 总下载cap800,000,000，连接1，socket30秒，series180秒，零自动重试；首工具失败停止，资格阴性继续报告。
- 原始ZIP含像素字节，但仅 `pydicom.dcmread(stop_before_pixels=True)`；无MR像素/模型/GPU。
- 输出：
  - `literature/source_cache/mc_rc_next12_headers_2026-10-03/attempt_01.json`
  - 各series header JSON；
  - `data/mc_rc_next12_header_gate/*.zip`。
- **最后一次poll确认 session40497 live，完成10/25：**
  - 015 `_T2_T2_3D_DRIVE` header资格false；
  - 015两 `_T2_I.A.C. * T2 TSE` true；
  - 019两series true；
  - 020一series true；
  - 022三series true；
  - 024 `_T2_t2_spc_rst_tra_p2_iso` true。
- 下一步先poll40497；**不要因观察超时重启**。未确认其终态。

### 本次身份审计初步结果

已用 `rg -l` 在 baseline/pre/design/processing/docx/handoff/innovation 文本中查011/012/013，排工具、runs、test目录、source_cache。

只命中：

- 旧官方metadata/API/候选表；
- 011/012/013来源预检记录；
- 归档manifest及导航/脚本。

没有匹配的项目模型效果文件。**这仅初查，不是完整全项目曝光证明。尚未写正式身份审计脚本或冻结split。**

下一轮应扩大到全部候选71/102 namespace PatientID和UID，对命中逐项分类，未知用途保留pending；不用数值后缀匹配。元数据/源预检不算模型效果。旧8人所有时点一角色；新3+12不能先看模型效果再选confirm。

重要模型泄漏：

- 已存 `literature/source_cache/mc_rc_official_2026-10-02/mc_rc_models_zenodo_attempt_01.response`：
  - Zenodo10363647，作者nnU-Net模型有MC-RC、SC-GK、两者混合版本。
  - MC-RC模型约8.7GB、SC-GK/混合各约7.2GB，不能在当前磁盘预算盲下载。
  - MC-RC/混合模型训练可能包含候选患者，不能用于未见确认。
- 当前已用官方UNet2d5 checkpoint来自旧VS-SEG242来源；所有共享58患者已排除。
- 未来矩阵优先从头训练或训练身份完整已知权重；新来源任务能力仍待实测。

### 新检索已完成，尚未获取/核读新正文

`search_task_adaptation_direct_2026_10_03.py` 已 **exit0**，4个NCBI PMC检索均成功：

- 输出：`literature/source_cache/task_adaptation_direct_search_2026-10-03/attempt_01.json`
- 原始query/summary响应及SHA保存。
- 查询返回12+2+1+12 = **27题名行**，含重复，不计新全文。
- 总命中21、2、1、73。

有用候选：

1. **Autoencoder based self-supervised test-time adaptation for medical image analysis**
   - PMC8316425，DOI10.1016/j.media.2021.102136。
   - **已在之前 `2026-10-03_predicted_region_fulltext_reading.md` / selection出现，必须去重，不重复计新阅读。**
2. **Reconstruction from multi-planar MRI with foundation models for uterine fibroid analysis**
   - PMC13385847，DOI10.1038/s41746-026-02780-6。
   - 新候选；尚未读取正文。
3. **TumorSynth: Integrated Brain Tumor and Tissue Segmentation on Brain MRI Scans of Any Resolution and Contrast**
   - PMC13036690，DOI10.1148/rycan.250222。
   - 新候选；尚未读取正文。
4. **Synthetic data in generalizable, learning-based neuroimaging**
   - PMC11752692，DOI10.1162/imag_a_00337；综述需区分原研究。
5. **Carotid atherosclerotic plaque segmentation in multi-weighted MRI using a two-stage neural network: advantages of training with high-resolution imaging and histology**
   - PMC10244753，DOI10.3389/fcvm.2023.1127653。
6. 既读FeTA2024重复命中两次；SynthSeg已是既有先例，不当新发现。
7. Representation Disentanglement for Multi-modal Brain MRI Analysis
   - PMC8844656，DOI10.1007/978-3-030-78191-0_25。

公开全文获取可以复用：

- `literature/fetch_task_normalization_context_2026_10_03.py`：
  EFetch `db=pmc,id=数字,rettype=full,retmode=xml`；
  要确认body和DOI，保留raw XML并提取title/p/table-wrap/fig/disp-formula及floats-group。
- 如果拿PDF再用已应用的PDF skill；现有MiKTeX Poppler可用，pypdf等缺失不需安装。
- 网络stdlib公开访问本轮成功，未遇审批阻塞。不要安装包或改环境。

### 下一步清单

1. **poll40497，确认25来源生产终态。**
2. 完成全部25label源资格，沿用0.05mm物理grid、binary非空、qform/sform、exactUID/PatientID/StudyUID。
   - 可借鉴上一批：
     - `experiments/audit_mc_rc_011_013_label_grid.py`
     - `experiments/verify_mc_rc_011_013_header_label.py`
   - 不用上一失败额外1e-4体素阈值；保留全部阴性。
   - 独立重读1475头/25labels，不解码MR像素，不跑模型。
3. 正式扩大项目曝光/身份审计，结合旧8+新3+新12预检，产出能实际使用的patient角色准备/冻结；未证明项不能虚构完成。
4. 从新检索候选取2–3个真正未读直接正文（优先TumorSynth和多平面fibroid），实际读方法/训练输入/对照/结果/限制，做好去重与阅读登记。
5. 科学方向：在相同observations和任务训练预算下，任务模型适应后是否还有可修正缺层损失。宽任务适配、强度归一化、synthetic训练均可能已有先例，不能提前声称创新。
6. 归档本次continuation公开消息、用户这次compaction请求、工具/失败记录；本轮新SESSION文件、报告、README新入口 **尚未写**。
7. 最后新stage静态验收+全局证据/链接manifest同步；旧验收保留。goal保持active，未经实际claim确认不得complete。

本次已发送公开更新两条：

- 开始：“上一轮有实质进展……推进患者身份与数据角色核验……继续避开GPU和训练进程。”
- 后续：“可用磁盘约18GB……保留15GB底线，固定12患者……011/012/013只见于metadata/preflight，扩大身份审计后再冻结角色。”

新goal turn不是no-progress：确实新增了固定来源下载和27行公开检索证据。下一代理接续，不重新开始上一阶段。
