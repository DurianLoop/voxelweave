# 用户转交的上一模型接续摘要

来源：本轮用户消息。以下保存其研究状态、材料位置、边界和尚待完成的工作，属于用户转交内容，不表示本次重新执行或全部已完成。后续变化见 `SESSION_UPDATE_AUTHOR_ENSURE_MSLESSEG_2026-10-02.md`。

## 目标与约束

科学目标仍 **active，尚未达成**：持续研究、探索、验证，直到形成可发表且独立验证的 claim。上一目标回合是 **progress**（三篇风险正文核读、CPU 假设审计及独立复算）；当前回合也新增了实质来源证据。

- 工作目录 `D:\MRI`；PowerShell；Python `D:\conda\envs\MRI\python.exe`。
- 不使用 GPU、不控制用户终端训练、不读取锁定 IXI test、不改根环境或 `.gitignore`。
- 不新建/委派代理。
- 所有来源、代码、结果、失败、后续准备及公开对话保存到 `innovation`。
- 网络公开读取和 CPU 验证已授权，无须再次确认。

## 唯一活跃长任务

**继续同一个 unified exec session `83910`，不要重启或终止。**

命令：
`D:\conda\envs\MRI\python.exe -B innovation\experiments\vs_seg_full_volume_queue.py`

- 当前回合起始实际 poll 成功，**2026-10-02 11:19:59 UTC** 仍 live。
- 当时 **13/45** 七条件完成，216 的 HAT 完成；之后尚未再次 poll。
- 状态：`experiments/vs_seg_full_volume_queue/attempt_01.json`
- 日志：`experiments/vs_seg_full_volume_queue/inference_attempt_01.log`
- 合同 SHA256：`061d9f0912197321a62cbc0871195b34ecca7a3d20c9efa263bb19d0a729c7d5`
- 335 引用、45 CISS +1 TSE、七条件、主要 HAT−pipeline PCHIP 比较不变。
- 不评分动态子集；全部推断后自动逐患者 regenerate，再完整分析。202已有认证会复用。
- 两个主要患者 bootstrap CI 上限均 <0 才支持原联合方向。001/202的 HAT Dice 改善仍是反证。

**本回合其他工具全部已结束。** metadata session `51510` 已 poll 返回 exit 0；没有需要继续 poll 的其他 handle。

## 上一回合已完成归档

入口：

- `SESSION_HANDOFF_RISK_ACTION_QUEUE_ACTIVE_2026-10-02.md`
- `SESSION_UPDATE_RISK_ACTION_ASSUMPTIONS_2026-10-02.md`
- `SESSION_VISIBLE_DIALOGUE_RISK_ACTION_2026-10-02.md`
- `literature/2026-10-02_risk_action_fulltext_collision_matrix.md`
- `RISK_ACTION_ASSUMPTION_CPU_RESULT_2026-10-02.md`
- `RISK_ACTION_FOLLOWUP_PREPARATION_2026-10-02.md`

三篇 JATS：TIP2012 weighted SURE 参数选择、ICASSP2021 ENSURE、MRM2026 Rep2Rep。合成固定观测风险、协方差、重复噪声审计通过；独立标量 quadrature 270配置/40比较、差最大2.78e−16。不是患者证据/新理论。

上一回合最终 verify：29注册PDF、1223 evidence、1661本地链接，零错误；三个静态 stage manifest 均 write/read-only通过，189主冻结代码/协议未变。**本回合新增很多文件后，全局 manifest 现在需要刷新；本回合新 stage verifier/会话归档尚未写。**

## 当前回合：重要新增证据

### 1. Kuestner 作者仓库已找到、提交已固定

原 DOI `10.1002/mrm.30030` 正文仍没取得，但新 GitHub 精确 DOI 查询命中：

`https://github.com/midas-tum/recon_uncertainty`

公开 README 明确给出题名、五位作者和 DOI。GitHub API ref 403 rate limit后**没有重试API**；普通匿名仓库 HTML 成功，唯一 currentOid 固定：

`ce0e6ede3682a6901bfdd6ddc85b44ef28e72f3a`

已保存按提交读取的 README、训练入口、3个 dataset Python、dataset config、4个模型配置、losses.py。**没有导入或执行作者代码/安装/训练。**

证据目录：`literature/source_cache/author_repo_and_mslesseg_2026-10-02/`

索引：`public_page_attempt_01.json`、`pinned_code_attempt_01.json`、`followup_attempt_01.json`。

已读相关实现：

- `experiments/train_ensemble.py`：创建一个 data module，循环最多20个 checkpoint预测，然后按同 subject/slice 堆叠。mean、平均sigma、`mean(y**2)-mean(y)**2`组成uncertainty。
- `ensemble/dataset/transforms.py`：测试时 mask seed从filename数字生成并恢复随机状态；各成员同filename/config得到同一mask。训练时随机mask。
- 明确是 k-space ensemble UQ，**尚不能据此认证整篇论文/全仓库没有相同 context-switch**；论文仍缺正文，代码阅读层级单列。
- 接下来可读 `losses.py` 的 NLL和配置筛选，必要时公开 experiments目录树查看别的评价脚本；不要重试限流API或跑代码。

### 2. ENSURE 长稿正文与证明缺口显著推进

ICASSP正文 ref21链接 arXiv `2010.10631`：abs成功；v1 PDF **406**，失败保留，没有重复；abs明示最新 v4，2022-12-02，题名 *ENSURE: A General Approach for Unsupervised Training of Deep Image Reconstruction Algorithms*。

精确 TMI DOI：`10.1109/TMI.2022.3224359`。

Europe PMC认证正式 **2023**卷期，PMCID **PMC10210546**，作者 Aggarwal/Pramanik/John/Jacob。跟随页面明确的 `https://arxiv.org/html/2010.10631v4`，正文200成功，90104字符，带 MathML `alttext` LaTeX 提取。

文件：`literature/source_cache/author_repo_and_mslesseg_2026-10-02/ensure_long_attempt_01_maintext.txt`

**关键已核读：**

- 行编号 `[052]`–`[075]`，Lemma1及其证明。
- `[060]` 原文明确：**“Denoting the error … and ignoring its dependence on s, we obtain”**。
- Eq11b / `[062]`使用 **≈**。
- `[063]`明确 Q=平均projection、W²=Q；这澄清会议版权重表达。
- `[075]` weighted risk→MSE引用同样论证。
- `[240]`–`[260]` Appendix已读：Gaussian sufficient statistic、integration by parts、weighted divergence / LS交叉项。
- `[228]`不可逆W时不能估完整MSE；`[229]`训练每图mask固定、总体期望近似与真实训练之间gap。
- 这**明确支持“不能忽略mask依赖误差”这一条件提醒**。不要把之前合成反例改说成推翻整篇ENSURE或新定理；长稿自身写了该近似。
- 还需分块读 `[076]`–`[130]`实现公式，以及数据/实验/限制相关段落；不能称全部长稿已核读或已复现。

### 3. MSLesSeg 正文、官方 RAW/处理包及逐扫描 CSV 已取得

新源论文：*MSLesSeg: baseline and benchmarking of a new Multiple Sclerosis Lesion Segmentation dataset*。

DOI `10.1038/s41597-025-05250-y`，PMC12126551。JATS及23段正文/表图文字已核读，未逐幅看图。

文件：`.../author_repo_and_mslesseg_2026-10-02/mslesseg_attempt_01_maintext.txt`。

重要事实：

- 75人、115 scans/timepoints，T1/T2/FLAIR。
- 原T2平均层厚 **4.24±.92 mm**，FLAIR **2.61±.62 mm**；平均值不能证明所有扫描都不薄。
- 发布图像配准至 MNI152 1mm、182×218×182 LAS；这不是原生薄层真值。
- 标签在注册FLAIR上手工，T1/T2辅助；junior rater+两senior审查。
- 数据段53 train /22 test；technical-validation又写编号54–77 /24 test。**需官方名单核清，不能挑计数。**
- STAPLE consensus评价把参与算法/GT纳入共同参考，有自包含；只记录设计边界，不当“首次共同偏差”新意。
- 官方作者 preprocessing repo：`alessiarondinella/MSLesSeg-2024`，固定提交 `8daf9a5a59fae6740d7ef83db982f2434f3ce470`。
- `registration.py`已读：各模态独立FLIRT→MNI，再BET；未执行。

官方 Figshare：article **27919209 v1**, DOI `10.6084/m9.figshare.27919209.v1`，**CC BY4.0**。

| ID | 名称 | 大小 |
| --- | --- | ---: |
|52771814|MSLesSeg Dataset.zip|1473284755|
|53623946|MSLesSeg_RAW.zip|1295472528|
|53623967|MSLesSeg-2024-main.zip|10966086|
|54605591|mat_files.zip|148946|
|54605609|README.md|2059|

README明确 RAW与mat transforms允许把分割映回原图；**尚未核实际mat/grid/映射**。

### 4. 轻量 ZIP metadata探索实际完成（很有用，下一步优先）

预写：`MSLESSEG_PUBLIC_ZIP_METADATA_PLAN_2026-10-02.md`。

执行：`literature/inventory_mslesseg_public_zips_2026_10_02.py`。

结果：`literature/source_cache/mslesseg_public_zip_metadata_2026-10-02/attempt_01.json`。

- **125021 bytes** range传输，零错误。
- 精确206/Content-Range，单请求≤1MB，总≤10MB。
- 未整包下载、未解码任何影像像素。
- 全ZIP MD5未重算，不能称已验证整包。小README大小/MD5实际验证成功。
- 两个完整central directory保留每个成员offset、method、CRC、大小。

**注册包：464文件**，115 T1 +115 T2 +115 FLAIR +115 masks；4 CSV，全部实际读取、Zip CRC核验：

`registered_metadata_00_attempt_01.csv` clinical_data.csv；`registered_metadata_01_attempt_01.csv` patient_scanners_info_FLAIR.csv；`registered_metadata_02_attempt_01.csv` patient_scanners_info_T1.csv；`registered_metadata_03_attempt_01.csv` patient_scanners_info_T2.csv。

**RAW包：353 NIfTI.gz**，118 T1、**117 T2**、118 FLAIR；与注册115不一致，需按P/时间点键联结。

示例 `P1/T1/P1_T1_T2.nii.gz`，RAW的 T1/T2目录名是时间点，后缀才是模态。

**CSV内容和完整患者/时间点联结尚未读/计算，是直接下一步。** 如果CSV提供每扫描原始spacing/MRAcquisitionType，可先筛完整名单；如仍需非像素NIfTI头，先另写117个RAW T2冻结协议，勿挑例或默认全部厚层。masks仅注册包，原图映射仍要mat资格核验。

## 当前回合代码/来源入口

计划：`literature/2026-10-02_author_material_and_ms_source_plan.md`、`literature/2026-10-02_author_source_adaptive_followup.md`。

代码：`search_author_material_and_ms_sources_2026_10_02.py`、`fetch_author_repo_and_mslesseg_2026_10_02.py`、`read_public_author_pages_2026_10_02.py`、`fetch_author_source_followup_2026_10_02.py`、`fetch_kuestner_pinned_code_2026_10_02.py`、`inventory_mslesseg_public_zips_2026_10_02.py`。

首检索目录：`source_cache/author_material_and_ms_sources_2026-10-02/`。

- 两GitHub query，DOI1结果、泛题名157首5（后者不是157篇阅读）。
- EPMC MSLesSeg5、MSSEG-2首10/11、2023+CrossMoDA3。
- crossMoDA2026扩展 DOI `10.1016/j.media.2026.104282`仍摘要；2022多机构/2023routine surveillance，但不能据此独立于旧242或已取得hrT2 labels。
- 未下载其他候选正文或影像，MSSEG-2只是索引候选。

## 失败与实现注意

- PowerShell `ConvertFrom-Json`遇OpenAlex摘要的 `To`/`to`重复case键失败；用Python `json.loads`。
- 一次here-string Python输出遇GBK `\xa0`失败；可复用脚本已 `sys.stdout.reconfigure(encoding='utf-8')`。
- 多个合并输出截断，必须分块读取，不能算全读。
- 作者代码只存`.response`静态阅读，不import/执行。
- 尽量用明确文件路径，Windows rg不展开目录通配。
- PDF MRI Python无pypdf/pdfplumber/fitz；本回合没有成功新增PDF，ENSURE长稿改取明确HTML，未安装库/环境。

## 下一步顺序

1. 实际poll同一 **83910**。
2. 读4个MSLesSeg CSV，按全部central-directory名单核115/117、患者75/编号77、原生T2每扫描参数；保存CPU资格计算与独立复查。不要凭平均层厚判全部不合格。
3. 若CSV显示薄层线索，预写全部RAW T2非像素header方案/资格阈值与失败，利用已有offset/range边界；若没有，保留来源不合格/未认证原因，勿下载整包或改MNI真值合同。
4. 补核ENSURE长稿实现/实验/限制，明确mask误差依赖近似已经在原文出现；写正式阅读结果，更新后续条件但不改旧历史报告。
5. Kuestner固定代码继续核NLL/测试mask/ensemble汇总；保持“作者代码核查，论文正文仍未得”层级。
6. 本回合尚缺 SESSION_UPDATE / VISIBLE_DIALOGUE / HANDOFF、新静态stage verifier和README入口；完成后刷新全局archive与read-only。运行中的VS-SEG整体manifest仍不是最终全量验证。
7. 45例推断和regenerate全部完成后，审原主比较及敏感性，再跑 `experiments/vs_seg_selection_sensitivity.py`。保留主要失败，不升次要成功。
8. 已评分45不能作为新方法未见确认；尚不训练收益头。科学目标保持active。

## 尚需归档的本回合公开消息

1. “我会继续推进到可发表主张的实证门槛。上一轮取得三篇正文并完成 CPU 假设审计，属于实际进展；这一轮先确认同一患者队列仍在运行，再补查最直接的重合工作和确认数据来源，新增记录继续保存到 D:\MRI\innovation。”
2. “同一队列仍然活跃，当前继续处理第 216 例。等待完整结果期间，我会补两处关键缺口：寻找 Kuestner 2024 的作者公开材料，核清方法是否重合；筛查新的高分辨率病灶数据，判断是否能用于后续独立确认。不同模态、重复病例和处理后网格都会明确标注。”
3. “找到了 Kuestner 2024 的作者代码仓库，并已核对题名、DOI 和作者，按具体提交保存公开材料。这能补强方法核查，但还不能替代未取得的论文正文。

   MSLesSeg 的正文则显示：原始 T2 平均层厚约 4.24 mm，公开影像经过 1 mm MNI 配准。目前不能把这个 1 mm 网格直接当作原生薄层参考；我会继续核官方文件和逐扫描信息，避免仅凭平均值排除可能的薄层子集。”

用户最新请求是做上下文checkpoint；不要把它当取消科学目标。
