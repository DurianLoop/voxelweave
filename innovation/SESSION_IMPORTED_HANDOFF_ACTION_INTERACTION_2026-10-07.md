# User-provided continuation summary (verbatim body)

## 目标与约束

长期 goal **active**：持续研究、读论文和验证，直到形成可发表 claim；不能把软件资格或显著性当作完成。用户允许 GPU，但**不得操作其终端训练进程**。

- 新增文件仅写 `D:\MRI\innovation`，不改根环境、`.gitignore` 或冻结证据；变化另立版本。
- 不委派代理。
- PowerShell；Python：`D:\conda\envs\MRI\python.exe -X utf8 -B`。
- 当前病灶任务划分：11开发患者/19series，4已见验证/9series，8保留确认/12series。
- 确认 `030/029/019/028/031/026/027/015` 和 locked IXI test 继续关闭。
- 本轮用户要求压缩上下文，不是取消研究目标。

## 第一优先：继续已有训练

**session `99542` 仍 live，不能重启。**

入口：

```text
innovation/experiments/run_mc_rc_3d_19series_common_init_cpu_wall_v2_2026_10_07.py
--attempt 02 --stop-after 19998 --wall-limit 108000
```

最后实际 poll 是本续作开始时的 **chunk `925441`**：

- native 提交 **3762** 更新。
- invocation02 新更新3663，累计正式墙钟 **7658.1113秒**。
- 工具返回同一 live session。
- PCHIP 最近实际历史快照仍99；之后未重新读取，不能冒称实时步数。
- 原训练继续共同初始化、同GT/增强流、AdamW LR/WD均 `.0001`，各19998/总39996。
- CPU4 intra-op/1interop、float32、below-normal；累计30h资源补充、8GB RAM/磁盘余量、训练保存250MB不变。
- 不读取中间 MRI 任务效果，不中途换设备/精度。

最近实际 GPU 查询仍上阶段 **17:50:03.129**，chunk `d297f5`：free1394MiB/total24455MiB/util59%，未达既定8,000,000,000bytes启动门槛。本续作尚未新查询。

最终56FOV主评价/独立重放入口已准备，**未执行真实最后模型评价**。只有训练真实terminal exit0、两臂最后19998权重冻结后，才能写原 final-exit receipt并执行。详细字段和 gates 见：

```text
innovation/experiments/mc_rc_3d_19series_final_eval_2026_10_07.py
innovation/experiments/evaluate_mc_rc_3d_19series_common_init_final_2026_10_07.py
innovation/experiments/verify_mc_rc_3d_19series_common_init_final_2026_10_07.py
```

## 上一 goal turn：实质进展，已冻结

新增核读3篇原文方法/主要实验：

- DeltaCNN，CVPR2022，PDF10页。
- SIGE，arXiv2211.02048v4，2023-09-13扩展作者稿，21页。
- DeepCache，CVPR2024，11页。
- 取得42物理页文本，完整选定核读29页及SIGE限制/引文段落，3关键页实际render/view_image；不称全部PDF阅读或作者实验复现。
- DeepCache arXiv响应超过32MB，首 acquisition actualexit1保留；CVF alternate成功，actualexit0。

创新判断收紧：**SIGE已有复用原图IN/GN统计；DeepCache已有跨扩散步高层cache和非均匀刷新。** 不把它们单独当首创。收益头亦已有Madras/Mozannar及SafeRestore/MoEDiff先例。

真实单001 observed-only局部缓存资格：

- 旧已认证 PCHIP_last1024，非当前中间模型。
- native256×256×30，共1,966,080体素。
- z14，r/c125:132，49输入体素归一化+.25；anchors和统计不变。
- physical243体素改变；受影响tile5、6、9、10。
- 保留原batch pair须重算tile4–11，**4forward vs完整8**。
- 全tile/physical/native概率SHA相同，误差0、阈值差0；原生产函数也逐位一致。
- 11gates true；session72885/chunka23c43 actualexit0。
- 整项资格真实28CPUforward/56tile，baseline64MiB概率RAM缓存；无GT、无任务评分、无训练/CUDA。
- anchors任务概率260801体素微小变化，max4.0054e-5；四域二值预测均不变。不能解释为病灶收益或只归因IN。
- cache初始化8forward，K个同支持动作总8+4K，对比8K，**至少3动作才省总调用**；单次计时不是benchmark。

全19开发series合成mask成本准备，session30385/chunk223f0f exit0：

- 1139tiles / 572完整forward。
- 中心单缺层ROI宽7/32/64分别需99/145/188缓存forward。
- 19/17/17series有节省；001/UID尾369177和另一UID尾103688在宽32/64无节省，保留全分母。
- 仅metadata+合成支持，无MRI/GT/model forward；不是19MRI等价或疗效资格。
- 全19概率cache4.777GB，逐series最大805306368bytes（768MiB）。

归档 **chunk `396060` actualexit0**：

- 79新增stage files，累计845证据，新增37,806,634bytes。
- 前763冻结证据SHA全不变。
- archive完成不等于训练完成。

关键入口：

```text
innovation/SESSION_RESULT_INCREMENTAL_INFERENCE_2026-10-07.md
innovation/SESSION_HANDOFF_INCREMENTAL_INFERENCE_LIVE_2026-10-07.md
innovation/INNOVATION_DECISION_AFTER_INCREMENTAL_INFERENCE_READING_2026-10-07.md
innovation/MC_RC_3D_LOCAL_EDIT_CACHE_QUALIFICATION_RESULT_2026-10-07.md
innovation/literature/2026-10-07_incremental_inference_primary_reading.md
innovation/literature/incremental_inference_stage_manifest_2026-10-07.json
innovation/SESSION_CHECKPOINT_RECEIPT_INCREMENTAL_INFERENCE_2026-10-07.json
```

上阶段可见对话、用户完整接续摘要、最终答复和冻结后观察均已另存，不修改它们。

## 当前续作的新发现：明确两条研究线，不能把全项目确认人数写成0

本续作目前**尚未新增文件、论文或实验**，只实际poll训练并复核原项目/旧科学证据。

根README确认项目本身就是**MRI体数据切片间SR**，HAT/SwinIR等2.5D工程与目前through-plane研究一致。未读用户训练日志或locked测试像素。

旧 MIRA 线已有独立来源证据：

- 原fastMRI权重对：MSValid84人/479目标，ΔO +19.7565pp，CI19.3276–20.1605，84/84正。
- 公开来源稿改用IXI权重：同MSValid84人是结果后同患者跟进，不能新增独立患者。
- ReMIND62/63人、248目标，+26.3999pp，发布DICOM含MPR。
- UPENN处理后374人/1496目标，+28.1156pp，全部derived/secondary；源选择受前两阳性启发。
- 不可把匿名来源简单相加当完全独立患者；不证明原始采集身份、临床或可部署风险。

**这些旧证据已经被严审，仍未过可发表门槛，不能仅因84人确认就宣布goal完成。**

最关键既有反证：

- PCHIP/linear解析配对在MSValid/ReMIND产生更大ΔO（29.2470/30.9585pp），否定深架构特有机制。
- 同几何后合成噪声仅极小效应，不能分解原上下文对照。
- 外部响应增量预测P25–P84为负，部署guard失败。
- MSD483病灶ROI解析控制同样有区域ΔO；神经相对解析差区间跨零。
- 同observed强PCHIP远优于相应神经病灶重建；临床增益未证。
- 原始身份/上下文/几何共变未隔离，Kuestner全文缺口、环境清洁复现/稿件同步等仍未闭合。
- 所以**“确认患者0”仅指当前3D病灶效益线**，不能概括所有MIRA历史实证。后续另立范围澄清，不回写冻结报告。

已读定位文件：

```text
innovation/MIRA_CLAIM_AUDIT_2026-09-30.md
innovation/MSVALID_EXTERNAL_CONFIRMATION_2026-09-30.md
innovation/MSVALID_CONFIRMATION_PROTOCOL_2026-09-30.md
innovation/PUBLIC_ONLY_CLAIM_REVIEW_STRESS_TEST_2026-10-01.md
innovation/CLAIM_PUBLICATION_GATE_2026-09-30.md
innovation/PUBLIC_ONLY_MIRA_MANUSCRIPT_DRAFT_2026-10-01.md
```

注意 publication gate 很长：读了前26行核心表格；先前合并全文输出有截断，不能称整个长文件已完整核读。公开英文稿目前本续作只读前70行；旧PDF仍两来源快照。

## Kuestner 缺口：不要重复已有工作

精确论文：

> Predictive uncertainty in deep learning-based MR image reconstruction using deep ensembles: Evaluation on the fastMRI data set  
> DOI `10.1002/mrm.30030`，PMID38282254，OpenAlexW4391320131，TUM mediaTUM1752940。

已有 Oct1/2：

- Wiley full/epdf/pdfdirect返回403。
- OpenAlex content XML401；不尝试凭据或绕过。
- EPMC无PMC全文。
- TUM页面无PDF，猜测doc URL返回HTML。
- arXiv有界题名查询未命中。
- **作者代码已于Oct2取得/核读**，不要把它当新发现：
  - repo `midas-tum/recon_uncertainty`
  - 固定commit `ce0e6ede3682a6901bfdd6ddc85b44ef28e72f3a`
  - README、train_ensemble、dataset三个文件、losses和4模型config。
  - test mask由filename seed固定，同test loader遍历checkpoints；ensemble mean/variance；异方差NLL。
  - GitHub API ref曾403 rate-limit，旧流程停止该API，不重试绕过。
- 已核作者代码不等于取得论文全文，不能排除未读段落有精确上下文切换。

本续作刚读：

```text
innovation/literature/2026-10-01_kuestner_fulltext_access_audit.md
innovation/literature/2026-10-02_author_code_ensure_long_and_mslesseg_reading.md
innovation/literature/2026-10-02_author_source_adaptive_followup.md
innovation/literature/2026-10-02_operator_multicontrast_abstract_access_result.md
```

没有启动新的网络请求。可考虑**尚未查过的合法公开作者/机构全文渠道**，但避免重跑旧403/401、重复作者代码阅读或以索引替全文。公开GET可用 `urllib.request.build_opener(urllib.request.ProxyHandler({}))`，只针对本次请求，不改系统代理；环境默认代理127.0.0.1:9无效。

## 当前续作应保存的两条实际公开进度

尚未建立本续作dialogue文件，应另立新文件保存：

1. “上一轮取得了三篇原文和真实缓存资格证据，属于实质进展。本轮继续接续同一训练进程，并复核原项目的训练与退化设置，收紧下一步的公平对照，避免把计算提速当成病灶任务收益。”
2. “复核旧资料发现，MIRA 机制研究已有 84 位 MSValid 患者的单配对外部确认。此前‘确认患者0’指当前病灶任务效益线，不能概括整个项目。本轮也会核查这条既有机制 claim 的证据边界与剩余缺口；19series 训练继续。”

## 清晰下一步

1. 先实际poll99542、查询GPU；同handle继续，不因超时重启。
2. 为本续作建立新记录，保存上述范围澄清和可见文字；先前79文件核心冻结不可修改。
3. 结合旧MIRA严审的真实反证选择有效下一动作，避免重新证明已知现象或只是整理表格。Kuestner正文渠道尚缺，但作者代码已读；不能把重复访问当进展。
4. 当前病灶效益路线仍优先完成充分适配，再按原完整56FOV评价与独立重放决定是否有剩余修正收益；未完成训练时不写terminal receipt、不生成“新疗效”。
5. 后续公平强PCHIP、同observed直接任务、SR/task配方、已知defer/双路径成本/random对照，真实联合动作完整FOV收益和全部成本；有残余才学习策略。
6. goal保持active。当前可发表claim未证实；不要因为旧统计确认或新软件资格就标complete。
