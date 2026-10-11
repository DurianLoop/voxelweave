## 目标与当前状态

继续目标：**研究、探索、验证，直到获得可发表且独立确认的 claim；不动用户原终端训练进程。** GPU 已授权。上一轮属于实质进展，当前仍无确认 claim，goal 保持 active。

工作区 `D:\MRI`，PowerShell，Python：`D:\conda\envs\MRI\python.exe -B -X utf8`。所有新增仅写 `innovation`；不安装、不委派、不删历史、不枚举或修改其他 PID；已执行或冻结代码不改，修复另版本。

## 冻结链与运行任务

ROUND50 已归档并独立核验：

- `six_resolution_training_preparation_2026_10_09/APPEND_ROUND50_INDEX.json`
- 原 7639 文件 SHA/bytes 保持，新增 89，累计 **7728**。
- index SHA：`97e4a4de6ff37a908732567e01f6e979125ea862dae1a7d4eb9a1f62979c4f73`
- archive `e5d048` exit0；post-check `d4d723` exit0。
- 接续文件：`POST_ARCHIVE_HANDOFF_ROUND50.md`。

**ROUND51 尚未归档、导出 buffers 或写最终研究报告。本次 checkpoint 摘要也尚未落盘，下一步先保存。**

唯一已确认 live：`qualify_full_real_pipeline.py`，session **44317**。最近 actual `e72f28` 仍含 session_id：

- **15000/35904**，elapsed `15996.148070500116` 秒。
- 强度/support 误差0，coordinate `1.1368683772161603e-13`。
- 不重启。仅真实 exit0/no session 后保存终态并执行 `audit_full_real_terminal_v2.py`。
- `full_real_pipeline_attempt01` 继续排除归档。

本轮作者源码下载 session **92352、31318 均已真实 exit0**，不要再 poll。没有其他新 live。

## ROUND51 数值探索

新增于六分辨率目录：

- `STABLE_REDUCTION_MODEL_SYNTHETIC_PROTOCOL_V1.md`
- `stable_reduction_task_model_v1.py`
- `verify_stable_reduction_model_cpu_v1.py`
- `stable_reduction_model_cpu_attempt01/receipt.json`

这是**另立的数值版本**：54个 FP32 参数、FP32卷积等保留；production norm 使用 FP64 `var_mean`，独立 reference 使用 FP64 显式中心化公式；两个分支 loss 也用 FP64 临时计算。不能称旧 production 或正式六臂已资格。

实际 **aecf3a exit1**，缓存 `round51_stable_reduction_cpu_start`：

- 原16³、3view、两步协议。
- 实际仅 step0、两分支各1次 CPU 更新，**本轮新增2个人工 CPU optimizer updates**。
- loss0、probability0、binary0。
- gradient `4.842877388000488e-8`。
- parameter **`3.4603290259838104e-6 > 3e-6`**。
- optimizer state `4.773028194904327e-9`。
- step1 未执行，未新增 GPU/MRI/GT/parent 运行。
- 尚未独立审计或定位本次最坏坐标。原 ROUND49/50 失败不改、不降低 gate。

## 新论文阅读

目录：`adaptive_acquisition_primary_followup_2026_10_09`。

两个固定版本均已读完全部抽取文字块；**阅读 provenance 尚未建立**，图像像素、参考条目未读。

**Swin UNETR，2111.14791v2**

- `foundation_primary_html_attempt01/swin_pretraining`
- 全部 **0–130 blocks** 已读。
- chunks：`a7d051`、`4b9de1`、`c01359`、`43eaa4`。
- **Algorithm S.1 伪代码正文可能漏抽取，尚需补读**，不能提前称全部原文结构已读。
- 关键：CT预训练权重只用于CT；MRI任务明确 **from scratch**，不能据此证明CT预训练迁移到MRI有效。
- 61.98M参数、五折模型选择与集成；不能把作者费用当本项目预算。
- 文字450K iterations与附录45K不同；5050总数与表格数据需独立算术核查，不猜原因。

**BrainSegFounder，2406.10395v3**

- `brainsegfounder_identity_html_attempt02`
- 全部 **0–108 blocks** 已读。
- chunks：`a41961`、`655ab4`、`abbaee`。
- 首获取因标题含不含“3D”不一致真实失败，保留。v2以固定官方URL、明确两个标题版本、全部8作者匹配核验，actual **e9bb10 exit0**。
- UKB T1w/T2-FLAIR预训练，41,400 participants；不能当普通单T2/VS适用性证明。
- BraTS四模态，单T1实验另报；ATLAS非五折，与训练集 leaderboard 比较，另100图像用于调参。
- Table4与Table8的 one-stage small Fold2 显示不同：`.9055` vs `.9186`；均值及相关数据/训练表差异需独立核查，不能借此推断本项目效果。
- 不下载权重、不替换现有模型；外部预训练须另立来源、患者重合、资源和比较合同。

查重首次 `rg` 有 tools目录权限噪声；修正glob后 **9b1bf9 exit1、无输出**，证明旧Markdown精确标题/ID未命中。不是全球查新。

## Greedy 作者代码核查

GitHub API **bc4ea6 exit1、403限流**，未重试API。公开网页取得 commit：

`d4e4164c5e7d13e57391f8a932ffd81958995dcd`

不是已认证2020发表版本。作者代码仅静态阅读，**未导入、未执行**。

已保存：

- `greedy_public_page_attempt01`
- `greedy_src_listing_attempt01`
- `greedy_selected_sources_attempt01`
- `greedy_policy_utils_fetch_attempt01`

实际读过：

- README 全文。
- `policy_model_utils.py` **全部253行**：chunks `7eb849`、`4f69c4`。
- `train_policy.py` **29–109行**：`c00fcc`；其它仅首42行。
- `data_loading.py` **101–162行**：`bb3fbe`；其它仅首42行。
- `compute_snr.py` 仅首42行。
- MI notebook先合并输出被截断，cells1–2已独立完整补读 **ff8f58**；其余cell覆盖须检查实际buffer再登记。

关键实际发现：

- `get_policy_probs` 把已测列 logits 设为 `-1e7`，再 softmax。
- MI notebook使用正确负熵，`probs+1e-11`；原HTML缺负号不能当作者实现错误。
- `optimiser.step()` 在完整 acquisition loop 之后，符合累积轨迹更新文字；HTML伪代码层级不能当实际训练行为。
- **target 单独用完整GT的均值/std归一化**（data_loading157）；返回的是 `gt_mean/std`，并非 observed ZF统计。不要误称它们来自观测。
- 这些GT统计用于质量评分反归一化；需区分合法模拟评价与部署条件，不能仅凭字段断言泄漏。
- MI仍按mask屏蔽后的概率聚合，没有单独扣除可选集合变化。尚未复现论文曲线或训练效果。

一次读源码请求0–260超真实253行，actual **04f5a4 exit1**；之后查真实边界并完整读取，保留失败。

## 下一步与资源

1. **先保存本摘要、公开进度和所有可用 ROUND51 buffers**。已缓存键均以 `round51_` 开头；保留真实获取失败和人工失败。
2. 补读 Swin Algorithm S.1，建立两论文与选定源码的实际阅读 provenance。
3. 独立核查原生HTML表格算术、监督/患者分母、预训练费用与版本差异；写研究决定，避免把预训练或条件MI本身称新方法。
4. 独立审计新数值失败，若继续定位另版本，禁止放宽阈值或跳过失败启动真实GPU。
5. poll44317，不重启；完成后按原终态审核流程。
6. ROUND51 接 **7728** 增量归档、排除live、独立post-check；goal继续 active。

约束保持：CPU1/interop1/below-normal，RAM/disk十进制8GB；GPU启动8192MiB、allocator min(10%,2.4GB/total)、peak2.5GB/runtimefree4GB；数值3e-6、坐标3e-12、二值0、六医学gate不降。

cap：prep7MB/FOV20MB/accepted6MB/adaptive2MB/other22.8MB，六臂104156359预算不变。最近 guard `24228e` 内：free `8039014400`，guardedfree `8001396705`；adaptive约870KB、prep约6.35MB，之后少量增加。下一行动先fresh guard，不能新增大下载预算。

11开发患者19series；19998 parent仅开发诊断，strict LOPO cold-init；4已见验证9series不作独立确认；8未见确认12series及lockedIXI保持关闭。

