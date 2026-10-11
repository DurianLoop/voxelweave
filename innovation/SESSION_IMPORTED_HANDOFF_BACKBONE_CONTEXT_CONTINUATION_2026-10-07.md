# 用户提供的接续摘要（保留原文）

## 目标与约束

继续基于 MRI 项目读论文、探索创新并验证，长期目标仍 active，**暂无独立确认的可发表 claim**。用户允许 GPU，但不得操作其终端训练进程。全部新文件仅写入 `D:\MRI\innovation`；不改根环境或 `.gitignore`，不委派代理、不读 locked IXI test。

角色保持：11开发患者/19series、4已见验证/9series、8确认/12series。确认患者 `030/029/019/028/031/026/027/015` 关闭，科学确认0。旧反证、失败、分母和门槛不变。

## 当前运行任务：必须先继续等待

CPU 两臂完整 context 骨干接续训练正在运行，**tool session ID `49978`，不要重启**。

- 入口：`innovation/experiments/run_mc_rc_3d_backbone_context_refit_v2_2026_10_07.py`
- 输出：`innovation/experiments/mc_rc_3d_backbone_context_refit_v2_2026_10_07/attempt01.json`
- 仅开发001同一series，从此前各臂全16tile head最后checkpoint接续全部参数。
- 两臂各1024更新；4 intra-op/1 interop线程、below-normal、AdamW恒定lr=.001、weight_decay=.0001、原三尺度BCE+Dice、无增强、同冻结tile流，最后checkpoint、阈值.5。
- 128轮，每轮完整16tile，包括空tile；总墙钟≤5400秒，输出≤120MB。
- **最后一次实际poll（13:32:37附近）**：native已完成1024并保存checkpoint；PCHIP到160/1024。状态可能已推进，应fresh poll。
- 两个最后checkpoint全部冻结后才评分，**不要提前评分native或打开验证/确认患者**。
- 原crop/full-FOV拟合gate保持。当前loss不能当能力成功。

独立核验脚本已写好并通过语法解析，尚未执行：

`innovation/experiments/verify_mc_rc_3d_backbone_context_refit_2026_10_07.py`

主训练exit0且complete后运行。核全部history/stream/GT计数/权重SHA及四域端点、module/functional重放；float32与独立float64坐标比较分开登记，float64通过不得改判float32失败。

## 已完成的新证据

1. CPU线程资格实际exit0：1线程3.4892742秒/更新，4线程1.5942602秒/更新；初始概率比较通过。12次资格更新全部丢弃，不计正式训练。
2. 19series窗口审计及独立核验完成：1139tile中341个起点非步幅8倍数，涉及11series；001为7/16。只是潜在基线因素，未证明MRI性能影响。
3. 合成IN非局部反例完成：crop输入不变，外部扰动使整图IN probe改变0.0222506；独立float64核验通过。说明对齐/halo不能单独令当前14个eval IN网络整图等价。
4. 背景crop采样概率枚举完成：001轴270、patch128，clamp中心采样两端质量47.7778%，均匀合法起点两端仅1.3986%。未验证训练效果。
5. 已核读3篇原文：Exact Tile-Based Segmentation完整XML176块；TIN固定v3实际10页；KIN固定v1共24页含补充。四页原始公式/表格实际渲染核读。报告：
   `innovation/literature/2026-10-07_exact_tiling_TIN_KIN_primary_reading.md`
6. KernelNorm追加定向核读物理页2–13、19–21；未读完整21页、未视觉核原图。**此追加阅读还需要单独写报告/阅读登记**，不要改旧三篇登记。
7. 已知KNConv的3D、dropout=0局部算子和合成数值资格完成：
   - `experiments/mc_rc_3d_local_kernel_normalization_2026_10_07.py`
   - `experiments/mc_rc_3d_local_kernel_normalization_2026_10_07/attempt01.json`
   - float64输出/梯度/局部性通过。
   - **float32资格失败**：constant_two最大误差0.0001884848；offset1000误差0.58210845。保留失败，尚未用于MRI训练，也不是完整论文训练配方。

## 创新判断

TIN Eq2与现有reference-IN外部参照标准化形式直接对应；KIN已有邻域统计替换及下游分类评估。因此“换参照统计/局部统计/修滑窗并评任务”不能独立包装为首创。

剩余候选仍是：充分任务适配后，仅由真实observed预测**具体缺层修正动作的paired任务收益**。须超过强PCHIP和同observed直接任务，并受SafeRestore/MoEDiff等先例约束。旧addback、QDA、线性及45CISS反证保留。

后续准备文档：

- `MC_RC_3D_BASELINE_CONTROLS_PREPARATION_2026-10-07.md`
- `MC_RC_3D_LOCAL_NORMALIZATION_PREPARATION_2026-10-07.md`

## GPU与归档状态

最近GPU仍free1394MiB、util93%左右。原fresh totals≥8,000,000,000bytes启动门槛、4GB运行余量、2.5GB peak保持；GPU pilot totals_v2 attempt02仍未运行。不要用CUDA另报free替代nvidia-smi共享显存。

旧head_context阶段冻结文件未修改。本阶段**尚未最终归档或关闭**。已保存用户上一摘要副本：

`SESSION_IMPORTED_HANDOFF_BACKBONE_CONTEXT_2026-10-07.md`

`SESSION_VISIBLE_DIALOGUE_BACKBONE_CONTEXT_2026-10-07.md`目前只记录最初三条进度，**还需追加后续公开进度和本次compaction答复**。

保留的新失败：骨干入口v1路径下标错误，正式更新0，v2修复；采样审计v1语法错误，v2修复；TIN首次15MB下载上限失败，v2取得27.84MB；TIN原formfeed分段误记12段，实际pdfinfo10页，已逐物理页重新提取。

## 接续顺序

1. Poll `49978`，完成既有两臂训练并确认实际退出，不重复启动。
2. 执行已准备的独立核验，报告全部gate及数值失败。
3. 补写KernelNorm定向阅读及局部算子结果；整理本阶段总览、创新判断、对话、源码/结果SHA manifest和归档凭证。
4. 再按真实结果决定下一开发对照；正式19series schedule仍未冻结，不把单001拟合称完整任务能力或独立确认。
