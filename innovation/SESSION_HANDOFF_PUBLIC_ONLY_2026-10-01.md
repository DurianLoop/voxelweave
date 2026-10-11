# MRI 创新研究：2026-10-01 本轮完整交接

## 用户约束与目标

用户要求在 GPU 被既有训练占用时继续批量读论文、依据过去 MRI 项目寻找可发表创新点，能用 CPU 验证的先验证，暂不能验证的记录方案，并把本轮材料放在 `D:\MRI\innovation`。持续目标是获得有先例排重和实证支持的可发表 claim。未启动、停止或占用用户的 GPU 训练，未动锁定测试集。`.gitignore` 等工作区既有改动保持原样。

## 已完成的文献与项目排重

[文献总综述](literature/2026-09-30_MRI_innovation_review.md)、[聚焦新增论文](literature/2026-09-30_focused_additional_papers.md)、[插值先例](literature/2026-09-30_interpolation_prior_art.md)、[扩散先例](literature/2026-09-30_diffusion_prior_art.md)、[slice-profile 先例](literature/2026-09-30_slice_profile_prior_art.md)和[近期不确定性近邻](literature/2026-09-30_mira_uncertainty_neighbours.md)记录各候选路线与重合点。Hu 2021 已论证 MRI 预测分歧漏掉系统误差；ensemble ambiguity/negative correlation 也早有代数。因此不能把“共同错误存在”或 `O` 的恒等式当新理论。旧 control/orientation 和 repaired wavelet 的局部动作增益与结构守卫不足，外部连续影响量预测留出为负，均已在[实验队列](EXPERIMENT_QUEUE.md)中停止相应正向主张。一次 arXiv API 实时刷新失败，不能宣称检索穷尽；投稿前需重新检索。

## 当前可审的固定对证据

| 证据层 | 主结果 | 结果后控制与边界 |
|---|---|---|
| [MSValid IXI 权重跟进](MSVALID_IXI_WEIGHTS_SECONDARY_RESULT_2026-10-01.md) | 同一先前已看过的 84 名 RRMS 患者、479 目标；`Delta O=+24.1856` 百分点，95% 患者 CI `+23.7150` 至 `+24.6726`，84/84 人正。 | [共同缩放/相位反向](MSVALID_IXI_WEIGHT_POSTRESULT_CONTROLS_RESULT_2026-10-01.md)分别 `+24.0358`（CI `+23.5813` 至 `+24.5032`）和 `+24.0681`（CI `+23.5902` 至 `+24.5537`）；两者均 84/84 人、479/479 目标成功。权重对在看过同患者另一权重对结果后选择，非独立源确认。 |
| [ReMIND 后续新来源](REMIND_NATIVE_T2_CONFIRMATION_RESULT_2026-10-01.md) | TCIA 术前脑肿瘤 2D T2 63 份清单，1 人因事前 24 层门槛被排除；62 人、248 目标，`Delta O=+26.3999` 点，95% 分层患者 CI `+25.6945` 至 `+27.1686`，62/62 人正；普通 T2/BLADE 两组均正。方案在打开该来源像素前冻结。 | [共同缩放/相位反向](REMIND_POSTRESULT_CONTROLS_RESULT_2026-10-01.md)分别 `+26.3236`（CI `+25.5927` 至 `+27.1091`）和 `+26.3049`（CI `+25.6051` 至 `+27.0733`），62/62 人、248/248 目标均成功。[代数分解](REMIND_ERROR_ALIGNMENT_DECOMPOSITION_RESULT_2026-10-01.md)中质量失衡 `+0.0779` 点、误差对齐 `+26.3220` 点，属于恒等式描述。DICOM `ImageType` 含 `MPR`。 |

所有上述新增推理为 CPU float32、PyTorch 两线程，结果独立只读复核通过。两来源均用同一 IXI T2 训练的本地 HAT/SwinIR 固定权重；伴随完整邻层图像、signed geometry 和潜在预处理共变。当前最强句子只能是：**该固定模型对在两个不同公开脑 T2 患者来源的发布层上下文中，共享输入伴随高度对齐的成对误差及低输出分歧；不相交上下文提高同目标回顾性误差可观测比例。** 不推断纯原始采集身份因果、病例级校准风险、真实薄层解剖恢复、病灶安全或临床效果。

## 后续追加的线性负对照

在主结果与其他控制均已可见后，先写下[固定方案](PUBLIC_LINEAR_PARTNER_CONTROL_PLAN_2026-10-01.md)，再把 SwinIR 伙伴换为原生强度线性插值，保持 HAT0、目标、支撑和患者统计不变。[全量结果](PUBLIC_LINEAR_PARTNER_CONTROL_RESULT_2026-10-01.md)为 MSValid `Delta O=+20.5445` 点（84/84 人、479 目标；95% 患者区间 +20.1283 至 +20.9729）与 ReMIND `+22.9386` 点（62/62 人、248 目标；分层区间 +22.3772 至 +23.5257）。脚本逐目标重放 HAT MAE 与支撑像素数；独立复核器在两来源均 `PASS`。因此双学习模型、跨架构配对**不是**上下文大效应的必要条件；原 `Delta O` 与线性 `Delta O` 之差不是可识别的网络特有贡献。该对照仍为结果后探索，不增加独立样本来源。

[匿名逐患者对照图](figures/PUBLIC_LINEAR_CONTROL_COMPARISON_NOTE_2026-10-01.md)将原 SwinIR 与线性伙伴的 `Delta O` 分来源并列，源 CSV 哈希和绘图脚本均有记录；图中不含患者 ID 或像素。它是描述性比较，不是网络贡献的估计。

## 本轮稿件与图

[公开来源路线审计](PUBLIC_ONLY_MIRA_MANUSCRIPT_ROUTE_2026-10-01.md)排除了尚待权利/伦理核实的 fastMRI/NingXia 图表。完整[英文 Markdown 内稿](PUBLIC_ONLY_MIRA_MANUSCRIPT_DRAFT_2026-10-01.md)已加入两来源同权重结果后控制和线性负对照；[5 页 PDF](PUBLIC_ONLY_MIRA_MANUSCRIPT_DRAFT_2026-10-01.pdf)及[逐患者图](figures/PUBLIC_TWO_SOURCE_FIGURE_NOTE_2026-10-01.md)均不包含原始患者影像像素或身份字段。[严审压力测试](PUBLIC_ONLY_CLAIM_REVIEW_STRESS_TEST_2026-10-01.md)记录新意、线性基线、相位混杂、MPR、选择史和部署终点的主要质疑。[复现补充材料内稿](PUBLIC_ONLY_REPRODUCIBILITY_SUPPLEMENT_2026-10-01.md)汇总来源、代码与权重哈希、只读核验命令和环境漂移。

PDF 从最终 Markdown 用 `pandoc ... --standalone -V geometry:margin=1in` 生成 TeX；因本机 MiKTeX 缺 `footnote.sty`/`bookmark.sty`，中间 TeX 中移除未使用的 longtable footnote 宏，并将 `bookmark` 替换为 `hyperref`。两次 `pdflatex` 均 exit 0，日志无 overfull、未定义引用或 LaTeX error；PDF 5 页全部渲染并逐页检查，表、图、公式、参考文献无裁切。最终 PDF SHA-256：`77F074A2C1362928F6D30FEC5931BABE0811A69AD70F75BF566A81390E7CEB84`。这是科学内稿，尚未套目标场合模板；参考文献栏明确需要正式引文核对。

## 下一步顺序

1. 核实 IXI 衍生权重发布/share-alike 义务、MSValid 与 ReMIND 正式作者引文及 TCIA 推荐引用；由真实作者确认署名和对外发布范围。
2. 按目标期刊/会议要求重排正文与补充材料，并提供可复现脚本、权重来源/哈希、匿名逐患者统计及完整纳排流程；实际投稿前刷新相邻论文检索。
3. 若要超越上下文依赖审计，先找到能证明原始独立采集层的来源，事前固定几何/内容匹配或已知前向算子控制，再在全新患者与目标上测纯身份问题。若要可部署评分，另需 acquired-only 分数及外部排序/校准对照；当前影响量分支的严格外部留出为负。
4. 用户 GPU 训练完成且原协议允许时，单独审计锁定测试；不能把这里的 CPU 审计改写为新重建器的性能验证。

归档和链接验证命令：`D:\conda\envs\MRI\python.exe -B innovation\verify_archive.py`。最终复核通过：25 份论文 PDF、114 份阅读证据文件、459 个本地链接，`errors=[]`。主结果、两来源共同缩放/反向控制和线性对照的五个独立只读复核器亦重新通过。当前 MRI 环境实际为 NumPy 2.4.3，而根目录 `environment.yml` 写 `numpy<2` 且漏列 pydicom；见[复现补充材料](PUBLIC_ONLY_REPRODUCIBILITY_SUPPLEMENT_2026-10-01.md)，不得把该 YAML 当精确环境锁。本轮的 PDF 和研究记录都在 `innovation`；原稿与旧实验文件只作为只读来源。
