# 用户提供的接续摘要（原文）

任务仍 **active**，尚无可发表且独立确认的 claim。本次是上下文交接，不是暂停。用户要求持续读论文、探索验证，允许 GPU，但不得干预其终端训练或其他 PID；所有新增材料和公开对话放在 `D:\MRI\innovation`。

### 接续第一步

**实际 poll 原训练 session `29823`，不要重启。**

最后真实返回 `58df89` 仍有 `session_id`：

- 首分支 `native_reference_intensity`：2750 → **2860/2992 更新**
- median step `2.0737549000186846 秒`
- 累计 `6017.212067999993 秒`
- loss `.10025569796562195` 仅作进度，不选择 checkpoint。

其余三分支尚无实际完成记录。四分支各2992、总11968更新；CPU4/interop1/below-normal，wall27000秒、训练目录45MB、磁盘/RAM各8GB储备，无optimizer恢复。冻结训练源、配方不改，滚动receipt/journal/state不冻结哈希。

训练入口：`innovation/spatial_adaptation_matched_2026_10_08/run_matched_adaptation.py`  
Python：`D:\conda\envs\MRI\python.exe -X utf8 -B`

GPU授权持续有效。本轮 `0a9aac` totals仍为24455MiB总、1394MiB空闲，未达到8192MiB启动门槛；未枚举或操作其他PID。

### 已有有效归档

上一轮是 **progress**，归档已真正完成，不重跑：

- 原5976哈希保持，新增84，累计 **6060**
- `tumor_qc_strength_followup_2026_10_08/APPEND_INDEX.json`
- index SHA `3851809bc4bb6d6a92d9da526ea699b7299c54ff315fdf6b9430e3e202fce01c`
- proof SHA `fb48c2d2338f049d836cc8e1ee6728332f53cd724f052b01ebc7399eb39ec54c`
- archive session3820，实际 `f0c36e exit0`
- 同目录POST文件、`LAST_POST_ARCHIVE_HANDOFF.md`、`FINAL_PUBLIC_RESPONSE.json`、`VISIBLE_DIALOGUE_TURN20_PART02.md` 为index后附，下一delta纳入。

此前39996原训练、99步四分支396更新、旧36FOV及V4全部56数值核验已经真正完成；医学门槛未过，不重跑。

### 本轮 turn21 实质进展，**尚未归档**

新目录：`innovation/vs_task_baseline_followup_2026_10_08`

已完成：

1. 两篇不同期刊原文主文/主表核读。
2. 图像双插值、标签保持原样的可执行增强原型。
3. 三个非医学synthetic/表格CPU脚本真实exit0。
4. 全部11开发患者/19series、两输入38batch真实入口资格真实exit0。
5. 来源登记、笔记、下一试验准备、公开对话和实际工具落盘。

**原训练仍live，无新增神经训练或患者医学效果，也未评分验证/确认。**

#### 两篇新原文

**A. Artificial intelligence for personalized management of vestibular schwannoma: a multidisciplinary clinical implementation study**

- DOI `10.1093/jamiaopen/ooaf163`，PMC12772638，firstPublicationDate2026-01-06。
- XML：`primary_attempt01/clinical_vs.xml`
- SHA `54fa48e991a4db6a84a9e514658815dfd3f80ee9a9211a22aacf5b7a8de0cf88`
- 完整核读提取blocks0–126，科学主文0–88；Table1单元格完整读。
- 外链supplementary ZIP中的AppendixA/B未取得，图像像素/作者代码/模型未核。
- internal开发UCLH MC-RC，external模拟KCH50患者，作者声明患者不重合。
- standard先进行，CAS35天后，随机的是病例顺序，**没有counterbalance两种会诊先后**；模拟决策不影响实际care。
- 50患者中36全accepted、8一个session人工fallback、6整例人工修订，保留全部分母。
- abstract将internal Dice .9392给T1C、.9331给T2；正文block54反过来。保留冲突，不静默统一，也不当外部50例Dice。
- Table1 mean：prep156→174秒、MDTM81→75秒；合计多12秒/例。
- Table1 total：prep7650→8724秒、MDTM3756→2904秒；合计多222秒。
- mean×50的差是600秒，**两列不一致，不能混算、造显著性或完整净临床收益**。
- person-time也不同于顺序wall-time；多角色出勤/额外预读/算法生成成本缺失。
- block41 “more than 1 axial slice”时不展示volume语义可疑，未查代码不修正。

**B. Deep Learning-Based Inner Ear Subregion Segmentation in 3D T2-Weighted MRI Using Label-Preserving Data Augmentation**

- DOI `10.1002/nbm.70266`，PMC12983123，firstPublicationDate2026-04-01。
- XML：`primary_attempt01/label_preserving.xml`
- SHA `10cd90b719c5ad6f82e4d86775bfd5b84123d4e5d94f350fe391fb86bc485ad3`
- 完整核读blocks0–89，科学主文0–62，Table1/2完整读。
- 外链docx supplement、图片像素、作者代码未核。
- 三个内耳解剖区域，**不是VS肿瘤任务**。74 MRI exams：50训练/24时间独立测试，未证74独立患者；左右耳48samples不是48患者。外部8 images/16耳来自VS-SEG。
- 内部3T FSE .3125mm/.4mm；外部1.5T有CISS或FSE、1.5mm厚，不能统称CISS或纯spacing因果。
- 已有“图像rotation/scale后inverse、GT不动”的直接先例。只验证x-axis rotation与scale；主文缺完整范围、概率、batch/updates、padding/axis细节。
- SwinUNETR、96x96x32crop、500epochs、Dice+CE等权、AdamW1e-4/wd1e-3、TitanXP12GB。
- 内部区域Dice .902/.881/.926→.905/.880/.929；一类稍降。外部 .872/.802/.866→.956/.887/.913。
- HD单位/实现未完整认证；Results与Discussion关于internal显著性不一致。
- 普通image-roundtrip/标签插值保护不能作为首创。

#### 原获取失败与修复

两查询各8记录，总命中43/20，含重复，不是系统综述。已有crossMoDA2026、MC-RC2024、VS cascade2025去重。

`fetch_selected_primaries.py` session12809，实际 **`1de6d5 exit1`**：第二篇XML使用Unicode U+2010连字符，索引ASCII `-`，严格title断言失败。两XML已下载。

`reconcile_identity_and_extract_v2.py` **`991f9d exit0`**：只解析本地文件，将U+2010→ASCII、折叠空白、忽略末句点及大小写，同时精确核DOI/PMCID。**零新增GET，不改原脚本，不把原fetch exit1改成0，不补造丢失的内层HTTP结果。**

#### 新原型与实际资格

`label_preserving_roundtrip.py`：

- 使用原项目`spatial_transform.theta`。
- 第一矩阵采样后，**完整齐次矩阵求逆**第二次采样；三Euler角同序逐一取负不是逆。
- image两次trilinear、zero padding、align_corners=False、float64坐标/中间值，最终float32；GT逐位不变；identity/disabled直接skip。
- 是项目原型，**没有执行作者代码或称忠实复现**。

真实结果：

- `qualify_roundtrip_synthetic.py` **8fb81e exit0**
  - 全生产patch64x128x128，四配方，32固定点独立两级八邻域oracle。
  - max error `1.8631661324874926e-08`。
  - 三轴错误neg-angle inverse偏差 `10.359868944780587 voxel`。
  - constant图像roundtrip mean `.8613933324813843`、边缘min0，说明标签不变不等于图像信息无损。
- `qualify_roundtrip_texture.py` **49f6f4 exit0**
  - 补齐预写checkerboard/wide phantom，两配方。
  - oracle max `2.9750514052295784e-08`。
  - 32点资格，**不是全概率体素独立验证**。
- `audit_clinical_time_table.py` **560478 exit0**
  - 精确保留时间两列、36/8/6患者分母、假定k的person-time算术；不估新临床净收益。
- `qualify_real_roundtrip_development.py` session37558，**b2c07b exit0**
  - 11开发患者/19series、native/reference与合法raw-PCHIP共38batch。
  - input/physical GT哈希匹配旧QPATH认证；两输入母GT、geometry、pivots、stress参数配对；GT逐位不变。
  - MRI加载38次、GT19次；model arrays/forward/updates均0。
  - 用时 `127.91305500001181 秒`。
  - 原4验证/8确认/lockedIXI未开，没有患者Dice或增强收益结果。

### 当前重要文件

新目录内：

- `PRIMARY_READING_AND_PROJECT_DECISIONS.md`
- `MATCHED_ROUNDTRIP_NEXT_TRIAL_PREPARATION.md`
- `READING_PROVENANCE.json`：**f3aa14 exit0**；已绑定笔记/配方/原型等来源，别修改已绑定内容。
- `ACTUAL_TOOL_OBSERVATIONS_PART01.json`：33项工具完整恢复，含失败/截断/旧猜测路径不存在。
- `ACTUAL_TOOL_OBSERVATIONS_PART02.json`：登记和最新训练返回。
- `VISIBLE_DIALOGUE_TURN21_PART01.md`
- `README.md`
- `NEXT_STAGE_HANDOFF.md`
- 根innovation新增 `CURRENT_RESEARCH_STATUS_VS_ROUNDTRIP_2026-10-08.md`

**尚未编写/执行本轮archive脚本，尚无新APPEND_INDEX/PROOF。**

末次资源 `7fa1b4`：newstage916542bytes（之后又有工具snapshot/登记/文档），workspacefree8054243328bytes；root `.gitignore`、`environment.yml`哈希不变。

### 下一步

1. **实际poll29823**，原训练继续，不能据时间推断首分支已结束。
2. 为turn21新增归档脚本，接6060，并纳入turn20后附文件。可参考：
   `tumor_qc_strength_followup_2026_10_08/archive_completed_reading.py`
   - 使用同六段历史chain，再加其84份index。
   - 全6060旧哈希核验，不修改旧index。
   - live training目录除了原`frozen_config.json`全部排除。
   - 新stage总量<=5MB，保留8GB磁盘/RAM。
3. 实际archive terminal之后写POST观察、最后handoff、公开PART02和最终回复；这些后附下个delta纳入。
4. 四训练分支真正exit0后才保存实际terminal，标`observed_unified_exec_session=29823`，运行：
   `capture_training_terminal.py → evaluate_matched.py → capture_evaluation_terminal.py → summarize_matched.py`
   必须四last2992、11968日志核实后才加载验证像素。`check_prepared_entry.py`仅语法/冻结来源资格。
5. 主比较spatial2992−intensity2992；不能用旧99步归因。完整36生产+36functionalFOV、3e-6概率/3e-12坐标/零二值、六医学门槛不降。
6. 能力不足先普通强基线；新的roundtrip是普通增强候选，未来另立same-parent/schedule/exposure/预算与低通控制，不改当前四臂。能力足且动作余量存在才开展patient-fold外实际动作损害差、强QC/error-cost/defer及全成本，冻结后打开8未见确认一次。

固定边界：异质T2不统称CISS；11开发19series、已见4验证9series；**8未见确认12series与lockedIXI关闭**。不缩分母、不挑中间state、不删困难例、不降六医学门槛、不安装依赖、不委派代理、不改根环境或.gitignore、不枚举/干预其他PID。普通增强、3D、预训练、QC/error maps、metadata、收益头本身都有先例。
