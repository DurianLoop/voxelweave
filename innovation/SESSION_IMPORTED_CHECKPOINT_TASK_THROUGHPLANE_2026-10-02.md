# 用户提供的接续摘要原文

以下内容是本轮开始时用户提供的前一模型工作摘要，作为继承上下文保存，数字均属于当时的状态，不是本轮末状态。前缀说明：Another language model started to solve this problem and produced a summary of its thinking process. You also have access to the state of the tools that were used by that language model. Use this to build on the work that has already been done and avoid duplicating work. Here is the summary produced by the other language model, use the information in this summary to assist with your own analysis:

## 持续目标与约束

用户要求持续基于 MRI 既有项目读论文、找创新并验证，直到获得可发表且独立验证的 claim；所有对话、来源、代码、结果、失败及准备保存在 `D:\MRI\innovation`。**目标仍 active，尚无可发表 claim，不可标记完成。**

- 工作目录 `D:\MRI`，PowerShell，日期 2026-10-02。
- Python：`D:\conda\envs\MRI\python.exe`。
- 不使用 GPU、不控制用户终端训练进程、不读取锁定 IXI test、不改环境或 `.gitignore`。
- 不新建/委派子代理。
- 公开来源下载、CPU 验证及本地准备已有授权，无须重新确认。
- 上一目标回合是实质 progress；当前回合确认了活跃任务，并新增近邻检索及全文来源。

## 最重要：一个长队列正在运行

**不要重新启动或终止它。**

- 命令：`D:\conda\envs\MRI\python.exe -B innovation\experiments\vs_seg_full_volume_queue.py`
- unified exec **session ID `83910`**。
- 本回合实际 `write_stdin` 确认 handle 仍 live；日志也持续产生新结果。
- 状态：`innovation/experiments/vs_seg_full_volume_queue/attempt_01.json`
- 子进程日志：`.../inference_attempt_01.log`
- 最新观察：**202、203 两名主病例全部七条件完成，204 native 完成**；2/45 主病例完成，研究不完整。
- 驱动器先完成固定 45 CISS + 1 TSE 推断，再顺序调用逐患者 verifier `--regenerate`；有效的 202 核验复用。最后自动写完整结果 JSON/Markdown。
- 剩余推断初估约 7 小时，另约 2 小时多复查；不是实测完成时间。
- 除 `83910` 外，**本回合所有查询/下载命令均已结束**。
- 轮询同一 session；观察超时不等于结束，不可因此重启。

交接入口：
`innovation/SESSION_HANDOFF_VS_SEG_CPU_QUEUE_ACTIVE_2026-10-02.md`

## 冻结研究与已验证成果

新队列合同：
`innovation/experiments/vs_seg_full_volume_cohort/run_contract.json`

SHA256：
`061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5`

冻结 335 文件、软件版本、权重、来源及标签。**不改冻结文件。** 协议：
`innovation/VS_SEG_FULL_VOLUME_COHORT_PROTOCOL_2026-10-02.md`

- 主名单固定 45 ORIGINAL 3D CISS；TSE VS-SEG-248 单列。
- 七条件：native、raw linear、raw PCHIP、pipeline linear、pipeline PCHIP、HAT、SwinIR。
- 唯一 phase-0 x4 观测；保留观测层逐位一致；恢复全部内部余数 1/2/3；尾部复制末观测，不进入图像目标。
- 主比较只为 **HAT − pipeline PCHIP**。
- 支持域 NMSE 和完整体积原 JSON Dice 的患者 bootstrap 95% 区间上限都 <0，才支持候选“图像改善、任务降低”联合方向。
- 5000 draws、seed20261012；45 人全部完成前不作正式统计；不得改挑 SwinIR 或删小病灶。
- raw PCHIP、RT 标签、观测范围、1 mm 边界带、空预测、病灶 NMSE 两种汇总均保留。

已完成：

1. 通用重建与 001 七条件保存输出逐位一致；一条件分割逐位一致；448 八窗技术探针通过。
2. 边界物理点全对距离、不同边界点数、轴置换、空值、独立 bootstrap 循环通过。
   - pooled ASSD、方向均值平均 MASD、pooled HD95 明确区分。
   - 旧检查和实现快照保留；修订在独立推断前完成。
3. 合成 45/44 人检查验证冻结统计：只有双负且完整才通过，44/45 不计算正式分析。
4. 202 七条件推断 **574.707 秒**，独立输出核验与全部重建再生成 **180.794 秒、零错误**，CUDA false。
   - pipeline PCHIP：NMSE `0.0014703662380717488`，原 JSON Dice `0.8714048254671838`
   - HAT：NMSE `0.0011530626187039761`，Dice `0.8871035058430717`
   - 主差：NMSE `−0.0003173036193677727`、Dice **`+0.015698680375887952`**
   - **这是反证，未支持任务损失方向；不改变主比较。**
5. 45 人实际旧规则覆盖与独立向量化复查全部通过：
   - 原 JSON 19/45，RT 18/45；加旧 literal TV 名称限制仅 16/45、15/45。
   - 原 JSON 入选病灶体积中位 **5.228 cm³**，排除者 **0.701 cm³**；阳性层中位15/8。
   - 这是本项目旧规则的覆盖偏向，**未验证方法排名变化，不能推广为全领域偏差**。

结果入口：
- `VS_SEG_FULL_VOLUME_COHORT_PROGRESS_2026-10-02.md`
- `SESSION_UPDATE_VS_SEG_CPU_COHORT_2026-10-02.md`
- `GPU_FOLLOWUP_TASK_FIDELITY_PREPARATION_2026-10-02.md`
- `SESSION_VISIBLE_DIALOGUE_VS_SEG_CPU_COHORT_2026-10-02.md`
- `README.md`

## 上一回合新增文献

已取得并重点核读三篇指标方法全文 XML/BioC：
- Reinke2024，DOI `10.1038/s41592-023-02150-0`
- Metrics Reloaded2024，DOI `10.1038/s41592-023-02151-z`
- Taha2015，DOI `10.1186/s12880-015-0068-x`

报告：
`literature/2026-10-02_task_metric_reading_and_innovation_limits.md`

广义任务感知重建、指标失真、小病灶偏差、小波、残差 flow、误差头/conformal 已有先例，不能包装为新意。Fischer2023、Morshuis2024、SliceBridge2026 已有全文核读。Kuestner DOI `10.1002/mrm.30030` 全文仍未取得，只能摘要层比较。

## 本回合新增检索：需要接着读正文

计划：
`literature/2026-10-02_task_throughplane_collision_search_plan.md`

脚本：
`literature/search_task_throughplane_collisions_2026_10_02.py`

索引：
`literature/source_cache/task_throughplane_collision_2026-10-02/attempt_02.json`

两个 Europe PMC + 两个 Crossref 查询，共返回 **25+5+10+10=50条**，不是50篇全文/去重论文。全部标题已初筛，若干相关摘要已读。检索有边界，不构成系统综述或优先权证明。

第一尝试 GBK 读写失败；已修正 UTF-8/stdout，保存 `search_v1_snapshot.py` 和 attempt01。原响应未删。

筛出尤其重要的直接近邻：

1. **Katayama2026 CISS / vestibular schwannoma**
   - DOI `10.1007/s12194-026-01073-7`，PMC13546317。
   - 39例，**同一 raw data** 的 Canon SR-DLR/DLR/ZIP，三阅片者、病灶/脑神经显示、ERD/ERS/SNR/CNR。
   - 摘要已读；全文已取得，**尚未核读正文**。
   - 最可能限制“首次 CISS 肿瘤 SR 临床/任务评价”的主张。

2. **Zhou2022 brain tumor SR / slice interpolation**
   - DOI `10.1002/acm2.13758`，PMC9680577。
   - 摘要：237患者，每人一张 T2-FLAIR，ESRGAN派生 MRBT-SR-GAN；BRATS Dice .724→.786；还展示 slice interpolation。
   - 全文已取得，**正文尚未核读**。需查真值、LR构造、分割训练/评价以及插值实验是否与分割实验相同。

3. **Fetal SR biometry/volumetry bias2025**
   - DOI `10.1007/s00247-025-06347-7`，PMC12513972。
   - 全文已取得，**正文尚未核读**。
   - 结构索引显示84健康胎儿、252重建、SVRTK/NeSVoR等、多个读者及体积比较，数据非公开。不能仅从结构索引称已全文阅读。

4. **Wintergerst ISBI2025 spinal lesion SR**
   - DOI `10.1109/isbi60581.2025.10981088`，PMC13130011。
   - 摘要：53 MS患者，SR/linear isotropic增强分割敏感性，但 lesion volume 与 EDSS 无显著关联。
   - **全文尚未取得**：Europe PMC XML500；NCBI BioC HTTP200其实是 `[Error] No result...` 非XML，已识别并保留。可继续尝试公开 PMC HTML/PDF/arXiv/作者仓库；勿称全文已读。

其他仅摘要/元数据候选：
- `10.1109/tmi.2025.3628113`，*Multi-Contrast MRI Super-Resolution in Brain Tumors: Arbitrary-Scale Implicit Sampling and Unsupervised Fine-Tuning*。APTw肿瘤、5T FLAIR、参考高分辨率模态及 test-time fine-tuning；非相同单T2信息预算。
- `10.1016/j.compmedimag.2026.102786`，*Self-supervised isotropic reconstruction for abnormality detection in anisotropic MRI*。2225 OAI knee scans、8:1 TSE、多视图GAN和健康counterfactual diffusion，含下游分割；仅摘要。
- `10.1016/j.mri.2026.110675`，*Target-driven acquisition and super-resolution reconstruction for magnetic resonance imaging*。Crossref元数据，2026年7月；尚无摘要/正文。
- `PMC7852179` sparse self-attention slice interpolation 是 **电子显微镜**，不是MRI，不应当MRI实证来源。

## 新全文文件与下一步阅读方式

脚本：
`literature/fetch_task_throughplane_fulltexts_2026_10_02.py`

索引：
`literature/source_cache/task_throughplane_fulltexts_2026-10-02/attempt_01.json`

同目录有以下 JATS XML、`*_fulltext.txt`、`*_maintext.txt`：
- `ciss_vs_2026`：maintext **38,551字符**
- `brain_tumor_slice_2022`：**39,943字符**
- `fetal_srr_bias_2025`：**44,312字符**

maintext按 `\n\n` 分段，包含 `[title]`、`[p]`、`[table-wrap]`、`[fig]`；嵌套表格/图注可能重复。最后工具只打印了段落索引，输出被截断，**不能据此称正文核读完成**。建议每次读取10–20k字符，避免一次输出截断。

CISS段索引关键：
- 6：Patients
- 11：Acquisition
- 13：same raw data reconstruction
- 15：SR-DLR principles
- 17–29：reader evaluation
- 39–49：ROI/metrics
- 51：statistics
- 54：patient characteristics
- 56–58：qualitative results/Table1
- 73–75：quantitative/Table2
- 后续discussion/limitations须重新列索引读取。

全文抓取第一版因 spinal HTTP200非XML而 ParseError，未写最终索引；三篇有效全文其实已下载。已保存 `fetch_v1_snapshot.py`，修订 fetch 内XML验证后成功写索引。此失败还需纳入本回合对话/失败记录。

## 下一步顺序

1. 继续轮询 live **83910**，不重启、不改冻结代码、不做动态子集正式推断。
2. 核读上述三篇新正文和完整表格，优先 CISS2026、brain tumor2022；写明确方法级碰撞矩阵。
3. 尝试 spinal2025 的公开正文路径；不可用仍保留摘要层，继续其他工作，不把整个目标标 blocked。
4. 准备覆盖子集与全队列比较的**次要探索**，与冻结主要分析严格区分，不能以首例方向改主要问题。
5. 长队列全部输出、自动复查完成后，审查主要联合判据、raw PCHIP、双标签/范围/边界带、空值及病灶 NMSE两种汇总；再判断新意，失败则保留并继续探索。
6. 本回合新对话、查询/下载失败和来源尚未写独立 SESSION 文件，需补归档；也保存本 checkpoint。
7. 两个 manifests 当前因增量文件而已过时。队列日志在变，避免把运行中快照当最终全量验证。结束后再刷新：
   - `innovation/literature/verify_vs_seg_stage_archive.py --write` / verify
   - `innovation/verify_archive.py --write` / verify
   - stage verifier此前只显式纳入 task_metric 文件，**新增 task_throughplane 来源/报告需扩展纳入**，或单独写阶段清单。
   - 上回合启动前核验：10,546文件、3,126,906,806字节；全局29注册PDF、1155 evidence、1531链接，零错误。新XML不增加PDF注册计数。

不要把启动长队列、成功的软件测试或取得论文全文等同于实现“可发表 claim”。
