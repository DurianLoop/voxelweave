# 本次用户提供的接续摘要

以下保存本次可见用户消息所附前模型交接内容，描述交接当时状态；后续实测见本批SESSION_UPDATE与结果文件。该摘要不能代替不可见历史对话的逐字原文。

目标仍 **active**：持续研究至获得可发表且独立确认的 claim，尚未达成。本次是 compaction，不是停止研究。上一轮属于实质进展。

### 约束与环境

- 工作区 `D:\MRI`；新增内容全部放 `D:\MRI\innovation`。
- Python：`D:\conda\envs\MRI\python.exe -X utf8 -B`。
- 不用 GPU，不动用户终端训练，不读 locked IXI test，不改根环境或 `.gitignore`，不新建/委派代理。
- CPU 单线程、自身低优先级；磁盘至少 15 GB、可用内存至少 8 GB。
- 原45 CISS及MC-RC已见8开发患者不能作为未来完全未见确认。科学独立确认仍0。

### 前阶段已完整完成，不重跑

入口：

- `innovation/SESSION_HANDOFF_ORDER_RISK_AND_PHASE_2026-10-03.md`
- `innovation/INNOVATION_DECISION_AFTER_POST_TASK_AND_PHASE_2026-10-03.md`

完整45人 JSON full Dice：raw `.74459750`、pipeline `.65476150`、post `.65284400`。order_rms风险候选、残差相加、anchors带宽恢复解释均已失败停止。

前阶段8篇重点正文/415证据块及实验归档已验收。首次归档因 DOI 大小写误判失败，修正后通过：

- 首失败：`SESSION_ARCHIVE_VERIFICATION_ORDER_RISK_AND_PHASE_2026-10-03.json`
- 成功续验：`SESSION_ARCHIVE_VERIFICATION_ORDER_RISK_AND_PHASE_2026-10-03_attempt_02.json`
- 28历史检查＋6剩余检查通过；当时全局29个主注册PDF、1987证据文件、2336链接，errors=[]。
- **该清单尚未同步本次新阶段内容。**

### 本次新增 CPU 实验

事前方案及脚本：

- `TASK_STATS_SWAP_CPU_PILOT_PLAN_2026-10-03.md`
- `experiments/task_stats_swap_cpu_pilot.py`

固定202/203/204，raw/post图像×raw/post整volume mean/std四格。原两个对角格复用旧已复核预测，只新增两个交叉格，共 **6次CPU前向**。不改重建图像、anchors或tail，只交换任务归一化统计。

**producer session56242 已实际 exit0**，全部6预测通过保存指标核验：

- `experiments/task_stats_swap_cpu_pilot/attempt_01.json`
- `run_contract.json`
- 六个记录、预测NPZ、verification JSON、`stdout.jsonl`
- 全部30固定配对端点已生成。

JSON full结果：

| 比较 | 三人平均 ΔDice |
|---|---:|
| post_rawstats−post_poststats | +.001410324010 |
| raw_poststats−raw_rawstats | +.000937623111 |
| post_rawstats−raw_rawstats | +.034770117763 |
| post_poststats−raw_poststats | +.032422170642 |
| normalization_image_interaction | −.002347947121 |

主要比较逐人：202 `−.000768344059`、203 `+.002298443881`、204 `+.002700872208`。RT主要均值 `+.001523343559`。

**关键解释限制：这三人旧 post−raw 的JSON full均值为 +.033359793753，RT +.035143371676，与全45人的负均值相反。不能用本三人解释全队列损失、宣称归一化恢复或计算唯一“归因百分比”。** 三人是此前固定技术预检名单，不能改挑患者；全部标签/域/交互保留，无bootstrap。

### 当前唯一待核实进程

已启动最终独立复核：

- 脚本：`experiments/verify_task_stats_swap_cpu_pilot.py`
- **session79154：最后一次工具返回确认 live，尚未再次poll。**
- 预期输出：`experiments/task_stats_swap_cpu_pilot/independent_inputs_domains_and_all30_estimates.json`

它检查冻结输入SHA、六交叉网络输入的手工NumPy重放、六对角输入SHA、四格×三人×两标签×三个采集域的72 confusion单元及30 Fraction端点。没有新前向。

**下一步先poll79154；不要因为超时重启。** 若失败保留首proof/traceback，再修正独立追加尝试。

### 本次新增论文与技能

已应用 PDF 技能：

`C:/Users/user/.codex/plugins/cache/openai-primary-runtime/pdf/26.904.11930/skills/pdf/SKILL.md`

原环境无 pypdf/pdfplumber/fitz；使用现有 MiKTeX 的 `pdftotext.EXE`、`pdftoppm.EXE`，没有安装依赖或修改环境。

取得三份公开原始PDF及逐页文本：

目录：`literature/source_cache/masked_normalization_primary_2026-10-03/`

1. **Region Normalization for Image Inpainting**，AAAI2020，DOI `10.1609/aaai.v34i07.6967`。
   - `region_normalization.pdf`，8页。
   - 已重点读全篇正文；实际查看第3页公式/图。
   - 直接占位：未知/损坏区域改变全空间统计，按已知/未知区域分别归一化；RN-B早层、RN-L后层。Places2/CelebA实验，无MRI任务。
   - 原文示例统计假设不能当任意MRI解剖区域的定理。

2. **Image Inpainting for Irregular Holes Using Partial Convolutions**，ECCV2018，DOI `10.1007/978-3-030-01252-6_6`。
   - `partial_convolution.pdf`，16页。
   - 实际重点读3、5–9、12–14页；第5页公式已视觉查看。
   - 第9页已明确讨论holes污染BN mean/variance及冻结encoder BN。
   - masked/reweighted convolution、mask更新、observed compositing均有直接先例，不可宽称创新。
   - 不要声称完整16页均已核读或作者实验复现。

3. **Normalization-Equivariant Neural Networks with Application to Image Denoising**，NeurIPS2023，DOI `10.52202/075280-0249`。
   - `normalization_equivariance.pdf`，23页。
   - 已读1–10页及附录第21页；第3页已视觉查看。
   - affine kernel sum=1＋channel sort pooling；padding限制、BN/attention不兼容、更长训练等条件。
   - **第21页Table6已明确“logit等变→argmax标签不变”并有分类实验，且norm-equiv分类误差较差。不能将这个推导或简单分类应用当新意。**
   - 未读全部附录/另附supplement，未复现实验。

获取/提取记录：

- `attempt_01.json`：PDF下载成功但因pypdf缺失未提取，失败保留。
- `extraction_failed_attempt_02.json`：NeurIPS链接解析仅接受双引号，遇单引号失败；旧脚本快照保留。
- `extraction_attempt_03.json`：HTMLParser修正、Poppler提取成功，绑定三PDF及文本SHA。
- `rendering_provenance.json`：三个PNG已实际通过 `view_image` 查看，但其 `visual_review_completed` 仍false，**需要另追加真实阅读/视觉登记**。
- `_pages.json`、`_poppler_layout.txt`均在同目录。
- 检索原响应：`source_cache/masked_normalization_restoration_search_2026-10-03/`。
- 尚未生成本批正式阅读报告或reading_provenance。

### 尚需完成

1. 核实79154最终状态，完成所有输入/端点复核。
2. 生成统计互换正式报告、全部30端点/90逐人差CSV及采集域结果，绑定provenance；突出三人方向与全45不同、效应小且混合。
3. 写三篇论文正式阅读笔记/阅读登记，准确记录已读页和三页视觉检查；保留两个提取失败。
4. 更新创新判断：**anchor-only统计可保留为控制，但“排除未知区域统计”“归一化等变”都有直接先例，不再当独立创新。** 不用三人微小改善挽救旧失败。
5. 后续选择需有区分力：可做全45无需前向的统计漂移审计或真实新来源资格核验；不要盲目扩展失败干预、重复旧神经队列或宣布新方法。
6. 归档当前阶段对话、用户本次compaction请求、上述handoff；当前阶段记录还未写入新的SESSION文件。旧README仍是前阶段入口。
7. 更新静态清单与全局证据/链接核验，保留历史验收记录，不覆盖首失败。全部新增文件仅innovation。

最近公开消息已说明：6次统计互换完成、最终复核启动，三人原post−raw为正与45人相反；新论文进一步收紧归一化新意。整体科学目标保持active。
