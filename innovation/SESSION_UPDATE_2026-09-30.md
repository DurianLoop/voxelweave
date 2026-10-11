# 本次续作会话记录（2026-09-30）

## 用户要求与边界

用户要求继续基于 `D:\MRI` MRI 项目批量读论文寻找创新点，在 GPU 被其他训练占用期间先探索能 CPU 验证的方向，把本轮材料放在本目录；随后强调要继续审查至有边界的可发表 claim。执行中未向既有训练发送指令，未启动 GPU 推理/训练，未打开 IXI 锁定 test；对已有脏工作区及原稿只读审计，新增脚本、结果、论文笔记均保留在 `innovation`。

## 这次完成的研究工作

1. 继既有文献材料，全文核读并归档两篇近邻预印本：[Giannakopoulos 等 fastMRI 像素级 conformal 区间](literature/Pixelwise_Uncertainty_Accelerated_MRI_2026.pdf)及[Guo 等线性逆问题内在歧义分解](literature/Intrinsic_Ambiguity_Inverse_Problems_2026.pdf)。逐节笔记在[近邻核读](literature/2026-09-30_mira_uncertainty_neighbours.md)；arXiv 检索快照、URL、版本、哈希在[来源登记](literature/2026-09-30_sources.json)。前者 4× brain 的 0.91 误差相关依赖图像模糊，未模糊 Pearson 0.39；后者 MRI 是 50 张 knee 切片的模型方差分解示意，较完整校准对照发生在 EEG。两者不支持 MIRA 的宽泛首创措辞。
2. 已有[事前 MSValid 主结果](MSVALID_EXTERNAL_CONFIRMATION_2026-09-30.md)保持原样：84 人、479 目标、单 HAT→SwinIR 配对 `delta O=+19.7565` 个百分点，95% 患者 CI +19.3276 至 +20.1605，84/84 正。已有[结果后反向/线性控制](MSVALID_POSTHOC_CONTROL_RESULT_2026-09-30.md)完成和记录，分别 +19.4985/+14.6189 个百分点；它们不是新的独立确认。
3. 新拟定并运行[共同 min/max 控制](MSVALID_COMMON_NORM_RESULT_2026-09-30.md)：两相位真实锚点并集共用 min/max，CPU float32 完整 84 人、479 目标；`delta O=+19.4771` 个百分点，探索性 95% CI +19.0337 至 +19.9065，84/84 正。相对原结果减少 0.2794 个百分点。[只读重算](experiments/verify_msvalid_common_norm.py)从逐目标数据核对患者等权统计、同种子 bootstrap 和哈希，已通过。共同统计量包含另一组锚点极值，不能当作部署实验；相位/完整邻层内容仍共变。
4. 对[外部响应影响拟实验](MSVALID_INFLUENCE_FUTURE_PROTOCOL_2026-09-30.md)做了纯元数据[几何检查](experiments/msvalid_influence_geometry.json)：84/84 人和 479/479 目标具备六邻层池，固定 HAT 参考时可构造 1,916 个共享一个锚点的候选。没有执行模型响应探针，不能把几何可行性说成 beyond-count 支持。
5. [投稿证据门槛](CLAIM_PUBLICATION_GATE_2026-09-30.md)、[原稿修订准备](MIRA_MANUSCRIPT_REVISION_PREP_2026-09-30.md)、[实验队列](EXPERIMENT_QUEUE.md)及 README 已更新。现有 CVPR 主文仍写无未触及队列，未同步新的单配对结果；原稿和构建未修改。fastMRI release/图像授权与 NingXia 来源/伦理/同意仍需作者真实资料，不得代填。没有经验证的新主重建方法或可部署风险评分。

## 当前最强可写 claim 与待办

可写：在已测冻结插值器和两个旧脑队列中，共享真实测量伴随成对误差可观测性降低；一个先冻结的 HAT→SwinIR 对照在不同来源 RRMS T2 队列复制了不相交锚点提高 `O` 的现象，且结果后控制表明独立归一化差异不是唯一解释。这是**有边界的机制审计候选**。不能写纯身份因果、首次 MRI 误差预测、校准个体分数、临床安全或真实薄层恢复。

待办：执行外部固定锚数响应影响探针并保留失败；取得尚缺的数据/伦理材料；将单配对方法/结果、近邻引文和限制整合进真实投稿稿件并重建检查；必要时在第二个未触及队列按新的事前协议复制。投稿门槛尚未全部通过，目标继续进行中。

当时核验：`verify_archive.py` 通过（24 PDF、111 证据文件、160 本地链接、0 错误）；共同归一化只读复核通过（84 人、479 目标、bootstrap 精确重现）。后续新增论文与严格影响量审计的最终核验见下段。
# 本次接续完成的严格影响量审计（2026-09-30）

P13–P24 的 MSValid CPU 推理正常完成（12 人、24 目标、216 上下文），未触碰 GPU 训练进程。P1–P12 冻结训练映射对 P13–P24 的线性几何留出 MAE 增益为 +0.005095，但结果后加入精确上下文类别后为 -0.000188，目标内排序不变。原稿 fastMRI/IXI 的同架构 acquired-only 一共享数据在目标+精确上下文控制后四层残余 rank 相关为 +0.242 至 +0.342；五折病例留出 MAE 增益很小，3/4 探索性区间跨零。全部输入哈希、脚本、逐行预测和结论见[独立审计](INFLUENCE_EXACT_CONTEXT_AUDIT_2026-09-30.md)。投稿门槛和 README 已按负结果更新；完整 84 人响应、物理 ID 负对照和其他幅度仍未执行。旧稿、原始表及 GPU 训练均未修改。

最终归档检查：25 PDF、114 证据文件、197 本地链接、零错误。原稿 fastMRI-HAT 精确固定效应偏相关用独立 dummy-OLS 复算为 `0.2919865871094715`，与新脚本一致。

## 后续接续：误差分解与响应锚点负对照

在不触碰 GPU 训练的前提下，从保存的 MSValid 479 目标表按[结果后方案](MSVALID_ERROR_ALIGNMENT_DECOMPOSITION_PLAN_2026-09-30.md)做误差余弦/伙伴质量对称代数分解：[结果](MSVALID_ERROR_ALIGNMENT_DECOMPOSITION_RESULT_2026-09-30.md)为主 `Delta O=+19.7565` 个百分点中的对齐项 +19.6110、质量失衡项 +0.1456 个百分点；目标内伙伴 MSE 5% 匹配的 75 个目标亦全部为正。该分解不是独立机制测量。

按[事先写下的错配方案](ACQUIRED_RESPONSE_ID_PLACEBO_PLAN_2026-09-30.md)，CPU 逐一读取并核验原稿 834 份 acquired-only 响应 NPZ 的 SHA-256；在四个同架构模型/队列层中，正确物理锚点响应配对相对两种错配的精确上下文残余相关优势均为正（+0.185 至 +0.304，探索性检查对象区间均大于零）。[完整结果](ACQUIRED_RESPONSE_ID_PLACEBO_RESULT_2026-09-30.md)及脚本、逐上下文分数均在本目录。MSValid 跨架构的精确上下文留出负结果仍保留；真实采集的物理 ID 因果随机化及完整外部响应方案仍未完成。README、投稿门槛、实验队列和原稿修订准备已同步这些边界，原稿与训练均未改动。

追加后归档复核为 25 PDF、114 证据文件、219 个本地链接、零错误；逐上下文输出共 3,336 行，原影响量复核最大差小于 `1e-16`。

又从原始 acquired-only CSV 只读复核四种响应幅度/符号在精确目标与上下文控制后的关联：16/16 层×幅度组合为正，范围 +0.1688 至 +0.4643；最低值是 fastMRI-HAT 的 `.02`。[数值表与脚本](experiments/original_influence_exact_context_amplitude/summary.json)已保存。这没有替代其余幅度的锚点错配负对照。

另从同批保存数组重新组合旧队列的 HAT→SwinIR 跨架构配对；按[冻结诊断方案](CROSS_ARCH_ACQUIRED_RESPONSE_PLAN_2026-09-30.md)，核验 834 份响应 NPZ 和 417 份目标 NPY 的哈希后，在两队列中都看到正确锚点响应相对错配的精确上下文残余优势（fastMRI +0.212，IXI +0.114）。[完整报告](CROSS_ARCH_ACQUIRED_RESPONSE_RESULT_2026-09-30.md)保留 fastMRI 小幅病例留出正增益及 IXI 区间跨零/排序不变的负结果。旧队列跨架构机制可见，但 MSValid 严格基线负结果未被替代；本轮没有启动 GPU 推理或训练。

