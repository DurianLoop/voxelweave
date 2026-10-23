# 自研方法与实验结果总汇

**展示与交接入口：**要比较自研模型和既有baseline、按梯队筛选，请先看[自研模型效果与候选筛选](self_model_baseline_tiers.md)；后续研究和写文章请读[完整研究交接](research_handoff_20261023.md)。本文件保留详细研究档案，避免将全部历史尝试等同于当前推荐模型。

为便于GitHub接手，原Git忽略的轻量汇总结果已按原字节复制至[交接证据快照](handoff_evidence_20261023/README.md)，相关链接指向快照；逐患者/切片明细、权重、影像和部分目录仍属本地资产，见[来源可用性索引](handoff_evidence_20261023/source_availability.csv)。指标未重算，协议边界不变。

整理日期：2026-10-23。位置：`docx/experiment/self_innovation_methods_and_results.md`。本文件与[统一实验主表](experiment_master_table.md)并列，集中整理本项目自己提出、设计或改进的方法，以及相应的完整实验、消融、诊断、负结果和待验证方案。

这里的“自研”表示项目内提出或实现的路线，不自动表示已证明文献首创。外部模型的复现成绩只在解释自研结果时作为对照；内部工程基线、使用外部预训练权重的混合模型、依赖真值的 oracle 和正式自研候选均明确标注。

## 阅读口径

- **按实验实际状态记账。** 优先采用逐例指标、`summary`、`completion`、`gate`、独立核验及最终报告；旧 README、主表或交接中“正在运行/待运行”仅代表当时状态。例如 I3Net–PAST latent bridge 已有两臂各 80 轮的完整 validation 结果，不能继续记作仅 smoke。
- **不同协议分别报告。** 旧 native-volume 主表、256²/observed-only 开发协议、GT 每层范围评分、病例观测范围评分、validation 与 test、病例/series/切片等权、归一化与原始强度 MAE/MSE，均不能直接混排。`mini`、`smoke`、训练内拟合也不能当作正式独立测试。
- **数值保留来源含义。** PSNR/NCC/SSIM 通常越高越好，MAE/MSE 通常越低越好；可靠性指标依各表定义。强度阈值 Dice/HD95 proxy 不等同人工解剖标注分割，oracle 上限不等同可部署性能。
- **实验数不等于独立创新数。** 同一底座的配置、种子、预算、消融或诊断可各有实验记录，但不重复称作全新方法。未实际产生数值的目录和预期目标记为“未完成/仅方案”，不填预期成绩。
- **保留失败及修正。** test 多轮参与开发、患者交叉、归一化目标信息、DICOM 混序列修复、自比较剔除、真值可访问范围等会影响解释的问题随结果一并记录。文件日期或哈希不能单独证明前瞻性预注册。

资料覆盖 `design/`、`docx/design/`、`docx/experiment_notes/`、相关早期进展及 `innovation/` 的本地研究产物；大型工具环境、第三方代码副本和重复论文快照不作独立自研成果。相同实验的重复导出不重复计数。本次整理没有重新训练、重新开启确认集或更改原实验主表。

## 方法路线总览

| 路线 | 项目内提出的核心内容 | 已有证据/当前状态 | 本文位置 |
|---|---|---|---|
| PAST-Net / MA3 / G 系列 | 相位条件、真实锚点结构迁移、coarse 残差、门控及双域建模；多代局部结构和损失改进 | 有大量 fastMRI 开发结果；后续修订协议下多数增量小或未过完整门槛 | 下文 PAST 系列 |
| PAST v2、物理几何/上下文/跨视图/方向/小波 | 控制容量与真实观测范围，逐项验证结构和训练因素 | 有完整单 seed 验证、质量守卫及失败结果 | 下文 PAST v2 与诊断 |
| IXI 小波、IXI-STC、I3Net–PAST latent bridge | 跨域微调、四/六锚点潜轨迹、冻结 I3Net latent 读出 | 已有 IXI test 或配对 validation；分开记录，未支持新的 SOTA 主张 | 下文 IXI 与混合模型 |
| FAST-Net | phase FiLM + 轻量 depthwise 多尺度上下文 + 置信门控 bounded residual | 找到设计方案；未找到以此名称完成的独立正式训练结果 | 本节后方“仅方案” |
| SCPI-Net | 一个条件模型联合任意 phase/尺度，联合 x2/x4/x6 与连续一致性 | 找到设计方案；未找到独立的连续尺度成品实验 | 本节后方“仅方案” |
| RASI-Net / RASINet / committee | 后验可靠性代理、模型间分歧、共享误差分析、候选选择与预算优化 | 有多数据集、多倍率、模型库、最终选择及失败分析 | 下文 RASI 与研究框架 |
| ACSI-Net / ACSINet v1/v2 | 轻量分组插值、z 轴一致性评价、四锚点窗口与 NCC-profile 约束 | v1 有正式 test115；v2/v2.1 有 smoke/mini，未通过继续 full 的门槛 | 下文 ACSI |
| ECSI-Net / ECSINet | change-aware 轻量残差与质量/算力 Pareto 设计 | 已实现并有静态检查；未找到实际训练或质量/速度评价结果 | 下文 ECSI |
| MIRA 与共享测量影响框架 | 误差可观察性分解、共享锚点/有限响应影响、同目标配对干预 | 有机制、跨架构及外部发布层审计；部署评分及若干泛化控制失败 | 下文 MIRA 与创新研究 |
| 任务驱动重建/动作净收益 | 在同观测、同预算下预测加采集/重建动作对患者任务的收益 | 有大量来源、能力、分割、校准与成本实验；未见确认队列保持关闭 | 下文 innovation |
| 内部 ResUNet / 早期工程实验 | 本地搭建残差 CNN 与数据/训练管线验证 | 已有结果；定位为工程基线，不单列文献首创贡献 | 本节后方与 PAST 历史 |

设计命名依据：[自研模型设计总览](../design/design_overview_table.md)。历史文档中的“可成文/潜力/目标”属于当时的设计判断，不作为已达成的实验证据。

## 仅方案或尚无独立完成结果的自研方向

### FAST-Net：Fast Adaptive Slice Transfer Network

提出轻量相位自适应切片迁移：用邻片、线性 coarse、差分和 phase 组成输入，采用 depthwise 大核与多尺度分支，phase FiLM 调制，输出 `coarse + confidence × alpha × tanh(residual)`。计划 Tiny/Base/Large 分别用 32/48/64 通道；Base 建议 10 块、5×5 depthwise，损失为 L1 + 0.05 gradient + 0.001 residual，可选 symmetry。

计划实验包括去 phase FiLM、去 confidence gate、去 bounded residual、普通 3×3 替换大核、不同规模及质量/速度/显存 Pareto。**这些是方案与拟做消融，未找到独立 FAST-Net 完成结果，不能填入目标 I3Net/HAT 的成绩。** 后续 ECSI、PAST 中相近模块的真实实验归各自方法，不自动视为此方案已完成。

来源：[FAST-Net 原始设计](../design/design2_fastnet_efficient_sota.md)。

### SCPI-Net：Scale-Continuous Phase-aware Interpolation Network

提出 `f(L, R, p, scale)` 统一连续位置与尺度插值：scale/phase encoder 调制条件残差主干，以 coarse 提供低频先验；计划 x2/x4/x6 均衡混合采样、课程训练，加入 phase/z-smooth、scale consistency 与 symmetry 约束，并评估未见 scale/phase。

**目前找到的是设计方案，未找到以 SCPI-Net 名称完成的联合训练、未见倍率泛化和一模型对多模型实验。** 已有 x2/x4/x6 分倍率 baseline 或 RASI 多倍率评价不等于完成连续尺度网络。

来源：[SCPI-Net 原始设计](../design/design4_scpinet_scale_continuous.md)。

## 内部工程基线：ResUNet residual

项目自行搭建的 residual CNN，用于数据、训练和评价管线验证。它是本地工程基线，不标为独立首创网络。以下为既有统一主表的 T2/x4 结果，采用该表自己的 native-volume 与统计口径；NingXia 为 8-fold 病例级 CV。

| 数据集/协议 | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|
| IXI-T2，test n=115 | 27.4611 | 0.8812 | 25.2395 | 4985.4989 | 0.9552 |
| fastMRI-brain-T2 expanded，test n=24 | 22.2549 | 0.7374 | 53.5705 | 11842.8147 | 0.8955 |
| NingXia-T2，8-fold CV | 23.3816 | 0.7209 | 97.0409 | 36316.2290 | 0.8785 |

来源：[统一实验主表](experiment_master_table.md)。x2/x6 与补充训练预算结果仍按原表各节独立维护；本文件末附该方法的多尺度记录摘录。

---

## PAST-Net：相位感知结构迁移网络与全部研究分支

PAST-Net（Phase-Aware Structure-Transfer Network）是工作区明确维护的自研确定性 MRI 层间插值主线。T2 x4任务为每4层保留1张真实观测，预测q=0.25/0.50/0.75的3张缺失层。基本形式为`预测 = 线性粗插值 + 置信度门控有界残差`。初版输入左右锚点、粗插值、phase、方向差分与绝对差分，后来发展为四锚点rich conditioning、宽MA3、多尺度空间/潜特征交互、误差尾部目标和空间/FFT双域残差。

下面保留正式full、mini、smoke、失败/消融和诊断结果；它们属于同一研究演进，不能全部包装成独立新架构。AdamW、EMA、FiLM、Haar、FFT等通用组件本身不单独构成原创性主张。数值优先采用实际CSV、validation summary、completion与gate；过时文档状态已更正。

基础来源：[design/design1_pastnet/reference/original_design_blueprint_20260706.md](../../design/design1_pastnet/reference/original_design_blueprint_20260706.md)、[design/design1_pastnet/README.md](../../design/design1_pastnet/README.md)、[design/design1_pastnet/results/experiment_ledger.md](../../design/design1_pastnet/results/experiment_ledger.md)、[design/PASTNET_RESEARCH_SUMMARY_2026-09-24.md](../../design/PASTNET_RESEARCH_SUMMARY_2026-09-24.md)。

### PAST 历史各族机制、消融与判定

| 阶段 / 版本 | 主要方法或变量 | 结果与判定 | 来源 |
|---|---|---|---|
| v1 / extend60 | linear coarse、phase-aware gate、空间confidence、有界residual；继续训练 | full22.9327→23.2583 dB；可训练但信息/结构不足 | [design/design1_pastnet/experiments/01_initial/fastmri_v1_full_analysis_20260715.md](../../design/design1_pastnet/experiments/01_initial/fastmri_v1_full_analysis_20260715.md) |
| MA / MA2 | prev/left/right/next四真实锚点、外侧valid mask与delta | MA2 full23.6079，比extend60 +0.3495；多锚点是早期主要有效信息 | [design/design1_pastnet/experiments/01_initial/fastmri_ma2_full_analysis_20260716.md](../../design/design1_pastnet/experiments/01_initial/fastmri_ma2_full_analysis_20260716.md) |
| MA3 warm / PSNR FT | 13通道rich multi-anchor、local residual refinement、Laplacian/edge和PSNR微调 | warm90 23.8580，FT30 23.9310，FT60 23.9307；继续微调饱和 | [design/design1_pastnet/results/research_timeline_20260722_20260907.md](../../design/design1_pastnet/results/research_timeline_20260722_20260907.md) |
| MA3C / MA3CG | interval z-curvature；guarded/calibrated teacher trust-region | mini有结果，旧full缺summary，不能补成正式结论 | 同上 |
| MA3J / MA3JF | 联合三个offset的interval residual head；JF加大joint、调整sym/grad | MA3JF23.9731，PSNR比I3Net低0.0371，SSIM/MAE较好；0.4140M参数、61.0523GFLOPs | 同上 |
| MA4W | 128通道/16块window residual大模型 | 3.1506M参数，full23.5719，明显退化 | 同上 |
| G01—G06 | 冻结头校准、全量解冻、强symmetry、z-curvature、teacher trust-region及组合 | 仅0.00x—0.01x或负收益；不作核心突破 | [design/design1_pastnet/experiments/02_g01_g10/architecture_sweep_20260723.md](../../design/design1_pastnet/experiments/02_g01_g10/architecture_sweep_20260723.md) |
| G07 / G08 | 64通道wide MA3 vs deeper MA3 | G07 24.2910，对MA3JF +0.3178，24/24胜、近似95%CI[+0.2661,+0.3696]；G08 24.0547 | [design/design1_pastnet/results/g01_g10_full200_results_20260806.md](../../design/design1_pastnet/results/g01_g10_full200_results_20260806.md) |
| G09 / G10 | window lite与rescue | 22.5658/22.4406；停止 | 同上 |
| G071—G075 | 优化配方、anchor reliability、多尺度context、组合RAdam、输出端interval3D | G07124.3351为稳定底座；G073 SSIM/MAE 24/24改善、保留context；reliability和输出3D无独立价值 | [design/design1_pastnet/experiments/03_g071_g075/optimization_context_20260806.md](../../design/design1_pastnet/experiments/03_g071_g075/optimization_context_20260806.md) |
| G076—G078 | 单尺度latent Conv3D、三offset self-attention、双尺度latent Conv3D | 24.3333/24.3332/24.3382；短token attention无额外收益，双尺度有小信号 | [design/design1_pastnet/experiments/04_g076_g080/latent_interval_20260820.md](../../design/design1_pastnet/experiments/04_g076_g080/latent_interval_20260820.md) |
| G079 / G080 | G078加top10% tail MSE；hybrid attention+tail+pyramid | G07924.4032；对G078 +0.064959，24/24胜，95%CI[+0.056478,+0.073156]；代价MAE+0.104282、Dice约−0.00244；G080无额外收益 | [design/pastnet_v2/results/historical_evidence.json](../../design/pastnet_v2/results/historical_evidence.json) |
| G081 | PhaseFlow双向可变形锚点对齐 | 24.4187，较G079 +0.0156弱正信号 | [design/design1_pastnet/experiments/05_g081_g085/aggressive_methods_20260829.md](../../design/design1_pastnet/experiments/05_g081_g085/aggressive_methods_20260829.md) |
| G082 | Fourier连续坐标INR decoder | 24.4121，+0.0089，停止 | 同上 |
| G083 | 三阶段ConvGRU unrolled error feedback | 24.4091，+0.0060，停止 | 同上 |
| G084 | spatial expert + FFT low/mid/high expert和可学习gate | 24.4423；对G079 +0.039189，95%CI[+0.034601,+0.043715]，五主指标24/24全胜；未达+0.10结构门槛 | [design/pastnet_v2/results/historical_evidence.json](../../design/pastnet_v2/results/historical_evidence.json) |
| G085 | anchor-clamped五切片volumetric U-Net | 24.4085；输出端3D仅微调级收益 | [design/design1_pastnet/results/experiment_ledger.md](../../design/design1_pastnet/results/experiment_ledger.md) |
| G086 | G084低学习率warmup/cosine restart60 | 24.446977，best54；对G084 +0.004633，23/24胜，95%CI[+0.003807,+0.005406]；低于+0.03续训门槛，冻结 | [design/pastnet_v2/results/historical_evidence.json](../../design/pastnet_v2/results/historical_evidence.json) |
| G087—G090 | 从头四锚点sparse-window U-Net；依次加Flow、FFT、Flow+FFT+3D | 3.14—3.40M参数，best33—37；最好G08924.1089仍低于G084 0.33345；G090较G089 −0.05918（95%CI[−0.0883,−0.0298]）；停止 | [design/design1_pastnet/experiments/06_g086_g090/sparse_window_20260905.md](../../design/design1_pastnet/experiments/06_g086_g090/sparse_window_20260905.md) |

G086有效结构为：四稀疏锚点+phase/validity/difference/curvature → query线性coarse → 共享锚点encoder与phase软融合 → 64通道/10块MA3 → 多尺度空间context → 1/2、1/4尺度三phase潜特征Conv3D → 空间/FFT双域expert → 有界修正+coarse skip。共同loss包括Charbonnier、MSE、gradient、edge、轻symmetry、z-curvature、residual regularization、tail10 MSE与base guard。

### PAST 旧协议 fastMRI x4：全部现存 full 结果

以下为38个有正式summary的full profile；24病例、旧native-volume评分，MAE/MSE为原MRI强度单位。每run仅抽取PAST行，排除同文件Linear/Cubic。旧test-24已经被多轮开发查看，应称为历史development test。G086比本地I3Net24.0102高约0.4368 dB，不等于独立最终SOTA。

| Profile | 记录方法 | n | PSNR | SSIM | MAE | MSE | NCC | 原始来源 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full | pastnet | 24 | 22.932690 | 0.768235 | 45.917264 | 10275.226742 | 0.910832 | [design/fastmri_brain_pastnet_2p5d/runs/full/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/26343ecf00c2__summary_metrics.csv) |
| full_extend60 | pastnet | 24 | 23.258329 | 0.775995 | 43.935069 | 9501.809007 | 0.917831 | [design/fastmri_brain_pastnet_2p5d/runs/full_extend60/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/8b54c205662c__summary_metrics.csv) |
| full_ma2_90 | pastnet_ma2 | 24 | 23.607870 | 0.783939 | 42.385015 | 8659.874621 | 0.923991 | [design/fastmri_brain_pastnet_2p5d/runs/full_ma2_90/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/d0755dd8debc__summary_metrics.csv) |
| full_ma3_psnr_ft30 | pastnet_ma3 | 24 | 23.930984 | 0.793772 | 40.492302 | 8066.071121 | 0.929670 | [design/fastmri_brain_pastnet_2p5d/runs/full_ma3_psnr_ft30/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/3e4a9abf3700__summary_metrics.csv) |
| full_ma3_psnr_ft60 | pastnet_ma3 | 24 | 23.930729 | 0.793941 | 40.477481 | 8061.510965 | 0.929661 | [design/fastmri_brain_pastnet_2p5d/runs/full_ma3_psnr_ft60/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/d099ebb3d46f__summary_metrics.csv) |
| full_ma3_warm90 | pastnet_ma3 | 24 | 23.857968 | 0.791652 | 40.753960 | 8210.453194 | 0.928519 | [design/fastmri_brain_pastnet_2p5d/runs/full_ma3_warm90/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/c9382383ed25__summary_metrics.csv) |
| full_ma3jf_150 | pastnet_ma3j | 24 | 23.973136 | 0.795161 | 40.300788 | 7978.773721 | 0.930493 | [design/fastmri_brain_pastnet_2p5d/runs/full_ma3jf_150/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/e3bb7c36e322__summary_metrics.csv) |
| full_ma4w_150 | pastnet_ma4w | 24 | 23.571898 | 0.777655 | 43.325508 | 8696.669248 | 0.923636 | [design/fastmri_brain_pastnet_2p5d/runs/full_ma4w_150/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/b5b18c9de948__summary_metrics.csv) |
| full_pastnet_g01_ma3jf_cal200 | pastnet_ma3j | 24 | 23.983240 | 0.795269 | 40.294857 | 7962.360328 | 0.930555 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g01_ma3jf_cal200/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/96709e7b4e07__summary_metrics.csv) |
| full_pastnet_g02_ma3j_unfrozen200 | pastnet_ma3j | 24 | 23.974844 | 0.795130 | 40.318561 | 7978.353411 | 0.930416 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g02_ma3j_unfrozen200/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/7ef98d67853c__summary_metrics.csv) |
| full_pastnet_g03_ma3j_sym200 | pastnet_ma3j | 24 | 23.952163 | 0.794205 | 40.412317 | 8020.997490 | 0.930175 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g03_ma3j_sym200/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/aacbb0dd10fd__summary_metrics.csv) |
| full_pastnet_g04_ma3c_z200 | pastnet_ma3c | 24 | 23.984789 | 0.794956 | 40.260012 | 7963.073129 | 0.930629 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g04_ma3c_z200/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/589df9a428b1__summary_metrics.csv) |
| full_pastnet_g05_ma3cg_soft200 | pastnet_ma3cg | 24 | 23.940415 | 0.794163 | 40.434383 | 8043.360066 | 0.929816 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g05_ma3cg_soft200/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/77e62648f44e__summary_metrics.csv) |
| full_pastnet_g06_ma3j_zstrong200 | pastnet_ma3j | 24 | 23.975699 | 0.795083 | 40.286014 | 7978.316279 | 0.930485 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g06_ma3j_zstrong200/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/63997d29ba95__summary_metrics.csv) |
| full_pastnet_g071_cosine_ema200 | pastnet_ma3 | 24 | 24.335086 | 0.804652 | 38.506581 | 7370.848319 | 0.935584 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g071_cosine_ema200/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/6275bdcf662e__summary_metrics.csv) |
| full_pastnet_g072_reliability_opt200 | pastnet_ma3af | 24 | 24.332972 | 0.804674 | 38.511088 | 7375.385513 | 0.935552 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g072_reliability_opt200/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/e73765d5f6fb__summary_metrics.csv) |
| full_pastnet_g073_multiscale_opt200 | pastnet_ma3ms | 24 | 24.328516 | 0.805583 | 38.435628 | 7384.604736 | 0.935484 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g073_multiscale_opt200/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/c11bd626bc06__summary_metrics.csv) |
| full_pastnet_g074_afms_radam200 | pastnet_ma3afms | 24 | 24.329849 | 0.805581 | 38.429358 | 7382.014916 | 0.935510 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g074_afms_radam200/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/5210f385f2ef__summary_metrics.csv) |
| full_pastnet_g075_interval3d_opt200 | pastnet_ma3ir | 24 | 24.333755 | 0.804664 | 38.499836 | 7373.872087 | 0.935605 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g075_interval3d_opt200/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/3dc7875376f8__summary_metrics.csv) |
| full_pastnet_g076_latent_conv120 | pastnet_ma3lc | 24 | 24.333343 | 0.805773 | 38.403896 | 7376.361428 | 0.935552 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g076_latent_conv120/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/d617ed7b3616__summary_metrics.csv) |
| full_pastnet_g077_latent_attention150 | pastnet_ma3la | 24 | 24.333213 | 0.805797 | 38.399123 | 7377.040201 | 0.935552 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g077_latent_attention150/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/e60172b6ad4c__summary_metrics.csv) |
| full_pastnet_g078_latent_multiscale160 | pastnet_ma3lms | 24 | 24.338196 | 0.805912 | 38.380194 | 7368.136600 | 0.935624 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g078_latent_multiscale160/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/b637a6767144__summary_metrics.csv) |
| full_pastnet_g079_tail_aware160 | pastnet_ma3lt | 24 | 24.403155 | 0.805964 | 38.484476 | 7239.443717 | 0.936450 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g079_tail_aware160/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/3f1dc0fb401b__summary_metrics.csv) |
| full_pastnet_g07_ma3_wide200 | pastnet_ma3 | 24 | 24.290977 | 0.803080 | 38.890451 | 7448.957648 | 0.934988 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g07_ma3_wide200/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/1b7673ba7639__summary_metrics.csv) |
| full_pastnet_g080_hybrid_tail180 | pastnet_ma3lh | 24 | 24.402034 | 0.806007 | 38.482917 | 7243.952882 | 0.936417 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g080_hybrid_tail180/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/4ca52ed0ea76__summary_metrics.csv) |
| full_pastnet_g081_phase_flow140 | pastnet_ma3ad | 24 | 24.418729 | 0.806575 | 38.421832 | 7216.466934 | 0.936680 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g081_phase_flow140/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/1c1a18e2ba17__summary_metrics.csv) |
| full_pastnet_g082_coord_inr160 | pastnet_ma3ci | 24 | 24.412058 | 0.806234 | 38.456194 | 7223.012188 | 0.936592 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g082_coord_inr160/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/95bd6e047c48__summary_metrics.csv) |
| full_pastnet_g083_unrolled160 | pastnet_ma3ur | 24 | 24.409108 | 0.806215 | 38.463881 | 7231.329762 | 0.936535 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g083_unrolled160/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/c1adb73635ec__summary_metrics.csv) |
| full_pastnet_g084_dual_domain140 | pastnet_ma3df | 24 | 24.442344 | 0.807311 | 38.310031 | 7173.393354 | 0.937057 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g084_dual_domain140/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/16e6b068a175__summary_metrics.csv) |
| full_pastnet_g085_volumetric180 | pastnet_ma3vs | 24 | 24.408471 | 0.806142 | 38.457845 | 7230.785234 | 0.936544 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g085_volumetric180/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/47c45a3db623__summary_metrics.csv) |
| full_pastnet_g086_dual_restart60 | pastnet_ma3df | 24 | 24.446977 | 0.807465 | 38.289388 | 7165.787159 | 0.937124 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g086_dual_restart60/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/814cb0a9bb4f__summary_metrics.csv) |
| full_pastnet_g087_sparse_window200 | pastnet_ma3sw | 24 | 24.085948 | 0.790281 | 40.806827 | 7737.203224 | 0.931764 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g087_sparse_window200/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/8b7995dc013e__summary_metrics.csv) |
| full_pastnet_g088_sparse_flow200 | pastnet_ma3sf | 24 | 24.063757 | 0.789472 | 40.923951 | 7742.810579 | 0.931597 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g088_sparse_flow200/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/4d325adf2ffa__summary_metrics.csv) |
| full_pastnet_g089_sparse_dual200 | pastnet_ma3sd | 24 | 24.108897 | 0.790968 | 40.762775 | 7686.019758 | 0.932255 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g089_sparse_dual200/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/c197f43afa4a__summary_metrics.csv) |
| full_pastnet_g08_ma3_deep200 | pastnet_ma3 | 24 | 24.054711 | 0.797280 | 39.807729 | 7840.317807 | 0.931428 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g08_ma3_deep200/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/74b874924c65__summary_metrics.csv) |
| full_pastnet_g090_sparse_hybrid220 | pastnet_ma3sh | 24 | 24.049714 | 0.789013 | 41.038830 | 7764.128278 | 0.931557 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g090_sparse_hybrid220/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/0d2fb0d0555a__summary_metrics.csv) |
| full_pastnet_g09_ma4w_lite200 | pastnet_ma4w | 24 | 22.565798 | 0.745631 | 49.267780 | 10941.189634 | 0.904571 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g09_ma4w_lite200/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/ad8321c49dbd__summary_metrics.csv) |
| full_pastnet_g10_ma4w_rescue200 | pastnet_ma4w | 24 | 22.440561 | 0.740610 | 49.898234 | 11220.817812 | 0.902044 | [design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g10_ma4w_rescue200/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/443321bde22a__summary_metrics.csv) |

存在目录但缺正式summary：`full_ma3c_150`；`full_ma3cg_150`；`full_ma3j_150`。目录/checkpoint/eval文件夹本身不替代结果。

### PAST 旧协议 fastMRI x4：全部 mini 筛选

每组4病例，初始化与训练子集可能不同，不能与full24病例横比。

| Profile | 记录方法 | n | PSNR | SSIM | MAE | MSE | NCC | 原始来源 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mini | pastnet | 4 | 20.276900 | 0.657850 | 65.413635 | 17381.852105 | 0.853436 | [design/fastmri_brain_pastnet_2p5d/runs/mini/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/c42f84308237__summary_metrics.csv) |
| mini_ma | pastnet_ma | 4 | 20.419695 | 0.663943 | 64.283949 | 16920.342319 | 0.854793 | [design/fastmri_brain_pastnet_2p5d/runs/mini_ma/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/ef2d6369de35__summary_metrics.csv) |
| mini_ma2 | pastnet_ma2 | 4 | 20.713817 | 0.675048 | 63.360437 | 15884.236254 | 0.862644 | [design/fastmri_brain_pastnet_2p5d/runs/mini_ma2/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/59c1763e132b__summary_metrics.csv) |
| mini_ma3 | pastnet_ma3 | 4 | 20.371900 | 0.648744 | 66.198302 | 17014.163981 | 0.852361 | [design/fastmri_brain_pastnet_2p5d/runs/mini_ma3/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/ba4ca97e4d5b__summary_metrics.csv) |
| mini_ma3_psnr_ft | pastnet_ma3 | 4 | 21.289692 | 0.706833 | 57.553474 | 14087.327840 | 0.879663 | [design/fastmri_brain_pastnet_2p5d/runs/mini_ma3_psnr_ft/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/329fbceec4e7__summary_metrics.csv) |
| mini_ma3_warm | pastnet_ma3 | 4 | 21.111647 | 0.692731 | 59.079451 | 14551.447673 | 0.875315 | [design/fastmri_brain_pastnet_2p5d/runs/mini_ma3_warm/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/08a5850daf68__summary_metrics.csv) |
| mini_ma3c | pastnet_ma3c | 4 | 23.382188 | 0.787787 | 42.686897 | 8767.963186 | 0.925513 | [design/fastmri_brain_pastnet_2p5d/runs/mini_ma3c/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/a5a7298af590__summary_metrics.csv) |
| mini_ma3cg | pastnet_ma3cg | 4 | 23.389586 | 0.789143 | 42.504918 | 8748.556135 | 0.925678 | [design/fastmri_brain_pastnet_2p5d/runs/mini_ma3cg/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/53635ffd8235__summary_metrics.csv) |
| mini_ma3j | pastnet_ma3j | 4 | 23.391985 | 0.788317 | 42.597195 | 8776.204631 | 0.925633 | [design/fastmri_brain_pastnet_2p5d/runs/mini_ma3j/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/b3c3a4cc2852__summary_metrics.csv) |
| mini_ma3jf | pastnet_ma3j | 4 | 23.392281 | 0.789104 | 42.506874 | 8742.018273 | 0.925706 | [design/fastmri_brain_pastnet_2p5d/runs/mini_ma3jf/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/25695a8fae20__summary_metrics.csv) |
| mini_ma4w | pastnet_ma4w | 4 | 19.592801 | 0.614014 | 72.981392 | 20184.744934 | 0.822631 | [design/fastmri_brain_pastnet_2p5d/runs/mini_ma4w/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/7139c956bd94__summary_metrics.csv) |

### PAST 旧协议 fastMRI x4：全部有指标 smoke

仅验证训练、推理、恢复与指标流水线；不作正式性能结论。

| Profile | 记录方法 | n | PSNR | SSIM | MAE | MSE | NCC | 原始来源 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| smoke | pastnet | 1 | 17.651503 | 0.527637 | 87.669506 | 23761.464735 | 0.820338 | [design/fastmri_brain_pastnet_2p5d/runs/smoke/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/a23eb3e7221e__summary_metrics.csv) |
| smoke_ma3c | pastnet_ma3c | 1 | 23.247906 | 0.776587 | 42.623433 | 6620.316542 | 0.952627 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_ma3c/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/088618c1d772__summary_metrics.csv) |
| smoke_ma3cg | pastnet_ma3cg | 1 | 23.317709 | 0.781096 | 41.704198 | 6528.169949 | 0.953397 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_ma3cg/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/eb0adb37ae6b__summary_metrics.csv) |
| smoke_ma3j | pastnet_ma3j | 1 | 23.163838 | 0.774621 | 42.838561 | 6738.699029 | 0.951900 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_ma3j/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/01df69c234db__summary_metrics.csv) |
| smoke_ma4w | pastnet_ma4w | 1 | 17.535361 | 0.432143 | 92.872270 | 24533.023872 | 0.814891 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_ma4w/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/b75a6d046236__summary_metrics.csv) |
| smoke_pastnet_g01_ma3jf_cal | pastnet_ma3j | 1 | 23.377496 | 0.783494 | 41.455907 | 6431.178358 | 0.954045 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g01_ma3jf_cal/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/f5998fc25235__summary_metrics.csv) |
| smoke_pastnet_g02_ma3j_unfrozen | pastnet_ma3j | 1 | 23.252456 | 0.781419 | 42.019194 | 6571.489448 | 0.953415 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g02_ma3j_unfrozen/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/e97f461e2096__summary_metrics.csv) |
| smoke_pastnet_g04_ma3c_z | pastnet_ma3c | 1 | 23.318984 | 0.778451 | 41.910253 | 6517.784532 | 0.953629 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g04_ma3c_z/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/e9ab168a32d9__summary_metrics.csv) |
| smoke_pastnet_g05_ma3cg_soft | pastnet_ma3cg | 1 | 23.325550 | 0.780351 | 41.802046 | 6517.306152 | 0.953492 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g05_ma3cg_soft/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/c28b40bce7a5__summary_metrics.csv) |
| smoke_pastnet_g06_ma3j_zstrong | pastnet_ma3j | 1 | 23.319314 | 0.779453 | 41.989426 | 6527.955268 | 0.953390 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g06_ma3j_zstrong/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/7ff9a5e76b7e__summary_metrics.csv) |
| smoke_pastnet_g071_continue | pastnet_ma3 | 1 | 23.485209 | 0.792545 | 40.412902 | 6229.746067 | 0.955513 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g071_continue/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/d624decd2a2c__summary_metrics.csv) |
| smoke_pastnet_g071_opt | pastnet_ma3 | 1 | 23.517119 | 0.792839 | 40.302861 | 6192.715847 | 0.955706 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g071_opt/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/560e0546edde__summary_metrics.csv) |
| smoke_pastnet_g072_reliability | pastnet_ma3af | 1 | 23.369695 | 0.791568 | 40.570618 | 6394.909478 | 0.954524 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g072_reliability/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/19b3b8ac43de__summary_metrics.csv) |
| smoke_pastnet_g072_reliability_opt | pastnet_ma3af | 1 | 23.486266 | 0.792924 | 40.538164 | 6229.986464 | 0.955420 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g072_reliability_opt/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/6a22d4e4b9a8__summary_metrics.csv) |
| smoke_pastnet_g073_multiscale | pastnet_ma3ms | 1 | 23.377740 | 0.789869 | 40.809344 | 6368.469998 | 0.954581 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g073_multiscale/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/764fdba75af2__summary_metrics.csv) |
| smoke_pastnet_g073_multiscale_opt | pastnet_ma3ms | 1 | 23.483093 | 0.793155 | 40.527127 | 6234.059597 | 0.955396 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g073_multiscale_opt/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/898efee5c7a7__summary_metrics.csv) |
| smoke_pastnet_g074_afms_radam | pastnet_ma3afms | 1 | 23.485038 | 0.792963 | 40.533583 | 6231.605062 | 0.955410 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g074_afms_radam/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/c653e1674b79__summary_metrics.csv) |
| smoke_pastnet_g074_parammatch | pastnet_ma3 | 1 | 17.568694 | 0.436020 | 92.264931 | 24280.047852 | 0.814229 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g074_parammatch/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/6e273d121fd2__summary_metrics.csv) |
| smoke_pastnet_g075_fusion_context | pastnet_ma3afms | 1 | 23.461790 | 0.791345 | 40.943273 | 6283.930257 | 0.955021 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g075_fusion_context/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/f95974994a48__summary_metrics.csv) |
| smoke_pastnet_g075_interval3d_opt | pastnet_ma3ir | 1 | 23.485289 | 0.792979 | 40.537368 | 6231.121501 | 0.955412 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g075_interval3d_opt/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/1431dbfd6253__summary_metrics.csv) |
| smoke_pastnet_g076_latent_conv | pastnet_ma3lc | 1 | 23.563121 | 0.796505 | 39.963293 | 6134.430176 | 0.956262 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g076_latent_conv/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/6c326ffddfac__summary_metrics.csv) |
| smoke_pastnet_g077_latent_attention | pastnet_ma3la | 1 | 23.564808 | 0.796511 | 39.952469 | 6132.420844 | 0.956269 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g077_latent_attention/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/149c3fddaa0d__summary_metrics.csv) |
| smoke_pastnet_g078_latent_multiscale | pastnet_ma3lms | 1 | 23.563499 | 0.796549 | 39.965020 | 6134.574490 | 0.956257 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g078_latent_multiscale/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/874b06b9160f__summary_metrics.csv) |
| smoke_pastnet_g079_tail_aware | pastnet_ma3lt | 1 | 23.587214 | 0.796454 | 40.076152 | 6105.691840 | 0.956447 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g079_tail_aware/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/cb5c8eb22b5e__summary_metrics.csv) |
| smoke_pastnet_g07_ma3_wide | pastnet_ma3 | 1 | 17.633809 | 0.525520 | 89.138445 | 23942.376628 | 0.818906 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g07_ma3_wide/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/c6fbd13bcad0__summary_metrics.csv) |
| smoke_pastnet_g080_hybrid_tail | pastnet_ma3lh | 1 | 23.587070 | 0.796478 | 40.056156 | 6105.115560 | 0.956453 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g080_hybrid_tail/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/bc992afd17f8__summary_metrics.csv) |
| smoke_pastnet_g081_phase_flow | pastnet_ma3ad | 1 | 23.619085 | 0.796650 | 40.196204 | 6060.787082 | 0.956747 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g081_phase_flow/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/5347f7b6523a__summary_metrics.csv) |
| smoke_pastnet_g082_coord_inr | pastnet_ma3ci | 1 | 23.617476 | 0.796642 | 40.173519 | 6061.523465 | 0.956731 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g082_coord_inr/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/c5a37b382c04__summary_metrics.csv) |
| smoke_pastnet_g083_unrolled | pastnet_ma3ur | 1 | 23.620156 | 0.796596 | 40.196559 | 6058.133898 | 0.956749 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g083_unrolled/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/3604fae2fb4e__summary_metrics.csv) |
| smoke_pastnet_g084_dual_domain | pastnet_ma3df | 1 | 23.618164 | 0.796604 | 40.244475 | 6061.835666 | 0.956741 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g084_dual_domain/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/e5576735c69e__summary_metrics.csv) |
| smoke_pastnet_g085_volumetric | pastnet_ma3vs | 1 | 23.621284 | 0.796680 | 40.178793 | 6056.530084 | 0.956761 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g085_volumetric/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/264eeb526512__summary_metrics.csv) |
| smoke_pastnet_g086_dual_restart | pastnet_ma3df | 1 | 23.638146 | 0.798748 | 40.057407 | 6041.417291 | 0.956877 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g086_dual_restart/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/d56f975fdd12__summary_metrics.csv) |
| smoke_pastnet_g087_sparse_window | pastnet_ma3sw | 1 | 17.559304 | 0.523611 | 89.793672 | 24368.601997 | 0.815987 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g087_sparse_window/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/037451c111b7__summary_metrics.csv) |
| smoke_pastnet_g088_sparse_flow | pastnet_ma3sf | 1 | 17.580188 | 0.521911 | 89.415302 | 24254.538411 | 0.816357 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g088_sparse_flow/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/abcf366eb3f8__summary_metrics.csv) |
| smoke_pastnet_g089_sparse_dual | pastnet_ma3sd | 1 | 17.654987 | 0.525521 | 88.175082 | 23811.319770 | 0.819170 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g089_sparse_dual/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/cf9fed3d5ea8__summary_metrics.csv) |
| smoke_pastnet_g08_ma3_deep | pastnet_ma3 | 1 | 17.575034 | 0.445924 | 90.406288 | 24274.242405 | 0.817162 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g08_ma3_deep/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/849518217241__summary_metrics.csv) |
| smoke_pastnet_g090_sparse_hybrid | pastnet_ma3sh | 1 | 17.589230 | 0.524965 | 89.387724 | 24188.066406 | 0.816598 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g090_sparse_hybrid/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/16b2dfa82a22__summary_metrics.csv) |
| smoke_pastnet_g09_ma4w_lite | pastnet_ma4w | 1 | 17.557107 | 0.524050 | 89.858114 | 24382.647027 | 0.815995 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g09_ma4w_lite/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/22c937fac2d3__summary_metrics.csv) |
| smoke_pastnet_g10_ma4w_rescue | pastnet_ma4w | 1 | 17.558527 | 0.524614 | 89.812953 | 24372.517578 | 0.815960 | [design/fastmri_brain_pastnet_2p5d/runs/smoke_pastnet_g10_ma4w_rescue/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/520b3027c52b__summary_metrics.csv) |

### PAST 预测融合探针（诊断，不作为单一新模型）

保留全部11个MA3/MA4系数和4个checkpoint融合，不能只报最优24.0565。系数已在开发数据观察，不作为最终独立主排名。

| 融合方案 | n | PSNR | SSIM | MAE | MSE | NCC |
| --- | --- | --- | --- | --- | --- | --- |
| blend_ma3_0p7_ma4_0p3 | 24 | 24.056494 | 0.795376 | 40.232941 | 7831.494719 | 0.931952 |
| blend_ma3_0p6_ma4_0p4 | 24 | 24.052291 | 0.794606 | 40.380270 | 7834.929928 | 0.931940 |
| blend_ma3_0p8_ma4_0p2 | 24 | 24.037397 | 0.795522 | 40.196157 | 7868.113137 | 0.931573 |
| blend_ma3_0p5_ma4_0p5 | 24 | 24.024940 | 0.793217 | 40.633539 | 7878.418966 | 0.931535 |
| blend_ma3_0p9_ma4_0p1 | 24 | 23.995257 | 0.795041 | 40.275538 | 7944.785179 | 0.930808 |
| blend_ma3_0p4_ma4_0p6 | 24 | 23.974994 | 0.791223 | 40.988365 | 7961.961607 | 0.930735 |
| blend_ma3_1p0_ma4_0p0 | 24 | 23.930729 | 0.793941 | 40.477481 | 8061.510965 | 0.929661 |
| blend_ma3_0p3_ma4_0p7 | 24 | 23.903373 | 0.788641 | 41.439594 | 8085.557977 | 0.929542 |
| blend_ma3_0p2_ma4_0p8 | 24 | 23.811307 | 0.785496 | 41.982316 | 8249.208067 | 0.927959 |
| blend_ma3_0p1_ma4_0p9 | 24 | 23.700269 | 0.781821 | 42.612299 | 8452.911826 | 0.925988 |
| blend_ma3_0p0_ma4_1p0 | 24 | 23.571898 | 0.777655 | 43.325508 | 8696.669248 | 0.923636 |

来源：[design/fastmri_brain_pastnet_2p5d/runs/full_ma4w_150/metrics/blend_ma3_ma4_probe/summary.csv](handoff_evidence_20261023/source_files/ea9def33b041__summary.csv)。

| 融合方案 | n | PSNR | SSIM | MAE | MSE | NCC |
| --- | --- | --- | --- | --- | --- | --- |
| avg_ft30_ft60 | 24 | 23.932282 | 0.793882 | 40.478616 | 8061.667005 | 0.929687 |
| avg_warm_ft30 | 24 | 23.906271 | 0.793163 | 40.556072 | 8116.991664 | 0.929295 |
| blend_70ft30_30ft60 | 24 | 23.932106 | 0.793844 | 40.482576 | 8062.918857 | 0.929685 |
| blend_85ft30_15warm | 24 | 23.926080 | 0.793680 | 40.497140 | 8076.880341 | 0.929600 |

来源：[design/fastmri_brain_pastnet_2p5d/runs/full_ma3_psnr_ft60/metrics/blend_probe_outputs/summary_metrics.csv](handoff_evidence_20261023/source_files/1dd4bc65105e__summary_metrics.csv)。

### PAST 旧协议 IXI x4：全部正式和 smoke 记录

G07 full为115病例。旧G086固定profile `full_g086_dual_interval160_test115`未发现完成full，不能把单病例smoke当泛化结果。

| Profile | 等级 | n | PSNR | SSIM | MAE | MSE | NCC | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full_g07_ma3_wide200_test115 | full | 115 | 29.989239 | 0.915528 | 19.723950 | 3291.936051 | 0.973299 | [design/ixi_pastnet_2p5d/runs/full_g07_ma3_wide200_test115/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/d88b2c19493b__summary_metrics.csv) |
| smoke | smoke | 1 | 27.450979 | 0.857799 | 26.388355 | 3273.300141 | 0.956871 | [design/ixi_pastnet_2p5d/runs/smoke/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/e91fb7e90bbc__summary_metrics.csv) |
| smoke_g07_ma3_wide | smoke | 1 | 27.504276 | 0.825448 | 26.812244 | 3234.491974 | 0.957797 | [design/ixi_pastnet_2p5d/runs/smoke_g07_ma3_wide/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/e6e1f6e91dd9__summary_metrics.csv) |
| smoke_g086_dual_interval | smoke | 1 | 31.673480 | 0.944413 | 16.214524 | 1438.982492 | 0.983349 | [design/ixi_pastnet_2p5d/runs/smoke_g086_dual_interval/metrics/summary_metrics.csv](handoff_evidence_20261023/source_files/1ca5338c5ee8__summary_metrics.csv) |

G07 29.9892比同旧协议I3Net31.3058低1.3165 dB；fastMRI开发胜出未自动迁移到IXI。来源：[design/design1_pastnet/results/ixi_g07_test115_results_20260811.md](../../design/design1_pastnet/results/ixi_g07_test115_results_20260811.md)。

### PAST v2：干净 validation 合同下的全部 full

旧train/val交叉的一名患者被隔离后，validation为23患者/69区间/207缺失层；train111患者。共同评价为256²、只从真实观测网格算min/max、range=1、仅缺失层、不clamp、先series后patient等权，MAE/MSE为归一化单位。冻结G086在此合同25.515590；同预算control训练后25.562011。不能与旧fastMRI24.4470相减当收益。下列均为seed3407开发筛选，未做最终3seed确认。

| 分支 | 机制与可归因对照 | 判定 | 来源 |
|---|---|---|---|
| geometry | 原始DICOM毫米间距/方向经零初始化FiLM；对control | +0.002126，13/23胜、CI跨0，未达+0.08；停止 | [design/pastnet_v2/README.md](../../design/pastnet_v2/README.md) |
| correspondence-only | coarse作query，在锚点1/4、1/2特征3×3邻域读取对应；去掉geometry | +0.002471，18/23胜、95%CI[+0.001158,+0.003992]，未达+0.10；停止 | [design/pastnet_v2_independent/README.md](../../design/pastnet_v2_independent/README.md) |
| STC local | 四槽潜特征值/斜率/曲率多尺度轨迹拟合 | extended的同容量对照；对control +0.004119 | [design/pastnet_v2_context/README.md](../../design/pastnet_v2_context/README.md) |
| STC extended | 六槽真实稀疏上下文、valid mask与query轨迹拟合 | 对control+0.005208，对local仅+0.001089、CI跨0；停止 | 同上 |
| LACV crossview | 保留anchor轴，在(anchor,x)/(anchor,y)平面交互 | +0.014654，22/23胜、其余守卫过；不足+0.10，停止 | [design/pastnet_v2_crossview/README.md](../../design/pastnet_v2_crossview/README.md) |
| QGCR global | coarse query读取每锚点整幅1/8特征图 | +0.009011，不足+0.10，停止 | [design/pastnet_v2_globalmatch/README.md](../../design/pastnet_v2_globalmatch/README.md) |
| soft-tail | 同架构将hard top10% MSE改平滑CVaR | +0.002913；MAE/Dice均值守卫失败，停止 | [design/pastnet_softtail/README.md](../../design/pastnet_softtail/README.md) |
| orientation | 训练随机D4旋转/翻转；单方向推理、无TTA | +0.094388，未达+0.10；HD95强度代理退化+0.158420（95%CI[+0.061572,+0.264209]），SSIM略降；停止 | [design/pastnet_orientation/results/full_review.md](../../design/pastnet_orientation/results/full_review.md) |
| frame-context | 原方向主干增加低分辨率D4方向共享局部特征分支 | +0.000426、CI跨0；停止 | [design/pastnet_frame_context/results/full_review.md](../../design/pastnet_frame_context/results/full_review.md) |
| repair control | 按SeriesInstanceUID修复混合32层train volume为两个16层；逐像素验证、无重采样 | train1360→1356区间、仍111患者，val不变；+0.005442是数据修复收益 | [design/pastnet_series_integrity/results/full_review.md](../../design/pastnet_series_integrity/results/full_review.md) |
| wavelet3 | 10个depthwise卷积引入共享原卷积核的三级Haar算子、新增640gate参数 | 对repair +0.017549，23/23胜、95%CI[+0.012126,+0.024497]，其余守卫全过；仍不足+0.10，停止 | [design/pastnet_wavelet_trunk/results/full_review.md](../../design/pastnet_wavelet_trunk/results/full_review.md) |

| 配置 | 完成轮数 / best | PSNR | SSIM | MAE（归一化） | MSE（归一化） | NCC | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| control | 64/49 | 25.562011 | 0.835088 | 0.024628355 | 0.003099146 | 0.939549 | [design/pastnet_v2/runs/full_control_seed3407_vram20/validation/summary.json](handoff_evidence_20261023/source_files/56071e487948__summary.json) |
| geometry | 57/42 | 25.564138 | 0.835105 | 0.024623911 | 0.003097722 | 0.939578 | [design/pastnet_v2/runs/full_geometry_seed3407_vram20/validation/summary.json](handoff_evidence_20261023/source_files/76343324a587__summary.json) |
| correspondence-only | 67/52 | 25.564482 | 0.835147 | 0.024622676 | 0.003097662 | 0.939580 | [design/pastnet_v2_independent/runs/full_correspondence_only_seed3407_vram20/validation/summary.json](handoff_evidence_20261023/source_files/b98aa69b5958__summary.json) |
| STC local | 71/56 | 25.566130 | 0.835200 | 0.024617290 | 0.003095958 | 0.939612 | [design/pastnet_v2_context/runs/full_trajectory_local_seed3407_vram20/validation/summary.json](handoff_evidence_20261023/source_files/32a4ca59923f__summary.json) |
| STC extended | 71/56 | 25.567219 | 0.835213 | 0.024616874 | 0.003095697 | 0.939619 | [design/pastnet_v2_context/runs/full_trajectory_extended_seed3407_vram20/validation/summary.json](handoff_evidence_20261023/source_files/241a9a3bbc56__summary.json) |
| LACV crossview | 80/80 | 25.576666 | 0.835511 | 0.024586427 | 0.003090753 | 0.939735 | [design/pastnet_v2_crossview/runs/full_crossview_seed3407_vram20/validation/summary.json](handoff_evidence_20261023/source_files/8f33a4bcb522__summary.json) |
| QGCR global | 79/64 | 25.571022 | 0.835314 | 0.024604673 | 0.003093921 | 0.939665 | [design/pastnet_v2_globalmatch/runs/full_global_seed3407_vram20/validation/summary.json](handoff_evidence_20261023/source_files/2cbd3bd2ce1a__summary.json) |
| soft-tail | 64/49 | 25.564924 | 0.835145 | 0.024629490 | 0.003097018 | 0.939580 | [design/pastnet_softtail/runs/full_soft_tail_seed3407_vram20/validation/summary.json](handoff_evidence_20261023/source_files/ca757df4eef9__summary.json) |
| orientation | 32/17 | 25.656399 | 0.834677 | 0.024606142 | 0.003024985 | 0.940835 | [design/pastnet_orientation/runs/full_orientation_seed3407_vram20/validation/summary.json](handoff_evidence_20261023/source_files/9c24c8aff549__summary.json) |
| frame-context | 63/48 | 25.562437 | 0.835099 | 0.024627973 | 0.003098833 | 0.939554 | [design/pastnet_frame_context/runs/full_shared_seed3407_vram20/validation/summary.json](handoff_evidence_20261023/source_files/4d3151ce3bba__summary.json) |
| repair control | 67/52 | 25.567453 | 0.835200 | 0.024612513 | 0.003096434 | 0.939625 | [design/pastnet_series_integrity/runs/full_repair_seed3407_vram20/validation/summary.json](handoff_evidence_20261023/source_files/d1e3bfb1a76b__summary.json) |
| wavelet3 | 77/62 | 25.585002 | 0.835582 | 0.024564628 | 0.003085626 | 0.939853 | [design/pastnet_wavelet_trunk/runs/full_wavelet3_seed3407_vram20/validation/summary.json](handoff_evidence_20261023/source_files/6711b1ba1dd1__summary.json) |

| 配置 | Dice强度代理 | HD95强度代理 | tail10 MSE |
| --- | --- | --- | --- |
| control | 0.977189 | 5.402722 | 0.026967 |
| geometry | 0.977197 | 5.370199 | 0.026954 |
| correspondence-only | 0.977202 | 5.379044 | 0.026954 |
| STC local | 0.977210 | 5.334973 | 0.026938 |
| STC extended | 0.977209 | 5.359483 | 0.026935 |
| LACV crossview | 0.977251 | 5.311503 | 0.026896 |
| QGCR global | 0.977206 | 5.342826 | 0.026921 |
| soft-tail | 0.977189 | 5.386994 | 0.026942 |
| orientation | 0.977188 | 5.561142 | 0.026153 |
| frame-context | 0.977189 | 5.400875 | 0.026964 |
| repair control | 0.977208 | 5.344048 | 0.026946 |
| wavelet3 | 0.977250 | 5.289898 | 0.026854 |

Dice/HD95为强度阈值代理，不是组织/病灶分割。wavelet3总992819参数，推理52.963ms/缺失层，repair control47.841ms（+10.7%）；训练20.717GiB、约16.20h，未运行J1 full。患者间配对稳定不等于跨训练seed稳定。`pastnet_v2/runs/full_control_seed3407`是先前目录，本表采用实际完成且用于各gate的`_vram20` control。

### PAST 训练内探针、失败容量筛选与信息审计

这些诊断没有新神经网络full，也不与validation混排；check患者见过历史模型并参与开发，不能称为独立未见患者泛化。

| 尝试 | 数据 / 机制 | 全部主要结果与判定 | 来源 |
|---|---|---|---|
| 初始误差/信息审计 | 23干净val；旧归一化固定探针 | 中心phase最差；低/中/高频误差59.46%/34.03%/6.51%，top10%像素承载87.42%误差；各探针见下表 | [design/pastnet_v2/docs/01_证据与信息审计.md](../../design/pastnet_v2/docs/01_证据与信息审计.md) |
| 残差可预测性 | 冻结control；112train series/111患者/340区间/1020层；56fit/55check；32² ridge，self/local/extended | check基点26.866222；总增益+0.024857/+0.027663/+0.028215；远端对local仅+0.000552（调整CI[+0.000178,+0.000935]）；MAE退化1.34%/1.55%/1.52%；三探针失败，未进val | [design/pastnet_residual_audit/REPORT_ZH.md](../../design/pastnet_residual_audit/REPORT_ZH.md) |
| MAE不退约束 | 同56fit/55check；5种自身预测特征、每phase5系数、256² ridge、±0.05 | 无约束+0.025205，MAE+0.00030238、49/55胜；约束+0.002331（95%CI[+0.001480,+0.003403]）、MAE−0.00000288、42/55胜；未达+0.05，停止 | [design/pastnet_mae_constraint/README.md](../../design/pastnet_mae_constraint/README.md) |
| 解码幅度/梯度诊断 | 冻结control，同340train区间 | 主/detail/dual饱和0%/1.8665%/0%；饱和位置仅1.448%误差；低中高误差51.13%/40.10%/8.78%，loss输出梯度32.77%/33.81%/33.43%；不支持放宽bounded residual | [design/pastnet_decoder_audit/REPORT_ZH.md](../../design/pastnet_decoder_audit/REPORT_ZH.md) |
| 成熟latent分频读出 | 冻结64ch mixed latent；56fit175区间、55check165区间；shared65系数vs frequency193自由度，ridge0.001、±0.05 | control26.866222/shared26.888657/frequency26.890270；frequency对control+0.024048、对shared+0.001613；MAE+2.0841%；两效应门槛和MAE失败，不进神经full | [design/pastnet_latent_readout/REPORT_ZH.md](../../design/pastnet_latent_readout/REPORT_ZH.md) |
| bilateral transport | 两尺度25候选位移，比较L(x−td)/R(x+(1−t)d)，零投影；新增5185参数；4train区间96步 | bilateral MSE0.001982956→0.001964698（−0.9208%），stationary→0.001964999（−0.9056%）；合成平移MSE降99.72%但真实容量不足5%，未进val/full，未保存容量权重 | [design/pastnet_bilateral_transport/README.md](../../design/pastnet_bilateral_transport/README.md) |

| 固定探针（23val，旧诊断合同） | PSNR | MAE（归一化） | MSE（归一化） |
| --- | --- | --- | --- |
| diagnostic_nearer_real | 23.459073 | 0.034830063 | 0.004795727 |
| g086 | 25.899779 | 0.023665063 | 0.002880373 |
| linear | 20.786566 | 0.048553958 | 0.009028500 |
| oracle_four_envelope | 26.123840 | 0.014245322 | 0.002712802 |
| oracle_six_envelope | 26.855144 | 0.012147326 | 0.002310559 |
| oracle_target_lowres | 26.635417 | 0.028077908 | 0.002537218 |
| oracle_tvl1_target_alignment | 25.757022 | 0.024511155 | 0.002864113 |

来源：[design/pastnet_v2/results/audit_validation/summary.csv](../../design/pastnet_v2/results/audit_validation/summary.csv)。oracle使用target选择融合/低频/配准，不能部署、不能作为输入，不是整个生成模型的Bayes上限。fastMRI多数16层volume只有4张唯一真实x4观测，六槽边界会重复，不能说获得了6张独立采集。

### IXI wavelet3 迁移：test115（2026-10-03）

固定fastMRI wavelet3权重，IXI404train/58val微调80轮，seed3407；validation未clamp best32.1814、epoch80；锁权重后测115test患者/11001缺失层。统一256²、observed-only min/max、range=1、预测clamp[0,1]、患者等权。I3Net保留完整4→13滑窗、逐窗裁剪后重叠平均，最多利用6张真实锚点；PAST每区间4锚点。双方预训练、训练预算、损失和精度不同，属于固定checkpoint比较。

| 方法 | n / split | PSNR | SSIM | MAE（归一化） | MSE（归一化） | NCC |
|---|---|---|---|---|---|---|
| PAST wavelet3 | 115 test | 31.7358 | 0.9198 | 0.0125329 | 0.0009489 | 0.9692 |
| I3Net（外部参照） | 115 test | 33.8452 | 0.9419 | 0.0101137 | 0.0006097 | 0.9788 |

PAST−I3 PSNR −2.1094，95%CI[−2.2689,−1.9487]，3/115胜，困难四分位−1.6938。八项质量均落后：Dice proxy0.9503 vs0.9575、HD95 proxy2.7563 vs2.2518、tail10 MSE0.0083301 vs0.0052904。未晋级。

PAST/I3推理54.93/11.73ms每缺失层、峰值0.954/0.375GiB，包含CPU拷贝/打包，不含IO/评分，两模型同时驻留，PAST AMP/I3 FP32。PAST训练58.69h、20.71GiB，20000次尝试更新3次AMP跳过；末30轮best仍增0.0513，不能宣称完全收敛，也不因已见test自动续训。

主要评分差异已经定量核实：旧主表每GT切片max−min，新表病例观测范围；115例原始平面均256²，差异主要由data_range造成。同一预测折回旧范围，I3为31.3057435（与旧31.3057511差0.0000076），PAST29.1963；配对−2.1094保持。不能把33.8452与31.3058相减当模型进步；SSIM不能从汇总线性折算。

来源：[design/pastnet_ixi_wavelet/RESULTS_ZH.md](../../design/pastnet_ixi_wavelet/RESULTS_ZH.md)、[design/pastnet_ixi_wavelet/results/test115_seed3407/report.json](../../design/pastnet_ixi_wavelet/results/test115_seed3407/report.json)、[design/pastnet_ixi_wavelet/results/test115_seed3407/scoring_range_audit.json](../../design/pastnet_ixi_wavelet/results/test115_seed3407/scoring_range_audit.json)、[design/pastnet_ixi_wavelet/results/full_train_audit.json](../../design/pastnet_ixi_wavelet/results/full_train_audit.json)。[design/pastnet_ixi_wavelet_analysis/summarize.py](../../design/pastnet_ixi_wavelet_analysis/summarize.py)只是复核脚本，没有另一项模型。

### IXI-STC 四/六锚点配对 validation（2026-10-09，未晋级）

两臂同固定IXI wavelet3初始化、同容量STC、同数据顺序/损失/预算；六槽[-8,-4,0,4,8,12]，唯一变量为首尾远端真实锚点是否mask。1/4与1/8尺度拟合query中心潜特征值/斜率/曲率，零投影进入decoder前latent。seed3407各80轮、EMA best80；404train/58val，5595缺失层、患者等权。这里PSNR/SSIM用每GT切片范围，预测clamp；MAE/MSE归一化，与上个range=1 test表不能混排。

| 方法 / 58val | PSNR | SSIM | MAE（归一化） | MSE（归一化） | NCC | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| local，四锚点mask | 29.603433 | 0.912127 | 0.011693859 | 0.000834365 | 0.972168 | [design/pastnet_ixi_context/runs/full_local_seed3407/validation/summary.json](handoff_evidence_20261023/source_files/7b6abd91abe1__summary.json) |
| extended，六锚点 | 29.606836 | 0.912161 | 0.011691378 | 0.000834032 | 0.972186 | [design/pastnet_ixi_context/runs/full_extended_seed3407/validation/summary.json](handoff_evidence_20261023/source_files/4df00976364e__summary.json) |

extended−local +0.00340356，95%CI[+0.00081288,+0.00582258]，40/58胜；困难四分位+0.00010248；phase.25/.50/.75增益+0.00453380/+0.00398666/+0.00169023。七项质量方向不退，但未达+0.10效应门槛，停止，不追加seeds或候选test。共同初始化29.4089415；local/extended总增益+0.1944910/+0.1978946不能全部归于额外锚点。

local/extended提交训练62.8999/64.7125h、峰值20.819GiB，19997/20000实际AdamW更新；时间不含故障丢弃片段/停机/隔离smoke。中断同秒驱动更换但原始堆栈缺失，不能声称原因已证明。来源：[design/pastnet_ixi_context/RESULTS_ZH.md](../../design/pastnet_ixi_context/RESULTS_ZH.md)、[design/pastnet_ixi_context/results/gate_seed3407.json](../../design/pastnet_ixi_context/results/gate_seed3407.json)、[design/pastnet_ixi_context/results/completion_audit_20261009.json](../../design/pastnet_ixi_context/results/completion_audit_20261009.json)、[design/pastnet_ixi_context_recovery/README_ZH.md](../../design/pastnet_ixi_context_recovery/README_ZH.md)。

### I3Net–PAST latent bridge：已完成 full（2026-10-16，失败）

主表及`SMOKE_REPORT_ZH.md`仍写full待启动，但原始两臂completion与gate已落盘，各80轮完成，应以实际结果为准。

冻结历史I3Net提供同四真实锚点的64ch跨平面latent及预测基点，PAST小波MA3做query读出，修正限±0.05。blind屏蔽进入新读出的I3latent，latent开放它；两臂同初始化/容量/顺序/优化/预算。这是使用外部I3预训练权重的混合模型，没有增加真实观测，不能写成独立从零网络。

404train/58val，5595缺失层，per-GT-slice range、窗口clamp后均匀融合、患者等权；未读test。训练BF16 bridge/冻结I3与loss FP32，validation FP32；micro4×累积4，7/10块重计算。可训练桥接1,001,972（新读出9,153），冻结I3 23,205,197，总部署24,207,169参数。

| 方法 / 58val | PSNR | SSIM | MAE（归一化） | MSE（归一化） | NCC | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| blind（best77） | 31.671419 | 0.933914 | 0.009492220 | 0.000528059 | 0.980966 | [design/ixi_latent_bridge/runs/full_blind_seed3407/validation/summary.json](handoff_evidence_20261023/source_files/7f34cc3df417__summary.json) |
| latent（best67） | 31.671476 | 0.933917 | 0.009492344 | 0.000528099 | 0.980964 | [design/ixi_latent_bridge/runs/full_latent_seed3407/validation/summary.json](handoff_evidence_20261023/source_files/2ff9644c9f0d__summary.json) |
| 冻结I3Net（外部基点） | 31.652247 | 0.933237 | 0.009484674 | 0.000530647 | 0.980880 | [design/ixi_latent_bridge/results/gate_seed3407.json](handoff_evidence_20261023/source_files/128b49ed3c5b__gate_seed3407.json) |

latent−blind仅+0.00005754，97.5%CI[−0.00057640,+0.00069455]，32/58胜；latent−冻结I3 +0.01922886，97.5%CI[+0.01437901,+0.02410609]，55/58胜。分别低于+0.05/+0.10预登记门槛。对blind MAE+0.000000124、MSE+0.0000000394、NCC−0.000001598；对I3 MAE+0.000007670（97.5%CI全正），质量守卫也失败。困难四分位、时间/显存守卫通过不能替代核心失败。

blind/latent每轮1890.567/1891.432s，峰值19.2317GiB；推理122.7827/122.7335ms每缺失层，I3 12.6655ms，约9.69倍开销。停止机制，不追加seeds/test，没有SOTA。来源：[design/ixi_latent_bridge/PROTOCOL_ZH.md](../../design/ixi_latent_bridge/PROTOCOL_ZH.md)、[design/ixi_latent_bridge/results/gate_seed3407.json](handoff_evidence_20261023/source_files/128b49ed3c5b__gate_seed3407.json)、[design/ixi_latent_bridge/runs/full_blind_seed3407/completion.json](handoff_evidence_20261023/source_files/046dd670d3ad__completion.json)、[design/ixi_latent_bridge/runs/full_latent_seed3407/completion.json](handoff_evidence_20261023/source_files/5be2cd8014f2__completion.json)。

### 早期自行搭建的内部工程基线（非独立创新主张）

ResUNet residual是自行实现的确定性CNN工程baseline，原文明确不能写成创新。以下旧25病例结果不同于后来115例主表。

| 旧数据 / x4 | n | PSNR | SSIM | MAE | MSE | NCC | 来源 |
|---|---|---|---|---|---|---|---|
| IXI-PD ResUNet residual | 25 test | 30.2173 | 0.9212 | 30.2874 | 6170.1477 | 0.9846 | [docx/progress/Mar/5.25.md](../../docx/progress/Mar/5.25.md) |
| IXI-T1 ResUNet residual | 25 test | 28.8887 | 0.8808 | 37.8351 | 8148.3277 | 0.9621 | [docx/progress/Mar/5.27.md](../../docx/progress/Mar/5.27.md) |
| IXI-T2 ResUNet residual（旧25例） | 25 test | 27.4698 | 0.8874 | 29.3855 | 5680.4368 | 0.9508 | [docx/progress/Mar/5.28.md](../../docx/progress/Mar/5.28.md) |

PD/T1/T2相对Linear PSNR +3.8038/+4.2445/+1.3585，各25/25病例胜。约0.4890M参数、15.0701GFLOPs；PD mask-PSNR/mask-SSIM/Auto-Dice/Auto-HD95为25.6850/0.8894/0.9698/0.2378，T1为24.3403/0.8896/0.9314/1.1292，T2为21.9361/0.8715/0.9027/1.2456，Auto是代理。新主表T2 test115为27.4611，与旧25例27.4698分开。

早期TopCoW GAN v4继承师兄项目，[pre/v4（本地资产，见索引）](handoff_evidence_20261023/source_availability.csv)及[pre/topcow_gan（本地资产，见索引）](handoff_evidence_20261023/source_availability.csv)不列本人原创，相关35.7656等分数不纳入创新主表；[pre/topcow_diffusion（本地资产，见索引）](handoff_evidence_20261023/source_availability.csv)、[pre/ixi_diffusion（本地资产，见索引）](handoff_evidence_20261023/source_availability.csv)、[pre/ixi_hifidiff_strict（本地资产，见索引）](handoff_evidence_20261023/source_availability.csv)为baseline/复现管线。来源：[docx/progress/周报.md](../../docx/progress/周报.md)、[docx/progress/Mar/5.11.md](../../docx/progress/Mar/5.11.md)、[pre/topcow_diffusion/README.md](../../pre/topcow_diffusion/README.md)。

### PAST 的比较边界与未实现状态

旧fastMRI24是被重复使用的开发test，v2 23是干净validation，IXI wavelet115为用户指定探索test，STC/bridge58是validation。split、归一化、data_range、clamp与上下文不同，不能跨表直接排名。

真实z-spacing /x4间隔中位数：fastMRI5.00/20.00mm，IXI1.25/5.00mm，NingXia fold00 train/val4.40/17.60mm；同为T2 x4并不等于同物理难度。134/135 fastMRI train/val series恢复几何，异常者使用known mask。来源：[design/pastnet_v2/docs/01_证据与信息审计.md](../../design/pastnet_v2/docs/01_证据与信息审计.md)。

geometry累加correspondence链已停止，独立correspondence-only才有正式full。没有找到满足全部实用晋级门槛的PAST v2最终候选，没有最终3seed或NingXia PAST正式结果。旧IXI G086仅smoke，不与后来的wavelet/STC/bridge混同。所有失败只否定当前实现和预算，不能外推为MRI信息上限；target oracle、训练内探针、患者bootstrap不能替代独立seed与锁定外部test。


---

## ACSI-Net：解剖一致性分组插值网络

**项目自研内容。** 两端真实稀疏锚点、全部线性粗插值中间层、相位图、有向差值和绝对差值联合条件化；anchor/coarse/phase/difference 四支编码后，用 AnatomyBlock、confidence 门控 residual 和浅层 3D z-refinement 一次恢复一组中间层。损失包含 Charbonnier、xy-gradient、z-gradient、z-Laplacian、edge-z、anatomy-weighted L1 和 residual regularization。目标是轻量的体积连续性插值；“3D 一致性优于强基线”是待检验假设。

| IXI T2 ×4，ACSI v1 阶段 | 评估病例 | PSNR↑ | SSIM↑ | MAE↓ | MSE↓ | NCC↑ | ZGE↓ | ZLE↓ | EdgeZ↓ | NCC-z-MAE↓ | 参数 M / 每生成层 FLOPs G | 判定 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| smoke | 1 | 26.0174 | .7942 | 33.5206 | 4430.8866 | .9495 | .0149 | .0233 | .0098 | .0161 | .0633 / 2.7273 | 链路筛查；PSNR 低于 Linear 27.4291 |
| mini | 5 | 25.7478 | .8438 | 43.0894 | 11134.6133 | .9229 | .0172 | .0255 | .0128 | .0555 | .2129 / 9.1244 | 小规模可行；Linear PSNR 25.0849 |
| full_test115 | 115 | 29.3904 | .9078 | 20.8475 | 3675.8976 | .9701 | .011285 | .017786 | .009948 | .025556 | .3442 / 14.6843 | 正式结果；轻量竞争性模型，强解剖一致性主张未通过 |
| 同口径 Linear（参照） | 115 | 26.1722 | .8529 | 29.2781 | 6553.8673 | .9390 | .0143 | .0207 | .0110 | .0413 | 0 / 0 | ACSI 重建指标 115/115 全胜 |
| 同口径 Cubic（参照） | 115 | 25.7138 | .8422 | 31.1269 | 7217.2979 | .9303 | .0148 | .0208 | .0114 | .0403 | 0 / 0 | ACSI 重建指标 115/115 全胜 |
| I3Net（外部架构本地复跑参照） | 115 | 31.3058 | .9285 | 17.5276 | 2565.3177 | .9788 | .009680 | .015543 | .008974 | .019664 | 23.205 / 100.776 | ACSI 四项 3D 指标均不如它 |

v1 full 训练配置为 30 epochs、batch 6×累积4、48通道、8块、z-refine通道8。manifest 的 train/val/test 数字字段为 null，115例由实际汇总和 eval ID 列表确认，不以 null 补造训练样本数。对 I3Net 的 ZGE/ZLE/EdgeZ/NCC-z-MAE 病例胜数仅 5/9/7/5（均除以115）。ACSI 参数约少67.4倍、每生成层FLOPs约少6.86倍，但不能据此声称真实整卷推理同倍加速。

证据：[模型](../../design/acsinet/model.py)、[损失](../../design/acsinet/losses.py)；[smoke分阶段表](handoff_evidence_20261023/source_files/4b4607666bbe__paper_table.md)、[mini分阶段表](handoff_evidence_20261023/source_files/322e547724db__paper_table.md)、[full_test115重建CSV](handoff_evidence_20261023/source_files/90b5e0874922__summary_metrics.csv)、[full_test115三维一致性CSV](handoff_evidence_20261023/source_files/2ade0d3fbb9c__summary_3d_consistency.csv)；[ACSI对I3Net主张审计](../../docx/experiment_notes/acsinet_3d_consistency/acsi_vs_i3net_claim_audit_2026-07-09.md)、[对I3Net三维一致性CSV](../../docx/experiment_notes/acsinet_3d_consistency/acsi_vs_i3net_summary_3d_consistency.csv)、[全部参照重建CSV](../../docx/experiment_notes/acsinet_3d_consistency/ixi_full_test115_reconstruction_summary.csv)。

## ACSI-v2 / v2.1：四锚点窗口与 NCC-profile 一致性约束

**自研变化。** 四稀疏锚点在×4下恢复13层窗口（0/4/8/12强制保留，9个生成位置）；输入为4 anchors+13 coarse+13 phase+3 difference+3 absolute-difference，共36通道。零初始化残差/3D尾部，使初始网络等价于线性粗插值。v2.1 新增预测与GT相邻切片 NCC 曲线匹配，并加大 z-gradient/z-Laplacian/edge-z 权重，试图避免把单纯平滑当成解剖连续。

| 阶段（IXI T2 ×4） | train / val / eval | epochs | PSNR↑ | SSIM↑ | MAE↓ | MSE↓ | NCC↑ | ZGE↓ | ZLE↓ | EdgeZ↓ | NCC-z-MAE↓ | 状态 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| v2 smoke | eval 1 | 1 | 26.5416 | .8490 | 30.1155 | 3973.5656 | .9501 | .0106 | .0132 | .0080 | .0277 | 低于 Linear/Cubic，链路通过不等于有效 |
| v2 mini | 8 / 2 / 2 | 3 | 23.9040 | .7648 | 54.0138 | 15693.9528 | .8805 | .0209 | .0320 | .0119 | .1049 | 重建略超 Linear，3D 基本持平或较差 |
| v2.1 mini_consistency | 8 / 2 / 2 | 8 | 23.9142 | .7656 | 54.0037 | 15764.7194 | .8802 | .02095 | .03199 | .01194 | .10473 | 预设晋级失败，未启动 full_test115 |
| mini_consistency Linear | 同2例 | — | 23.8926 | .7638 | 54.6535 | 16518.7019 | .8756 | .02086 | .03194 | .01187 | .10246 | v2.1 四项3D指标均未超过它 |
| mini_consistency Cubic | 同2例 | — | 23.3145 | .7435 | 60.9144 | 20319.2395 | .8548 | .02219 | .03276 | .01266 | .09518 | v2.1 NCC-z-MAE 仍较差 |

v2模型约 .0637M 参数、每192×192窗口4.787G FLOPs、每生成层 .5319G。v2.1 相邻层预测 NCC=.97949，Linear=.97723，Cubic=.96693，GT=.87477；输出仍过度相关。原定“至少三项3D指标同时超过Linear/Cubic”未通过。下一步 residual-only / residual+z-refine / full-loss 消融在报告中是建议，未找到完成结果，不能写成已做。

证据：[v2进展](../../design/acsinet_v2/docx/进展_2026-07-09.md)、[v2.1筛查报告](../../design/acsinet_v2/reports/anatomy_consistency/mini_consistency_2026-07-14.md)；[smoke重建CSV](handoff_evidence_20261023/source_files/cf5a005cd669__summary_metrics.csv)、[mini重建CSV](handoff_evidence_20261023/source_files/3e341cafd595__summary_metrics.csv)、[mini_consistency重建CSV](handoff_evidence_20261023/source_files/e4ed88aa2dad__summary_metrics.csv)、[mini_consistency三维一致性CSV](handoff_evidence_20261023/source_files/34f784c4080b__summary_3d_consistency.csv)、[复杂度JSON](handoff_evidence_20261023/source_files/8af9efce97b5__complexity.json)。

## RASI-Net 训练型原型：可靠性感知分组插值

**自研内容。** 在锚点+coarse+phase+差值的组输入上加入 PhaseFiLM、depthwise ReliabilityBlock、通道注意力，同时输出 residual/confidence/log-variance；`prediction=coarse+sigmoid(confidence)*0.75*tanh(residual)`，uncertainty用softplus(log-variance)。重建与不确定性共同训练。

| IXI T2 ×4 阶段 | 样本/训练 | PSNR↑ | SSIM↑ | MAE↓ | MSE↓ | NCC↑ | pixel error–U corr | slice error–U corr | risk-AURC↓ | MAE@低U 50%↓ | 参数M / 每生成层FLOPs G |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| smoke | eval1 | 26.5423 | .8473 | 30.0443 | 3966.2439 | .9501 | −.1654 | .1292 | 34.5782 | — | .0413 / 1.6924 |
| mini | train16 / val4 / eval5，5 epochs | 25.1963 | .8339 | 45.6286 | 12493.6609 | .9137 | .6532 | .8215 | 8.9841 | 1.8911 | .151879 / 6.30719 |

mini 同5例 Linear PSNR25.0849/SSIM.8268/MAE47.0867，Cubic24.6061/.8131/51.1790。辅助说明报告列 failure AUROC=1、top-k recall=1，但仅5例。当前 `runs/full_test115/` 有manifest及空产物目录，未发现metrics/checkpoint文件，不能把存在full配置写成full训练完成。项目后续已转向不训练重建器的post-hoc可靠性主线，训练型RASI只保留筛查证据。

证据：[RASI模型](../../design/rasinet/model.py)、[smoke分阶段表](handoff_evidence_20261023/source_files/85047ac33df4__paper_table.md)、[mini重建CSV](handoff_evidence_20261023/source_files/d9b7394b0a9f__summary_metrics.csv)、[mini可靠性CSV](handoff_evidence_20261023/source_files/b274fef027b6__summary_reliability.csv)、[mini复杂度JSON](handoff_evidence_20261023/source_files/0ec4a9caa4de__complexity.json)、[learned RASI辅助消融说明](../../design/rasinet/reports/posthoc_uncertainty/learned_rasi_ablation_note.md)。

## RASI post-hoc / target-excluded committee disagreement

**项目提出的使用方式与评价协议。** 复用已有插值输出，不重训重建模型；对目标模型m从committee中排除m，体素分数为`median_b|ŷ_m−ŷ_b|`，仅真正生成的切片上评分，部署支持可由目标预测1%前景形成，病例内聚合进行复核优先级排序。需区分早期`baseline_disagreement`表和后续target-conditioned/统一支持/nested研究，不能把不同分数、支持和强度单位的AURC混为同一个终点。

### 早期完整三队列 post-hoc 结果（历史口径）

以下来自实际完整汇总CSV；pixel corr为all-pixel均值，非零corr是独立的更严格支持敏感性。NingXia为22个序列/检查、8患者的OOF资料；22不能作为22独立患者。

| 数据/倍率 | 目标模型 | n | pixel corr | nonzero corr | slice corr | AURC↓ | MAE@低U50%↓ | failure AUROC↑ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| IXI T2 ×4 | ACSI | 115 | .5667 | .4037 | .4178 | 4.2948 | 1.4552 | .9871 |
| IXI T2 ×4 | HAT | 115 | .6090 | .4628 | .4578 | 4.4683 | 1.5250 | .9871 |
| IXI T2 ×4 | I3Net | 115 | .5018 | .3068 | .3567 | 3.9249 | 1.4225 | .9822 |
| IXI T2 ×4 | SwinIR | 115 | .6153 | .4711 | .4572 | 4.4922 | 1.5253 | .9871 |
| fastMRI-brain T2 ×4 | HAT | 24 | .4895 | .3176 | .2850 | 15.4140 | 7.4665 | 1 |
| fastMRI-brain T2 ×4 | I3Net | 24 | .4138 | .2347 | .3457 | 13.6226 | 7.1036 | 1 |
| fastMRI-brain T2 ×4 | SwinIR | 24 | .5122 | .3500 | .2942 | 15.6157 | 7.3133 | 1 |
| NingXia T2 ×4 | HAT | 22 | .4581 | .2904 | .2671 | 30.4454 | 24.5532 | .9474 |
| NingXia T2 ×4 | I3Net | 22 | .4856 | .3137 | .3555 | 32.8816 | 26.1346 | .9474 |
| NingXia T2 ×4 | SwinIR | 22 | .4562 | .2886 | .2758 | 30.2951 | 24.4725 | .9474 |

背景会明显抬高pixel相关，不能只报all-pixel。相对linear/cubic residual proxy的完整正负结果位于同CSV；总体risk-coverage通常不如baseline disagreement，但部分slice相关更高。failure definition改变结论：例如IXI ACSI的top-ZGE/top-ZLE AUROC仅.445；NingXia bottom-mask-SSIM AUROC仅.3333，不能将top-MAE检测结果外推成所有结构失败检测。

4-view flip TTA是外部常用参照，本项目完成的proxy消融，不列为原创算法：SwinIR在fastMRI/IXI/NingXia的slice corr分别.7673/.8557/.6665，均高于disagreement .2942/.4572/.2758；pixel corr .4786/.5748/.4033和AURC15.7601/4.6478/30.7713均未稳定优于disagreement。额外运行耗时26.6/663.5/49.2秒，不能与纯stored-output评分等同。

证据：[IXI115可靠性CSV](../../design/rasinet/reports/posthoc_uncertainty/full_test115/full_test115_reliability_summary_cn.csv)、[fastMRI24可靠性CSV](../../design/rasinet/reports/posthoc_uncertainty/fastmri_full/fastmri_full_reliability_summary_cn.csv)、[宁夏22可靠性CSV](../../design/rasinet/reports/posthoc_uncertainty/ningxia_cv/ningxia_cv_reliability_summary_cn.csv)、[masked/domain-shift CSV](../../design/rasinet/reports/posthoc_uncertainty/paper_experiments/domain_shift_masked_summary.csv)、[失败定义消融报告](../../design/rasinet/reports/posthoc_uncertainty/paper_experiments/paper_experiment_summary.md)、[三队列TTA对比](../../design/rasinet/reports/posthoc_uncertainty/tta_variance_cross_dataset_summary.md)。底层逐病例数据另在`design/rasinet/runs/posthoc_uncertainty/`各profile的metrics目录。

### committee / score / mask / pooling 的设计搜索及负迁移

候选族包含median/mean/trimmed/max/q75/q90、目标到committee中心距离、pairwise分歧、gradient/Laplacian结构域、shared/target分解；mask包含target1%、输入前景、committee union等；voxel/case pooling包含mean、tail/quantile、worst pooling。committee按frozen-primary、low-cost、high-fidelity、family-balanced、availability-conditioned bank等规则构造。注册数367不等于367全部跑出完整评估；当前registry240行有开发数值、4行frozen-validation，完整明细由主汇总附表记录。

开发=IXI×4+fastMRI×2/×4/×6；一次性冻结验证=NingXia×2/×4/×6，每层22个OOF检查；主目标I3Net/HAT/SwinIR。

| 历史 finalist | 开发 mean / worst nAURC↓ | 开发ρ↑ | 宁夏 mean / worst nAURC↓ | 宁夏ρ↑ | 宁夏 RRR50↑ | 判定 |
|---|---|---:|---|---:|---:|---|
| 预设 baseline `c_c98f4ad5b505` | .08871 / .19062 | .90577 | .07021 / .12522 | .90150 | 21.79% | 原预设分数保留 |
| 开发选择 universal `c_f5fed2ef96c3` | .04032 / .09889 | .94696 | .11556 / .20701 | .83851 | 19.92% | 明确负迁移 |
| low-cost `c_a7d0a77ecf68` | .08666 / .15876 | .90628 | .08024 / .16570 | .89322 | 21.22% | 未证实优于baseline |
| shared-difficulty `c_cc96ad828dc6` | .03649 / .09329 | .95181 | .11078 / .19536 | .84754 | 20.37% | 开发好，验证失败 |

这些是历史结果：后续审计确认旧选择实现未实现声明的cost rank/one-SE，跨模型fidelity用了不同target-derived支持、high-fidelity实际还包含Linear/Cubic、所谓universal随可用模型变化、aggregate bootstrap错误flatten profiles，不能当作最终无缺陷选择实验。原结果仍保留，不用新结果抹去负迁移。

证据：[四finalist汇总CSV](handoff_evidence_20261023/source_files/3f23d19b5ee0__finalist_summary.csv)、[分profile验证CSV](handoff_evidence_20261023/source_files/9388732c030a__finalist_validation_results.csv)、[冻结验证配置](handoff_evidence_20261023/source_files/e12e0959c3ec__frozen_finalists_validated.yaml)、[367候选注册表](../../design/rasinet/results_registry.csv)、[旧优化审计与纠正要求](../../design/rasinet/CURRENT_OPTIMIZATION_AUDIT.md)。

### 修正后的 nested optimization / 物理跨倍率一致性

修正内容包括共同GT支持只用于离线fidelity标签、真实cost-rank+one-SE、8外折患者/检查分离选择、inner-only校准、profile内对齐bootstrap及world-coordinate generated-plane匹配。共187个开发profile-case、66个宁夏factor-case、8,712个target-member记录；广交互搜索561,492个候选、1,320个分层finalists。8外折×3倍率×11目标×2角色产生528项选择；另保留神经peer强制纳入的amended协议敏感性。不能把这些重复profile/factor数当独立患者数。

| 修正后宁夏汇总，三主目标×三倍率 | mean nAURC↓ | caseρ↑ | RRR50↑ | 结论 |
|---|---:|---:|---:|---|
| frozen baseline | .077209 | .884058 | 21.9067% | 共同支持后的比较基点，与旧.07021不同 |
| physical consistency | .051571 | .911412 | 21.3708% | nAURC改善，RRR50无确定改善 |
| frozen+physical固定rank混合 | .050427 | .908489 | 21.5991% | 与physical差−.001144，CI跨0，未证明混合必要 |
| mean disagreement | .080860 | .883305 | 21.4534% | 未超过预设median |
| unconstrained nested triage / low-cost | .270359 | .705225 | 19.9438% | 显著失败，不能推为优化成功 |
| amended robust nested triage | .298562 | .670221 | 19.4112% | 再次失败 |
| amended robust nested low-cost | .400892 | .559996 | 18.5613% | 失败 |
| shared-difficulty | .404506 | .537076 | 13.2515% | 失败 |

physical−baseline配对ΔnAURC=−.025639，profile-aligned95%CI[−.063291,−.000595]；但该是当阶段profile-aligned推断，paper后续改用examination-cluster后，宁夏CI跨0，见下节PC历史纠正。跨倍率逐条物理匹配1,518/1,518成功，阈值.001mm，仅匹配两倍率均为生成层的共同世界平面，不作插值。它推翻旧“138个shape不一致所以跨尺度不可计算”的结论。

尺度异质性：physical的×2/×4/×6 nAURC=.075071/.053207/.026435，对应baseline=.070069/.063110/.098450；×2点估计较差，不能只报×6大幅改进。target attribution即使使用共同误差支持和内层校准，平均matched advantage约.060、within-caseρ约.126、top1约27.3%；×2/×4/×6 top1为27.27%/22.73%/31.82%，不足以可靠识别究竟哪个模型错。

证据：[nested纠正报告](../../design/rasinet/revision_report_nested_optimization.md)、[物理对齐审计](../../design/rasinet/cross_scale_physical_alignment_audit.md)、[最终分尺度/目标汇总CSV](handoff_evidence_20261023/source_files/76dd725acd46__nested_aggregate_results.csv)、[profile-aligned配对CI](handoff_evidence_20261023/source_files/3a7e7994e8c8__profile_aligned_paired_summary.csv)、[目标归因CSV](handoff_evidence_20261023/source_files/7933b47029af__target_attribution_nested_results.csv)、[1,518条物理匹配记录](handoff_evidence_20261023/source_files/538fce3131b2__cross_scale_physical_pair_scores.csv)、[主张来源映射](handoff_evidence_20261023/source_files/f53e27e15c2f__nested_claim_traceability.csv)。

### shared-error stress与当前证据缺口

20个固定IXI检查×4目标×5强度的patch stress：target-only从强度0→1，target MAE57.6606→66.2485，disagreement33.1349→42.6054；对所有成员施加相同patch时MAE同样上升、committee MAE70.3227→78.6013，但disagreement恒为33.1349。共享误差在差分中消失；该分数只能排查可见差异，不能证明低分即正确。

成本报告实测stored-output scoring 30例均值1.184秒、P95 2.872秒、CPU RSS峰值.89GiB；不含在线多模型推理。统一硬件在线latency/显存未补齐，reader/临床任务未做。

**当前文件冲突。** `experiment_plan.md`声称full benchmark有161 examination/504组/33,672病例结果，但本次读取`outputs/icassp_full_benchmark/summary.csv`仅236行且每行cases=2，analysis也没有primary，表现为小样本产物。不能用这份当前CSV证明报告的full计数；上面的115/24/22早期post-hoc与nested CSV独立存在。`unresolved_todos.md`仍有旧“只支持×4”的文字，已被实际nested多尺度证据超越，不能机械照抄。

证据：[shared-error stress CSV](handoff_evidence_20261023/source_files/453899e6c2bd__summary.csv)、[stored-output成本CSV](handoff_evidence_20261023/source_files/4b7eb2562849__summary.csv)、[历史实验清单](../../design/rasinet/experiment_plan.md)、[当前存在冲突的benchmark CSV](handoff_evidence_20261023/source_files/437970ee0cce__summary.csv)。

## ECSI-Net：change-aware高效残差插值（已实现，无真实训练结果）

**项目自研内容。** 外部`[L,R,C,P]`扩展为`[L,R,C,P,D,A]`，linear coarse作为基底，depthwise E-Block+ECA编码；mask branch控制轻量residual，`ŷ=C+M*R`。mask末层负bias初始化偏向coarse；预设主张为quality–efficiency Pareto而非全指标SOTA。

2026-07-15静态验收PASS：4/6通道随机输入均输出`2×1×16×16`；公式校验、mask∈[0,1]、loss有限、checkpoint round-trip和stride不匹配拒绝通过；mask随机值约.110214–.115006；11/11执行器测试通过。这些不是MRI真实结果。

本次目录仍无`runs/`；当时GPU预检因外部计算进程约18,158/24,455MiB占用未通过，profile/smoke/mini未启动。虽然存在×2/×4/×6和full_test115配置，未产生真实质量、速度、显存、mask健康度、Pareto或跨队列结论。没有fastMRI独立包、未接入宁夏CV；不能把计划放行阈值当已达到的数字。

证据：[ECSI说明](../../design/ixi_ecsinet_2p5d/README.md)、[模型](../../design/ixi_ecsinet_2p5d/model.py)、[静态检查结果](../../design/ixi_ecsinet_2p5d/reports/efficiency/static_validation.md)、[完整验收/未完成清单](../../design/ixi_ecsinet_2p5d/reports/efficiency/checklist.md)、[原始设计](../../docx/design/design6_ecsinet_efficiency.md)。

## 自研研究方法与实验协议：PC、测量依赖、shared influence、MIRA与采样收益

这些是项目提出/发展的研究方法、审计框架和实验设计，**不等同于新重建网络**。基础三角不等式、误差差分恒等式、协方差展开、leave-one-out和一致性不确定性本身属于既有数学/研究工具；本项目的可区分贡献是固定同一缺失目标、操纵真实物理锚点/采样上下文，结合有限响应、共同误差分解、信息合同和完整反证。HAT/SwinIR/I3Net/SAINT/CycleINR等只作冻结参照，不归为作者原创网络。

### PC-v1 / PC-v2：同世界平面的跨倍率一致性

PC-v1匹配×2/×4/×6同一NIfTI世界平面，用绝对预测差及固定聚合揭示至少一个输出有误。`d(f_a,f_b)≤d(f_a,y)+d(f_b,y)`只提供单向错误证据；低PC不能认证准确。PC-v2使用共同per-case尺度归一化，为探索分支，不以独立倍率归一化任意消除信号。

| 结果合同 | n | 主要结果 | 实际结论 |
|---|---:|---|---|
| fastMRI8例推导后16例定位确认 | 16、960配对平面 | pixel Spearman中位.693[.649,.743]，sliceρ.799，case-pairρ.915，top10%错误富集2.49倍[2.32,2.72] | 多粒度误差定位关联可重复；同项目已被长期研究的队列，不称全研究历史未触及 |
| 宁夏OOF定位复现 | 22、1,464平面 | pixelρ.489[.477,.500]、sliceρ.727、case-pairρ.883、富集2.06倍[2.00,2.15] | 有效关联，小患者簇边界 |
| fastMRI PC vs committee，examination-cluster纠正 | 24 | ΔnAURC−.0698[−.1597,−.0183]，p=.005，9/9 profiles方向正 | 比较优势获得支持 |
| 宁夏PC vs committee，examination-cluster纠正 | 22 | ΔnAURC−.0256[−.0957,.0092]，p=.164；6/9方向正、22/22 LOO保留均值方向 | **撤回早期“宁夏CI排除0”**；优势异质且不确定 |
| 共同尺度PC-v2探索 | fastMRI24 | normalized PC vs normalized error ρ=.593；nAURC .114 vs normalized committee .266，Δ−.152[−.278,.017] | 归一化后残留关联，比较CI跨0 |
| 与4-view flip-TTA的18个匹配profiles | 2队列×3倍率×3目标 | 18/18 PC更优；mean ΔnAURC fastMRI−.0340(p=.0035)、宁夏−.1143(p=.0015) | 只证明该合同下优于flip-TTA，非所有扰动 |

blur反证：8个固定fastMRI病例，最大共享均匀blur令MAE+3.69而cross-model score−12.79、PC−7.89；两个评分都更“平静”却更错。自然宁夏14个low-PC/high-error平面，12个集中×4/×6第一生成层，构成stable-wrong边界。raw PC/raw MAE nAURC .019、ρ.965很高，但dynamic range与PCρ.851、与raw errorρ.643；尺度共变不能省略。

证据：[PC最终历史报告](../../design/paper/ARCHIVE/RESEARCH_RECORDS/REPORTS_AND_AUDITS/FINAL_RESEARCH_REPORT.md)、[完整反证](../../design/paper/ARCHIVE/RESEARCH_RECORDS/REPORTS_AND_AUDITS/FALSIFICATION_REPORT.md)、[机制与尺度混杂报告](../../design/paper/ARCHIVE/RESEARCH_RECORDS/FOUNDATION_AND_NOTES/MECHANISM_REPORT.md)、[Plan3多架构/TTA扩展](../../design/paper/ARCHIVE/PLANS/PLAN02_TO_PLAN04/PLAN3_RESEARCH_REPORT.md)。

### shared/observable error分解、检查难度与曲率模型

项目将配对误差拆成共识与差异能量，发现fastMRI/宁夏中shared consensus约80.9%/86.5%、observable diversity约19.1%/13.5%。误差方差的病例部分.583/.839，倍率部分.258/.125，架构部分.103/.006；138个case–architecture单位均×2误差<×4<×6。说明检查/采样难度可跨架构共享，增加架构种类不自动形成有用错误多样性。

输入难度proxy来自相邻已采集层RMSE：raw error相关fastMRI .719、宁夏.780、IXI115六方法均值.982；归一化终点后降为.503/.465/.251。曲率–spacing回归在held-out fastMRI较spacing alone提升ρ .595→.722、R² .329→.479；无拟合rank向宁夏转移ρ .606，但绝对校准失败，fastMRI简单anchor-change更强，**普适曲率定律被否定**。target curvature只作回顾性机制量，不能当部署输入。

证据：[Plan3误差分解与检查难度](../../design/paper/ARCHIVE/PLANS/PLAN02_TO_PLAN04/PLAN3_RESEARCH_REPORT.md)、[Plan4曲率/spacing与物理干预](../../design/paper/ARCHIVE/PLANS/PLAN02_TO_PLAN04/PLAN_4_REPORT.md)。

### 同目标 shared/disjoint物理锚点干预与身份/几何控制

方法在同一个缺失目标上，固定reference A0，比较伴随B0（共享phase0锚点）与B2（phase2互补锚点）；早期反序/flip共享对照与后来的干净跨架构对照分开保存。即使锚点不相交，解剖、模型先验、预处理仍可能共享，不能等同统计独立或纯单因素因果识别。

早期Plan4 zero-vs-max overlap：fastMRI192平面ρ .960 vs .605，Δ.355[.225,.557]；宁夏248平面 .891 vs .699，Δ.193[.111,.306]。disjoint分歧幅度反而只有共享对照的.59–.77倍，否定“分歧越大越有用”。解析Linear/Cubic病例ρ fastMRI .977/.974、宁夏.958/.967。需要新获取两个phase才可用时已付×2采集成本，所以“免费前瞻加密决策”解释撤回。

最新完整五核心20有序跨模型对×两脑队列（每例五目标，27,800逐平面、200终点汇总）：

| 对照终点 | fastMRI24 | IXI115 |
|---|---|---|
| 局部observable gain范围 | +6.236至+16.022个百分点 | +13.113至+28.531个百分点 |
| 局部ΔO、alignment下降、disagreement上升的同时CI方向 | 各20/20通过 | 各20/20通过 |
| 固定reference误差排序改善同时CI正 | 0/20 | 16/20 |
| pair平均误差排序改善同时CI正 | 0/20 | 20/20 |

IXI未显著的4个fixed-reference方向均以I3Net为伴随；fastMRI SAINT→I3Net点估计甚至为负。局部可见性与全局病例排序必须分开。原始GT支持明确为target-informed；后续support/geometry敏感性不将其偷偷重命名为acquired-only。family均值ΔO fastMRI10.478pp[9.625,11.354]、IXI21.775pp[21.257,22.332]；leave-one-architecture-out仍全正，但模型对共享病例，不是20独立重复。fastMRI full-four-anchor+双residue资格为0，不能靠填边界补齐；镜像方向差fastMRI−.937pp[−1.555,−.339]保留为方向警告。

13实现的相位接口后来全部覆盖；另8实现采用退化self-control，shared O=0是构造事实，其正ΔO仅为相位敏感性，**不算13架构都验证shared-error机制**。

证据：[完整五核心实验报告](../../design/paper/FINAL_SCIENTIFIC_STRENGTHENING/FINAL_REPORT_ZH.md)、[跨架构结果解释](../../design/paper/FINAL_SCIENTIFIC_STRENGTHENING/CROSS_ARCH_INTERPRETATION.md)、[模型家族稳健性](../../design/paper/FINAL_SUBMISSION_PREPARATION/CROSS_ARCH_FAMILY_ROBUSTNESS.md)、[几何敏感性](../../design/paper/FINAL_SUBMISSION_PREPARATION/CROSS_ARCH_GEOMETRY_SENSITIVITY.md)、[支持区域敏感性](../../design/paper/FINAL_SUBMISSION_PREPARATION/CROSS_ARCH_SUPPORT_SENSITIVITY.md)、[13实现覆盖审计](../../design/paper/ARCHITECTURE_COVERAGE_CLOSURE/ARCHITECTURE_COVERAGE_CHANGELOG.md)、[额外8实现相位控制明细](../../design/paper/ARCHITECTURE_COVERAGE_CLOSURE/EXPANDED_PHENOMENON_BREADTH.md)。

### finite-response shared influence / MIRA框架

共享影响量按同一物理锚点的有限响应内积求和，分母为双方**全部**锚点响应能量（含非共享锚点）；旧“逐共享锚点余弦均值”文字已纠正。MIRA提供输入合同、物理锚点一致性、预测配对、影响量、可选目标评价和七字段报告卡；输出54条设计区分记录，NA字段不借其它合同结果补齐，不合成为万能标量。相同目标改动不改变acquired-only分数、锚点ID冲突拒绝等API检查通过。

历史目标知情HAT/SwinIR六队列层中18个broad-grid influence-over-count优势.036–.089、cluster CI均正；fixed-count在fastMRI/IXI支持，在宁夏全跨0/部分反向；42个幅度/符号/场/方向稳定性层通过、最低.942，但跨物理平面相关.779–.954，仅1/3 plane-pair gate通过。SAINT历史beyond-count .0138[−.0024,.0289]、fixed-count .0634[−.0211,.1488]为有效空结果；I3Net/CycleINR历史.90稳定性门槛失败，不能被新合同覆盖。

Plan17剔除966行reference自比较后保留7,728观察，HAT/SwinIR六分层beyond-count优势仍正：fastMRI .0614/.0855、IXI .1279/.1177、宁夏 .0701/.0603（均六分层同时CI正）；这是历史target-informed合同的敏感性，不是最新acquired-only八模型结果。

最新acquired-only合同：六采集切片池；最近两个采集层前景并集为support，非零采集强度Q99−Q1为scale；FP32无AMP/TF32，响应先哈希冻结再读GT作评价。8实现（7神经+Linear）×fastMRI24/IXI115，共16实测单元；新增五实现产生2,085响应文件、66,720上下文/幅度观察。13模型×2队列大表26行中10行不合格留NA。下表摘自最新CSV，区间为每队列/每端点八模型同时95%家族，所有稳定性/符号都纳入，5,000联合有效draw。

| 实现 | fastMRI beyond-count [CI] | IXI beyond-count [CI] | 最小rank稳定性 fastMRI / IXI（门槛） | fixed-count反例/边界 |
|---|---|---|---|---|
| Linear解析控制 | .07661[.06080,.09241] | .08260[.07671,.08849] | .98196 / .98911（.90） | IXI为−.07571[−.12576,−.02566]，显著负 |
| HAT | .10332[.08527,.12136] | .09782[.08763,.10802] | .96429 / .92982（.85） | 两队列fixed-count正 |
| SwinIR | .09332[.07759,.10906] | .09325[.08145,.10505] | .94205 / .88031（.85） | 两队列fixed-count正 |
| SAINT-style | .03275[.01186,.05364] | .13279[.12445,.14113] | .95069 / .99634（.90） | 新信息合同两队列正；旧空结果保留 |
| ArSSR | .08160[.06885,.09434] | .12319[.11843,.12794] | .96378 / .99899（.90） | 两队列fixed-count正 |
| ResUNet | .09414[.07804,.11024] | .12723[.12022,.13424] | .98937 / .99775（.90） | fastMRI−.10299[−.26037,.05439]跨0 |
| SMamba-UNet | .07817[.05963,.09671] | .09606[.08280,.10932] | .91754 / .96817（.90） | fastMRI .20192[−.01107,.41492]跨0 |
| ACVTT | .09167[.07818,.10516] | .08169[.07115,.09222] | **.78923 / .89762（.90，均FAIL）** | 即使beyond-count正，不能计稳定机制支持；fastMRI fixed-count跨0 |

因此16单元中14同时稳定通过且beyond-count CI正；**不等于fixed-count全部正，也不是13模型普适证明**。不合格：Cubic双锚退化为Linear，ResSRDiff有额外随机采样，I3Net/CycleINR冻结四锚合同不支持全部上下文，Pix2Pix固定通道不能表达每个分数位置。实际可用适配实现与原论文官方架构精确复现也需区分。

工程侧ACVTT/IXI和ResUNet两队列在生成科学结果前因batch1/4一致性失败，按冻结补记改为single-sample并保持原容差；已完成ACVTT/fastMRI科学稳定性失败不重跑。不得把执行修复当作提高成功率的科学选择。

证据：[MIRA框架与审计报告](../../design/paper/PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/FINAL_REPORT_ZH.md)、[可执行MIRA API](../../design/paper/PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/scripts/mira.py)、[剔除自比较结果CSV](handoff_evidence_20261023/source_files/afd13b015baa__nonself_influence_summary.csv)、[最新八实现扩展报告](../../design/paper/CONTINUOUS_INFLUENCE_EXPANSION/FINAL_REPORT_ZH.md)、[13模型双队列完整大表CSV](../../design/paper/CONTINUOUS_INFLUENCE_EXPANSION/CONTINUOUS_INFLUENCE_BIG_TABLE.csv)、[全部次要终点/幅度/符号CSV](../../design/paper/CONTINUOUS_INFLUENCE_EXPANSION/ALL_SECONDARY_SIGNS.csv)、[更新MIRA报告卡CSV](../../design/paper/CONTINUOUS_INFLUENCE_EXPANSION/UPDATED_MIRA_REPORT_CARD.csv)。

### 条件协方差命题与固定上下文实测

在固定bias/Jacobian和边际输入协方差前提下，`κ=tr(J_A C J_Bᵀ)`使预期误差内积+κ、预期平方差−2κ；不是逐样本保证或E[比值]定理。12组×100,000模拟验证正/零/负κ边界。真实固定上下文：哈希选12个IXI检查，HAT/SwinIR，四个exact-one-shared上下文，ε=.0025/.005/.01/.02，四Rademacher场及负场；coupled与8×8独立Cartesian设计保持经验边缘分布相同。

8个模型×幅度均值效应均负且同时CI低于0；`−2κ`恒等式闭合最大残差5.60e−12仅为代数检查。固定ε0=.0025奇响应预测其它幅度的median相对近似误差1.9%–10.6%，最坏126.4%，最大原生平方强度差112.14；384条全部保留，96组合86 aligned/10 near-orthogonal/0 opposing。后续SAINT48新例median误差.008%–1.069%、worst3.199%、全aligned；不能借其较好结果抹去HAT/SwinIR失败，也未验证神经opposing分支。

证据：[条件命题模拟CSV](handoff_evidence_20261023/source_files/a759eb83af78__proposition_numerical_check.csv)、[HAT/SwinIR固定上下文实测](../../design/paper/FINAL_SCIENTIFIC_STRENGTHENING/PROPOSITION1_VALIDATION.md)、[SAINT追加实测](../../design/paper/ARCHITECTURE_COVERAGE_CLOSURE/ARCHITECTURE_COVERAGE_CHANGELOG.md)。

### Anchor-CV、预算加密收益与三条失败方法分支

Anchor-CV仅用已采集锚点做留出/相邻插值重建差异，作为零额外神经调用的检查难度proxy；leave-one-out操作本身不是新发明。Plan11同模型×4→×2受益（同病例/同模型/common-support MAE差）598有效配对，fastMRI13/13模型Anchor-CV相关正（中位.8513），宁夏12/13正（中位.7267）；candidate-bank median分别11/11(.8348)、10/11(.7098)。宁夏ResSRDiff负向反例保留。Plan13控制当前×4误差后，fastMRI/宁夏26个Anchor-CV条件关联CI全部跨0，强原始相关未证明额外采样价值信息。

IXI I3Net115对×2/×4、7,334共同缺失平面：MAE33.6466→25.6206，受益8.0260，115/115正；两个倍率权重不同，不能称纯增加测量的因果效应。Anchor-CV与raw受益ρ.843，控制当前误差后.216[.007,.430]；只归一化分数而保留raw受益后ρ−.238，50%预算较随机−.920MAE[−1.635,−.149]。后续2×2单位合同：raw分数/raw受益ρ.843、raw/normalized−.375、normalized/raw−.238、normalized/normalized .539；匹配归一化单位50%预算相对随机+.000655[.000151,.001537]。正负方向均有解释价值，不可用最后一个正结果撤回前一个不同合同负结果。

| 自研探索分支 | 构造 | 最终状态与证据 |
|---|---|---|
| 最小influence上下文选择 | 开发冻结，以局部influence择上下文，对比random/count/diversity/PC/adjacent/Anchor | 确认/迁移未通过，非有效改进；[完整summary CSV](handoff_evidence_20261023/source_files/d6d0d94389ac__p7_cvpr_influence_context_selection_summary.csv)、[配对deltas](handoff_evidence_20261023/source_files/31f725ec3d8c__p7_cvpr_influence_context_selection_deltas.csv) |
| 多锚jackknife IQR | 多锚子上下文输出离散度，开发选定后锁定 | 未提供超出adjacent MAE的稳定增量；[summary CSV](handoff_evidence_20261023/source_files/be9092795055__p7_cvpr_multi_anchor_jackknife_summary.csv) |
| covariance/influence residualization | 零拟合协方差推导残差化 | 未形成一致确认/迁移收益；[summary CSV](handoff_evidence_20261023/source_files/b879dfd79093__p7_cvpr_influence_residualization_summary.csv)、[配对deltas](handoff_evidence_20261023/source_files/4a3f47073c6c__p7_cvpr_influence_residualization_deltas.csv) |
| 单一acquired-only guard | `max(F_dev(D_norm),F_dev(AnchorCV_norm))`，fastMRI12开发/12内部评价，再固定转IXI115 | fastMRI两对各0 stable-wrong阳性，AP/AUC=NA；IXI各仅2阳性，12个guard-minus-baseline同时CI全跨0，停止评分搜索 |

guard IXI HAT/SwinIR AP=.508696（disagreement=.508929，Anchor-CV=.510204）；I3Net/CycleINR .017391（.014448/.018141）。5,000抽样仅3,918两对共同有效；旧队列重新划分不产生pristine holdout。证据：[guard完整评价CSV](handoff_evidence_20261023/source_files/b91cf407f26f__score_evaluation.csv)、[对全部基线的配对差CSV](handoff_evidence_20261023/source_files/f5dd5d782c2f__score_paired_deltas.csv)。

二维解析variance proxy控制也保留：Linear/Cubic双成员在IXI115改变测量共享，局部observable gain约.321，固定reference error的variance rank增益.0313[.0122,.0503]及.0361[.0158,.0564]（两方向同时CI）；fastMRI24全部因几何不足排除。两个成员方差与平方差有确定关系，不计两个独立方法证明。证据：[解析variance proxy汇总CSV](handoff_evidence_20261023/source_files/2ff60d578b7c__practical_proxy_summary.csv)、[几何资格逐例排除CSV](handoff_evidence_20261023/source_files/d4263e353b8a__practical_proxy_geometry_exclusions.csv)。

### 亮区解剖加权规则：TopCoW探索→CAS2023固定迁移

**项目提出的固定规则。** 在phase0两个最近采集锚点各自1%绝对强度前景中取95百分位亮区，合并支持后取预测差异均值。只用采集输入定义支持，不用血管标签选阈值；它是bright-region weighting，不是血管分割器。TopCoW125例/10,779共同缺失平面先观察整体/血管端点不一致后提出规则，属事后探索；随后不改规则迁移CAS2023全部100例/6,412平面，合计225例/17,191平面。解析Linear/四点Lagrange Cubic不冒充神经MRA验证。

| 血管MAE排名亮区−一般前景Δρ（两目标同队列/context同时95%CI） | Linear | Cubic | 相关整体误差代价 |
|---|---|---|---|
| TopCoW shared | +.102[.008,.195] | +.104[.011,.197] | 整体Δρ−.216/−.217 |
| TopCoW disjoint | +.217[.100,.334] | +.222[.110,.334] | −.250/−.235 |
| CAS shared | +.010[−.038,.059] | +.005[−.048,.057] | −.136/−.138 |
| CAS disjoint | +.073[.017,.130] | +.070[.014,.126] | −.085/−.084 |

CAS disjoint血管排名ρ从.880/.877升至.953/.947，但CAS四组血管risk-coverage CI均跨0，不能称已证明筛查收益。TopCoW标准disjoint虽局部observable gain约34.5pp、125/125正，血管排名反而−.0430/−.0383（CI跨0），血管归一化超额risk面积增加.001400/.001355（CI正），说明局部可见性不自动改善解剖筛查。TopCoW固定解析×4→×2：Linear整体MAE24.678→12.879、血管156.431→63.935；Cubic24.510→10.361、血管142.115→37.495，均125/125病例受益正。

不相交分歧需额外phase2数据，不能叫无额外采集成本；标签区域MAE也不是诊断终点。证据：[Plan14完整报告](../../design/paper/PLAN14_SCIENTIFIC_STRENGTHENING/FINAL_REPORT_ZH.md)、[TopCoW局部效应CSV](handoff_evidence_20261023/source_files/2c906ce35f1a__topcow_effects.csv)、[TopCoW排名CSV](handoff_evidence_20261023/source_files/88bd5918d2b9__topcow_rankings.csv)、[TopCoW风险覆盖CSV](handoff_evidence_20261023/source_files/4630fc9ea2f6__topcow_risk_coverage.csv)、[TopCoW亮区排名CSV](handoff_evidence_20261023/source_files/18146f66a924__bright_anchor_rankings.csv)、[CAS固定迁移排名CSV](handoff_evidence_20261023/source_files/1dcb37433ad8__cas_transfer_rankings.csv)、[IXI四种单位合同相关CSV](handoff_evidence_20261023/source_files/63d3d5de08eb__ixi_scale_contract_correlations.csv)、[IXI四种单位合同预算CSV](handoff_evidence_20261023/source_files/285aeeb0f8e6__ixi_scale_contract_budgets.csv)。

### 研究链的统一边界与状态

PC/committee可提供错误相关和复核优先级；MIRA/influence是机制与信息合同审计工具；bright-region固定规则有特定解析MRA迁移结果。本节所列paper阶段合同没有低分正确性认证、校准患者风险或reader/诊断收益；其部署净收益也未获得真正未触及队列的完整确认。此判断仅限本节合同，**不概括整个项目缺少外部科学确认**：后续innovation旧MIRA已有MSValid84人单配对外部确认，详见下文相应结果及2026-10-07研究范围澄清。科学搜索多次按协议终止，失败分支应作为已完成负实验保留，不能合并成“所有创新都成功”。后续报告中的局部正结果不抵消旧合同的空结果、数值稳定性失败、共同误差盲区和单位敏感性。

paper目录README仍写Plan17为最新，但`FINAL_SCIENTIFIC_STRENGTHENING`、`ARCHITECTURE_COVERAGE_CLOSURE`及`CONTINUOUS_INFLUENCE_EXPANSION`包含后续实际完成结果；以对应最新CSV/最终报告为准。底层历史可在`design/paper/ARCHIVE/`追溯，不能把各阶段重复分析累计成独立样本或独立研究重复。


---

## 创新探索、MIRA 审计与患者任务收益研究（innovation 目录）

本节覆盖本地 `innovation/` 的自有研究设计、实验、诊断和工程实现。HAT、SwinIR、I3Net、PCHIP、QDA、ExtraTrees、SURE、defer、GIN/IPA、SSC、预训练或常规增强是文献方法/对照，不计为用户原创算法；原创工作主要是项目内提出的问题、比较合同、动作设计、反证诊断与实现。这里的“原创探索”也不等于已证明首创或已达到发表要求。

**确认范围必须分开：**旧 MIRA 机制线在 MSValid 84 人/479 目标上有事前冻结的单配对外部确认；当前 MC-RC/3D 病灶任务收益线仍无保留患者确认。后者的“科学确认 0”不能扩大为整个项目从无外部确认。`innovation/` 最新已保存接续到 ROUND53；历史文件里的 live/未完成只描述记录当时，本文不推断当前后台进程。依据：[RESEARCH_SCOPE_CLARIFICATION_2026-10-07.md](../../innovation/RESEARCH_SCOPE_CLARIFICATION_2026-10-07.md)、[POST_ARCHIVE_HANDOFF_ROUND52_V2.md](../../innovation/gpu_full_fov_and_atomic_capture_2026_10_09/POST_ARCHIVE_HANDOFF_ROUND52_V2.md)。

### A. MIRA：共享测量、成对误差可见性与连续响应审计

**方法思想。**固定缺失目标和参考预测 A，让伴随预测 B 从共享实际锚点切换到不相交锚点，分析分歧显示了多少成对误差（`O`），并将误差对齐、总误差和分歧分开报告。进一步用小幅输入扰动建立按真实物理锚点 ID 配对的响应内积，检验是否超出共享锚点数/精确上下文模板。`O` 在评分时需要隐藏参考，不是可部署的校准错误分数；相位切换同时改变邻片内容、几何和可能的归一化，因此不称纯采集身份因果干预。

| 自有实验/诊断 | 数据与合同 | 关键结果 | 判断与证据 |
| --- | --- | --- | --- |
| 原多架构同目标共享控制 | fastMRI、IXI；五种冻结实现、20 个有序跨架构配对 | 不相交锚点的 ΔO 队列内同时区间均为正；fastMRI 约 +6.2–16.0、IXI +13.1–28.5 个百分点 | 是测量依赖的审计证据；不等于新重建器或临床安全。[MIRA_CLAIM_AUDIT_2026-09-30.md](../../innovation/MIRA_CLAIM_AUDIT_2026-09-30.md)；主原稿在 [main.tex](../../design/paper/CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.tex) |
| 连续响应影响扩展 | 8 个实现、16 模型/队列单元（含 Linear 控制） | 14 单元同时通过预定数值门槛与 beyond-count 同时区间；保留数值失败及 fixed-count 负/空项 | 不是 8 个独立神经架构因果复制。[CONTINUOUS_INFLUENCE_BIG_TABLE.md](../../design/paper/CONTINUOUS_INFLUENCE_EXPANSION/CONTINUOUS_INFLUENCE_BIG_TABLE.md) |
| acquired-only guard | 历史 fastMRI/IXI | fastMRI 内评无阳性；IXI 两配对各仅 2 阳性；全部 12 项相对基线的同时 AP 区间跨 0 | 部署筛查/风险证书失败；不可用机制正结果覆盖。[claim_evidence_matrix.md](../../design/paper/PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/claim_evidence_matrix.md) |
| MSValid 事前冻结单配对外部确认 | 84 RRMS T2 患者、479 目标；固定 fastMRI 权重 HAT0，SwinIR0→2；acquired-only 支持 | ΔO **+19.7565 pp**，95% 患者 CI **[+19.3276,+20.1605]**；84/84 正；伙伴 MAE 141.68→139.06 | 窄的上下文切换效应得到外部确认；非 20 配对全复制、非临床收益。[MSVALID_EXTERNAL_CONFIRMATION_2026-09-30.md](../../innovation/MSVALID_EXTERNAL_CONFIRMATION_2026-09-30.md) |
| 反向相位、线性伙伴及共同归一化 | 同 84/479，结果后控制 | 反向 HAT2/SwinIR2→0 ΔO +19.4985 pp；HAT0/线性0→2 +14.6189 pp；共同 min/max 仍正 | 缩放差/固定方向/双深模型不是唯一解释，仍未分离内容和几何。[MSVALID_POSTHOC_CONTROL_RESULT_2026-09-30.md](../../innovation/MSVALID_POSTHOC_CONTROL_RESULT_2026-09-30.md)、[MSVALID_COMMON_NORM_RESULT_2026-09-30.md](../../innovation/MSVALID_COMMON_NORM_RESULT_2026-09-30.md) |
| IXI 权重次级复制 | 同 84/479；IXI-HAT/SwinIR | shared O 1.0420%、disjoint 25.2276%；ΔO **+24.1856 pp**，CI **[+23.7150,+24.6726]**；84/84 正 | 权重依赖性敏感性；不增加独立患者。[MSVALID_IXI_WEIGHTS_SECONDARY_RESULT_2026-10-01.md](../../innovation/MSVALID_IXI_WEIGHTS_SECONDARY_RESULT_2026-10-01.md) |
| ReMIND 发布层外部跟进 | 62 完成患者、248 目标（63 尝试范围/失败单列）；IXI 权重 | ΔO **+26.3999 pp** | 来源有 MPR，保留为发布上下文现象，非原始采集身份。[REMIND_NATIVE_T2_CONFIRMATION_RESULT_2026-10-01.md](../../innovation/REMIND_NATIVE_T2_CONFIRMATION_RESULT_2026-10-01.md)、[REMIND_NATIVE_T2_SOURCE_AUDIT_2026-10-01.md](../../innovation/REMIND_NATIVE_T2_SOURCE_AUDIT_2026-10-01.md) |
| UPENN 处理后 T2 第三来源 | 374/374 患者、1,496 目标 | ΔO **+28.1156 pp**，CI **[+27.9006,+28.3309]**；374/374 正；固定分母 +28.4961 pp | 所选 DICOM 全为 derived/secondary；后知情第三来源，非纯原始采集。[UPENN_GBM_PROCESSED_T2_CONTEXT_RESULT_2026-10-01.md](../../innovation/UPENN_GBM_PROCESSED_T2_CONTEXT_RESULT_2026-10-01.md)、[UPENN_FIXED_DENOMINATOR_RESULT_2026-10-01.md](../../innovation/UPENN_FIXED_DENOMINATOR_RESULT_2026-10-01.md) |
| 分母、误差对齐及解析伙伴反证 | MSValid/ReMIND 原 727 目标 | 固定共享总误差分母后方向保留；纯 PCHIP0/linear 相位切换 ΔO **+29.2470/+30.9585 pp**，146/146 患者正，高于原神经对点估计 | 大效应不要求学习架构，收窄“深架构特有机制”措辞。[FIXED_DENOMINATOR_TWO_SOURCE_RESULT_2026-10-01.md](../../innovation/FIXED_DENOMINATOR_TWO_SOURCE_RESULT_2026-10-01.md)、[TWO_SOURCE_ANALYTIC_CONTEXT_FALSIFICATION_RESULT_2026-10-01.md](../../innovation/TWO_SOURCE_ANALYTIC_CONTEXT_FALSIFICATION_RESULT_2026-10-01.md)；分解见两来源 `*_ERROR_ALIGNMENT_DECOMPOSITION_RESULT*` |
| 同几何独立合成噪声控制 | MSValid84/479；同 phase0 干净发布层，合成 magnitude A/B；1%/5% 噪声 | ΔO_noise −0.000339 pp（CI 跨0）/+0.002529 pp（CI [+0.000276,+0.004900]） | 幅度极小，不能复制约 +24 pp 相位切换效应；不是实测独立扫描，也不能估计原效应的噪声因果份额。[MSVALID_MATCHED_GEOMETRY_NOISE_CONTROL_RESULT_2026-10-01.md](../../innovation/MSVALID_MATCHED_GEOMETRY_NOISE_CONTROL_RESULT_2026-10-01.md) |
| 仅替换位置通道 | MSValid/ReMIND 各3人，共35目标 | ΔO_map +3.9182/+3.0666 pp；完整邻片切换同子集 +25.5017/+23.9789 pp；伴随 MAE 同时上升 | 输入错配敏感性，非位置因果份额。[POSITION_CHANNEL_ONLY_PILOT_RESULT_2026-10-01.md](../../innovation/POSITION_CHANNEL_ONLY_PILOT_RESULT_2026-10-01.md) |

#### 连续影响、错配 placebo 与外部预测的全结果

| 研究项 | 关键数字 | 最新结论/证据 |
| --- | --- | --- |
| 原响应物理 ID 错配负对照 | fastMRI HAT/SwinIR 正确减两错配平均偏相关 **+.1846/+.2340**；IXI **+.3036/+.2842**；834 NPZ 哈希核验、影响量复算最大误差 9.72e−17 | 内部锚点特异性增强；错配响应标签不等于随机化真实扫描身份。[ACQUIRED_RESPONSE_ID_PLACEBO_RESULT_2026-09-30.md](../../innovation/ACQUIRED_RESPONSE_ID_PLACEBO_RESULT_2026-09-30.md) |
| HAT→SwinIR 跨架构响应 | fastMRI24人72目标/IXI115人345目标；正确减错配 **+.2124/+.1139**；类别+影响量 MAE 增量仅 **+.000937/+.000066**，后者 CI 跨0 | 机制相关有方向，预测不稳。[CROSS_ARCH_ACQUIRED_RESPONSE_RESULT_2026-09-30.md](../../innovation/CROSS_ARCH_ACQUIRED_RESPONSE_RESULT_2026-09-30.md) |
| 六项同时区间 | 六层均正：fastMRI HAT [.0488,.3203]、SwinIR [.0391,.4289]、跨架构 [.0009,.4238]；IXI [.2256,.3815]/[.2064,.3619]/[.0403,.1875] | family 为看过单项后定义；SAINT 混合/跨零项不在其中，不能被背书。[RESPONSE_PLACEBO_SIX_FAMILY_RESULT_2026-10-01.md](../../innovation/RESPONSE_PLACEBO_SIX_FAMILY_RESULT_2026-10-01.md)、[SAINT_EXACT_CONTEXT_AUDIT_2026-09-30.md](../../innovation/SAINT_EXACT_CONTEXT_AUDIT_2026-09-30.md) |
| MSValid 阶段1探索 | 12人24目标、216上下文；粗几何调整 rank 偏相关 +.5681，但精确上下文后 **+.0386，CI [−.2788,+.3157]** | 粗调整阳性由精确模板解释，不能称外部连续机制复制。[MSVALID_INFLUENCE_STAGE1_RESULT_2026-09-30.md](../../innovation/MSVALID_INFLUENCE_STAGE1_RESULT_2026-09-30.md)、[INFLUENCE_EXACT_CONTEXT_AUDIT_2026-09-30.md](../../innovation/INFLUENCE_EXACT_CONTEXT_AUDIT_2026-09-30.md) |
| 剩余60患者一次留出预测 | P1–24 拟合，P25–84 评分；120目标、1080上下文；精确几何基线余弦 MAE .027280，加影响量 .027448，差 **−.000168 [−.000398,+.000070]**；O误差差 **−.000090 [−.000184,+.000009]** | **停止连续影响量作为跨来源可行动预测/上下文选择分数的主张**。该负结果不撤销另一端点的 MSValid 主 ΔO。[MSVALID_INFLUENCE_P25_P84_RESULT_2026-10-01.md](../../innovation/MSVALID_INFLUENCE_P25_P84_RESULT_2026-10-01.md) |
| 目标误差排序 | disjoint−shared concordance：MSValid +.1411 [.0681,.2161]；ReMIND +.0645 [−.0242,.1452] | ReMIND 未确认；disjoint 还需要原 phase0 x4 未采集的 phase2 层，不可部署。[TWO_SOURCE_TARGET_ERROR_RANKING_RESULT_2026-10-01.md](../../innovation/TWO_SOURCE_TARGET_ERROR_RANKING_RESULT_2026-10-01.md) |
| 等观测量 ensemble 控制 | disjoint 相对 shared ensemble MSE 降24.58%/26.78%；但对同 phase0+2 union PCHIP 相对收益 MSValid +8.12% [6.94,9.33]、ReMIND **+.91% [−.52,2.42]** | **停止跨来源可行动融合方法 claim**；新增观测与既有 ΔO 代数不构成新方法收益。[TWO_SOURCE_EQUAL_INFORMATION_CONTROLS_RESULT_2026-10-01.md](../../innovation/TWO_SOURCE_EQUAL_INFORMATION_CONTROLS_RESULT_2026-10-01.md) |

### B. 病灶局部误差与图像/任务脱节的原始实证

| 自有问题/实验 | 样本与结果 | 结论/证据 |
| --- | --- | --- |
| MSD 标注肿瘤区域的 context 可见性 | 484 尝试、483 完成、1932 肿瘤阳性目标；肿瘤 ΔO **+11.6537 pp [11.2256,12.0681]**；肿瘤−同层局部阴性 ΔO **+.5819 pp [.2302,.9337]**，267/483 正 | 窄的注册发布层区域审计通过；同观测 PCHIP 肿瘤 MSE 236.57 vs disjoint deep average1208.05，482/483 更优，因此非恢复性能/临床获益。[MSD_TASK01_TUMOR_ROI_CONTEXT_RESULT_2026-10-01.md](../../innovation/MSD_TASK01_TUMOR_ROI_CONTEXT_RESULT_2026-10-01.md) |
| MSD 解析反证 | 同483/1932，PCHIP0/linear 的肿瘤−局部 ΔO **+.9428 pp [.5503,1.3381]**；与神经结果差 CI 跨0 | 区域现象不要求深网络。[MSD_TASK01_ANALYTIC_CONTEXT_CONTROL_RESULT_2026-10-01.md](../../innovation/MSD_TASK01_ANALYTIC_CONTEXT_CONTROL_RESULT_2026-10-01.md) |
| MSD 同邻片/同处理强基线 | raw linear 肿瘤 MSE805.23，HAT1597.15、SwinIR1403.28；匹配 min/max+resize/clip 的 pipeline linear1068.26，仍分别少528.89/335.02 | 固定 IXI→注册 MSD 的 ROI 负结果；非通用架构失败。[MSD_EQUAL_NEIGHBOR_LINEAR_AUDIT_RESULT_2026-10-01.md](../../innovation/MSD_EQUAL_NEIGHBOR_LINEAR_AUDIT_RESULT_2026-10-01.md)、[MSD_PIPELINE_LINEAR_CONTROL_RESULT_2026-10-01.md](../../innovation/MSD_PIPELINE_LINEAR_CONTROL_RESULT_2026-10-01.md) |
| 全图掩盖局部误差的反证 | MSD full-support HAT−rawLinear MSE −20.12 [−140.48,+96.99]，SwinIR −221.40 [−350.15,−102.88]；同患者肿瘤正差/全图负差 HAT195、SwinIR197人 | 保留局部/全局异号，拒绝“模型全图崩坏”。MSValid84/84、ReMIND62/62两模型全图均优于rawLinear。[MSD_FULL_SUPPORT_EQUAL_NEIGHBOR_POSTRESULT_RESULT_2026-10-01.md](../../innovation/MSD_FULL_SUPPORT_EQUAL_NEIGHBOR_POSTRESULT_RESULT_2026-10-01.md)、[TWO_SOURCE_EQUAL_NEIGHBOR_PERFORMANCE_CHECK_RESULT_2026-10-01.md](../../innovation/TWO_SOURCE_EQUAL_NEIGHBOR_PERFORMANCE_CHECK_RESULT_2026-10-01.md) |
| IXI validation 同邻片诊断 | 58人232目标；HAT/SwinIR各57/58人全图 MSE 优于线性；患者均差 −1923.06/−1853.99 | 排除“所有域相同代码都失败”；validation 曾用于开发，无病灶标签，不是独立确认。[IXI_VALIDATION_EQUAL_NEIGHBOR_DIAGNOSTIC_RESULT_2026-10-01.md](../../innovation/IXI_VALIDATION_EQUAL_NEIGHBOR_DIAGNOSTIC_RESULT_2026-10-01.md) |
| ds007045 真薄层来源资格 | 当前363对；359严格同网格，原T2中327厚层2D；仅34个≤1.5mm 3D（31来自一站点） | 不能把重采样1mm grid当原始薄层真值；原363全队列恢复方案停止。[DS007045_SOURCE_QUALIFICATION_AND_ACQUISITION_RESULT_2026-10-01.md](../../innovation/DS007045_SOURCE_QUALIFICATION_AND_ACQUISITION_RESULT_2026-10-01.md) |
| ds007045 34例预写CPU复制 | 33完成/132目标，一来源超时；主SwinIR 肿瘤NMSE差 **−.00000340 [−.00004633,+.00004103]**、full−.00078717；次要HAT肿瘤 **+.00015243**、full−.00079957，CI均相应单侧 | **主“全图收益但肿瘤损害”复制失败**；HAT仅次要线索，不能改主。raw/同处理PCHIP后验敏感性仍保留HAT信号、SwinIR主失败。[DS007045_THIN3D_MODEL_PILOT_RESULT_2026-10-01.md](../../innovation/DS007045_THIN3D_MODEL_PILOT_RESULT_2026-10-01.md)、[DS007045_THIN3D_PCHIP_SENSITIVITY_RESULT_2026-10-01.md](../../innovation/DS007045_THIN3D_PCHIP_SENSITIVITY_RESULT_2026-10-01.md) |

#### VS-SEG 45 CISS：原预设负向主假设被反证

固定45主患者及1 TSE次要病例，322/322推断条件完成；图像按患者独立再生成，任务计数/坐标/边界独立核。**原要求 HAT 图像NMSE改善同时 Dice下降，实际 Dice改善，故原负向联合 claim 停止。**不能转挑 SwinIR 或 raw 基线挽救原主张。

| 输入条件 | 全45 original-JSON full Dice | 支持域 NMSE | absRVE | 空预测/边界非有限 |
| --- | ---: | ---: | ---: | --- |
| native | .907439 | 0 | .091841 | 0/0 |
| raw Linear | .702047 | .001558215 | .365888 | 2/2 |
| raw PCHIP | .744598 | .001590720 | .269818 | 1/1 |
| pipeline Linear | .562119 | .001446984 | .490245 | 7/7 |
| pipeline PCHIP | .654762 | .001446617 | .376793 | 3/3 |
| HAT | .691143 | .001201606 | .313156 | 2/2 |
| SwinIR | .639134 | .001208329 | .363553 | 4/4 |

主 HAT−pipelinePCHIP：NMSE **−.000245011 [−.000275237,−.000217049]**，45/45下降；Dice **+.036381704 [.007181222,.071980619]**，26提高/16降低/3相同。HAT−rawPCHIP Dice **−.053454294 [−.099770378,−.015642155]**；同一模型因处理合同不同可得到相反比较方向。RT 标签主 Dice差+.037034794，1mm边界带排除后区间跨0；112敏感性端点完整保留。次要 TSE248 native Dice.932071、rawPCHIP.838363，而HAT/SwinIR/pipelineLinear均0，不能并入45主名单。证据：[VS_SEG_COMPLETE_EVIDENCE_RESULT_2026-10-03.md](../../innovation/VS_SEG_COMPLETE_EVIDENCE_RESULT_2026-10-03.md)、[VS_SEG_SELECTION_SENSITIVITY_REAL_RESULT_2026-10-03.md](../../innovation/VS_SEG_SELECTION_SENSITIVITY_REAL_RESULT_2026-10-03.md)、[primary_patient_differences.csv](../../innovation/experiments/vs_seg_complete_analysis_cpu/primary_patient_differences.csv)。

### C. 处理顺序、带宽、归一化与任务上下文的机制诊断

| 自有对照 | 实际范围/数字 | 判定及证据 |
| --- | --- | --- |
| 原网格插值→resize vs resize→插值 | 45 CISS/2565内部缺层；显式clip四组合均0像素改变；Linear最大差≤1.80e−7，PCHIP所有45差>.000001，最大差约 .00913–.01976 | PCHIP不交换是已知非线性性质；顺序NMSE差仅整体pipeline−raw点估计的.8414%，不解释全部任务差。[VS_SEG_RESAMPLING_ORDER_CPU_RESULT_2026-10-03.md](../../innovation/VS_SEG_RESAMPLING_ORDER_CPU_RESULT_2026-10-03.md) |
| post-resize 完整任务 | 45人 raw/pipeline/post PCHIP full Dice **.74460/.65476/.65284** | 先原网格插值不能恢复原网格raw任务表现。[VS_SEG_POST_RESIZE_TASK_CPU_RESULT_2026-10-03.md](../../innovation/VS_SEG_POST_RESIZE_TASK_CPU_RESULT_2026-10-03.md) |
| 可观测 order 风险排序 | 全45已见输入特征与病灶/任务order变化的固定CPU诊断 | 原候选失败，停止部署风险排序。[OBSERVABLE_ORDER_RISK_CPU_RESULT_2026-10-03.md](../../innovation/OBSERVABLE_ORDER_RISK_CPU_RESULT_2026-10-03.md) |
| anchors-only 修改×归一化控制 | 固定202/203/204×raw/mixed-post=6体积；missing原数组完全不变，但ownstats使每对 **11,440,128/11,440,128** missing网络输入变，最大差 .12815–.20043；fixedstats均0 | 只保留重建missing像素不足以隔离任务输入；需固定stats。[ANCHOR_NORMALIZATION_CONTROL_CPU_RESULT_2026-10-03.md](../../innovation/ANCHOR_NORMALIZATION_CONTROL_CPU_RESULT_2026-10-03.md) |
| 相位/anchor带宽任务pilot | 全45相位诊断+三人12条件；post anchors fixed平均ΔDice **−.00505**；fixed missing输入不变时三人预测仍变288/593/186体素 | 不支持简单“anchor带宽恢复即可提升”的解释，固定候选停止。边界分解/实际missing输出反例保留。[ANCHOR_BANDWIDTH_DIAGNOSTIC_CPU_RESULT_2026-10-03.md](../../innovation/ANCHOR_BANDWIDTH_DIAGNOSTIC_CPU_RESULT_2026-10-03.md)、[ANCHOR_BANDWIDTH_TASK_CPU_PILOT_RESULT_2026-10-03.md](../../innovation/ANCHOR_BANDWIDTH_TASK_CPU_PILOT_RESULT_2026-10-03.md)、[ANCHOR_PILOT_BOUNDARY_DECOMPOSITION_CPU_RESULT_2026-10-03.md](../../innovation/ANCHOR_PILOT_BOUNDARY_DECOMPOSITION_CPU_RESULT_2026-10-03.md)、[ANCHOR_PILOT_OUTPUT_DOMAIN_AUDIT_CPU_RESULT_2026-10-03.md](../../innovation/ANCHOR_PILOT_OUTPUT_DOMAIN_AUDIT_CPU_RESULT_2026-10-03.md) |
| 三人任务统计互换 | 6次CPU；主ΔDice **+.0014103**，小且异质；三人post−raw为正，与全45为负不同 | 不外推；全45 post std平均−2.4882%、相同anchor scale+2.5525%，单调关联不足。[TASK_STATS_SWAP_CPU_PILOT_RESULT_2026-10-03.md](../../innovation/TASK_STATS_SWAP_CPU_PILOT_RESULT_2026-10-03.md)、[FULL45_NORMALIZATION_DRIFT_CPU_RESULT_2026-10-03.md](../../innovation/FULL45_NORMALIZATION_DRIFT_CPU_RESULT_2026-10-03.md) |
| 残差相加控制 | 六开发项/297缺层，仅2/6达到原门槛 | 固定候选停止；不是已验证恢复策略。[RESIDUAL_ADDBACK_CPU_RESULT_2026-10-03.md](../../innovation/RESIDUAL_ADDBACK_CPU_RESULT_2026-10-03.md) |
| 直接observed投影的精确秩 | 19开发series：z均全列秩；12/19面内有零空间；observed维数86,999,040，rank58,334,368；患者等权保留维数比 **.6746856073** | 是线性维数证书，不能解释为MRI信息/病灶丢失百分比。两同均值/方差合成observed经direct投影逐位同，native先PCHIP输出相差 .04252584。[OBSERVED_PROJECTION_INFORMATION_RESULT_2026-10-08.md](../../innovation/OBSERVED_PROJECTION_INFORMATION_RESULT_2026-10-08.md) |
| 共同投影observed anchors再分支 | 全19/11；direct与densePCHIP共享float32锚点、statistics/availability/z map；新旧direct全体积19/19逐位同；独立Hermite max9.54e−7 | 为因子解释的输入控制；尚无分割收益。理想float64坐标原门槛9/19/30样点失败仍保留。[COMMON_PROJECTED_OBSERVED_INPUT_RESULT_2026-10-08.md](../../innovation/COMMON_PROJECTED_OBSERVED_INPUT_RESULT_2026-10-08.md) |

### D. 选择性修正：从局部 oracle 到可见收益预测的失败链

动作族采用固定基底 `b` 与候选 `r` 的 `b+α(r−b)`，包含整层、patch、患者幅度、病灶约束及同预算策略。二次式/凸优化/成本敏感学习属于已知工具，项目贡献候选在明确的 MRI 动作净收益问题和公平合同，非仅把误差标签改名收益。

| 自有实验 | 分母/动作 | 主要结果 | 判定/证据 |
| --- | --- | --- | --- |
| 方向增强的层选择与守卫 | 历史fastMRI23人207缺层 | 全方向+ .09439dB但HD95代理+.15842；仅真值选PSNR好层+.13201dB仍HD95+.10942；逐层全指标均不退35/207，+.04988dB/HD95−.05076；phase/mm LOPO全选增强 | 简单phase/mm整层门控无额外收益。[CPU_RESULTS_2026-09-30.md](../../innovation/experiments/CPU_RESULTS_2026-09-30.md) |
| orientation局部连续oracle | 同23/207；tile32、stride16、Hann融合 | control25.56147、orientation25.65622、最佳固定α=.70为25.67698、整层oracle25.70912、patchoracle25.82512dB；patch超固定 **+.14815dB**，但HD95仍比control差+.05130 | 有空间异质性，结构守卫未过；truth不可部署。[LOCAL_ACTION_STUDY_2026-09-30.md](../../innovation/experiments/LOCAL_ACTION_STUDY_2026-09-30.md) |
| 可见特征scalar/patch选择 | 相同基础模型的选择器LOPO | scalar超固定+.00742dB；patch25.68950 vs25.67568，**+.01382dB**，20/23 PSNR好，HD95略差 | 只回收很小oracle空间；checkpoint早已见validation，非全pipeline OOF。同上 |
| 患者幅度/严格守卫 | truth patch oracle再乘β | 群体代理全不退最大β=.1，+.03586dB；真值逐患者β +.13747dB，5/23退回base；预测β仍借truth patch，+.10241dB且仅11/23过患者守卫 | 没有可部署安全策略。同上 |
| repaired wavelet3局部oracle | 修复版同23/207，不能与orientation跨合同相减 | control25.56683、wavelet25.58459、patchoracle25.60110；超固定仅 **+.01651dB**，HD95比固定差+.00623 | 当前动作对余量过小，停止大型gate投入。同上 |
| MC-RC三人主动作oracle | 004/005/006，195缺层；pipelinePCHIP→HAT/tile32 | 全支持gain .147614/.177642/.240365dB，病灶双guard仅005通过；raw次要 .819447/.409169/.659883均过 | **主pipeline分支仅1/3、停止收益头**，不改raw为主。[MC_RC_THREE_DEVELOPMENT_ACTION_ORACLE_RESULT_2026-10-02.md](../../innovation/MC_RC_THREE_DEVELOPMENT_ACTION_ORACLE_RESULT_2026-10-02.md) |
| MC-RC新增001/002 raw复核 | 45缺层、14976tiles | raw oracle gain .167287/.404077dB；001病灶NMSE目标等权恶化约14.9%、像素权8.94%，两guard失败 | 五人raw无约束门槛失败。[MC_RC_001_002_RAW_ACTION_ORACLE_RESULT_2026-10-02.md](../../innovation/MC_RC_001_002_RAW_ACTION_ORACLE_RESULT_2026-10-02.md) |
| 五人病灶约束oracle | 240缺层、34872tiles；隐藏truth+病灶label双约束 | constrained gain **.165081/.404077/.819447/.409169/.659883dB**；001仅10/1344tile改，代价.002206dB；超最优病灶可行共同α .654892/.197077/.256517/.246278/.206631dB | 事后数值oracle存在余量；不能当可见区域/收益预测或Dice成功。[MC_RC_FIVE_DEVELOPER_CONSTRAINED_ORACLE_RESULT_2026-10-02.md](../../innovation/MC_RC_FIVE_DEVELOPER_CONSTRAINED_ORACLE_RESULT_2026-10-02.md) |
| 五人30可见特征联合策略 | 5折patient LOPO、α五值、ridgeλ=.01、13政策 | 联合gain −.066440/.039271/.493958/−.031182/.367433dB；仅004/006过完整门槛；平均NMSE **.001703424** 劣于固定α=.5的 **.001696555** | **固定策略停止**，不调λ/特征/guard救结论。[MC_RC_VISIBLE_JOINT_DEVELOPMENT_DIAGNOSTIC_RESULT_2026-10-02.md](../../innovation/MC_RC_VISIBLE_JOINT_DEVELOPMENT_DIAGNOSTIC_RESULT_2026-10-02.md) |
| 收益头与绝对误差头等价审计 | 同10头、同输入/权重/标准化/penalty，线性标签坐标变换 | 最大坐标差≤6.085e−16，逐tile动作完全同 | 标签改名不增加信息、不构成算法贡献；只适用该线性合同。同上 |

### E. 合成风险/校准/指标审计（有精确验证，无患者疗效）

| 原创的项目内反证实验 | 实际结果 | 解释边界与证据 |
| --- | --- | --- |
| 固定phase缺层收益不可识别 | 16维、4观测；两truth同观测、同b/r，真实收益+.75/−2.25，投影收益都0 | 观测代理通常不足以识别missing动作收益；非新不可识别理论。[RISK_ACTION_ASSUMPTION_CPU_RESULT_2026-10-02.md](../../innovation/RISK_ACTION_ASSUMPTION_CPU_RESULT_2026-10-02.md) |
| 完整Σ SURE vs 对角Σ、重复噪声 | σ=.4；ρ=−.6/0/+.6真实gain +.112/−.080/−.272，完整Σ精确；对角结果 −.272/−.080/+.112；跨重复γ=0/.5/1使noisy-target从−.272变−.080/+.112 | 条件错误可反号；不否定完整Σ SURE，也不证明MRI噪声满足假设。六条件各20万draw，独立quadrature270配置。同上 |
| mask依赖动作排名 | 81固定场景、972风险、5346比较，**548严格反号/1458并列**；Fraction最大误差8.88e−16；独立评价mask恢复全风险 | 这些是合成配置数，不是548患者；不把已有mask依赖条件当新理论漏洞。[MASK_DEPENDENT_ACTION_RANKING_CPU_RESULT_2026-10-02.md](../../innovation/MASK_DEPENDENT_ACTION_RANKING_CPU_RESULT_2026-10-02.md) |
| 完美校准risk仍可选有害动作 | 4组400样本、同100调用预算；baseline最高risk选A错误200→205；两路径risk差选B→160；随机期望181.25；always400次→125 | 高风险不等于高动作收益；同信息risk差/cost/defer必须是强对照。CRC有限n的18行算术不等于真实CRC失效。[CALIBRATED_RISK_VS_ACTION_GAIN_CPU_RESULT_2026-10-07.md](../../innovation/CALIBRATED_RISK_VS_ACTION_GAIN_CPU_RESULT_2026-10-07.md) |
| gain>0概率不等于最大期望Dice | 4二值位置、57600有序配置；期望gain与期望cost决策全同；P(gain>0)>.5有4942动作差异，4558严格正regret；例P正=.75但期望gain−.025 | 主目标若为均值任务收益需保留gain幅度；不只做受益二分类。[TASK_GAIN_TARGET_CPU_AUDIT_RESULT_2026-10-07.md](../../innovation/TASK_GAIN_TARGET_CPU_AUDIT_RESULT_2026-10-07.md) |
| 联合Dice interaction精确分解 | 合成不相交FP移除，TP/FP/FN可加而Dice interaction=**1/15**；另1344配置精确核 | 正Dice交互可能完全来自分式分母，非神经协同；已备`dice_pair_decomposition`分开分式/非加性counts。[MC_RC_3D_ACTION_COMPOSITION_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_ACTION_COMPOSITION_RESULT_2026-10-07.md) |
| 8患者确认统计可达性 | 若8独立、无ties，6/7/8正差双侧sign p=.2890625/.0703125/.0078125；8/8的95% CP下界.630583；family7 Bonferroni最小p=.0546875 | 12series不能当12独立患者，不能称95%患者改善/零伤害；仅限制该二元检验合同。[RESULTS_CONTINUATION_TURN29.md](../../innovation/resolution_degradation_controls_2026_10_08/RESULTS_CONTINUATION_TURN29.md) |

### F. 观测病灶定位、支持传播与成本边界

| 方法/诊断 | 实际结果 | 状态/证据 |
| --- | --- | --- |
| 原始标签接触观测层审计 | 历史15series/8开发人，phase0未见完全隐藏的missing成分；四phase最大成分均接触observed；787030前景坐标核验 | 不能用“病灶完全避开observed”解释所有失败；不证明MRI能识别标签。[MC_RC_LABEL_ANCHOR_VISIBILITY_RESULT_2026-10-03.md](../../innovation/MC_RC_LABEL_ANCHOR_VISIBILITY_RESULT_2026-10-03.md) |
| 理想观测标签传播 | 同15/8、759缺层，两侧真实observed标签union+2mm；15/15过原几何gate；FG覆盖 .995560–1，边界 .992188–1，ROI占 .000347–.027643 | annotation oracle，非部署。[MC_RC_OBSERVED_REGION_PROPAGATION_RESULT_2026-10-03.md](../../innovation/MC_RC_OBSERVED_REGION_PROPAGATION_RESULT_2026-10-03.md) |
| 冻结分割器预测observed ROI | 原15/8；主ROI **0/15**过覆盖/面积gate；11series TP0，其中8空、3误定位 | 停止固定checkpoint/半径/阈值配置；完整native对照16series也0/16保护ROI，不能全归因抽层。[MC_RC_FROZEN_PREDICTED_REGION_CPU_RESULT_2026-10-03.md](../../innovation/MC_RC_FROZEN_PREDICTED_REGION_CPU_RESULT_2026-10-03.md)、[MC_RC_NATIVE_COMPETENCE_CPU_RESULT_2026-10-03.md](../../innovation/MC_RC_NATIVE_COMPETENCE_CPU_RESULT_2026-10-03.md) |
| observed QDA/LDA | 四模型、原16series，**0/16**；1216anchor-plane/model和864missing核 | 低容量可见表示未通过，非所有定位方法不可能。[MC_RC_ANCHOR_QDA_CPU_RESULT_2026-10-03.md](../../innovation/MC_RC_ANCHOR_QDA_CPU_RESULT_2026-10-03.md) |
| 19series先验/forest诊断 | empiricalQDA/balancedQDA/ExtraTrees，11patient LOPO；FG覆盖 **.8820%/98.9361%/92.2123%**，boundary1.2061/98.2023/93.8427%，ROI .3035/12.9525/9.0258%；三者原gate均0/19 | balanced覆盖增加但面积广；不能由约99%均值称每患者达99%。固定主balancedQDA FG/boundary均过且有条件省算12/19。[MC_RC_ANCHOR_PRIOR_FOREST_DIAGNOSTIC_RESULT_2026-10-07.md](../../innovation/MC_RC_ANCHOR_PRIOR_FOREST_DIAGNOSTIC_RESULT_2026-10-07.md) |
| 19series匹配annotation oracle | union+2mm FG99.9649%、boundary99.9229%、ROI.4716%；原gate19/19，≥99%双覆盖且条件省算18/19；总572dense/181conditional forward | 很小ROI也可能影响所有窗口，001一series N=k=8；新增012单体素hidden标签成分不改旧15范围。[MC_RC_MATCHED_ANCHOR_ORACLE_RESULT_2026-10-08.md](../../innovation/MC_RC_MATCHED_ANCHOR_ORACLE_RESULT_2026-10-08.md) |
| 重复动作两种计费语义 | m5：A=(N+mk)/(mN)，B=(N+mk)/(N+mN)；理想 .617953/.514961；empiricalQDA .577788/.481490；balancedQDA **1.028457/.857047**；forest1.019888/.849906 | 完整patient workload先合并series；pooled较有利不能替代患者平均。定位/生成/transfer等未计；重打包未执行。[MC_RC_MATCHED_ORACLE_BUDGET_RESULT_2026-10-08.md](../../innovation/MC_RC_MATCHED_ORACLE_BUDGET_RESULT_2026-10-08.md) |

当前范围以11开发患者/19series、4已见验证/9series、8未见确认/12series为准。历史15→16→19及39→40来源更正保留原合同，不追改旧分母。原40合格系列中19开发，8确认患者不开放效果。来源/身份链见[MC_RC_SOURCE_DENOMINATOR_CORRECTION_RESULT_2026-10-03.md](../../innovation/MC_RC_SOURCE_DENOMINATOR_CORRECTION_RESULT_2026-10-03.md)、[MC_RC_LOCAL_IDENTITY_AND_ALLOCATION_RESULT_2026-10-03.md](../../innovation/MC_RC_LOCAL_IDENTITY_AND_ALLOCATION_RESULT_2026-10-03.md)、[MC_RC_NEXT12_SOURCE_PREFLIGHT_RESULT_2026-10-03.md](../../innovation/MC_RC_NEXT12_SOURCE_PREFLIGHT_RESULT_2026-10-03.md)。

### G. 任务模型能力：2.5D/全局局部、覆盖×增强、3D上下文与低LR

这些是为公平评价重建/动作而实施的自有任务配方与能力诊断；标准U-Net/损失/增强/低LR本身不作创新。固定最后checkpoint、阈值.5、完整native FOV，保留失败；不能把弱task上的差异叫SR收益。

| 实验 | 训练预算/范围 | 主要结果 | 结论/证据 |
| --- | --- | --- | --- |
| 稀疏2.5D任务初训 | 122609参数；多患者10人18series/4000步，013整人留出；另单0124000步 | 多患者训练内012 PCHIP Dice **.010724**、013留人 **0**；单012训练Dice **.555150**，recall.551374，absRVE仅1.360%但FP84148/FN86779 | 主/单fit门槛均失败；体积接近掩盖位置错误。[MC_RC_SPARSE_TASK_TRAINING_CPU_RESULT_2026-10-03.md](../../innovation/MC_RC_SPARSE_TASK_TRAINING_CPU_RESULT_2026-10-03.md) |
| 全局/局部任务20k | 981602参数、11开发/19series、observedPCHIP；4验证9series/18输入 | PCHIP验证 fullDice **.127522**、missing.135304、recall.144965、absRVE.772949，3漏检series；linear.126314 | 六gate仅“患者full/missing正”通过。[MC_RC_GLOBAL_LOCAL_TASK_CPU_RESULT_2026-10-03.md](../../innovation/MC_RC_GLOBAL_LOCAL_TASK_CPU_RESULT_2026-10-03.md) |
| 固定plane/单012 loss诊断 | 单012两损失各4000；固定z38另1000 | fullDice .865312/.823786仍未过fit；固定plane Dice .9841105 | 能拟合plane不等于整FOV能力；并非loss创新。[MC_RC_GLOBAL_LOCAL_SINGLE_CASE_LOSS_CPU_RESULT_2026-10-03.md](../../innovation/MC_RC_GLOBAL_LOCAL_SINGLE_CASE_LOSS_CPU_RESULT_2026-10-03.md)、[MC_RC_GLOBAL_LOCAL_FIXED_PLANE_FIT_CPU_RESULT_2026-10-03.md](../../innovation/MC_RC_GLOBAL_LOCAL_FIXED_PLANE_FIT_CPU_RESULT_2026-10-03.md) |
| 单012覆盖×增强四臂 | 原legacy_aug复用，三新臂各4000（12000新updates） | legacy_aug/legacy_none/coverage_aug/coverage_none fullDice **.865312/.965504/.747641/.914331**；missing .865501/.966269/.761014/.921029；仅两个none过fit | 单病例/单seed；覆盖改变不能证明泛化。[MC_RC_COVERAGE_AUGMENTATION_FACTORIAL_CPU_RESULT_2026-10-03.md](../../innovation/MC_RC_COVERAGE_AUGMENTATION_FACTORIAL_CPU_RESULT_2026-10-03.md) |
| 全19无增强20k | 同初权重/流/预算，关闭整个增强bundle；CPU训练、GPU网络评价 | 开发Dice **.686214**；验证PCHIP **.068768**、missing.072294、recall.046885、absRVE1.371381，4 TP0 | 六gate全部失败。[MC_RC_NO_AUGMENTATION_FULL_TASK_RESULT_2026-10-03.md](../../innovation/MC_RC_NO_AUGMENTATION_FULL_TASK_RESULT_2026-10-03.md) |
| intensity-only GPU20k | 只scale[.9,1.1]/shift[−.1,.1]，同初权重/19series/固定流 | 开发Dice **.342909**；验证 **.222203**、missing.224017、recall.230261、absRVE.695023，3 TP0 | 六gate五项失败；CPU/GPU差只描述，不纯增强因果。[MC_RC_INTENSITY_ONLY_FULL_TASK_RESULT_2026-10-03.md](../../innovation/MC_RC_INTENSITY_ONLY_FULL_TASK_RESULT_2026-10-03.md) |
| 3D单001两臂512全网更新 | native/rawPCHIP各512 | foreground cropDice .834883/.814870；完整FOV **.351453/.256330**；recall约.975但absRVE3.549951/5.617211 | crop好不代表完整背景控制；两臂fit失败。[MC_RC_3D_CPU_FIXED_FIT_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_CPU_FIXED_FIT_RESULT_2026-10-07.md) |
| 冻骨干head拟合 | 4分支各1024，bias-only1参数/full-head17参数 | native bias/full FOV .240725/.590714；PCHIP .407837/.372671；full-head训练crop .943708/.907710 | 特征可拟合crop，仍无完整能力。[MC_RC_3D_FROZEN_FEATURE_HEAD_FIT_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_FROZEN_FEATURE_HEAD_FIT_RESULT_2026-10-07.md) |
| 全16推断tile head覆盖 | 两臂各1024、17参数 | 完整Dice **.678448/.475659**；absRVE.574679/1.189911 | 比局部head提高，原.90fit仍失败；采样/loss域同时变化非单因素。[MC_RC_3D_ALL_TILE_HEAD_FIT_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_ALL_TILE_HEAD_FIT_RESULT_2026-10-07.md) |
| 全骨干全context1024高LR | lr=.001，每臂自身既有初始化/同tile流 | native完整Dice **0**、PCHIP **.973981**；native三head前景max约1.07e−7/1.37e−6/3.00e−5 | native崩塌是真实失败；不能直接解释为SR收益或某个唯一因素。[MC_RC_3D_BACKBONE_CONTEXT_REFIT_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_BACKBONE_CONTEXT_REFIT_RESULT_2026-10-07.md)、[MC_RC_3D_BACKBONE_COLLAPSE_DIAGNOSTIC_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_BACKBONE_COLLAPSE_DIAGNOSTIC_RESULT_2026-10-07.md) |
| 低LR受控回跑 | 只lr .001→.0001，各1024、各自相同init/同流 | native **.967647**、PCHIP **.963253**，recall.976261/.972305、absRVE.017804/.018793，两臂fit/strict均过 | 证明已见单series标准配方可拟合，非两输入恢复公平比较；允许进入19series资格。[MC_RC_3D_BACKBONE_CONTEXT_LOW_LR_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_BACKBONE_CONTEXT_LOW_LR_RESULT_2026-10-07.md) |
| 19series标签网格往返 | 全11/19 GT；原float32 vs独立float64 | patientDice **.96783554**、recall.96388237、absRVE.01734134；hard gate18/19，011Dice.877419；原float32概率门槛仅14/19但binary全同，新float64映射19/19过 | 当前弱模型不能全由标签往返解释；不是模型上界。[MC_RC_3D_LABEL_ROUNDTRIP_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_LABEL_ROUNDTRIP_RESULT_2026-10-07.md) |

### H. 共同初始化多患者3D最终训练与匹配增强的完整结果

原共同初始化训练真实完成 **39996 updates（native/raw各19998）**，全部11开发/19series，同初始state、同patient/series/GT/增强流、AdamW恒lr1e−4，最后state不按效果挑。全56 FOV评价技术完成；初V3概率映射严格核22/56失败，随后新V4修复最终native概率映射坐标精度，**56/56严格通过、旧binary/医学指标完全不变**。不能用软件修复说医学gate成功。依据：[RESULT.md](../../innovation/final_training_medical_execution_2026_10_08/RESULT.md)、[OBSERVED_EVALUATION_EXIT_V3.json](../../innovation/lossless_final_evaluation_entry_2026_10_08/OBSERVED_EVALUATION_EXIT_V3.json)。

| 最后19998模型 | 开发11人/19series fullDice | 已见验证4人/9series fullDice | missingDice | recall | absRVE | 六gate |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| native_reference | .890639 | .506632 | .507568 | .462613 | .474591 | 3/6 |
| raw_PCHIP | .859645 | .445159 | .445335 | .372408 | .571475 | 1/6；1series零TP且空预测 |

两臂都没达到充分验证能力；全native额外信息不能当部署动作收益，开发高/验证低只支持泛化问题的描述，不识别采集协议/优化原因。纵向方向事后诊断3患者5区间，两臂均2方向错误/涉及2患者，patient-first错误比例.5；无临床阈值/确认。异质高分辨率T2范围包含FIESTA/SPC等，当前MC-RC全体不能统称CISS。

**固定99步配对续训**：从各自父state开始，basic/strong各99、重置相同optimizer、同流，共396更新；36 production+36 functional全FOV strict过，六医学gate仍无全过。表中parent仅描述，不以它替代匹配basic。证据：[FINAL_DESCRIPTIVE_COMPARISON.md](../../innovation/adaptation_paired_pilot_2026_10_08/FINAL_DESCRIPTIVE_COMPARISON.md)。

| 输入/99步条件 | fullDice | missingDice | recall | absRVE | 六gate |
| --- | ---: | ---: | ---: | ---: | --- |
| native basic | .432088 | .434118 | .389185 | .571816 | 1/6 |
| native strong | .507813 | .508967 | .507842 | .601841 | 2/6 |
| raw basic | .523190 | .522249 | .462381 | .451181 | 2/6 |
| raw strong | .526725 | .524898 | .528917 | .487844 | 3/6 |

**固定2992步匹配空间/强度增强四臂**：各臂完整最后2992，共11968训练记录；全部11人各272次曝光、19series存在；完整已见验证36 production+36 functional FOV strict过。开发全76 production+76 functional FOV也已真实完成，不能继续引用旧status里的12652 live。后者最终receipt和exit证明在 [receipt.json](../../innovation/development_capacity_after_matched_2026_10_09/evaluation_attempt01/receipt.json)、[ACTUAL_DEVELOPMENT_EVALUATION_EXIT.json](../../innovation/development_capacity_after_matched_2026_10_09/ACTUAL_DEVELOPMENT_EVALUATION_EXIT.json)。

| 输入/2992增强 | 开发fullDice | 开发missingDice | 开发recall | 开发absRVE | 验证fullDice | 验证missingDice | 验证recall | 验证absRVE | 验证六gate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| native/intensity | .862924 | .861525 | .889303 | .110832 | .468329 | .470420 | .559930 | 1.112327 | 2/6 |
| native/spatial | .866582 | .869931 | .843003 | .101387 | .521877 | .521347 | .453378 | .483695 | 3/6 |
| raw/intensity | .880839 | .882150 | .863256 | .073956 | .518307 | .519431 | .512911 | .512050 | 2/6 |
| raw/spatial | .860915 | .861270 | .846439 | .088107 | .463237 | .462797 | .446741 | .932067 | 2/6 |

native spatial−intensity验证mean fullDice +.053548，但仅020正（+.273676），其余3患者负，去020均值−.019828，4人recall全降；raw平均−.055071、2正2负，所有描述leave-one-out均负。024各分支recall约.112–.136，主要漏检；025 raw spatial absRVE2.0069。两个spatial tailFP=0仍失败，不能把泛化差全归因tail FP。11968日志首544/末544 mean loss：native intensity .134606/.142504，spatial .188604/.169896，raw intensity .150976/.147216，spatial .205888/.179692；loss描述不等于优化因果证明。证据：[FINAL_MATCHED_COMPARISON.md](../../innovation/spatial_adaptation_matched_2026_10_08/FINAL_MATCHED_COMPARISON.md)、[MEDICAL_RESULTS_AND_NEXT_ACTION.md](../../innovation/imputation_mask_and_conditional_uncertainty_2026_10_09/MEDICAL_RESULTS_AND_NEXT_ACTION.md)、[EXPERIMENT_STATUS_AND_NEXT_TRIALS.md](../../innovation/conditional_uq_and_task_capacity_followup_2026_10_09/EXPERIMENT_STATUS_AND_NEXT_TRIALS.md)。

### I. observed-only特征、患者暴露、缓存与联合动作实现

| 自有实现/资格 | 关键结果 | 限制/证据 |
| --- | --- | --- |
| 观测留出特征 | 11人19series、38唯一fold；linear normalizedMSE **.284702297**、PCHIP **.286547508**，差.001845211（.6481%）；18/19series、10/11patient差正 | 留出改变采样间距/输入量，含背景，不能推原x4病灶任务哪种更好；改变heldout真值+10000，source/prediction SHA不变。19行17特征的任务gain/cost为null。[OBSERVED_HOLDOUT_FEATURE_RESULT_2026-10-08.md](../../innovation/OBSERVED_HOLDOUT_FEATURE_RESULT_2026-10-08.md) |
| 真实特征成本 | 同19series/38fold/17特征；一次CPU1 cold child **23.8487972s**；显式生产阶段19.377979s，含检查series21.491695s；插值11.861229s | 单次无缓存控制，不是完整患者部署延迟/benchmark；任务、定位、动作等费用未齐。[DEPLOYMENT_FEATURE_COST_RESULT_2026-10-08.md](../../innovation/DEPLOYMENT_FEATURE_COST_RESULT_2026-10-08.md) |
| 患者registry和暴露接口 | 19/19特征exact、11fold整患者series分组正确；11项metadata注错拒绝；label/cost仍null | head-only LOPO不能称全pipeline外折；19998父模型见过全11GT，严格LOPO需cold-init。[RESULT.md](../../innovation/task_utility_patient_exposure_2026_10_08/RESULT.md) |
| 局部编辑完整FOV cache | 开发001、old PCHIP_last1024；49 native体素+.25→243physical变化；原16window中8需算，完整8forward/cache4；全部tile/physical/native概率SHA相同/binary0；RAM64MiB | 初始化必付8forward，K>2同支持动作才少总调用；单次计时6.3620→3.2340s非稳定2倍benchmark。19series合成中心ROI宽7/32/64时572dense→99/145/188conditional，条件费用非医学收益。[MC_RC_3D_LOCAL_EDIT_CACHE_QUALIFICATION_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_LOCAL_EDIT_CACHE_QUALIFICATION_RESULT_2026-10-07.md) |
| 联合动作lattice | 同开发001、三个7×7合成+ .25动作，全部8subset；A/B/C成本4/6/1，AB6而单项相加10，ABC7而相加11；完整/cache7非空状态逐位同 | 面积不等于费用；实际116CPUforward，7动作binary变化全0，无GT/Dice收益。AB概率mixed max3.33786e−6，AC/BC约2.27e−13；非零浮点不代表病灶交互。[MC_RC_3D_ACTION_COMPOSITION_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_ACTION_COMPOSITION_RESULT_2026-10-07.md) |
| 有限context/halo整数依赖 | 两路144输出支持集合一致；相位mod8支持宽92/100、最大半径51→halo56；patch64×128×128内部core0×16×16 | 当前14个eval IN依赖全tile，不满足局部统计条件；结构集合非医学等价。[MC_RC_3D_FINITE_CONTEXT_HALO_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_FINITE_CONTEXT_HALO_RESULT_2026-10-07.md) |
| PCHIP参照内部统计IN | 合成primitive最大差5.73e−7/4.63e−7；同输入三个head/binary0差；非同输入linear普通IN vs PCHIP-referenceIN head差.169379/.182337/.083286，预测变428/53/0 | 单弱模型无GT敏感性，非任务改善；两原失败保留。[MC_RC_3D_REFERENCE_IN_PREFLIGHT_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_REFERENCE_IN_PREFLIGHT_RESULT_2026-10-07.md) |
| 训练/部署前景点位置诊断 | 2992冻结前景采样点，训练/部署Gaussian权重到最近边界26.8901/24.6018；<8体素权重 .2342%/.5188%，<16为3.7427%/6.0316% | 不支持严重漏检由“大量边缘主导”直接解释；非因果介入。[CENTER_POSITION_FINDINGS.md](../../innovation/task_capacity_mechanism_audit_2026_10_09/CENTER_POSITION_FINDINGS.md) |

### J. 真实上下文支持、分辨率增强及完整数值资格（工程成果和失败）

这些实现为了让普通强基线/医学动作比较可信可执行，不将数值证书、缓存、autograd、透明存储或标准增强当新医学算法。重要的失败也保留完整分母和版本。

| 项目内工作 | 已实测结果 | 最新状态/证据 |
| --- | --- | --- |
| 真实FOV/halo支持审计 | 旧76开发patch中60有正权重source邻居越fullFOV直接证人，其余16不证明足够；保守bbox均不fit | crop边界损失与插值平滑不同，不证明医学失败原因。[CURRENT_RESEARCH_STATUS_RESOLUTION_SUPPORT_2026-10-08.md](../../innovation/CURRENT_RESEARCH_STATUS_RESOLUTION_SUPPORT_2026-10-08.md) |
| roundtrip image-only完整schedule | 2992步/5984geometry、11/19；1785 active、4199primitive identity；完整前景曝光90636500中18无足支持（来自010一个series） | 38stress“FG不足0”不能外推完整schedule。全target gate使active仅272/1785可用（15.2381%），整schedule4.54545%，5/11患者和9/19series零执行；不当充分强baseline、不启动此配方2992训练。[FULL_SCHEDULE_COMPLETION_RESULTS.md](../../innovation/real_context_and_author_code_followup_2026_10_08/FULL_SCHEDULE_COMPLETION_RESULTS.md) |
| 原增强全真实管线 | 35904字段目标；首版6216成功后6217字段full error3.814697e−6>3e−6；float64统计v2修当前失败但完整跑14673后第14674仍失败 | 成功prefix不继承；后一失败是resolution差经gamma传播；精确Fraction发现half-ULP/ties-even单点，不能据此改oracle迎合生产。[RESULTS_AND_NEXT_ACTION.md](../../innovation/intensity_precision_failure_diagnosis_2026_10_09/RESULTS_AND_NEXT_ACTION.md)、[FAILED_V2_FINDINGS_AND_NEXT.md](../../innovation/resource_recovery_and_generalization_controls_2026_10_09/FAILED_V2_FINDINGS_AND_NEXT.md) |
| 新完整certified schedule | 最终session44317真正exit0；**35904字段、5984case-kind steps、38MRI输入/19母GT**完成，elapsed30733.331590s；intensity/support max0，coordinate1.136868e−13；独立全身份/journal审计通过 | 是全数值管线资格，未重跑医学数组，不等于强task或六臂训练完成。[ROUND52_RESEARCH_AND_VALIDATION_RESULT.md](../../innovation/gpu_full_fov_and_atomic_capture_2026_10_09/ROUND52_RESEARCH_AND_VALIDATION_RESULT.md)、[receipt.json](../../innovation/full_certified_schedule_2026_10_09/full_real_terminal_audit_attempt01/receipt.json) |
| 无损预测压缩 | 14组合成（含最大512×512×144）；56 reader跨格式值逐位同、padding0；结构化样例4719940→9009bytes，随机样例反增1054 | 保持binary科学内容，不推真实压缩比或推断加速；V2 import失败另建V3。最终56FOV已运行，以后续真实RESULT为准。[RESULT.md](../../innovation/lossless_final_evaluation_entry_2026_10_08/RESULT.md)、[RESULT.md](../../innovation/final_training_medical_execution_2026_10_08/RESULT.md) |
| CPU/GPU整FOV严格数值诊断 | 原native全FOV概率差约3.3346e−6（部分记录5.3346e−6为原诊断对象）仍超3e−6；首Conv同，首IN3.0518e−5；两个FP32 IN候选5.7220e−6/5.3644e−6均失败且慢 | 不放宽原概率gate；重复tile不增加患者。[ROUND47_RESEARCH_AND_VALIDATION_RESULT.md](../../innovation/six_resolution_training_preparation_2026_10_09/ROUND47_RESEARCH_AND_VALIDATION_RESULT.md)、[ALL_TILES_AND_FP32_NEGATIVE_FINDINGS.md](../../innovation/gpu_full_fov_and_atomic_capture_2026_10_09/ALL_TILES_AND_FP32_NEGATIVE_FINDINGS.md) |
| 完整图offload透明性 | save_on_cpu与独立saved_tensors_hooks人工各两步，3heads/loss/54参数gradient/update/162 Adam字段每步逐位同；240保存/224恢复，GPU peak2.279604GB、显式CPU payload2.810693GB | 不等于独立CPU算术参考，人工case不外推19series成本。[ROUND48_RESEARCH_AND_VALIDATION_RESULT.md](../../innovation/six_resolution_training_preparation_2026_10_09/ROUND48_RESEARCH_AND_VALIDATION_RESULT.md) |
| FP64 norm+FP32图/Adam敏感性 | norm数学可过，但人工full图step0参数差1.0646414e−5>3e−6；near-zero同号gradient相差约1.54e−9被Adam放大；stable reduction后仍3.460329e−6失败 | 没改Adam eps/LR/阈值迎合；只解释该人工坐标，不解释全部实模型。[ROUND50_RESEARCH_AND_VALIDATION_RESULT.md](../../innovation/six_resolution_training_preparation_2026_10_09/ROUND50_RESEARCH_AND_VALIDATION_RESULT.md)、[ROUND51_RESEARCH_AND_VALIDATION_RESULT.md](../../innovation/six_resolution_training_preparation_2026_10_09/ROUND51_RESEARCH_AND_VALIDATION_RESULT.md) |
| FP64 graph新分支 | 54 FP32参数/Adamstate、FP64中间图，人工GPU/CPU两步param max1.49e−8/binary0；原fullpatch首版OOM，0forward/update | 人工小图过不继承全尺寸。[ROUND51_RESEARCH_AND_VALIDATION_RESULT.md](../../innovation/six_resolution_training_preparation_2026_10_09/ROUND51_RESEARCH_AND_VALIDATION_RESULT.md) |
| compact-double-norm/原尺寸修复 | 单FP64 buffer/解析一阶VJP、逐段checkpoint/消费释放skip；8种random/constant/nearconstant/sparse×affine数学case过3e−6，Decimal FD max5.13e−12；原patch2×1×64×128×128三view完整两步 **GPU2/CPU2，param max3.72529e−9、prob2.66015e−8、binary0、peak2.304770GB、388.233s** | v1/v2全patchbackward OOM保留；custom autograd只认一阶，不认证二阶。是本地工程实现，非医学收益。[ROUND52_RESEARCH_AND_VALIDATION_RESULT.md](../../innovation/gpu_full_fov_and_atomic_capture_2026_10_09/ROUND52_RESEARCH_AND_VALIDATION_RESULT.md) |
| 新compact19真实资格 | 目标38case-kind×两步=GPU76/CPU76updates、228/228whole-modelforward、152内存capture | 最新保存ROUND53仍为prefix：case0/rawPCHIP CPUstep1；case0/native两步binary0/step1param7.45e−9。**未有全19终态、完整FOV/磁盘atomic/真实费用资格，正式六臂未ready。**[POST_ARCHIVE_HANDOFF_ROUND52_V2.md](../../innovation/gpu_full_fov_and_atomic_capture_2026_10_09/POST_ARCHIVE_HANDOFF_ROUND52_V2.md) |

### K. 仍保留的原创研究候选与明确停止项

**优先待检验假设：**在同一合法observed稀疏MRI、同预算和强普通task/增强控制之后，采集可见性或observed动作响应特征，是否能预测具体SR/TTA/联合动作的真实患者分割净收益，超过强static/always/none、same-budget random、metadata-only、SSC/QC/defer、同信息同容量action-conditioned risk差及去额外采集特征对照。gain是baseline−action真实完整FOV病灶损害差，特征/定位/候选/teacher/阈值/费用拟合都按患者折内，严格外折task需cold-init；19998 parent见过全11GT不能作LOPO warm start。最终联合收益需直接全FOV执行，不由单动作label相加；所有probe、生成、传输、cache初始化、fallback/defer、训练/评价均计费。尚未实测人类时间，不能称临床省时。

候选二为**预算受约束的动作组合交互与联合费用**，必须超强单动作/静态组合/固定顺序/一步greedy/random，并先分离Dice分式、threshold/支持冲突和真实网络效应；联合选择、RL、收益cost比greedy、条件MI均有已读先例，不单独作算法新颖性。候选三为**响应感知的目标薄层query/独立原始采集身份实验**，需要真实薄层reference、实测slice response与同平面独立采集来源，当前来源门槛未闭合；已知profile IXI-train三人12条件pilot仅5/12选对设定核、6个blur条件0/6选对、missing误差零改善/两条件恶化，固定实现停止。证据：[KNOWN_PROFILE_HOLDOUT_PILOT_RESULT_2026-10-01.md](../../innovation/KNOWN_PROFILE_HOLDOUT_PILOT_RESULT_2026-10-01.md)、[INNOVATION_DECISION_MEMO_2026-10-01.md](../../innovation/INNOVATION_DECISION_MEMO_2026-10-01.md)、[FUTURE_EXPERIMENT_REGISTRY_ROUND51_V2.json](../../innovation/adaptive_acquisition_primary_followup_2026_10_09/FUTURE_EXPERIMENT_REGISTRY_ROUND51_V2.json)、[ROUND52_RESEARCH_AND_VALIDATION_RESULT.md](../../innovation/gpu_full_fov_and_atomic_capture_2026_10_09/ROUND52_RESEARCH_AND_VALIDATION_RESULT.md)。

当前明确停止/未成功的分支包括：旧orientation直接大型gate；repaired-wavelet额外局部gate；continuous influence外部可行动score；跨来源disjoint ensemble性能claim；MSD→ds007045主SwinIR病灶损害复制；VS45 HAT−pipelinePCHIP原负向联合claim；残差相加；order风险/固定anchor带宽恢复；原pipeline三人和raw五人无约束收益头；五人30特征ridge联合策略；冻结分割/QDA-LDA/窄ROI定位；各弱task配方；完整roundtrip gate的“充分强增强”资格；多次严格GPU/CPU数值候选。停止仅针对已固定实现/动作/来源，不伪装成所有可能方法的不可能证明。

当前不能作为“原创成功方法”的已知思路有：多锚点/phase/mask conditioning、query、spatial/FFT expert gate、收益标签重参数化、联合采样重建分割/RL、普通增强/分辨率随机化、GIN/IPA/SSC、预训练、reference IN、缓存/halo/offload、自监督风险已有数学定义。新意仍须落在经过对照和保留患者确认的具体MRI结果。

### L. 来源资格与未能执行的实验（保留失败、不给成像结果）

| 来源/路线 | 本地已核状态 | 对原创问题的影响/证据 |
| --- | --- | --- |
| fastMRI重复T2 | 61头筛查与64对清单扩展；4技术匹配对无独立时间/精确来源权利证明 | 未启动身份像素实验。[FASTMRI_ALL_T2_HEADER_GATE_RESULT_2026-10-01.md](../../innovation/FASTMRI_ALL_T2_HEADER_GATE_RESULT_2026-10-01.md)、[FASTMRI_MANIFEST_LINKED_PAIR_RESULT_2026-10-01.md](../../innovation/FASTMRI_MANIFEST_LINKED_PAIR_RESULT_2026-10-01.md) |
| QIN重复T2 | 15对中0同几何合格 | 无同平面身份实验。[QIN_REPEAT_T2_ALL_HEADER_RESULT_2026-10-01.md](../../innovation/QIN_REPEAT_T2_ALL_HEADER_RESULT_2026-10-01.md) |
| Kirby21 | 有重复T2w几何参考，但3D Fourier/名义2mm；重叠1mm发布层不是独立2D采集 | 来源不满足原2D身份问题。[KIRBY21_REPEAT_T2_SOURCE_GATE_RESULT_2026-10-01.md](../../innovation/KIRBY21_REPEAT_T2_SOURCE_GATE_RESULT_2026-10-01.md) |
| ON-Harmony/Connectivity | T2wFLAIR GE MR750与9人within-scanner repeat代码无交集；57人retest论文T2仅session1 | 纸面/metadata门槛关闭，未跑影像。对应 `*_SOURCE_GATE_RESULT_2026-10-01.md` |
| UPENN labels | 232 metadata有纠正label，官方文件候选147，60薄层；DICOM与atlas NIfTI/seg设计上不对齐；两文件Aspera零bytes失败 | 不能把mask按patientID叠到1496 DICOM目标；新atlas实验尚无header。[UPENN_GBM_LABEL_ALIGNMENT_GATE_RESULT_2026-10-01.md](../../innovation/UPENN_GBM_LABEL_ALIGNMENT_GATE_RESULT_2026-10-01.md)、[UPENN_NIFTI_OFFICIAL_PACKAGE_INVENTORY_RESULT_2026-10-01.md](../../innovation/UPENN_NIFTI_OFFICIAL_PACKAGE_INVENTORY_RESULT_2026-10-01.md)、[UPENN_ASPERA_TWO_FILE_ACCESS_RESULT_2026-10-01.md](../../innovation/UPENN_ASPERA_TWO_FILE_ACCESS_RESULT_2026-10-01.md) |
| UCSF-PDGM | 495人501exam、6复查、298 BraTS21映射；文件级T2/mask线索；两次精确双文件Faspex500/零NIfTI | 同网格、未见身份及复制仍未证。[UCSF_PDGM_INDEPENDENT_T2_LABEL_SOURCE_GATE_RESULT_2026-10-01.md](../../innovation/UCSF_PDGM_INDEPENDENT_T2_LABEL_SOURCE_GATE_RESULT_2026-10-01.md)、[UCSF_PDGM_ASCLI_TWO_FILE_ACCESS_RESULT_2026-10-01.md](../../innovation/UCSF_PDGM_ASCLI_TWO_FILE_ACCESS_RESULT_2026-10-01.md) |
| VS-SEG旧精确TV名方案 | 原完整batch14例后中止，仅1模型完成；242例RTSTRUCT语义审计与目标上界说明原选择不可达 | 后续45全体积合同为新任务，不追称旧protocol完整。[VS_SEG_SOURCE_BOUND_AND_TASK_PREFLIGHT_RESULT_2026-10-02.md](../../innovation/VS_SEG_SOURCE_BOUND_AND_TASK_PREFLIGHT_RESULT_2026-10-02.md) |

以下附录保留本目录全部顶层结果报告的入口，详细行级数值/患者分母/失败/协议沿各报告链接回原CSV/JSON；文献原文和作者代码本身不列为原创方法。

### M. 有实质结果的原始报告索引

索引按原报告保留，不将结果后控制重复算作独立患者确认。来源/标签/头部资格另见正文 L；以下只列数值实验、任务能力、动作、诊断及工程资格。

| 编号 | 报告原题 | 仓库根相对入口 |
| --- | --- | --- |
| I001 | 原稿响应影响量的锚点错配负对照 | [ACQUIRED_RESPONSE_ID_PLACEBO_RESULT_2026-09-30.md](../../innovation/ACQUIRED_RESPONSE_ID_PLACEBO_RESULT_2026-09-30.md) |
| I002 | Pilot最后模型的描述比较，等待全部结果 | [DESCRIPTIVE_COMPARISON_PREPARATION.md](../../innovation/adaptation_paired_pilot_2026_10_08/DESCRIPTIVE_COMPARISON_PREPARATION.md) |
| I003 | 固定99步配对续训：完整评价 | [FINAL_DESCRIPTIVE_COMPARISON.md](../../innovation/adaptation_paired_pilot_2026_10_08/FINAL_DESCRIPTIVE_COMPARISON.md) |
| I004 | anchors/缺层相位梯度能量：45人解析结果 | [ANCHOR_BANDWIDTH_DIAGNOSTIC_CPU_RESULT_2026-10-03.md](../../innovation/ANCHOR_BANDWIDTH_DIAGNOSTIC_CPU_RESULT_2026-10-03.md) |
| I005 | 三人 anchors-only × 归一化任务预检：完整结果 | [ANCHOR_BANDWIDTH_TASK_CPU_PILOT_RESULT_2026-10-03.md](../../innovation/ANCHOR_BANDWIDTH_TASK_CPU_PILOT_RESULT_2026-10-03.md) |
| I006 | anchors-only对照必须控制全volume归一化 | [ANCHOR_NORMALIZATION_CONTROL_CPU_RESULT_2026-10-03.md](../../innovation/ANCHOR_NORMALIZATION_CONTROL_CPU_RESULT_2026-10-03.md) |
| I007 | 三人边界反向结果：事后计数分解 | [ANCHOR_PILOT_BOUNDARY_DECOMPOSITION_CPU_RESULT_2026-10-03.md](../../innovation/ANCHOR_PILOT_BOUNDARY_DECOMPOSITION_CPU_RESULT_2026-10-03.md) |
| I008 | 三人已保存预测：观测层、缺层和tail的实际响应 | [ANCHOR_PILOT_OUTPUT_DOMAIN_AUDIT_CPU_RESULT_2026-10-03.md](../../innovation/ANCHOR_PILOT_OUTPUT_DOMAIN_AUDIT_CPU_RESULT_2026-10-03.md) |
| I009 | 精确校准仍可能选中有害修正：实际CPU结果 | [CALIBRATED_RISK_VS_ACTION_GAIN_CPU_RESULT_2026-10-07.md](../../innovation/CALIBRATED_RISK_VS_ACTION_GAIN_CPU_RESULT_2026-10-07.md) |
| I010 | 共同投影 observed 输入控制：19 系列结果 | [COMMON_PROJECTED_OBSERVED_INPUT_RESULT_2026-10-08.md](../../innovation/COMMON_PROJECTED_OBSERVED_INPUT_RESULT_2026-10-08.md) |
| I011 | 真终态后的完整开发/已见验证比较入口 | [COMPLETE_COMPARISON_PREPARATION.md](../../innovation/conditional_uq_and_task_capacity_followup_2026_10_09/COMPLETE_COMPARISON_PREPARATION.md) |
| I012 | 当前证据、候选假设与后续执行准备 | [EXPERIMENT_STATUS_AND_NEXT_TRIALS.md](../../innovation/conditional_uq_and_task_capacity_followup_2026_10_09/EXPERIMENT_STATUS_AND_NEXT_TRIALS.md) |
| I013 | 旧队列 HAT→SwinIR 跨架构响应：机制可见，预测收益不稳 | [CROSS_ARCH_ACQUIRED_RESPONSE_RESULT_2026-09-30.md](../../innovation/CROSS_ARCH_ACQUIRED_RESPONSE_RESULT_2026-09-30.md) |
| I014 | 实际观测特征路径成本：一次CPU全19series | [DEPLOYMENT_FEATURE_COST_RESULT_2026-10-08.md](../../innovation/DEPLOYMENT_FEATURE_COST_RESULT_2026-10-08.md) |
| I015 | High-resolution 3D T2 pilot: primary SwinIR replication fails | [DS007045_THIN3D_MODEL_PILOT_RESULT_2026-10-01.md](../../innovation/DS007045_THIN3D_MODEL_PILOT_RESULT_2026-10-01.md) |
| I016 | Thin-3D T2 PCHIP sensitivity: HAT signal persists, confirmation remains open | [DS007045_THIN3D_PCHIP_SENSITIVITY_RESULT_2026-10-01.md](../../innovation/DS007045_THIN3D_PCHIP_SENSITIVITY_RESULT_2026-10-01.md) |
| I017 | CPU 可行性检查：已有预测与名义层厚 | [CPU_RESULTS_2026-09-30.md](../../innovation/experiments/CPU_RESULTS_2026-09-30.md) |
| I018 | 固定修正动作的局部收益与结构代价：CPU 开发性诊断 | [LOCAL_ACTION_STUDY_2026-09-30.md](../../innovation/experiments/LOCAL_ACTION_STUDY_2026-09-30.md) |
| I019 | Manifest-linked multi-T2 candidate screen: nonpixel result | [FASTMRI_MANIFEST_LINKED_PAIR_RESULT_2026-10-01.md](../../innovation/FASTMRI_MANIFEST_LINKED_PAIR_RESULT_2026-10-01.md) |
| I020 | 最终训练、医学评价、精度修复与文献决定 | [RESULT.md](../../innovation/final_training_medical_execution_2026_10_08/RESULT.md) |
| I021 | 固定完整45人：整volume统计反馈审计 | [FULL45_NORMALIZATION_DRIFT_CPU_RESULT_2026-10-03.md](../../innovation/FULL45_NORMALIZATION_DRIFT_CPU_RESULT_2026-10-03.md) |
| I022 | 全tile定位完成，两个FP32算术方案均失败 | [ALL_TILES_AND_FP32_NEGATIVE_FINDINGS.md](../../innovation/gpu_full_fov_and_atomic_capture_2026_10_09/ALL_TILES_AND_FP32_NEGATIVE_FINDINGS.md) |
| I023 | 完整FOV数值资格失败与后续定位 | [NUMERICAL_FINDINGS_AND_NEXT.md](../../innovation/gpu_full_fov_and_atomic_capture_2026_10_09/NUMERICAL_FINDINGS_AND_NEXT.md) |
| I024 | ROUND52：原尺寸两步通过，进入完整开发series资格 | [ROUND52_RESEARCH_AND_VALIDATION_RESULT.md](../../innovation/gpu_full_fov_and_atomic_capture_2026_10_09/ROUND52_RESEARCH_AND_VALIDATION_RESULT.md) |
| I025 | 固定2992匹配增强：完整医学结果与下一动作 | [MEDICAL_RESULTS_AND_NEXT_ACTION.md](../../innovation/imputation_mask_and_conditional_uncertainty_2026_10_09/MEDICAL_RESULTS_AND_NEXT_ACTION.md) |
| I026 | 响应影响量：精确上下文与留出预测复核 | [INFLUENCE_EXACT_CONTEXT_AUDIT_2026-09-30.md](../../innovation/INFLUENCE_EXACT_CONTEXT_AUDIT_2026-09-30.md) |
| I027 | 原完整检查失败后的诊断和修复 | [RESULTS_AND_NEXT_ACTION.md](../../innovation/intensity_precision_failure_diagnosis_2026_10_09/RESULTS_AND_NEXT_ACTION.md) |
| I028 | IXI validation-only diagnostic: frozen models versus the same two-neighbor linear baseline | [IXI_VALIDATION_EQUAL_NEIGHBOR_DIAGNOSTIC_RESULT_2026-10-01.md](../../innovation/IXI_VALIDATION_EQUAL_NEIGHBOR_DIAGNOSTIC_RESULT_2026-10-01.md) |
| I029 | 训练内已知 profile 小试：留出观测选核失败 | [KNOWN_PROFILE_HOLDOUT_PILOT_RESULT_2026-10-01.md](../../innovation/KNOWN_PROFILE_HOLDOUT_PILOT_RESULT_2026-10-01.md) |
| I030 | 最终评价无损存储入口的实际结果 | [RESULT.md](../../innovation/lossless_final_evaluation_entry_2026_10_08/RESULT.md) |
| I031 | 合成 mask 依赖如何影响两个动作的排序 | [MASK_DEPENDENT_ACTION_RANKING_CPU_RESULT_2026-10-02.md](../../innovation/MASK_DEPENDENT_ACTION_RANKING_CPU_RESULT_2026-10-02.md) |
| I032 | 两名MC-RC开发患者复核：原raw分支未过门槛 | [MC_RC_001_002_RAW_ACTION_ORACLE_RESULT_2026-10-02.md](../../innovation/MC_RC_001_002_RAW_ACTION_ORACLE_RESULT_2026-10-02.md) |
| I033 | 共同初始化正式训练前99步结果 | [MC_RC_3D_19SERIES_COMMON_INIT_SEGMENT99_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_19SERIES_COMMON_INIT_SEGMENT99_RESULT_2026-10-07.md) |
| I034 | 联合动作的真实开发MRI响应及精确指标控制 | [MC_RC_3D_ACTION_COMPOSITION_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_ACTION_COMPOSITION_RESULT_2026-10-07.md) |
| I035 | 全tile特征覆盖诊断：最后权重全部结果 | [MC_RC_3D_ALL_TILE_HEAD_FIT_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_ALL_TILE_HEAD_FIT_RESULT_2026-10-07.md) |
| I036 | native接续失败：无更新诊断结果 | [MC_RC_3D_BACKBONE_COLLAPSE_DIAGNOSTIC_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_BACKBONE_COLLAPSE_DIAGNOSTIC_RESULT_2026-10-07.md) |
| I037 | 低学习率完整 context 对照：实测结果 | [MC_RC_3D_BACKBONE_CONTEXT_LOW_LR_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_BACKBONE_CONTEXT_LOW_LR_RESULT_2026-10-07.md) |
| I038 | 完整context骨干接续拟合：最后模型结果 | [MC_RC_3D_BACKBONE_CONTEXT_REFIT_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_BACKBONE_CONTEXT_REFIT_RESULT_2026-10-07.md) |
| I039 | 两臂512更新CPU拟合：完整实际结果 | [MC_RC_3D_CPU_FIXED_FIT_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_CPU_FIXED_FIT_RESULT_2026-10-07.md) |
| I040 | 56完整FOV评价入口：执行准备与合成资格结果 | [MC_RC_3D_FINAL_EVALUATION_ENTRY_PREPARATION_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_FINAL_EVALUATION_ENTRY_PREPARATION_RESULT_2026-10-07.md) |
| I041 | 有限依赖分块的结构准备结果 | [MC_RC_3D_FINITE_CONTEXT_HALO_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_FINITE_CONTEXT_HALO_RESULT_2026-10-07.md) |
| I042 | 固定骨干、主head拟合：全部结果 | [MC_RC_3D_FROZEN_FEATURE_HEAD_FIT_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_FROZEN_FEATURE_HEAD_FIT_RESULT_2026-10-07.md) |
| I043 | 开发标签网格往返：完整结果 | [MC_RC_3D_LABEL_ROUNDTRIP_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_LABEL_ROUNDTRIP_RESULT_2026-10-07.md) |
| I044 | 局部输入修改的完整FOV缓存资格结果 | [MC_RC_3D_LOCAL_EDIT_CACHE_QUALIFICATION_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_LOCAL_EDIT_CACHE_QUALIFICATION_RESULT_2026-10-07.md) |
| I045 | 配对采样与完整FOV资格的实际结果 | [MC_RC_3D_PAIRED_SAMPLING_FOV_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_PAIRED_SAMPLING_FOV_RESULT_2026-10-07.md) |
| I046 | PCHIP参照内部统计的实现准备结果 | [MC_RC_3D_REFERENCE_IN_PREFLIGHT_RESULT_2026-10-07.md](../../innovation/MC_RC_3D_REFERENCE_IN_PREFLIGHT_RESULT_2026-10-07.md) |
| I047 | 19系列合法观测定位诊断：先验、覆盖和窗口费用 | [MC_RC_ANCHOR_PRIOR_FOREST_DIAGNOSTIC_RESULT_2026-10-07.md](../../innovation/MC_RC_ANCHOR_PRIOR_FOREST_DIAGNOSTIC_RESULT_2026-10-07.md) |
| I048 | 真实观测层 QDA/LDA：全量开发诊断与复核结果 | [MC_RC_ANCHOR_QDA_CPU_RESULT_2026-10-03.md](../../innovation/MC_RC_ANCHOR_QDA_CPU_RESULT_2026-10-03.md) |
| I049 | 单012覆盖×增强：固定预算完整结果 | [MC_RC_COVERAGE_AUGMENTATION_FACTORIAL_CPU_RESULT_2026-10-03.md](../../innovation/MC_RC_COVERAGE_AUGMENTATION_FACTORIAL_CPU_RESULT_2026-10-03.md) |
| I050 | 19真实开发输入与当前角色分母修正 | [MC_RC_DEVELOPMENT_INPUT_CPU_RESULT_2026-10-03.md](../../innovation/MC_RC_DEVELOPMENT_INPUT_CPU_RESULT_2026-10-03.md) |
| I051 | 五人病灶约束动作空间：数值复核通过，方法尚未验证 | [MC_RC_FIVE_DEVELOPER_CONSTRAINED_ORACLE_RESULT_2026-10-02.md](../../innovation/MC_RC_FIVE_DEVELOPER_CONSTRAINED_ORACLE_RESULT_2026-10-02.md) |
| I052 | 冻结全视野模型的全部训练内完整诊断 | [MC_RC_FROZEN_GLOBAL_LOCAL_DEVELOPMENT_DIAGNOSIS_CPU_RESULT_2026-10-03.md](../../innovation/MC_RC_FROZEN_GLOBAL_LOCAL_DEVELOPMENT_DIAGNOSIS_CPU_RESULT_2026-10-03.md) |
| I053 | 冻结模型的观测层预测区域：0/15通过，完整重放已复核 | [MC_RC_FROZEN_PREDICTED_REGION_CPU_RESULT_2026-10-03.md](../../innovation/MC_RC_FROZEN_PREDICTED_REGION_CPU_RESULT_2026-10-03.md) |
| I054 | 单012固定切面、完整tile覆盖的最小拟合结果 | [MC_RC_GLOBAL_LOCAL_FIXED_PLANE_FIT_CPU_RESULT_2026-10-03.md](../../innovation/MC_RC_GLOBAL_LOCAL_FIXED_PLANE_FIT_CPU_RESULT_2026-10-03.md) |
| I055 | 单012全视野、同预算loss配方诊断完整结果 | [MC_RC_GLOBAL_LOCAL_SINGLE_CASE_LOSS_CPU_RESULT_2026-10-03.md](../../innovation/MC_RC_GLOBAL_LOCAL_SINGLE_CASE_LOSS_CPU_RESULT_2026-10-03.md) |
| I056 | 全视野/局部任务基线：完整 CPU 验证结果 | [MC_RC_GLOBAL_LOCAL_TASK_CPU_RESULT_2026-10-03.md](../../innovation/MC_RC_GLOBAL_LOCAL_TASK_CPU_RESULT_2026-10-03.md) |
| I057 | 单配方intensity-only GPU20k：完整能力结果 | [MC_RC_INTENSITY_ONLY_FULL_TASK_RESULT_2026-10-03.md](../../innovation/MC_RC_INTENSITY_ONLY_FULL_TASK_RESULT_2026-10-03.md) |
| I058 | 四倍抽层标签覆盖：完全隐藏成分不能解释主条件失败 | [MC_RC_LABEL_ANCHOR_VISIBILITY_RESULT_2026-10-03.md](../../innovation/MC_RC_LABEL_ANCHOR_VISIBILITY_RESULT_2026-10-03.md) |
| I059 | 当前 19 系列匹配的理想观测标签支持 | [MC_RC_MATCHED_ANCHOR_ORACLE_RESULT_2026-10-08.md](../../innovation/MC_RC_MATCHED_ANCHOR_ORACLE_RESULT_2026-10-08.md) |
| I060 | 匹配支持的两种费用流程与未执行重打包 | [MC_RC_MATCHED_ORACLE_BUDGET_RESULT_2026-10-08.md](../../innovation/MC_RC_MATCHED_ORACLE_BUDGET_RESULT_2026-10-08.md) |
| I061 | 16 系列完整 native 能力对照：全量独立重放结果 | [MC_RC_NATIVE_COMPETENCE_CPU_RESULT_2026-10-03.md](../../innovation/MC_RC_NATIVE_COMPETENCE_CPU_RESULT_2026-10-03.md) |
| I062 | 无增强20k完整任务能力：开发与四验证结果 | [MC_RC_NO_AUGMENTATION_FULL_TASK_RESULT_2026-10-03.md](../../innovation/MC_RC_NO_AUGMENTATION_FULL_TASK_RESULT_2026-10-03.md) |
| I063 | 理想观测区域传播结果：几何可行，不能称可部署优势 | [MC_RC_OBSERVED_REGION_PROPAGATION_RESULT_2026-10-03.md](../../innovation/MC_RC_OBSERVED_REGION_PROPAGATION_RESULT_2026-10-03.md) |
| I064 | 观测预测 ROI 与当前 3D 缓存成本：结果 | [MC_RC_OBSERVED_ROI_CACHE_COST_RESULT_2026-10-07.md](../../innovation/MC_RC_OBSERVED_ROI_CACHE_COST_RESULT_2026-10-07.md) |
| I065 | 冻结观测 ROI 的真实 MRI 输入探针：结果 | [MC_RC_OBSERVED_ROI_REAL_INPUT_PROBE_RESULT_2026-10-07.md](../../innovation/MC_RC_OBSERVED_ROI_REAL_INPUT_PROBE_RESULT_2026-10-07.md) |
| I066 | 两个未训练增强因素臂：实际输入预检通过 | [MC_RC_PARTIAL_AUGMENTATION_PREFLIGHT_CPU_RESULT_2026-10-03.md](../../innovation/MC_RC_PARTIAL_AUGMENTATION_PREFLIGHT_CPU_RESULT_2026-10-03.md) |
| I067 | 真实开发标签支持的条件缓存空间 | [MC_RC_REAL_SUPPORT_CACHE_DIAGNOSTIC_RESULT_2026-10-07.md](../../innovation/MC_RC_REAL_SUPPORT_CACHE_DIAGNOSTIC_RESULT_2026-10-07.md) |
| I068 | CPU任务训练：完整执行、能力失败与单病例可拟合性诊断 | [MC_RC_SPARSE_TASK_TRAINING_CPU_RESULT_2026-10-03.md](../../innovation/MC_RC_SPARSE_TASK_TRAINING_CPU_RESULT_2026-10-03.md) |
| I069 | 三名开发患者的动作上限：主pipeline方向未过病灶门槛 | [MC_RC_THREE_DEVELOPMENT_ACTION_ORACLE_RESULT_2026-10-02.md](../../innovation/MC_RC_THREE_DEVELOPMENT_ACTION_ORACLE_RESULT_2026-10-02.md) |
| I070 | 五患者可见特征诊断：固定联合政策失败，收益标签与误差标签等价 | [MC_RC_VISIBLE_JOINT_DEVELOPMENT_DIAGNOSTIC_RESULT_2026-10-02.md](../../innovation/MC_RC_VISIBLE_JOINT_DEVELOPMENT_DIAGNOSTIC_RESULT_2026-10-02.md) |
| I071 | MSD Task01: same-neighbor linear baseline versus frozen IXI networks | [MSD_EQUAL_NEIGHBOR_LINEAR_AUDIT_RESULT_2026-10-01.md](../../innovation/MSD_EQUAL_NEIGHBOR_LINEAR_AUDIT_RESULT_2026-10-01.md) |
| I072 | MSD full-foreground baseline: regional error versus global metric | [MSD_FULL_SUPPORT_EQUAL_NEIGHBOR_POSTRESULT_RESULT_2026-10-01.md](../../innovation/MSD_FULL_SUPPORT_EQUAL_NEIGHBOR_POSTRESULT_RESULT_2026-10-01.md) |
| I073 | Full CPU replay: model preprocessing versus raw two-neighbor linear | [MSD_PIPELINE_LINEAR_CONTROL_RESULT_2026-10-01.md](../../innovation/MSD_PIPELINE_LINEAR_CONTROL_RESULT_2026-10-01.md) |
| I074 | Analytic interpolation falsification of the MSD tumor-region context effect | [MSD_TASK01_ANALYTIC_CONTEXT_CONTROL_RESULT_2026-10-01.md](../../innovation/MSD_TASK01_ANALYTIC_CONTEXT_CONTROL_RESULT_2026-10-01.md) |
| I075 | MSD first-case source and ROI qualification | [MSD_TASK01_FIRST_CASE_PIXEL_QUALIFICATION_RESULT_2026-10-01.md](../../innovation/MSD_TASK01_FIRST_CASE_PIXEL_QUALIFICATION_RESULT_2026-10-01.md) |
| I076 | MSD BrainTumour tumor-region context audit: complete result | [MSD_TASK01_TUMOR_ROI_CONTEXT_RESULT_2026-10-01.md](../../innovation/MSD_TASK01_TUMOR_ROI_CONTEXT_RESULT_2026-10-01.md) |
| I077 | MSValid 共同 min/max 敏感性结果（结果后探索） | [MSVALID_COMMON_NORM_RESULT_2026-09-30.md](../../innovation/MSVALID_COMMON_NORM_RESULT_2026-09-30.md) |
| I078 | MSValid 的 O 差异主要表现为误差对齐变化 | [MSVALID_ERROR_ALIGNMENT_DECOMPOSITION_RESULT_2026-09-30.md](../../innovation/MSVALID_ERROR_ALIGNMENT_DECOMPOSITION_RESULT_2026-09-30.md) |
| I079 | MSValid 外部确认：MIRA 的共享锚点失明现象 | [MSVALID_EXTERNAL_CONFIRMATION_2026-09-30.md](../../innovation/MSVALID_EXTERNAL_CONFIRMATION_2026-09-30.md) |
| I080 | MSValid 剩余 60 人影响量留出检验：严格几何基线下无增益 | [MSVALID_INFLUENCE_P25_P84_RESULT_2026-10-01.md](../../innovation/MSVALID_INFLUENCE_P25_P84_RESULT_2026-10-01.md) |
| I081 | MSValid 跨架构响应影响阶段 1：12 人探索性结果 | [MSVALID_INFLUENCE_STAGE1_RESULT_2026-09-30.md](../../innovation/MSVALID_INFLUENCE_STAGE1_RESULT_2026-09-30.md) |
| I082 | MSValid IXI 权重对：共同缩放与反向相位结果 | [MSVALID_IXI_WEIGHT_POSTRESULT_CONTROLS_RESULT_2026-10-01.md](../../innovation/MSVALID_IXI_WEIGHT_POSTRESULT_CONTROLS_RESULT_2026-10-01.md) |
| I083 | MSValid 次级复制：IXI 训练 HAT/SwinIR 权重 | [MSVALID_IXI_WEIGHTS_SECONDARY_RESULT_2026-10-01.md](../../innovation/MSVALID_IXI_WEIGHTS_SECONDARY_RESULT_2026-10-01.md) |
| I084 | Matched-geometry synthetic-noise control: full MSValid result | [MSVALID_MATCHED_GEOMETRY_NOISE_CONTROL_RESULT_2026-10-01.md](../../innovation/MSVALID_MATCHED_GEOMETRY_NOISE_CONTROL_RESULT_2026-10-01.md) |
| I085 | MSValid 反向相位与线性伙伴控制结果（结果后探索） | [MSVALID_POSTHOC_CONTROL_RESULT_2026-09-30.md](../../innovation/MSVALID_POSTHOC_CONTROL_RESULT_2026-09-30.md) |
| I086 | 仅观测层顺序差风险候选：固定配置停止 | [OBSERVABLE_ORDER_RISK_CPU_RESULT_2026-10-03.md](../../innovation/OBSERVABLE_ORDER_RISK_CPU_RESULT_2026-10-03.md) |
| I087 | 真实19系列的观测留出特征与独立核验结果 | [OBSERVED_HOLDOUT_FEATURE_RESULT_2026-10-08.md](../../innovation/OBSERVED_HOLDOUT_FEATURE_RESULT_2026-10-08.md) |
| I088 | 直接观测物理表示的精确线性秩及同统计合成见证 | [OBSERVED_PROJECTION_INFORMATION_RESULT_2026-10-08.md](../../innovation/OBSERVED_PROJECTION_INFORMATION_RESULT_2026-10-08.md) |
| I089 | 位置通道单独替换：两公开来源 CPU 探索诊断 | [POSITION_CHANNEL_ONLY_PILOT_RESULT_2026-10-01.md](../../innovation/POSITION_CHANNEL_ONLY_PILOT_RESULT_2026-10-01.md) |
| I090 | 公开来源线性伙伴负对照：两来源全量 CPU 结果 | [PUBLIC_LINEAR_PARTNER_CONTROL_RESULT_2026-10-01.md](../../innovation/PUBLIC_LINEAR_PARTNER_CONTROL_RESULT_2026-10-01.md) |
| I091 | 固定版本训练链：这次实际读到了什么 | [AUTHOR_TRAINING_CHAIN_FINDINGS.md](../../innovation/real_context_and_author_code_followup_2026_10_08/AUTHOR_TRAINING_CHAIN_FINDINGS.md) |
| I092 | 本阶段实际研究结果（完整资格与独立审计均通过） | [FULL_SCHEDULE_COMPLETION_RESULTS.md](../../innovation/real_context_and_author_code_followup_2026_10_08/FULL_SCHEDULE_COMPLETION_RESULTS.md) |
| I093 | 作者所链 ranker 已读，但不能替代 OOF 或集成实现 | [LESION_RANKER_FINDINGS_POST_ARCHIVE.md](../../innovation/real_context_and_author_code_followup_2026_10_08/LESION_RANKER_FINDINGS_POST_ARCHIVE.md) |
| I094 | ReMIND 主结果的误差对齐代数分解 | [REMIND_ERROR_ALIGNMENT_DECOMPOSITION_RESULT_2026-10-01.md](../../innovation/REMIND_ERROR_ALIGNMENT_DECOMPOSITION_RESULT_2026-10-01.md) |
| I095 | ReMIND 独立患者来源：术前 2D T2 冻结确认结果 | [REMIND_NATIVE_T2_CONFIRMATION_RESULT_2026-10-01.md](../../innovation/REMIND_NATIVE_T2_CONFIRMATION_RESULT_2026-10-01.md) |
| I096 | ReMIND 共同缩放与反向相位：全量结果后敏感性 | [REMIND_POSTRESULT_CONTROLS_RESULT_2026-10-01.md](../../innovation/REMIND_POSTRESULT_CONTROLS_RESULT_2026-10-01.md) |
| I097 | 固定残差相加CPU探索：2/6通过，整体停止 | [RESIDUAL_ADDBACK_CPU_RESULT_2026-10-03.md](../../innovation/RESIDUAL_ADDBACK_CPU_RESULT_2026-10-03.md) |
| I098 | 本阶段完成结果和边界 | [RESULTS.md](../../innovation/resolution_degradation_controls_2026_10_08/RESULTS.md) |
| I099 | 本次接续的实际结果 | [RESULTS_CONTINUATION_TURN29.md](../../innovation/resolution_degradation_controls_2026_10_08/RESULTS_CONTINUATION_TURN29.md) |
| I100 | v2失败已结束，后续从新的数值证据推进 | [FAILED_V2_FINDINGS_AND_NEXT.md](../../innovation/resource_recovery_and_generalization_controls_2026_10_09/FAILED_V2_FINDINGS_AND_NEXT.md) |
| I101 | 六个 HAT/SwinIR 锚点响应错配对照的同时区间 | [RESPONSE_PLACEBO_SIX_FAMILY_RESULT_2026-10-01.md](../../innovation/RESPONSE_PLACEBO_SIX_FAMILY_RESULT_2026-10-01.md) |
| I102 | 固定缺层收益代理的合成审计结果 | [RISK_ACTION_ASSUMPTION_CPU_RESULT_2026-10-02.md](../../innovation/RISK_ACTION_ASSUMPTION_CPU_RESULT_2026-10-02.md) |
| I103 | SAINT acquired-only 影响量的精确上下文复核 | [SAINT_EXACT_CONTEXT_AUDIT_2026-09-30.md](../../innovation/SAINT_EXACT_CONTEXT_AUDIT_2026-09-30.md) |
| I104 | 用户本次提供的接续摘要原文 | [SESSION_INHERITED_CPU_FINAL_RESULT_HANDOFF_VERBATIM_2026-10-07.md](../../innovation/SESSION_INHERITED_CPU_FINAL_RESULT_HANDOFF_VERBATIM_2026-10-07.md) |
| I105 | 本轮论文、联合动作与创新探索汇总 | [SESSION_RESULT_ACTION_COMPOSITION_2026-10-07.md](../../innovation/SESSION_RESULT_ACTION_COMPOSITION_2026-10-07.md) |
| I106 | 本轮入口：先验、合法定位与净成本 | [SESSION_RESULT_ANCHOR_PRIOR_2026-10-07.md](../../innovation/SESSION_RESULT_ANCHOR_PRIOR_2026-10-07.md) |
| I107 | 本轮研究总览：完整context骨干、原文排重与后续对照 | [SESSION_RESULT_BACKBONE_CONTEXT_2026-10-07.md](../../innovation/SESSION_RESULT_BACKBONE_CONTEXT_2026-10-07.md) |
| I108 | 本轮入口：共同投影控制与任务效益边界 | [SESSION_RESULT_COMMON_PROJECTED_2026-10-08.md](../../innovation/SESSION_RESULT_COMMON_PROJECTED_2026-10-08.md) |
| I109 | 本阶段入口：真实特征成本、下游分割先例与相对收益碰撞 | [SESSION_RESULT_DEPLOYMENT_FEATURE_COST_2026-10-08.md](../../innovation/SESSION_RESULT_DEPLOYMENT_FEATURE_COST_2026-10-08.md) |
| I110 | 本轮结果：三篇原文核读与公平直接稀疏基线资格 | [SESSION_RESULT_DIRECT_OBSERVED_2026-10-07.md](../../innovation/SESSION_RESULT_DIRECT_OBSERVED_2026-10-07.md) |
| I111 | 当前接续结果：最后模型评价入口已资格化，正式训练继续 | [SESSION_RESULT_FINAL_EVAL_PREPARATION_2026-10-07.md](../../innovation/SESSION_RESULT_FINAL_EVAL_PREPARATION_2026-10-07.md) |
| I112 | 本轮接续阅读与创新探索总览 | [SESSION_RESULT_HEAD_CONTEXT_AND_STATISTICS_2026-10-07.md](../../innovation/SESSION_RESULT_HEAD_CONTEXT_AND_STATISTICS_2026-10-07.md) |
| I113 | 本轮结果：增量推断阅读与MRI执行资格 | [SESSION_RESULT_INCREMENTAL_INFERENCE_2026-10-07.md](../../innovation/SESSION_RESULT_INCREMENTAL_INFERENCE_2026-10-07.md) |
| I114 | 低学习率接续阶段结果 | [SESSION_RESULT_LOW_LR_CONTEXT_2026-10-07.md](../../innovation/SESSION_RESULT_LOW_LR_CONTEXT_2026-10-07.md) |
| I115 | 本轮入口：匹配定位空间、共享费用先例与动作价值准备 | [SESSION_RESULT_MATCHED_ORACLE_2026-10-08.md](../../innovation/SESSION_RESULT_MATCHED_ORACLE_2026-10-08.md) |
| I116 | MRI 创新探索：本阶段实际结果 | [SESSION_RESULT_NATIVE_REFERENCE_AND_3D_PREPARATION_2026-10-07.md](../../innovation/SESSION_RESULT_NATIVE_REFERENCE_AND_3D_PREPARATION_2026-10-07.md) |
| I117 | 本阶段入口：合法观测留出特征、原文补读与收益实验准备 | [SESSION_RESULT_OBSERVED_HOLDOUT_2026-10-08.md](../../innovation/SESSION_RESULT_OBSERVED_HOLDOUT_2026-10-08.md) |
| I118 | 本轮入口：文献、冻结预测 ROI 和真实 MRI 输入成本 | [SESSION_RESULT_OBSERVED_ROI_2026-10-07.md](../../innovation/SESSION_RESULT_OBSERVED_ROI_2026-10-07.md) |
| I119 | 本轮结果：公平执行器归档与风险/收益强对照 | [SESSION_RESULT_PAIRED_AND_CALIBRATION_2026-10-07.md](../../innovation/SESSION_RESULT_PAIRED_AND_CALIBRATION_2026-10-07.md) |
| I120 | 可复用患者风险/成本强对照：本轮结果 | [SESSION_RESULT_PATIENT_BASELINE_2026-10-07.md](../../innovation/SESSION_RESULT_PATIENT_BASELINE_2026-10-07.md) |
| I121 | 本轮入口：投影输入解释与自监督原文 | [SESSION_RESULT_PROJECTION_INFO_2026-10-08.md](../../innovation/SESSION_RESULT_PROJECTION_INFO_2026-10-08.md) |
| I122 | 本轮入口：三篇原文与19系列真实支持诊断 | [SESSION_RESULT_REAL_SUPPORT_2026-10-07.md](../../innovation/SESSION_RESULT_REAL_SUPPORT_2026-10-07.md) |
| I123 | 本轮结果：一个新公开稿，强对照算子已验证，两个GPU修复均否定 | [ROUND47_RESEARCH_AND_VALIDATION_RESULT.md](../../innovation/six_resolution_training_preparation_2026_10_09/ROUND47_RESEARCH_AND_VALIDATION_RESULT.md) |
| I124 | 本轮研究结论与真实验证状态 | [ROUND48_RESEARCH_AND_VALIDATION_RESULT.md](../../innovation/six_resolution_training_preparation_2026_10_09/ROUND48_RESEARCH_AND_VALIDATION_RESULT.md) |
| I125 | ROUND50 实际科研结果与资格边界 | [ROUND50_RESEARCH_AND_VALIDATION_RESULT.md](../../innovation/six_resolution_training_preparation_2026_10_09/ROUND50_RESEARCH_AND_VALIDATION_RESULT.md) |
| I126 | ROUND51：论文约束与新的人工数值分支 | [ROUND51_RESEARCH_AND_VALIDATION_RESULT.md](../../innovation/six_resolution_training_preparation_2026_10_09/ROUND51_RESEARCH_AND_VALIDATION_RESULT.md) |
| I127 | 固定2992步匹配空间增强：完整结果 | [FINAL_MATCHED_COMPARISON.md](../../innovation/spatial_adaptation_matched_2026_10_08/FINAL_MATCHED_COMPARISON.md) |
| I128 | 2992个冻结前景采样点的实际结果 | [CENTER_POSITION_FINDINGS.md](../../innovation/task_capacity_mechanism_audit_2026_10_09/CENTER_POSITION_FINDINGS.md) |
| I129 | 动作收益监督目标：已完成的 CPU 资格检查 | [TASK_GAIN_TARGET_CPU_AUDIT_RESULT_2026-10-07.md](../../innovation/TASK_GAIN_TARGET_CPU_AUDIT_RESULT_2026-10-07.md) |
| I130 | 固定三人raw/post统计互换：CPU结果 | [TASK_STATS_SWAP_CPU_PILOT_RESULT_2026-10-03.md](../../innovation/TASK_STATS_SWAP_CPU_PILOT_RESULT_2026-10-03.md) |
| I131 | 本轮结果：任务驱动MRI先例与患者暴露接口 | [RESULT.md](../../innovation/task_utility_patient_exposure_2026_10_08/RESULT.md) |
| I132 | UCSF-PDGM v5 public package: one-case file listing | [UCSF_PDGM_SINGLE_CASE_FILE_LIST_RESULT_2026-10-01.md](../../innovation/UCSF_PDGM_SINGLE_CASE_FILE_LIST_RESULT_2026-10-01.md) |
| I133 | UPENN fixed-denominator sensitivity: result | [UPENN_FIXED_DENOMINATOR_RESULT_2026-10-01.md](../../innovation/UPENN_FIXED_DENOMINATOR_RESULT_2026-10-01.md) |
| I134 | UPENN-GBM tumor-label alignment gate for the DICOM T2 audit | [UPENN_GBM_LABEL_ALIGNMENT_GATE_RESULT_2026-10-01.md](../../innovation/UPENN_GBM_LABEL_ALIGNMENT_GATE_RESULT_2026-10-01.md) |
| I135 | UPENN-GBM processed T2: full-cohort released-plane context audit | [UPENN_GBM_PROCESSED_T2_CONTEXT_RESULT_2026-10-01.md](../../innovation/UPENN_GBM_PROCESSED_T2_CONTEXT_RESULT_2026-10-01.md) |
| I136 | 局部固定动作上限：一个已见开发病例的小幅空间与反证 | [VS_SEG_001_LOCAL_ACTION_ORACLE_RESULT_2026-10-02.md](../../innovation/VS_SEG_001_LOCAL_ACTION_ORACLE_RESULT_2026-10-02.md) |
| I137 | 45 CISS完整结果：原主假设被反证 | [VS_SEG_COMPLETE_EVIDENCE_RESULT_2026-10-03.md](../../innovation/VS_SEG_COMPLETE_EVIDENCE_RESULT_2026-10-03.md) |
| I138 | 固定完整体积队列：全部推断及输出复查结果 | [VS_SEG_FULL_VOLUME_COHORT_COMPLETE_RESULT_2026-10-02.md](../../innovation/VS_SEG_FULL_VOLUME_COHORT_COMPLETE_RESULT_2026-10-02.md) |
| I139 | 原始掩膜门槛已关闭；完整体积预检尚不支持独立 claim | [VS_SEG_ORIGINAL_MASK_AND_FULL_VOLUME_CPU_RESULT_2026-10-02.md](../../innovation/VS_SEG_ORIGINAL_MASK_AND_FULL_VOLUME_CPU_RESULT_2026-10-02.md) |
| I140 | 处理顺序与下游分割：post任务完整45人结果 | [VS_SEG_POST_RESIZE_TASK_CPU_RESULT_2026-10-03.md](../../innovation/VS_SEG_POST_RESIZE_TASK_CPU_RESULT_2026-10-03.md) |
| I141 | 全45处理顺序对照：裁剪未激活，PCHIP顺序效应小于整体处理效应 | [VS_SEG_RESAMPLING_ORDER_CPU_RESULT_2026-10-03.md](../../innovation/VS_SEG_RESAMPLING_ORDER_CPU_RESULT_2026-10-03.md) |
| I142 | 旧四目标筛选的全部112真实端点 | [VS_SEG_SELECTION_SENSITIVITY_REAL_RESULT_2026-10-03.md](../../innovation/VS_SEG_SELECTION_SENSITIVITY_REAL_RESULT_2026-10-03.md) |

另补原始机器结果：

- [innovation/development_capacity_after_matched_2026_10_09/evaluation_attempt01/receipt.json](../../innovation/development_capacity_after_matched_2026_10_09/evaluation_attempt01/receipt.json)
- [innovation/development_capacity_after_matched_2026_10_09/ACTUAL_DEVELOPMENT_EVALUATION_EXIT.json](../../innovation/development_capacity_after_matched_2026_10_09/ACTUAL_DEVELOPMENT_EVALUATION_EXIT.json)
- [innovation/full_certified_schedule_2026_10_09/full_real_terminal_audit_attempt01/receipt.json](../../innovation/full_certified_schedule_2026_10_09/full_real_terminal_audit_attempt01/receipt.json)
- [innovation/adaptive_acquisition_primary_followup_2026_10_09/compact_norm_fullpatch_independent_attempt03/receipt.json](../../innovation/adaptive_acquisition_primary_followup_2026_10_09/compact_norm_fullpatch_independent_attempt03/receipt.json)
- [innovation/gpu_full_fov_and_atomic_capture_2026_10_09/POST_ARCHIVE_HANDOFF_ROUND52_V2.md](../../innovation/gpu_full_fov_and_atomic_capture_2026_10_09/POST_ARCHIVE_HANDOFF_ROUND52_V2.md)


---

## 附录：RASI 候选搜索的全部已有开发数值

原始注册表共 367 个候选，其中 240 个有开发集 nAURC 数值，4 个有冻结验证指标。其余条目没有该表中的开发数值，不冒称已完成评价。下表逐行保留有数值候选，用于查询未入选结果；不是 240 个独立网络。数值显示到小数点后六位，完整精度及状态见原 CSV。

构造依次为 `score_family / mask / voxel_pooling / examination_pooling / committee_type / decomposition / alpha`；开发协议均为原表的 `ixi_x4;fastmri_x2;fastmri_x4;fastmri_x6`。只有 `validated_frozen` 行有验证成绩；其余不填。nAURC 的定义和优化目标沿用 RASI 正文。

来源：[results_registry.csv](../../design/rasinet/results_registry.csv)。

| 候选 ID | 构造 | 开发 mean nAURC | 开发 worst nAURC | 开发 mean ρ | 验证 mean nAURC | 验证 worst nAURC | 验证 mean ρ | 验证 RRR50 | 状态 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| c_c98f4ad5b505 | median / target_0.01 / mean / mean / frozen_primary / — / — | 0.088711 | 0.190620 | 0.905769 | 0.070209 | 0.125224 | 0.901499 | 0.217907 | validated_frozen |
| c_3031c10719f9 | median / committee_union / mean / mean / frozen_primary / — / — | 0.069214 | 0.146839 | 0.916102 | — | — | — | — | not_selected |
| c_e44215c7bc8a | mean / committee_union / mean / mean / frozen_primary / — / — | 0.075840 | 0.158758 | 0.911897 | — | — | — | — | not_selected |
| c_150262917cf3 | trimmed / committee_union / mean / mean / frozen_primary / — / — | 0.069214 | 0.146839 | 0.916102 | — | — | — | — | not_selected |
| c_8da4d84f8cf4 | center_median / committee_union / mean / mean / frozen_primary / — / — | 0.083647 | 0.148369 | 0.904982 | — | — | — | — | not_selected |
| c_b123520799b3 | median / target_0.01 / mean / mean / full_universal / — / — | 0.067843 | 0.191474 | 0.926059 | — | — | — | — | not_selected |
| c_1d0869feee30 | median / target_0.01 / mean / mean / neural_only / — / — | 0.041046 | 0.118150 | 0.950641 | — | — | — | — | not_selected |
| c_345f03e4865c | median / target_0.01 / mean / mean / analytical_only / — / — | 0.139958 | 0.268060 | 0.855095 | — | — | — | — | not_selected |
| c_d73514f23dfd | median / target_0.01 / mean / mean / family_balanced / — / — | 0.090861 | 0.202383 | 0.902960 | — | — | — | — | not_selected |
| c_4d8708178e25 | median / target_0.01 / mean / mean / analytical_anchor / — / — | 0.117092 | 0.242918 | 0.877960 | — | — | — | — | not_selected |
| c_32af676af424 | median / target_0.01 / mean / mean / low_cost / — / — | 0.133269 | 0.268060 | 0.861587 | — | — | — | — | not_selected |
| c_42eb7feb4866 | median / target_0.01 / mean / mean / high_fidelity / — / — | 0.045908 | 0.117313 | 0.940717 | — | — | — | — | not_selected |
| c_2c1382e4d2cf | median / committee_union / mean / mean / full_universal / — / — | 0.075931 | 0.173820 | 0.915015 | — | — | — | — | not_selected |
| c_1314df1ccb32 | median / committee_union / mean / mean / neural_only / — / — | 0.063642 | 0.158730 | 0.927294 | — | — | — | — | not_selected |
| c_5eb7e48d1262 | median / committee_union / mean / mean / analytical_only / — / — | 0.147536 | 0.236570 | 0.848125 | — | — | — | — | not_selected |
| c_0e09a0795acc | median / committee_union / mean / mean / family_balanced / — / — | 0.083619 | 0.194696 | 0.894481 | — | — | — | — | not_selected |
| c_505df316b09b | median / committee_union / mean / mean / analytical_anchor / — / — | 0.112009 | 0.208341 | 0.882669 | — | — | — | — | not_selected |
| c_814b14868330 | median / committee_union / mean / mean / low_cost / — / — | 0.140341 | 0.236570 | 0.859857 | — | — | — | — | not_selected |
| c_f5fed2ef96c3 | median / committee_union / mean / mean / high_fidelity / — / — | 0.040324 | 0.098887 | 0.946959 | 0.115560 | 0.207012 | 0.838509 | 0.199196 | validated_frozen |
| c_49438c6c61b4 | trimmed / committee_union / mean / mean / full_universal / — / — | 0.085531 | 0.184178 | 0.905015 | — | — | — | — | not_selected |
| c_a16a913d6d95 | trimmed / committee_union / mean / mean / neural_only / — / — | 0.069922 | 0.176649 | 0.919468 | — | — | — | — | not_selected |
| c_c0e7eb5ae2e2 | trimmed / committee_union / mean / mean / analytical_only / — / — | 0.147536 | 0.236570 | 0.848125 | — | — | — | — | not_selected |
| c_cbd5209f06dc | trimmed / committee_union / mean / mean / family_balanced / — / — | 0.088451 | 0.195951 | 0.892089 | — | — | — | — | not_selected |
| c_327b438576c6 | trimmed / committee_union / mean / mean / analytical_anchor / — / — | 0.112009 | 0.208341 | 0.882669 | — | — | — | — | not_selected |
| c_11da95167930 | trimmed / committee_union / mean / mean / low_cost / — / — | 0.140341 | 0.236570 | 0.859857 | — | — | — | — | not_selected |
| c_678a6fcecb51 | trimmed / committee_union / mean / mean / high_fidelity / — / — | 0.049378 | 0.098887 | 0.937321 | — | — | — | — | not_selected |
| c_c7af35aec8a7 | center_median / committee_union / mean / mean / full_universal / — / — | 0.080787 | 0.193253 | 0.900779 | — | — | — | — | not_selected |
| c_4bb536f515ec | center_median / committee_union / mean / mean / neural_only / — / — | 0.067060 | 0.165286 | 0.920249 | — | — | — | — | not_selected |
| c_3cda5d63848b | center_median / committee_union / mean / mean / analytical_only / — / — | 0.149068 | 0.236570 | 0.847542 | — | — | — | — | not_selected |
| c_e8419aca8f3f | center_median / committee_union / mean / mean / family_balanced / — / — | 0.089995 | 0.202293 | 0.878994 | — | — | — | — | not_selected |
| c_422d2f34b4ca | center_median / committee_union / mean / mean / analytical_anchor / — / — | 0.117705 | 0.214704 | 0.874502 | — | — | — | — | not_selected |
| c_9f47d44f6f54 | center_median / committee_union / mean / mean / low_cost / — / — | 0.144889 | 0.236570 | 0.858398 | — | — | — | — | not_selected |
| c_4bfd9d7be188 | center_median / committee_union / mean / mean / high_fidelity / — / — | 0.047436 | 0.121371 | 0.938471 | — | — | — | — | not_selected |
| c_e3ee4c1fab55 | mean / committee_union / mean / mean / full_universal / — / — | 0.088305 | 0.174423 | 0.902695 | — | — | — | — | not_selected |
| c_1fff38c414b4 | mean / committee_union / mean / mean / neural_only / — / — | 0.073753 | 0.168407 | 0.919830 | — | — | — | — | not_selected |
| c_582635e9faad | mean / committee_union / mean / mean / analytical_only / — / — | 0.147536 | 0.236570 | 0.848125 | — | — | — | — | not_selected |
| c_4d4502ea3507 | mean / committee_union / mean / mean / family_balanced / — / — | 0.087793 | 0.190705 | 0.893015 | — | — | — | — | not_selected |
| c_a7d0a77ecf68 | mean / committee_union / mean / mean / analytical_anchor / — / — | 0.086662 | 0.158758 | 0.906276 | 0.080241 | 0.165696 | 0.893218 | 0.212194 | validated_frozen |
| c_1d5744ca3912 | mean / committee_union / mean / mean / low_cost / — / — | 0.113888 | 0.236570 | 0.883449 | — | — | — | — | not_selected |
| c_e610d56cbf32 | mean / committee_union / mean / mean / high_fidelity / — / — | 0.053912 | 0.107556 | 0.929391 | — | — | — | — | not_selected |
| c_a4d0b7ae501a | median / target_0.01 / mean / mean / frozen_primary / shared_plus_target_z / 0.0 | 1.086965 | 1.317056 | -0.014471 | — | — | — | — | not_selected |
| c_8999b0a573cf | median / target_0.01 / mean / mean / frozen_primary / shared_plus_target_z / 0.25 | 0.206885 | 0.730974 | 0.746868 | — | — | — | — | not_selected |
| c_895323a5ddab | median / target_0.01 / mean / mean / frozen_primary / shared_plus_target_z / 0.5 | 0.160416 | 0.492648 | 0.818083 | — | — | — | — | not_selected |
| c_b4883bd01e23 | median / target_0.01 / mean / mean / frozen_primary / shared_plus_target_z / 0.75 | 0.128132 | 0.323099 | 0.865770 | — | — | — | — | not_selected |
| c_2974bf70bd3d | median / target_0.01 / mean / mean / frozen_primary / shared_plus_target_z / 1.0 | 0.093494 | 0.190648 | 0.902018 | — | — | — | — | not_selected |
| c_f6629ace487d | median / committee_union / mean / mean / frozen_primary / shared_plus_target_z / 0.0 | 1.124931 | 1.422103 | -0.021319 | — | — | — | — | not_selected |
| c_4ad261cd1d93 | median / committee_union / mean / mean / frozen_primary / shared_plus_target_z / 0.25 | 0.174066 | 0.477749 | 0.780403 | — | — | — | — | not_selected |
| c_bf7eb0f52c23 | median / committee_union / mean / mean / frozen_primary / shared_plus_target_z / 0.5 | 0.107123 | 0.244093 | 0.866087 | — | — | — | — | not_selected |
| c_bf7872e8d858 | median / committee_union / mean / mean / frozen_primary / shared_plus_target_z / 0.75 | 0.085599 | 0.196993 | 0.894280 | — | — | — | — | not_selected |
| c_cc8f1367a4b3 | median / committee_union / mean / mean / frozen_primary / shared_plus_target_z / 1.0 | 0.068738 | 0.172200 | 0.919776 | — | — | — | — | not_selected |
| c_9af2d8c1c6fc | trimmed / committee_union / mean / mean / frozen_primary / shared_plus_target_z / 0.0 | 1.124931 | 1.422103 | -0.021319 | — | — | — | — | not_selected |
| c_8a6e2a9ec7d4 | trimmed / committee_union / mean / mean / frozen_primary / shared_plus_target_z / 0.25 | 0.174066 | 0.477749 | 0.780403 | — | — | — | — | not_selected |
| c_f739417a5661 | trimmed / committee_union / mean / mean / frozen_primary / shared_plus_target_z / 0.5 | 0.107123 | 0.244093 | 0.866087 | — | — | — | — | not_selected |
| c_633d5394d08b | trimmed / committee_union / mean / mean / frozen_primary / shared_plus_target_z / 0.75 | 0.085599 | 0.196993 | 0.894280 | — | — | — | — | not_selected |
| c_9e25c3202ef6 | trimmed / committee_union / mean / mean / frozen_primary / shared_plus_target_z / 1.0 | 0.068738 | 0.172200 | 0.919776 | — | — | — | — | not_selected |
| c_e510e54424fb | center_median / committee_union / mean / mean / frozen_primary / shared_plus_target_z / 0.0 | 1.138093 | 1.270780 | -0.043284 | — | — | — | — | not_selected |
| c_a54eb768abb4 | center_median / committee_union / mean / mean / frozen_primary / shared_plus_target_z / 0.25 | 0.150742 | 0.439749 | 0.830695 | — | — | — | — | not_selected |
| c_fb9207c115af | center_median / committee_union / mean / mean / frozen_primary / shared_plus_target_z / 0.5 | 0.104357 | 0.226098 | 0.882662 | — | — | — | — | not_selected |
| c_1264176a7197 | center_median / committee_union / mean / mean / frozen_primary / shared_plus_target_z / 0.75 | 0.100390 | 0.219636 | 0.893028 | — | — | — | — | not_selected |
| c_686ef5b32872 | center_median / committee_union / mean / mean / frozen_primary / shared_plus_target_z / 1.0 | 0.091772 | 0.176440 | 0.909873 | — | — | — | — | not_selected |
| c_de6240147292 | mean / committee_union / mean / mean / frozen_primary / shared_plus_target_z / 0.0 | 1.142854 | 1.429822 | -0.017819 | — | — | — | — | not_selected |
| c_ee4c7c02b2ce | mean / committee_union / mean / mean / frozen_primary / shared_plus_target_z / 0.25 | 0.188998 | 0.546170 | 0.776692 | — | — | — | — | not_selected |
| c_6f422e8e4d82 | mean / committee_union / mean / mean / frozen_primary / shared_plus_target_z / 0.5 | 0.114848 | 0.357920 | 0.862893 | — | — | — | — | not_selected |
| c_6adcb844759d | mean / committee_union / mean / mean / frozen_primary / shared_plus_target_z / 0.75 | 0.089226 | 0.235447 | 0.900524 | — | — | — | — | not_selected |
| c_b5ad1fa42b1e | mean / committee_union / mean / mean / frozen_primary / shared_plus_target_z / 1.0 | 0.071749 | 0.175593 | 0.915763 | — | — | — | — | not_selected |
| c_0cfcf259fd17 | median / target_0.01 / mean / mean / full_universal / shared_plus_target_z / 0.0 | 1.067876 | 1.345232 | -0.009777 | — | — | — | — | not_selected |
| c_5e2427020254 | median / target_0.01 / mean / mean / full_universal / shared_plus_target_z / 0.25 | 0.214906 | 0.902327 | 0.740491 | — | — | — | — | not_selected |
| c_7fa2ba3d0da2 | median / target_0.01 / mean / mean / full_universal / shared_plus_target_z / 0.5 | 0.147116 | 0.640517 | 0.833011 | — | — | — | — | not_selected |
| c_7c118c91a0cf | median / target_0.01 / mean / mean / full_universal / shared_plus_target_z / 0.75 | 0.103601 | 0.427191 | 0.886929 | — | — | — | — | not_selected |
| c_c62d39eeeee8 | median / target_0.01 / mean / mean / full_universal / shared_plus_target_z / 1.0 | 0.069286 | 0.185410 | 0.925496 | — | — | — | — | not_selected |
| c_536aecc23d42 | median / committee_union / mean / mean / full_universal / shared_plus_target_z / 0.0 | 1.114157 | 1.330505 | -0.002969 | — | — | — | — | not_selected |
| c_41cf5e2fcd2e | median / committee_union / mean / mean / full_universal / shared_plus_target_z / 0.25 | 0.197459 | 0.750758 | 0.757504 | — | — | — | — | not_selected |
| c_73486fec4b9d | median / committee_union / mean / mean / full_universal / shared_plus_target_z / 0.5 | 0.129270 | 0.508083 | 0.828623 | — | — | — | — | not_selected |
| c_f471dd5f2a7b | median / committee_union / mean / mean / full_universal / shared_plus_target_z / 0.75 | 0.085254 | 0.240847 | 0.897251 | — | — | — | — | not_selected |
| c_539c46cf23ff | median / committee_union / mean / mean / full_universal / shared_plus_target_z / 1.0 | 0.073292 | 0.159500 | 0.922167 | — | — | — | — | not_selected |
| c_65ac5ed66029 | trimmed / committee_union / mean / mean / full_universal / shared_plus_target_z / 0.0 | 1.114221 | 1.405081 | 0.003588 | — | — | — | — | not_selected |
| c_bbf3f86b893d | trimmed / committee_union / mean / mean / full_universal / shared_plus_target_z / 0.25 | 0.203243 | 0.698459 | 0.760403 | — | — | — | — | not_selected |
| c_af0526e6a39d | trimmed / committee_union / mean / mean / full_universal / shared_plus_target_z / 0.5 | 0.129520 | 0.410434 | 0.844421 | — | — | — | — | not_selected |
| c_773e5450dafa | trimmed / committee_union / mean / mean / full_universal / shared_plus_target_z / 0.75 | 0.089635 | 0.170389 | 0.898555 | — | — | — | — | not_selected |
| c_d98356cea358 | trimmed / committee_union / mean / mean / full_universal / shared_plus_target_z / 1.0 | 0.086948 | 0.173433 | 0.909993 | — | — | — | — | not_selected |
| c_a349326ce5b5 | center_median / committee_union / mean / mean / full_universal / shared_plus_target_z / 0.0 | 1.096948 | 1.331512 | 0.012270 | — | — | — | — | not_selected |
| c_070a86c8284d | center_median / committee_union / mean / mean / full_universal / shared_plus_target_z / 0.25 | 0.190013 | 0.596484 | 0.765550 | — | — | — | — | not_selected |
| c_1e62f5547e1e | center_median / committee_union / mean / mean / full_universal / shared_plus_target_z / 0.5 | 0.118127 | 0.351390 | 0.844763 | — | — | — | — | not_selected |
| c_6a16945424e8 | center_median / committee_union / mean / mean / full_universal / shared_plus_target_z / 0.75 | 0.095339 | 0.289077 | 0.883898 | — | — | — | — | not_selected |
| c_be8d0b1ed7ab | center_median / committee_union / mean / mean / full_universal / shared_plus_target_z / 1.0 | 0.080982 | 0.198623 | 0.905888 | — | — | — | — | not_selected |
| c_867d0128bb13 | mean / committee_union / mean / mean / full_universal / shared_plus_target_z / 0.0 | 1.096873 | 1.405081 | 0.005106 | — | — | — | — | not_selected |
| c_697c631003d7 | mean / committee_union / mean / mean / full_universal / shared_plus_target_z / 0.25 | 0.213023 | 0.655183 | 0.746402 | — | — | — | — | not_selected |
| c_304e48300b4a | mean / committee_union / mean / mean / full_universal / shared_plus_target_z / 0.5 | 0.139041 | 0.369552 | 0.839559 | — | — | — | — | not_selected |
| c_b7a180775dc0 | mean / committee_union / mean / mean / full_universal / shared_plus_target_z / 0.75 | 0.097763 | 0.166336 | 0.896900 | — | — | — | — | not_selected |
| c_76e1dba29bea | mean / committee_union / mean / mean / full_universal / shared_plus_target_z / 1.0 | 0.091148 | 0.169008 | 0.906271 | — | — | — | — | not_selected |
| c_e9ea0f2a10ca | median / target_0.01 / mean / mean / neural_only / shared_plus_target_z / 0.0 | 1.045226 | 1.354485 | 0.012085 | — | — | — | — | not_selected |
| c_e6ce1eb5807c | median / target_0.01 / mean / mean / neural_only / shared_plus_target_z / 0.25 | 0.227246 | 0.839240 | 0.720478 | — | — | — | — | not_selected |
| c_eea77c9af893 | median / target_0.01 / mean / mean / neural_only / shared_plus_target_z / 0.5 | 0.153457 | 0.686518 | 0.791771 | — | — | — | — | not_selected |
| c_c3566cb7fb2f | median / target_0.01 / mean / mean / neural_only / shared_plus_target_z / 0.75 | 0.103383 | 0.457057 | 0.869277 | — | — | — | — | not_selected |
| c_ea686e5af180 | median / target_0.01 / mean / mean / neural_only / shared_plus_target_z / 1.0 | 0.047369 | 0.138651 | 0.945819 | — | — | — | — | not_selected |
| c_db847568694c | median / committee_union / mean / mean / neural_only / shared_plus_target_z / 0.0 | 1.089283 | 1.299473 | -0.000516 | — | — | — | — | not_selected |
| c_16118cb8b236 | median / committee_union / mean / mean / neural_only / shared_plus_target_z / 0.25 | 0.274521 | 1.145454 | 0.696797 | — | — | — | — | not_selected |
| c_8b0b747d433f | median / committee_union / mean / mean / neural_only / shared_plus_target_z / 0.5 | 0.188313 | 0.835149 | 0.776701 | — | — | — | — | not_selected |
| c_fc50cd2f4105 | median / committee_union / mean / mean / neural_only / shared_plus_target_z / 0.75 | 0.122226 | 0.595874 | 0.857107 | — | — | — | — | not_selected |
| c_a23eb72d9645 | median / committee_union / mean / mean / neural_only / shared_plus_target_z / 1.0 | 0.056616 | 0.142591 | 0.936335 | — | — | — | — | not_selected |
| c_ddf58fa72cdc | trimmed / committee_union / mean / mean / neural_only / shared_plus_target_z / 0.0 | 1.089106 | 1.294685 | 0.007112 | — | — | — | — | not_selected |
| c_eff12a3a6722 | trimmed / committee_union / mean / mean / neural_only / shared_plus_target_z / 0.25 | 0.272203 | 0.883147 | 0.695710 | — | — | — | — | not_selected |
| c_f9cd700a929a | trimmed / committee_union / mean / mean / neural_only / shared_plus_target_z / 0.5 | 0.189620 | 0.695796 | 0.778223 | — | — | — | — | not_selected |
| c_ca862617d390 | trimmed / committee_union / mean / mean / neural_only / shared_plus_target_z / 0.75 | 0.116918 | 0.387480 | 0.858339 | — | — | — | — | not_selected |
| c_aa6396869a6b | trimmed / committee_union / mean / mean / neural_only / shared_plus_target_z / 1.0 | 0.068052 | 0.183723 | 0.924016 | — | — | — | — | not_selected |
| c_1bcac316062c | center_median / committee_union / mean / mean / neural_only / shared_plus_target_z / 0.0 | 1.088649 | 1.345143 | 0.011516 | — | — | — | — | not_selected |
| c_7a53384ef585 | center_median / committee_union / mean / mean / neural_only / shared_plus_target_z / 0.25 | 0.260934 | 0.830545 | 0.710183 | — | — | — | — | not_selected |
| c_ec1da623599f | center_median / committee_union / mean / mean / neural_only / shared_plus_target_z / 0.5 | 0.175384 | 0.653893 | 0.785531 | — | — | — | — | not_selected |
| c_c577bb411f4d | center_median / committee_union / mean / mean / neural_only / shared_plus_target_z / 0.75 | 0.117187 | 0.325281 | 0.852549 | — | — | — | — | not_selected |
| c_7156777ce9d7 | center_median / committee_union / mean / mean / neural_only / shared_plus_target_z / 1.0 | 0.063972 | 0.166434 | 0.926518 | — | — | — | — | not_selected |
| c_29df35cae699 | mean / committee_union / mean / mean / neural_only / shared_plus_target_z / 0.0 | 1.100546 | 1.383117 | -0.004149 | — | — | — | — | not_selected |
| c_a1d9b0e01c0d | mean / committee_union / mean / mean / neural_only / shared_plus_target_z / 0.25 | 0.276831 | 0.875082 | 0.683971 | — | — | — | — | not_selected |
| c_d379d2051556 | mean / committee_union / mean / mean / neural_only / shared_plus_target_z / 0.5 | 0.191428 | 0.745504 | 0.772208 | — | — | — | — | not_selected |
| c_83e2b67cb8ef | mean / committee_union / mean / mean / neural_only / shared_plus_target_z / 0.75 | 0.128237 | 0.456416 | 0.839643 | — | — | — | — | not_selected |
| c_cd4af1539d62 | mean / committee_union / mean / mean / neural_only / shared_plus_target_z / 1.0 | 0.073338 | 0.176493 | 0.923871 | — | — | — | — | not_selected |
| c_f9c68a20222c | median / target_0.01 / mean / mean / analytical_only / shared_plus_target_z / 0.0 | 1.085404 | 1.317056 | -0.047930 | — | — | — | — | not_selected |
| c_f79593d1b6f2 | median / target_0.01 / mean / mean / analytical_only / shared_plus_target_z / 0.25 | 0.198885 | 0.532854 | 0.793041 | — | — | — | — | not_selected |
| c_3ed9502d59c7 | median / target_0.01 / mean / mean / analytical_only / shared_plus_target_z / 0.5 | 0.169241 | 0.411552 | 0.820327 | — | — | — | — | not_selected |
| c_c968a05b71e1 | median / target_0.01 / mean / mean / analytical_only / shared_plus_target_z / 0.75 | 0.152336 | 0.291655 | 0.835563 | — | — | — | — | not_selected |
| c_7193aab3f02d | median / target_0.01 / mean / mean / analytical_only / shared_plus_target_z / 1.0 | 0.134987 | 0.267819 | 0.859885 | — | — | — | — | not_selected |
| c_4e1e9642e468 | median / committee_union / mean / mean / analytical_only / shared_plus_target_z / 0.0 | 1.170313 | 1.374190 | -0.063832 | — | — | — | — | not_selected |
| c_e428b0c17a22 | median / committee_union / mean / mean / analytical_only / shared_plus_target_z / 0.25 | 0.184163 | 0.472777 | 0.799972 | — | — | — | — | not_selected |
| c_01e0ce20c038 | median / committee_union / mean / mean / analytical_only / shared_plus_target_z / 0.5 | 0.159042 | 0.289520 | 0.832469 | — | — | — | — | not_selected |
| c_50c2ffa892f9 | median / committee_union / mean / mean / analytical_only / shared_plus_target_z / 0.75 | 0.143968 | 0.226885 | 0.851813 | — | — | — | — | not_selected |
| c_d887383f8301 | median / committee_union / mean / mean / analytical_only / shared_plus_target_z / 1.0 | 0.147136 | 0.233017 | 0.852831 | — | — | — | — | not_selected |
| c_0b0a40c33a54 | trimmed / committee_union / mean / mean / analytical_only / shared_plus_target_z / 0.0 | 1.170313 | 1.374190 | -0.063832 | — | — | — | — | not_selected |
| c_01b7c40b2788 | trimmed / committee_union / mean / mean / analytical_only / shared_plus_target_z / 0.25 | 0.184163 | 0.472777 | 0.799972 | — | — | — | — | not_selected |
| c_d5df48881b85 | trimmed / committee_union / mean / mean / analytical_only / shared_plus_target_z / 0.5 | 0.159042 | 0.289520 | 0.832469 | — | — | — | — | not_selected |
| c_b6627431580d | trimmed / committee_union / mean / mean / analytical_only / shared_plus_target_z / 0.75 | 0.143968 | 0.226885 | 0.851813 | — | — | — | — | not_selected |
| c_9d591a9ebd7e | trimmed / committee_union / mean / mean / analytical_only / shared_plus_target_z / 1.0 | 0.147136 | 0.233017 | 0.852831 | — | — | — | — | not_selected |
| c_746169dd72d5 | center_median / committee_union / mean / mean / analytical_only / shared_plus_target_z / 0.0 | 1.168544 | 1.362159 | -0.067218 | — | — | — | — | not_selected |
| c_bdf52cb3d47b | center_median / committee_union / mean / mean / analytical_only / shared_plus_target_z / 0.25 | 0.185580 | 0.472777 | 0.800594 | — | — | — | — | not_selected |
| c_852e16f84867 | center_median / committee_union / mean / mean / analytical_only / shared_plus_target_z / 0.5 | 0.161549 | 0.289520 | 0.830974 | — | — | — | — | not_selected |
| c_2ead6dfdc394 | center_median / committee_union / mean / mean / analytical_only / shared_plus_target_z / 0.75 | 0.145756 | 0.230605 | 0.852717 | — | — | — | — | not_selected |
| c_6e389cbd3369 | center_median / committee_union / mean / mean / analytical_only / shared_plus_target_z / 1.0 | 0.148030 | 0.227270 | 0.854931 | — | — | — | — | not_selected |
| c_42f9ea576217 | mean / committee_union / mean / mean / analytical_only / shared_plus_target_z / 0.0 | 1.170313 | 1.374190 | -0.063832 | — | — | — | — | not_selected |
| c_321613fd6e87 | mean / committee_union / mean / mean / analytical_only / shared_plus_target_z / 0.25 | 0.184163 | 0.472777 | 0.799972 | — | — | — | — | not_selected |
| c_977a95875a3c | mean / committee_union / mean / mean / analytical_only / shared_plus_target_z / 0.5 | 0.159042 | 0.289520 | 0.832469 | — | — | — | — | not_selected |
| c_7174cf2782f9 | mean / committee_union / mean / mean / analytical_only / shared_plus_target_z / 0.75 | 0.143968 | 0.226885 | 0.851813 | — | — | — | — | not_selected |
| c_f996039dd7c4 | mean / committee_union / mean / mean / analytical_only / shared_plus_target_z / 1.0 | 0.147136 | 0.233017 | 0.852831 | — | — | — | — | not_selected |
| c_ee529e3c2b9c | median / target_0.01 / mean / mean / family_balanced / shared_plus_target_z / 0.0 | 0.946384 | 1.267245 | 0.138576 | — | — | — | — | not_selected |
| c_f4ba1de56925 | median / target_0.01 / mean / mean / family_balanced / shared_plus_target_z / 0.25 | 0.096843 | 0.204772 | 0.898917 | — | — | — | — | not_selected |
| c_dc950d4444b1 | median / target_0.01 / mean / mean / family_balanced / shared_plus_target_z / 0.5 | 0.097064 | 0.198510 | 0.899428 | — | — | — | — | not_selected |
| c_3c400bb5e564 | median / target_0.01 / mean / mean / family_balanced / shared_plus_target_z / 0.75 | 0.097224 | 0.208124 | 0.900211 | — | — | — | — | not_selected |
| c_fd6513e03a29 | median / target_0.01 / mean / mean / family_balanced / shared_plus_target_z / 1.0 | 0.098909 | 0.198993 | 0.900557 | — | — | — | — | not_selected |
| c_19fb69df0cd2 | median / committee_union / mean / mean / family_balanced / shared_plus_target_z / 0.0 | 1.012480 | 1.362649 | 0.108717 | — | — | — | — | not_selected |
| c_be1cda778b90 | median / committee_union / mean / mean / family_balanced / shared_plus_target_z / 0.25 | 0.085224 | 0.172262 | 0.895817 | — | — | — | — | not_selected |
| c_3fb9a7814671 | median / committee_union / mean / mean / family_balanced / shared_plus_target_z / 0.5 | 0.085844 | 0.176667 | 0.896425 | — | — | — | — | not_selected |
| c_e061e07b4baa | median / committee_union / mean / mean / family_balanced / shared_plus_target_z / 0.75 | 0.088739 | 0.177693 | 0.895144 | — | — | — | — | not_selected |
| c_51074e332d94 | median / committee_union / mean / mean / family_balanced / shared_plus_target_z / 1.0 | 0.088944 | 0.180100 | 0.894780 | — | — | — | — | not_selected |
| c_5ee469ef3f76 | trimmed / committee_union / mean / mean / family_balanced / shared_plus_target_z / 0.0 | 1.016099 | 1.395127 | 0.081163 | — | — | — | — | not_selected |
| c_2f6ff40faa13 | trimmed / committee_union / mean / mean / family_balanced / shared_plus_target_z / 0.25 | 0.091660 | 0.198200 | 0.891035 | — | — | — | — | not_selected |
| c_0754e33ad0b2 | trimmed / committee_union / mean / mean / family_balanced / shared_plus_target_z / 0.5 | 0.092593 | 0.161278 | 0.893817 | — | — | — | — | not_selected |
| c_9537e6ea7286 | trimmed / committee_union / mean / mean / family_balanced / shared_plus_target_z / 0.75 | 0.096593 | 0.173433 | 0.894419 | — | — | — | — | not_selected |
| c_86663733bb2e | trimmed / committee_union / mean / mean / family_balanced / shared_plus_target_z / 1.0 | 0.096623 | 0.178108 | 0.893330 | — | — | — | — | not_selected |
| c_6c381cdd40f2 | center_median / committee_union / mean / mean / family_balanced / shared_plus_target_z / 0.0 | 1.051728 | 1.502441 | 0.099132 | — | — | — | — | not_selected |
| c_53899d41e988 | center_median / committee_union / mean / mean / family_balanced / shared_plus_target_z / 0.25 | 0.097786 | 0.268567 | 0.873211 | — | — | — | — | not_selected |
| c_09c3ef68647f | center_median / committee_union / mean / mean / family_balanced / shared_plus_target_z / 0.5 | 0.093550 | 0.216676 | 0.877792 | — | — | — | — | not_selected |
| c_1035f2acfa91 | center_median / committee_union / mean / mean / family_balanced / shared_plus_target_z / 0.75 | 0.094877 | 0.200643 | 0.877962 | — | — | — | — | not_selected |
| c_0a9ef174d6bc | center_median / committee_union / mean / mean / family_balanced / shared_plus_target_z / 1.0 | 0.096640 | 0.223264 | 0.878161 | — | — | — | — | not_selected |
| c_a8f4348a49f9 | mean / committee_union / mean / mean / family_balanced / shared_plus_target_z / 0.0 | 1.027220 | 1.393967 | 0.082619 | — | — | — | — | not_selected |
| c_118e67a7b766 | mean / committee_union / mean / mean / family_balanced / shared_plus_target_z / 0.25 | 0.092217 | 0.215916 | 0.890633 | — | — | — | — | not_selected |
| c_5391846fd3fd | mean / committee_union / mean / mean / family_balanced / shared_plus_target_z / 0.5 | 0.091684 | 0.165978 | 0.897092 | — | — | — | — | not_selected |
| c_f187d269f514 | mean / committee_union / mean / mean / family_balanced / shared_plus_target_z / 0.75 | 0.092974 | 0.165043 | 0.898929 | — | — | — | — | not_selected |
| c_17668300ce5a | mean / committee_union / mean / mean / family_balanced / shared_plus_target_z / 1.0 | 0.092674 | 0.168115 | 0.898830 | — | — | — | — | not_selected |
| c_9de846a923d8 | median / target_0.01 / mean / mean / analytical_anchor / shared_plus_target_z / 0.0 | 0.949223 | 1.267245 | 0.106389 | — | — | — | — | not_selected |
| c_e7313137603e | median / target_0.01 / mean / mean / analytical_anchor / shared_plus_target_z / 0.25 | 0.120059 | 0.203430 | 0.872975 | — | — | — | — | not_selected |
| c_1bc20fa667bc | median / target_0.01 / mean / mean / analytical_anchor / shared_plus_target_z / 0.5 | 0.121611 | 0.223182 | 0.873124 | — | — | — | — | not_selected |
| c_36724566ff05 | median / target_0.01 / mean / mean / analytical_anchor / shared_plus_target_z / 0.75 | 0.122906 | 0.217587 | 0.871877 | — | — | — | — | not_selected |
| c_cd74ffec1a0f | median / target_0.01 / mean / mean / analytical_anchor / shared_plus_target_z / 1.0 | 0.124122 | 0.218347 | 0.870557 | — | — | — | — | not_selected |
| c_04061a410ee7 | median / committee_union / mean / mean / analytical_anchor / shared_plus_target_z / 0.0 | 1.000027 | 1.311919 | 0.096103 | — | — | — | — | not_selected |
| c_85c6541878f4 | median / committee_union / mean / mean / analytical_anchor / shared_plus_target_z / 0.25 | 0.129221 | 0.223509 | 0.878571 | — | — | — | — | not_selected |
| c_eac3d6cc5a08 | median / committee_union / mean / mean / analytical_anchor / shared_plus_target_z / 0.5 | 0.135692 | 0.222618 | 0.873382 | — | — | — | — | not_selected |
| c_9fb1a2f4824f | median / committee_union / mean / mean / analytical_anchor / shared_plus_target_z / 0.75 | 0.139984 | 0.225668 | 0.872245 | — | — | — | — | not_selected |
| c_65f0be89ab17 | median / committee_union / mean / mean / analytical_anchor / shared_plus_target_z / 1.0 | 0.141079 | 0.225668 | 0.871301 | — | — | — | — | not_selected |
| c_60b92d3c97ab | trimmed / committee_union / mean / mean / analytical_anchor / shared_plus_target_z / 0.0 | 1.000027 | 1.311919 | 0.096103 | — | — | — | — | not_selected |
| c_adda8aadc539 | trimmed / committee_union / mean / mean / analytical_anchor / shared_plus_target_z / 0.25 | 0.129221 | 0.223509 | 0.878571 | — | — | — | — | not_selected |
| c_5275eaa22ca2 | trimmed / committee_union / mean / mean / analytical_anchor / shared_plus_target_z / 0.5 | 0.135692 | 0.222618 | 0.873382 | — | — | — | — | not_selected |
| c_1f0f059964ce | trimmed / committee_union / mean / mean / analytical_anchor / shared_plus_target_z / 0.75 | 0.139984 | 0.225668 | 0.872245 | — | — | — | — | not_selected |
| c_4edf9f3cc5a7 | trimmed / committee_union / mean / mean / analytical_anchor / shared_plus_target_z / 1.0 | 0.141079 | 0.225668 | 0.871301 | — | — | — | — | not_selected |
| c_783a323ce3f2 | center_median / committee_union / mean / mean / analytical_anchor / shared_plus_target_z / 0.0 | 1.000734 | 1.267245 | 0.105051 | — | — | — | — | not_selected |
| c_53734e9cbb9e | center_median / committee_union / mean / mean / analytical_anchor / shared_plus_target_z / 0.25 | 0.133349 | 0.221763 | 0.872051 | — | — | — | — | not_selected |
| c_32bc24f17977 | center_median / committee_union / mean / mean / analytical_anchor / shared_plus_target_z / 0.5 | 0.137223 | 0.225668 | 0.870908 | — | — | — | — | not_selected |
| c_cb3830993376 | center_median / committee_union / mean / mean / analytical_anchor / shared_plus_target_z / 0.75 | 0.139835 | 0.225668 | 0.870644 | — | — | — | — | not_selected |
| c_350d30679337 | center_median / committee_union / mean / mean / analytical_anchor / shared_plus_target_z / 1.0 | 0.142130 | 0.225668 | 0.869320 | — | — | — | — | not_selected |
| c_c6d329a3cf4e | mean / committee_union / mean / mean / analytical_anchor / shared_plus_target_z / 0.0 | 1.008705 | 1.293373 | 0.109423 | — | — | — | — | not_selected |
| c_41a5d2ff2d91 | mean / committee_union / mean / mean / analytical_anchor / shared_plus_target_z / 0.25 | 0.092748 | 0.178386 | 0.906502 | — | — | — | — | not_selected |
| c_9a2443e2c29e | mean / committee_union / mean / mean / analytical_anchor / shared_plus_target_z / 0.5 | 0.096981 | 0.177207 | 0.906657 | — | — | — | — | not_selected |
| c_47b0cf39e551 | mean / committee_union / mean / mean / analytical_anchor / shared_plus_target_z / 0.75 | 0.099763 | 0.177207 | 0.905451 | — | — | — | — | not_selected |
| c_7f003f102c98 | mean / committee_union / mean / mean / analytical_anchor / shared_plus_target_z / 1.0 | 0.109014 | 0.218325 | 0.903903 | — | — | — | — | not_selected |
| c_0c31365217bf | median / target_0.01 / mean / mean / low_cost / shared_plus_target_z / 0.0 | 1.113011 | 1.417247 | -0.031001 | — | — | — | — | not_selected |
| c_4f70e63ff4d4 | median / target_0.01 / mean / mean / low_cost / shared_plus_target_z / 0.25 | 0.217813 | 0.574641 | 0.760531 | — | — | — | — | not_selected |
| c_7518e16610ce | median / target_0.01 / mean / mean / low_cost / shared_plus_target_z / 0.5 | 0.175566 | 0.411552 | 0.815612 | — | — | — | — | not_selected |
| c_784f1d3ff3b5 | median / target_0.01 / mean / mean / low_cost / shared_plus_target_z / 0.75 | 0.145487 | 0.291655 | 0.841523 | — | — | — | — | not_selected |
| c_5651c882a68c | median / target_0.01 / mean / mean / low_cost / shared_plus_target_z / 1.0 | 0.123199 | 0.217027 | 0.871757 | — | — | — | — | not_selected |
| c_998519396080 | median / committee_union / mean / mean / low_cost / shared_plus_target_z / 0.0 | 1.183622 | 1.601137 | -0.088316 | — | — | — | — | not_selected |
| c_0d1517bb9d59 | median / committee_union / mean / mean / low_cost / shared_plus_target_z / 0.25 | 0.225230 | 0.547595 | 0.750208 | — | — | — | — | not_selected |
| c_aa6e6b27d7fc | median / committee_union / mean / mean / low_cost / shared_plus_target_z / 0.5 | 0.176555 | 0.407182 | 0.808325 | — | — | — | — | not_selected |
| c_4ea2df966c03 | median / committee_union / mean / mean / low_cost / shared_plus_target_z / 0.75 | 0.144906 | 0.226688 | 0.860612 | — | — | — | — | not_selected |
| c_37f63af25602 | median / committee_union / mean / mean / low_cost / shared_plus_target_z / 1.0 | 0.139660 | 0.226280 | 0.872751 | — | — | — | — | not_selected |
| c_6bc9eb7da428 | trimmed / committee_union / mean / mean / low_cost / shared_plus_target_z / 0.0 | 1.183622 | 1.601137 | -0.088316 | — | — | — | — | not_selected |
| c_48790c168e15 | trimmed / committee_union / mean / mean / low_cost / shared_plus_target_z / 0.25 | 0.225230 | 0.547595 | 0.750208 | — | — | — | — | not_selected |
| c_4cc9defa9eab | trimmed / committee_union / mean / mean / low_cost / shared_plus_target_z / 0.5 | 0.176555 | 0.407182 | 0.808325 | — | — | — | — | not_selected |
| c_469320079fa4 | trimmed / committee_union / mean / mean / low_cost / shared_plus_target_z / 0.75 | 0.144906 | 0.226688 | 0.860612 | — | — | — | — | not_selected |
| c_b927cbca9bab | trimmed / committee_union / mean / mean / low_cost / shared_plus_target_z / 1.0 | 0.139660 | 0.226280 | 0.872751 | — | — | — | — | not_selected |
| c_d06d2a8d2596 | center_median / committee_union / mean / mean / low_cost / shared_plus_target_z / 0.0 | 1.182530 | 1.587108 | -0.084826 | — | — | — | — | not_selected |
| c_9f316c701e63 | center_median / committee_union / mean / mean / low_cost / shared_plus_target_z / 0.25 | 0.218200 | 0.547595 | 0.758289 | — | — | — | — | not_selected |
| c_37b7ad67406c | center_median / committee_union / mean / mean / low_cost / shared_plus_target_z / 0.5 | 0.175278 | 0.407182 | 0.815182 | — | — | — | — | not_selected |
| c_4faa41718f60 | center_median / committee_union / mean / mean / low_cost / shared_plus_target_z / 0.75 | 0.144529 | 0.232841 | 0.860688 | — | — | — | — | not_selected |
| c_452206226967 | center_median / committee_union / mean / mean / low_cost / shared_plus_target_z / 1.0 | 0.139617 | 0.221058 | 0.872871 | — | — | — | — | not_selected |
| c_4a0c499c17de | mean / committee_union / mean / mean / low_cost / shared_plus_target_z / 0.0 | 1.250100 | 1.665994 | -0.101554 | — | — | — | — | not_selected |
| c_6d011e79f546 | mean / committee_union / mean / mean / low_cost / shared_plus_target_z / 0.25 | 0.285497 | 0.949517 | 0.684666 | — | — | — | — | not_selected |
| c_a00c925daddb | mean / committee_union / mean / mean / low_cost / shared_plus_target_z / 0.5 | 0.189585 | 0.588177 | 0.785296 | — | — | — | — | not_selected |
| c_f0122254521f | mean / committee_union / mean / mean / low_cost / shared_plus_target_z / 0.75 | 0.130018 | 0.406288 | 0.849324 | — | — | — | — | not_selected |
| c_27c5beb86913 | mean / committee_union / mean / mean / low_cost / shared_plus_target_z / 1.0 | 0.088531 | 0.178322 | 0.905497 | — | — | — | — | not_selected |
| c_15eee33c3e87 | median / target_0.01 / mean / mean / high_fidelity / shared_plus_target_z / 0.0 | 1.052089 | 1.346005 | -0.003737 | — | — | — | — | not_selected |
| c_296050611a46 | median / target_0.01 / mean / mean / high_fidelity / shared_plus_target_z / 0.25 | 0.178008 | 0.550052 | 0.781763 | — | — | — | — | not_selected |
| c_2ed793f53423 | median / target_0.01 / mean / mean / high_fidelity / shared_plus_target_z / 0.5 | 0.108090 | 0.351144 | 0.858728 | — | — | — | — | not_selected |
| c_349174e20666 | median / target_0.01 / mean / mean / high_fidelity / shared_plus_target_z / 0.75 | 0.067780 | 0.208159 | 0.907030 | — | — | — | — | not_selected |
| c_2e9043f7e543 | median / target_0.01 / mean / mean / high_fidelity / shared_plus_target_z / 1.0 | 0.045318 | 0.103477 | 0.941177 | — | — | — | — | not_selected |
| c_bbeda0da5d73 | median / committee_union / mean / mean / high_fidelity / shared_plus_target_z / 0.0 | 1.016989 | 1.412198 | 0.025886 | — | — | — | — | not_selected |
| c_234d025114b9 | median / committee_union / mean / mean / high_fidelity / shared_plus_target_z / 0.25 | 0.149306 | 0.606026 | 0.796223 | — | — | — | — | not_selected |
| c_7ac8a786db32 | median / committee_union / mean / mean / high_fidelity / shared_plus_target_z / 0.5 | 0.097575 | 0.411500 | 0.852311 | — | — | — | — | not_selected |
| c_4904646f9686 | median / committee_union / mean / mean / high_fidelity / shared_plus_target_z / 0.75 | 0.064023 | 0.229403 | 0.896626 | — | — | — | — | not_selected |
| c_cc96ad828dc6 | median / committee_union / mean / mean / high_fidelity / shared_plus_target_z / 1.0 | 0.036494 | 0.093291 | 0.951809 | 0.110785 | 0.195357 | 0.847544 | 0.203747 | validated_frozen |
| c_6604024eeabe | trimmed / committee_union / mean / mean / high_fidelity / shared_plus_target_z / 0.0 | 1.062523 | 1.504824 | -0.044359 | — | — | — | — | not_selected |
| c_3a5195d3fcba | trimmed / committee_union / mean / mean / high_fidelity / shared_plus_target_z / 0.25 | 0.224704 | 1.062280 | 0.720498 | — | — | — | — | not_selected |
| c_283eb585e6a3 | trimmed / committee_union / mean / mean / high_fidelity / shared_plus_target_z / 0.5 | 0.156128 | 0.725050 | 0.786441 | — | — | — | — | not_selected |
| c_80f61206634f | trimmed / committee_union / mean / mean / high_fidelity / shared_plus_target_z / 0.75 | 0.102542 | 0.456893 | 0.847061 | — | — | — | — | not_selected |
| c_892a2cd6e686 | trimmed / committee_union / mean / mean / high_fidelity / shared_plus_target_z / 1.0 | 0.045641 | 0.093291 | 0.939345 | — | — | — | — | not_selected |
| c_036b35c69ce2 | center_median / committee_union / mean / mean / high_fidelity / shared_plus_target_z / 0.0 | 1.042284 | 1.505425 | -0.016310 | — | — | — | — | not_selected |
| c_ddb5bc8ee273 | center_median / committee_union / mean / mean / high_fidelity / shared_plus_target_z / 0.25 | 0.223671 | 1.207028 | 0.730246 | — | — | — | — | not_selected |
| c_39f47709221a | center_median / committee_union / mean / mean / high_fidelity / shared_plus_target_z / 0.5 | 0.144763 | 0.810614 | 0.798951 | — | — | — | — | not_selected |
| c_354932729544 | center_median / committee_union / mean / mean / high_fidelity / shared_plus_target_z / 0.75 | 0.090232 | 0.492103 | 0.868587 | — | — | — | — | not_selected |
| c_807d53858560 | center_median / committee_union / mean / mean / high_fidelity / shared_plus_target_z / 1.0 | 0.034343 | 0.094983 | 0.951277 | — | — | — | — | not_selected |
| c_ba7ba5ebc634 | mean / committee_union / mean / mean / high_fidelity / shared_plus_target_z / 0.0 | 1.104369 | 1.629450 | -0.063855 | — | — | — | — | not_selected |
| c_0f0d390ce691 | mean / committee_union / mean / mean / high_fidelity / shared_plus_target_z / 0.25 | 0.238361 | 1.038074 | 0.693217 | — | — | — | — | not_selected |
| c_4b04ed36a5da | mean / committee_union / mean / mean / high_fidelity / shared_plus_target_z / 0.5 | 0.174139 | 0.878256 | 0.764571 | — | — | — | — | not_selected |
| c_9f5c0eca8c14 | mean / committee_union / mean / mean / high_fidelity / shared_plus_target_z / 0.75 | 0.128504 | 0.580879 | 0.827150 | — | — | — | — | not_selected |
| c_d2c6bb17791d | mean / committee_union / mean / mean / high_fidelity / shared_plus_target_z / 1.0 | 0.047363 | 0.083892 | 0.935352 | — | — | — | — | not_selected |


---

## 附录：内部 ResUNet 的多尺度与预算敏感性结果

以下是统一实验主表内 ResUNet 的全部 Markdown 补充行；原生 T2/x4 三数据集行已在前文列出。60-epoch 与标准预算分别记录，不替换主排名。

| 原表分节/协议 | Scale | PSNR | SSIM | MAE | MSE | NCC |
|---|---|---:|---:|---:|---:|---:|
| fastMRI-brain-T2 expanded 多尺度补充（test n=24） | x2 | 24.1700 | 0.7913 | 39.7905 | 6909.6572 | 0.9338 |
| fastMRI-brain-T2 expanded 多尺度补充（test n=24） | x6 | 22.1434 | 0.7375 | 53.8609 | 12277.0333 | 0.8921 |
| NingXia-T2 多尺度补充（8-fold case-level CV） | x2 | 25.2629 | 0.7478 | 76.6937 | 25684.3115 | 0.9170 |
| NingXia-T2 多尺度补充（8-fold case-level CV） | x6 | 22.7683 | 0.7143 | 104.7535 | 42861.1183 | 0.8551 |
| NingXia-T2 60-Epoch 收敛敏感性（补充，不替代主排名） | x4 | 23.7562 | 0.7379 | 90.5450 | 33771.8800 | 0.8876 |
| NingXia-T2 60-Epoch 收敛敏感性（补充，不替代主排名） | x6 | 22.9161 | 0.7281 | 100.4640 | 41591.4635 | 0.8610 |

来源：[experiment_master_table.md](experiment_master_table.md)。
