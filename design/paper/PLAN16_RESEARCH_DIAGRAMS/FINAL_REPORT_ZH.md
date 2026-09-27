# Plan 16：两篇论文科研框架图重绘与替换

完成日期：2026-09-10。已完成两篇主稿图 1 的生成、科学语义检查、替换、LaTeX 重建及页面检查。两张新图均位于第 2 页。

| 论文 | 当前 PDF | 独立原尺寸图片 | 最终篇幅 |
|---|---|---|---|
| CVPR | [main.pdf](../CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.pdf) | [新框架图 PNG](generated/p16_cvpr_framework.png) | 9 页，技术正文止于第 8 页 |
| TMI | [main.pdf](../TMI/TMI_ARCH_GENERALIZED/main.pdf) | [新框架图 PNG](generated/p16_tmi_framework.png) | 11 页，原版为 10 页 |

## 1. 实际使用的工具

使用 **内置 `image_gen.imagegen`**，按 imagegen 技能执行。用户要求的名称为 **image2.5**；当前工具没有型号选择参数，也没有返回后端型号，因此不能声称已经验证使用了 image2.5。此限制已在开始工作时说明。本轮没有使用外部 CLI 或另行配置 API 密钥。

CVPR 图生成一次；TMI 图初次生成后进行了两次针对连接关系的编辑，共四次生成／编辑调用。最终 PNG 从工具输出原样复制到本目录及两稿 `figures` 目录，未对生成像素进行后期加工，也没有将位图包装成矢量图。

- CVPR：2109 × 746，RGB。
- TMI：2138 × 736，RGB。
- 原始工具输出路径、选中图片路径与 SHA-256 均见 [generation_manifest.json](generation_manifest.json)。

完整提示词保留如下，后续可直接据此继续迭代。图像生成具有随机性，提示词本身不保证逐像素复现。

1. [CVPR 初次生成](prompts/cvpr_generation.txt)
2. [TMI 初次生成](prompts/tmi_generation.txt)
3. [TMI 并行评分分支修正](prompts/tmi_parallel_branches_edit.txt)
4. [TMI 亮区掩膜连接修正](prompts/tmi_mask_connection_edit.txt)

## 2. 图中具体改了什么

**CVPR：物理测量 → 冻结插值器 → 局部影响 → 误差可观测性。** 用切片堆栈表达物理上下文，橙色表示共享锚点，虚线表示同一缺失目标；双路模型块表示同一冻结估计器在不同上下文中的调用。局部影响面板展示对共享锚点施加相同扰动并比较输出响应，误差向量面板展示共同误差在输出差分中抵消。图中模型块是功能示意，不暗示提出了新的网络层。图里的扰动记为 δ，正文使用 εξ，图注明确对应关系，避免与正文误差分解中的 δ 混淆。

**TMI：双路重建 → 来自已采集锚点的支撑 → 独立回顾性评价。** 将共享／不共享锚点作为两种上下文设计；两个预测先形成绝对差图，再分别由一般前景和固定亮区掩膜进行聚合。两个评分分支是并行关系。参考图像和血管标注仅进入右侧回顾性评价，不作为评分器输入。

TMI 初稿错误地将两次均值聚合连成串联，第一轮编辑改成并行后仍缺少亮区掩膜到下方聚合算子的连接；第二轮补齐。两个未采用版本保留在 `generated/tmi_initial_serial_pooling.png` 和 `generated/tmi_parallel_missing_mask_edge.png`，没有进入稿件。

两张图的切片、掩膜、误差箭头和差图都是示意图，图注已经明确其身份。TMI 亮区规则来自实际 MRA 分支，不把这个 acquired-support 分支冒充成全部历史 GT-mask 实验的协议。新图不构成新的实验结果或新增重建架构证据。

## 3. 文稿与篇幅处理

两篇 `main.tex` 改为直接引用 `p16_cvpr_framework.png` 和 `p16_tmi_framework.png`，旧图文件保留。

CVPR 调整了图 1 的声明位置，使总览出现在第 2 页；精简图注，并压缩结论中与正文重复的概括，保留队列／架构依赖、当前误差与量纲敏感性以及前瞻验证边界，保持技术正文 8 页。没有通过缩小正文字号解决篇幅问题。

TMI 将原单栏图改为跨栏图，便于阅读掩膜、分支和评价边界；更新图注及引言中的图示说明。最终主稿为 11 页，增长一页主要体现为参考文献延伸到第 11 页。保留可读性，未为恢复 10 页而删除实验内容。

逐项文本改动可查看 [CVPR diff](cvpr_source_changes.diff) 和 [TMI diff](tmi_source_changes.diff)。脚本核验确认：排除上述图块、图示引导句及 CVPR 结论精简后，两篇正文与改前版本一致。

## 4. 构建、视觉检查与文件保护

- 两稿均执行 `pdflatex → bibtex → pdflatex ×2`，无 LaTeX Error、未定义引用和 overfull 警告，见 [构建记录](build_logs/build_audit.json)。
- 渲染并查看两稿共 20 页的联系表，另外查看两张图所在的完整页面；未发现图文遮挡、出界或缺图。见 [最终页面预览目录](final_page_renders_verified)。
- 改动前共 **159 个文件**保存在 [original_snapshot](original_snapshot)，所有快照 SHA-256 核验通过，没有删除原文件。
- **42 个既有图像资产**保持原字节，包含原架构示意图与全部统计图；两份补充 PDF 也保持原字节。两篇文章的 baseline 表、数值和协议合格的负结果保留。
- 两个选中 PNG 在本轮目录和论文目录中的 SHA-256 完全一致；未发现预期改动范围之外的原文件变化。见 [verification.json](verification.json)。

所有交付文件位于 `D:\MRI\design\paper` 下。工具自动生成的原始文件位于其默认缓存目录，最终资产、提示词及生成来源记录均已复制或保存到 paper。

## 5. 本轮仍然存在的限制

1. 工具未公开具体后端型号，无法核验 image2.5 身份。
2. 新图是栅格图，标签与箭头没有独立的矢量编辑图层；后续如需逐字修改，应保留当前版本并重新生成或另做可编辑绘图版本。
3. TMI 主稿从 10 页增至 11 页，这是本轮可读性选择带来的实际篇幅变化。
4. 视觉质量改善不解除创新性、历史协议资格、神经模型 acquired-only 验证和临床收益等既有科学风险；本轮没有新增实验，也没有更改对接受概率的判断。科学证据及未解决问题继续以 [Plan 15 报告](../PLAN15_BASELINE_INTEGRATION/FINAL_REPORT_ZH.md) 为准。用户已接管的 A 类真实资料事项未另行展开。

## 6. 本机复建命令

在 `D:\MRI` 的 PowerShell 中执行：

```powershell
D:/conda/envs/MRI/python.exe -B design/paper/PLAN16_RESEARCH_DIAGRAMS/scripts/build.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN16_RESEARCH_DIAGRAMS/scripts/render.py
D:/conda/envs/MRI/python.exe -B design/paper/PLAN16_RESEARCH_DIAGRAMS/scripts/finalize.py
```

构建使用本机 MiKTeX，预览使用 Poppler。`install_and_build_setup.py` 是本轮从改前快照安装图稿的记录脚本，会重写两份主稿；后续已继续编辑文稿时不要重跑该安装脚本覆盖新改动。
