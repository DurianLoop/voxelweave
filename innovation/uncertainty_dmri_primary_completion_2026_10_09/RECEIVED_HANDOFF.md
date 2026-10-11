# 用户提供的上一模型交接摘要

科研 goal 仍 **active**：持续探索、验证，直到取得可发表且独立确认的 claim；目前未达到。上一轮属于 **实质进展**，本轮刚开始，已重新确认两个运行句柄仍 live。

## 约束与资源

- 全部新增写入 `D:\MRI\innovation`。
- GPU 已授权，无须再询问；最新实际 **1394 MiB 空闲、92% utilization**，低于新阶段预设 **8192 MiB**。
- 不干预、重启或迁移用户现有训练；不枚举/操作其他 PID。不安装依赖、不委派代理、不删除历史腾空间。
- Python：`D:\conda\envs\MRI\python.exe`，`-B -X utf8`。
- 最新磁盘 **8,016,527,360 bytes**，8GB 储备之外仅约16.5MB；还要预留 full2MB、原医学3MB、开发2.8MB。RAM约100GB。
- 六臂 final 权重仅 payload 就约33.73MB，当前不能假定可容纳。
- 11开发患者/19series；4已见验证患者/9series。**8未见确认患者/12series、lockedIXI 保持关闭**。
- 概率/强度 `3e-6`、坐标 `3e-12`、二值零差、原六医学门槛不降。
- 见过全11开发GT的19998父模型不能作严格LOPO外折初始化。
- 已冻结或被运行来源绑定的文件不修改；修复另建文件/attempt。

## 第一优先：两个实际 live 句柄

### 开发完整能力评价：12652

目录：`innovation/development_capacity_after_matched_2026_10_09`

**本轮最新实际 f82a04** 仍含 `session_id`：

- native/intensity：19/19
- native/spatial：19/19
- raw/intensity：5/19
- 合计 **43/76**，已完成者严格数值检查通过。

范围固定：四个last2992模型，全11开发患者/19series，**76 production + 76 functional完整FOV**，CPU4/interop1，wall5400s。不开验证影像/GT或确认集，不新训练，不挑臂解读 partial 指标。

真正整体 exit0、无session_id之后：

1. 保存真实返回为原目录 `ACTUAL_DEVELOPMENT_EVALUATION_TERMINAL_TOOL.json`，加 `observed_unified_exec_session=12652`。
2. 执行原 `capture_development_terminal.py`。
3. 审计成功后，执行已经准备且冻结的：`innovation/conditional_uq_and_task_capacity_followup_2026_10_09/compare_complete_development_and_validation.py`
4. 全四臂76开发+36已见验证、全部患者、4region/5指标；Fraction重算，任一未定义传播null，保留全分母。只是描述性能力比较，不是LOPO、因果或独立确认。

原runner/protocol不得修改；比较脚本若有问题另建修复版本。

### 完整强度资格：90446

目录：`innovation/full_real_intensity_v2_2026_10_09`

**本轮最新实际 b08823** 仍live：

- **10560/35904**
- elapsed **7135.873989399988s**
- isolated0
- full-chain最大 `1.9073486328125e-6`
- coordinate最大 `1.1368683772161603e-13`
- support最大 `5.706546346573305e-14`

不是全35904成功；不得继承旧6216前缀。

真正完整成功terminal后保存 `ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json`，加 `observed_unified_exec_session=90446`，执行已有 `audit_full_real_terminal.py`。

## 已完成医学结果

**不要再poll29823或78123。**

目录：`innovation/spatial_adaptation_matched_2026_10_08`

- 训练：95b0a1 exit0；df9ebf审计四last2992及11968配对记录。
- 医学：6ede46整体exit0；capture0fbd7c、summary a165da成功。
- 全36 production+36 functional FOV严格数值通过，**四臂全部未过六医学门槛**。
- patient-first fullDice：native/intensity .468329；native/spatial .521877；raw/intensity .518307；raw/spatial .463237。
- native spatial均值改善只有020一人正，其余三人负，四人recall都降；raw均值下降。
- 024共同严重漏检，recall约.112–.136；tail FP不是共同解释。
- Fraction全分解1f38d5完成；旧null过滤错误与独立修复均保留。

下一科学判断取决于完整开发能力：开发也弱→先补普通task能力/训练部署一致性；开发高验证弱→优先泛化/常规增强。不同患者/采集条件的均值差不能判因果。

## 上轮新增证据与准备

目录：`innovation/conditional_uq_and_task_capacity_followup_2026_10_09`

- 新完整主文+内嵌supp：**On hallucinations in tomographic image reconstruction**，arXiv **2012.00646v3**，DOI `10.1109/TMI.2021.3077857`。
- 178提取块；40公式/算法table节点，1真实结果表。完整读取注册 **bb9c87 exit0**；显示层截断部分已补读。
- 作者仓库官方重定向至 `comp-imaging-sci/hallucinations-tomo-recon`，固定commit：`d640d6b8b134572c06cb883b73fbd9694f808c87`
- 完整读3文件/336行：README144、compute_raw_maps109、compute_specific_maps83，逐Git blob验证；未执行作者模型。
- measurement/null分解、task-specific幻觉图已有直接先例。
- null-HM需要真实GT，不能作部署特征。
- indicator可忽略完全缺失的null结构；零幻觉量不代表无漏检。
- specific-map读取预存seg_mask，生成来源尚未核清。
- 不得把图像强度null-HM直接冒充病灶FP/FN。
- Tanno DOI `10.1016/j.neuroimage.2020.117366` 只取得metadata；publisher返回200但body0，**未取得/阅读全文**。EuropePMC503、OpenAlex429保留，不重试循环。
- **80c2d6 exit0**：全部11968训练轨迹描述。全11患者各272曝光、全19series存在。空间增强loss更高且末段下降，但不能替代完整FOV能力。
- 主要报告：`PRIMARY_AND_AUTHOR_FINDINGS.md`、`EXPERIMENT_STATUS_AND_NEXT_TRIALS.md`、`COMPLETE_COMPARISON_PREPARATION.md`、`README.md`。

核心候选仍是：**强task和普通增强之后，合法可见采集信息对具体paired病灶动作收益与完整费用是否有增量**。必须胜过同信息同容量QC/error、action-conditioned risk差、去采集特征、metadata-only及static/random/always-action/defer等控制。尚未证实新意或效果。

## 不可变归档与保存

上一阶段Papago+医学已归档 **6719**；最新本批真实 **6114ea exit0**，新增61，累计 **6780**。

最新目录：`innovation/conditional_uq_and_task_capacity_followup_2026_10_09`

- index SHA：`1a340f236131e76ade8f6f6cba493e82a6f8922c41250c7adf7570788e010c32`
- proof SHA：`c87423b26158704abba36e3b05016308d865da6f5f5af7a1ebeaf57924a62127`

不覆盖index或冻结源。开发/full live输出排除。

6780之后的未冻结增量需下一index纳入：`ACTUAL_ARCHIVE_TERMINAL_TOOL.json`、`POST_ARCHIVE_TOOL_OBSERVATIONS.json`、`FINAL_PUBLIC_RESPONSE.json`、`LAST_POST_ARCHIVE_HANDOFF.md`、`RECEIVED_USER_HANDOFF.md`、`RECEIVED_IDE_AND_ENVIRONMENT_CONTEXT.md`、`FINAL_SAVE_ACTUAL_TOOL_OBSERVATION.json`。

本轮刚产生的store keys **尚未落盘**：`turn37_initial_0`（12652最新poll）、`turn37_initial_1`（90446最新poll）、`turn37_initial_2`（GPU观察48a3d4）、`turn37_initial_3`（handoff读取edd8be）、`turn37_initial_4`（资源62e683）。

本轮公开commentary也需保存：

> 上一轮补读的论文改变了创新点和评价指标的选择，也完成了全部训练日志分析，属于实质进展。我继续检查两个正在运行的评估；开发集结果齐全后，先判断当前任务模型的能力瓶颈，再决定下一项实验。

继续优先推进真实终态和能力判断，科研goal保持active，不以阅读、软件资格或开发拟合作完成。

注：本文件按可见摘要保留语义及全部事实；部分原嵌套列表改为同层列表/连续文本，属于格式整理，不声称字节逐位原始聊天导出。工具store键是否可取得由本批ACTUAL_TOOL_OBSERVATIONS_PART01.json真实available字段决定。
