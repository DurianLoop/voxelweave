# MRI 自研模型与研究资产交接文档

交接日期：2026-10-23。适用对象：接续模型研究的学生/合作者，以及基于现有结果整理文章的人。工作区为 `D:\MRI`；代码来源快照为 `4a13f383aa0af28467eb8d1ee7693069376d68d8`，原分支 `migration-code-snapshot-20260926`。本次文档交付以该研究快照为基础同步到仓库 `main`。源码快照标识不表示本次又跑了实验；本次未训练模型、未开启保留患者确认、未重算临床效果。

## 1. 接手者先读这四个文件

| 文件 | 用途 |
|---|---|
| [自研模型与baseline梯队筛选](self_model_baseline_tiers.md) | 先看性能、差距与保留名单；同协议下五项指标和梯队 |
| [统一实验主表](experiment_master_table.md) | 已跑baseline的标准T2/x4主表及x2/x6、预算敏感性，保留原文 |
| [完整方法与结果总汇](self_innovation_methods_and_results.md) | 各代PAST、ACSI/RASI/ECSI、MIRA、任务收益探索与全部负结果入口 |
| [机器可读对比表](self_model_baseline_comparison.csv) | 按协议保存baseline与自研完整full记录，便于制作论文表和核算差值 |

证据交付说明与原路径/SHA索引见[交接证据快照](handoff_evidence_20261023/README.md)。文档可访问不等于原始影像和checkpoint已随Git提供；第7—9节明确列出需另行取回的资产。

## 2. 最重要的研究判断与保留名单

**优先保留两条模型路线：PAST成熟G系列的重建性能，ACSI v1的轻量质量折中。** 当前没有自研模型完成三数据集同合同、独立确认后的全面领先。后续的若干PAST结构增量、IXI小波/STC/latent桥接已经产生正式负结果，不能因为文档中还留有启动指令就继续原配置。

| 对象 | 当前证据 | 值得交接的价值 | 当前结论和后续定位 |
|---|---|---|---|
| PAST G086 | fastMRI旧test24：24.446977/.807465/38.289388/7165.787159/.937124 | 最成熟的PAST性能候选；0.992179M参数；空间/FFT双域、四真实锚点、MA3与latent机制可复用 | 对主表I3Net约+.4368dB，但旧test反复开发；保留固定权重，不再在同test追分 |
| PAST G084、G079、G078、G071、G07 | 对应双域、tail、latent、多尺度/优化、宽主干的演进 | 已有连续消融链，可解释G086从何而来；G07另有IXI115 | 精简为有明确变量的消融；不要把所有配置包装成独立创新 |
| PAST G07 | IXI115：29.989239/.915528/19.723950/3291.936051/.973299 | 已有两个域的完整模型记录，帮助识别域间收益差异 | IXI低于I3Net约1.3165dB；fastMRI开发胜出没有自动迁移 |
| ACSI v1 | IXI115：29.390368/.9078左右；完整五指标见筛选表 | 0.344247M参数，14.6843G FLOPs/生成层；轻量分组插值 | 对I3Net PSNR低约1.9154dB，四项3D误差也落后；适合效率论文候选，须补速度和跨域 |
| MA3JF | fastMRI23.973136，0.4140M参数、约61.0523G FLOPs/生成层 | 较小的PAST代表、历史joint-head消融底座 | 不当作最终G086成绩；可保留用于规模/质量权衡 |
| repaired control / wavelet3 | 干净fastMRI validation：25.567453/25.585002 | 修复数据与观测输入合同较明确；全质量方向较一致 | 小波增益+.017549dB，未达原+.10门槛；是研究底座，不是已晋级最终模型 |
| RASI post-hoc / MIRA | 三域可靠性结果、机制干预、多架构与发布层外部审计 | 适合机制/可靠性分析研究，与重建模型论文分线 | 不是新重建器；guard、可行动预测和若干优化失败，低风险认证未成立 |

参数少、FLOPs低和真实速度快是三件事。G086每生成层约148.863G FLOPs，高于I3Net约100.776G；不能因其参数量约少23倍便写“计算量减少23倍”。ACSI复杂度对比也不能直接等同相同倍数的实测加速。

## 3. 研究线、问题定义与代码地图

主任务是**T2 MRI through-plane interpolation**：在z轴每隔s层保留真实观测，恢复中间层；主倍率x4，扩展x2/x6。它不是k-space加速重建；合成抽层、发布层网格、真实厚层/薄层配对是不同数据问题。

| 代码/资料 | 作用 | 接续时先看 |
|---|---|---|
| `baseline/` | ACVTT、ArSSR、CycleINR、GAN、HAT、I3Net、ResSRDiff、SAINT、SMamba、SwinIR等本地复现/适配 | 主表方法定位与各run的配置，不能泛称严格官方复现 |
| [PAST历史总入口](../../design/design1_pastnet/README.md) | 原设计、G系列时间线、失败与消融 | 原始蓝图、experiment ledger、各阶段分析 |
| [fastMRI PAST settings](../../design/fastmri_brain_pastnet_2p5d/settings.py)、[run_all](../../design/fastmri_brain_pastnet_2p5d/run_all.py) | 历史PAST全部profile、训练/推理/评分 | profile、init_checkpoint、累计预算、数据/输出环境变量 |
| [IXI PAST](../../design/ixi_pastnet_2p5d/run_all.py) | G07正式IXI与其它旧profile | G07 full与G086 smoke区别 |
| [ACSI model](../../design/acsinet/model.py)、[settings](../../design/acsinet/settings.py)、[run_all](../../design/acsinet/run_all.py) | 轻量组重建、3D一致性评价 | 48ch/8块、三缺失层组输出、3D尾部与各loss |
| [ACSI v2](../../design/acsinet_v2/model.py) | 四锚点/13层窗口与NCC-profile后续 | 只有小规模结果，v2.1未晋级full |
| [PAST v2](../../design/pastnet_v2/README.md)与[2026-09-24研究汇总](../../design/PASTNET_RESEARCH_SUMMARY_2026-09-24.md) | 修订数据、真实观测归一化、物理/对应/跨视图/方向/小波实验 | 每分支paired gate、质量守卫与停止结论 |
| [IXI wavelet结果](../../design/pastnet_ixi_wavelet/RESULTS_ZH.md) | IXI微调、锁定测试、范围差异定量审计 | 115患者负结果，不重复打开旧test |
| [IXI STC结果](../../design/pastnet_ixi_context/RESULTS_ZH.md) | 四/六锚点容量匹配机制实验 | 80轮各臂完成，但效应门槛失败 |
| [latent bridge协议](../../design/ixi_latent_bridge/PROTOCOL_ZH.md)、[model](../../design/ixi_latent_bridge/model.py) | 冻结I3Net预测/latent与PAST残差混合 | 正式gate已失败；README“待full”属于历史文字 |
| [RASI复现入口](../../design/rasinet/README_REPRODUCE.md)、[nested入口](../../design/rasinet/README_NESTED_REPRODUCE.md) | 无重训的committee可靠性、选择与归因 | 统一support、target-exclusion、外折数据流和修正后的结果 |
| [paper目录](../../design/paper/README.md) | CVPR/TMI内稿、证据升级与MIRA框架 | 不能只读README；后续连续影响扩展更新了部分证据 |
| [innovation范围澄清](../../innovation/RESEARCH_SCOPE_CLARIFICATION_2026-10-07.md) | 后续任务驱动/动作净收益与旧MIRA两线区别 | 旧MIRA有窄外部确认；当前3D任务无保留患者确认 |

`processing/`负责数据准备、case-level CV、评估汇总与权重目录；`pre/`包含旧工程及若干当前入口依赖的公共模块，不能只拷一个model.py就认为能运行。

## 4. 各比较合同必须分别保存

| 合同 | 队列/用途 | 输入、评分与聚合 | 可以比较什么 |
|---|---|---|---|
| 旧统一主表 | IXI test115；fastMRI test24；宁夏8-fold | native-volume评估；旧PSNR每GT层范围；MAE/MSE原始强度；各方法按已有适配实现 | 同一数据集/尺度的历史五指标；不证明训练预算匹配 |
| fastMRI PAST旧开发 | 同test24 | 旧主表式评分；多轮模型搜索；旧数据还有后续识别并隔离的train/val交叉患者 | 展示G系列演进与候选信号；不是pristine holdout |
| fastMRI v2 | 111train/23validation，69interval/207missing | 256²、observed-only min/max、固定range=1、不clamp、series再patient等权；MAE/MSE归一化 | 同预算control及各变量分支；数据修复前/后需分别用control |
| IXI wavelet锁定test | 404train/58val/115test，每方法11001missing | 256²、observed-only范围、clamp[0,1]、患者等权 | 与同合同I3Net固定权重比较；预训练/预算不同仍披露 |
| IXI STC/bridge validation | 58val、5595missing | 每GT层range、clamp，MAE/MSE归一化；两个包还具有各自输入/容量合同 | STC local对extended；bridge blind对latent及同包冻结I3；不是test排序 |
| RASI/committee/MIRA | 对应模型、目标、support、profile | all-pixel/foreground、mean/tail pooling、raw/normalized AURC、patient/series统计对象必须随表给出 | 可靠性/机制端点；不能拿nAURC排重建PSNR |
| 当前3D任务线 | 11开发患者19series、4已见验证9series、8保留确认12series | full-FOV任务、patient-first、同观测/预算/动作及精度资格 | 开发/已见验证描述；8未见患者仍不启用效果 |

IXI相同固定I3Net预测在新range下33.8452dB，折算旧GT范围约31.3057dB；115例原尺寸均256²，主要差异不是分辨率。不能把这种代数改分数写成模型进步。SSIM不能从PSNR汇总值直接换算。

## 5. 数据、划分、来源与暴露状态

| 数据 | 已有规模/目录 | 接手要求 |
|---|---|---|
| IXI-T2 | `dataset/IXI/`；历史可用578 volumes、常用split404/58/115 | 以具体split ID文件为准；该三数之和577，不凭总数自行补病例；保留各阶段资格/排除记录 |
| fastMRI T2 expanded | `dataset/fastMRI_brain_T2/processed/`，160 NIfTI，旧112/24/24 | 依据metadata/splits/nifti_seed3407；v2隔离患者后111/23，不能继续沿用旧角色标成干净独立 |
| NingXia-T2 | `dataset/NingXiaData/`；8患者22T2 series，8-fold病例级CV | 同患者全部series在同角色，报告fold mean；取回权利与数据另行安排，不随Git公开影像 |
| fastMRI修复数据 | [series integrity修复](../../design/pastnet_series_integrity/results/full_review.md) | 原一个32层train混合两个SeriesInstanceUID，拆两个16层、无重采样；1360→1356训练interval；复制修复mapping及派生文件哈希 |
| MIRA外部发布层 | MSValid84/479、ReMIND62完成、UPENN派生T2 374/1496 | 所选源/人工标签/空间/原始或DERIVED/MPR身份不能互换；来源资格不等于临床真值 |
| 当前任务队列 | VS-SEG与后续合格异质高分辨率T2来源 | 原始mask、物理坐标、full-FOV mapping、patient角色和数值资格均须保留；不统称全体CISS |

旧test24已参与大量搜索；IXI wavelet test已用于一次指定探索，不能根据结果继续调参再称原test未触及；validation用来选checkpoint就不是新确认。重新随机划分被长期查看的病例也不会自动生成新的独立研究确认集。

## 6. 已完成、已停止和仅方案状态

| 路线 | 真实完成状态 | 结果/停止原因 | 接手时怎么做 |
|---|---|---|---|
| PAST G086 restart | full完成，best epoch54 | 对G084仅+.004633dB，低于原+.03续训门槛 | 冻结保存；不再加epoch追旧test |
| PAST v2各增量 | 共12个PAST完整配置；另有I3参照及诊断 | geometry/context/crossview/global效应小；orientation有质量代价；wavelet虽方向好仍效应不足 | 对应gate保持失败，作为负结果/底座，三seed未自动启动 |
| IXI wavelet | 80轮、best80、115患者正式评分 | 31.735821 vs I3 33.845219，−2.109398dB，CI全负；3/115胜 | 不启动此候选三seed，不清空结果重跑test |
| IXI STC local/extended | 各80轮；58val | +.0034036dB，CI虽正但不到+.10 | 停止六锚点机制；不得只因p/CI挑更宽模型 |
| I3Net–PAST bridge | blind/latent各80轮，best77/67 | latent−blind+.0000575，调整CI跨0；对I3+.019229仍不到+.10；约9.69倍推理成本 | 已停止；README预登记不覆盖实际gate=false |
| ACSI v1 | IXI test115 full | 轻量且质量竞争，强解剖一致性论点未过 | 作为效率候选继续新实验，而不是保留原最强解剖主张 |
| ACSI v2/v2.1、训练型RASI | smoke/mini，未有有效full成绩 | v2.1一致性门槛未过；RASI full只有配置/空目录 | 不在正式表填“已完成full” |
| ECSI | 实现/静态验收，无实际训练profile结果 | GPU预检当时未过；无质量速度Pareto证据 | 保留代码，不以方案目标当成绩 |
| FAST、SCPI | 设计方案 | 没有独立完成的名称对应结果 | 与后续相近模块区分；不是已验证网络 |
| 部署guard、连续影响外部预测、等信息ensemble、若干动作头 | 真实负结果 | 无可靠部署优势；部分完整队列反证了原假设 | 保存失败，不能从机制正结果转借部署有效性 |

最关键原始判定：[IXI wavelet report](../../design/pastnet_ixi_wavelet/results/test115_seed3407/report.json)、[STC gate](../../design/pastnet_ixi_context/results/gate_seed3407.json)、[bridge gate](handoff_evidence_20261023/source_files/128b49ed3c5b__gate_seed3407.json)。桥接两臂每轮约1890.567/1891.432秒，不是总训练秒数。

## 7. 模型资产、权重与初始化链

以下路径是本地定位，权重本体不推到普通Git。实际存在性、字节数与SHA-256见[checkpoint库存](handoff_evidence_20261023/checkpoint_inventory.csv)。库存仅核文件，不表示重新加载或重验医学效果。

| 模型 | 代码包 | 正式run/权重位置 | 依赖/选择 |
|---|---|---|---|
| G086 | `design/fastmri_brain_pastnet_2p5d` | `runs/full_pastnet_g086_dual_restart60/checkpoints/pastnet_epoch_best.pth` | 延续G084/G079历史初始化；还需manifest的累计训练预算、EMA选择与history |
| G084、G079 | 同上 | 各自`full_pastnet_g084_dual_domain140`、`full_pastnet_g079_tail_aware160`下同名best | 不能随机从头训练一个同名结构就当历史等预算复现 |
| MA3JF | 同上 | `runs/full_ma3jf_150/checkpoints/pastnet_epoch_best.pth` | 保存独立profile及init链 |
| IXI G07 | `design/ixi_pastnet_2p5d` | `runs/full_g07_ma3_wide200_test115/checkpoints/pastnet_epoch_best.pth` | 与fastMRI G07是不同训练实例 |
| ACSI v1 | `design/acsinet` | `runs/full_test115/checkpoints/acsinet_epoch_best.pth` | 30epoch、48ch、8blocks、z_refine_channels8、batch6×accum4，best而非随意final |
| fastMRI wavelet3 | `design/pastnet_wavelet_trunk` | `runs/full_wavelet3_seed3407_vram20/best.pth` | 从G086及修复数据control发展；对应代码vendor及640gate变化 |
| IXI wavelet3 | `design/pastnet_ixi_wavelet` | `runs/full_wavelet3_ixi_seed3407/best.pth` | 固定fastMRI小波权重微调；还需`manifest/history/completion`和test lock |
| IXI STC | `design/pastnet_ixi_context` | `runs/full_local_seed3407/best.pth`、`full_extended_seed3407/best.pth` | 同固定IXI小波初始化，两臂匹配，不能只交extended |
| latent bridge | `design/ixi_latent_bridge` | `runs/full_blind_seed3407/best.pth`、`full_latent_seed3407/best.pth` | 同时依赖冻结I3Net；总部署24,207,169参数，而非只算bridge约1M |

接手者还需取得**baseline实际权重**，尤其IXI的`full_test115_stable` I3Net、fastMRI I3Net、HAT/SwinIR等及宁夏每fold。模型名和论文名不能替代checkpoint身份。保存`best`、`final`、`last`各自含义；断点恢复需优化器、scheduler、EMA、scaler、RNG和已提交epoch，而仅推理通常用best。

### 既有主表权重包

本地已有 `exports/experiment_master_table_weights_2026-09-20.zip`，验证报告记大小7,100,188,153 bytes、458个权重、3598内容文件逐哈希核验、CPU加载校验PASS，SHA-256为 `248f785ccbdc1d16218f33d726cd5e1e673ab5a65401db7aa6ad04b6290944d9`。另有4个独立分包和[分包校验报告](../../exports/experiment_master_table_weights_2026-09-20_parts/split_validation_report.json)。

目录与定位见[权重包说明](../../exports/experiment_master_table_weights_2026-09-20/README_ZH.md)、[checkpoint目录](../../exports/experiment_master_table_weights_2026-09-20/CHECKPOINT_CATALOG_ZH.md)、[checkpoint索引](../../exports/experiment_master_table_weights_2026-09-20/checkpoint_index.csv)、[完整验证报告](../../exports/experiment_master_table_weights_2026-09-20/validation_report.json)。这是2026-09-20时点的包，不能假设包含之后IXI wavelet/STC/bridge；必须按本次库存另行交接新增权重。压缩包在本地存在，不表示已建立GitHub Release或云端下载链接。

## 8. 环境与第一次安全复现

训练环境建议从[environment.yml](../../environment.yml)和[requirements.txt](../../requirements.txt)起步：Python3.12、numpy<2、SciPy、scikit-image、nibabel、PyTorch CUDA12.8源等。原解释器为 `D:\conda\envs\MRI\python.exe`。这不是精确的全环境lock，换硬件/新PyTorch版本不能保证逐bit相同；需记录torch/CUDA/cuDNN、驱动、AMP/BF16/FP32和determinism设置。

```powershell
git clone https://github.com/DurianLoop/voxelweave.git
Set-Location voxelweave
conda env create -f environment.yml
conda activate MRI
$researchRepo = (Get-Location).Path
$env:PYTHONPATH = "$researchRepo\pre;$researchRepo\baseline;$researchRepo\design;$researchRepo"
python processing/verify_research_handoff.py
python -B -m fastmri_brain_pastnet_2p5d.run_all --help
python -B -m acsinet.run_all --help
```

这是接手方的操作说明，本次交接只执行只读文档/证据核对，没有运行上述训练入口。`--help`用于确认参数；如果模块导入就缺依赖，先处理该依赖，不把错误归咎于模型。

**先核资产，再核小样本，然后重放完整固定评价。** 顺序为：源码版本与checkpoint哈希→split ID/资格→预处理tensor与观测网格→单病例预测与输出范围→同合同指标→逐患者表与最终均值。各阶段留存容差与失败；GPU/CPU浮点差异不应被修改统计端点掩盖。

历史`run_all.py`会准备并清理输出，`--eval-only-checkpoint`仅免训练，**不意味着不写文件**。不要直接对原run重复调用。PAST可在设置中用`FASTMRI_BRAIN_PASTNET_RUN_ROOT`指向全新输出根；ACSI/旧IXI部分路径没有同类override，需在隔离checkout恢复数据并使用新的profile/目录。不要覆盖当前D盘已保存的预测/metrics。

以下仅说明准确的eval-only接口，**限隔离副本、新输出目录、split/数据已核实后执行**：

```powershell
# 在隔离checkout中；此根此前不存在。
$env:FASTMRI_BRAIN_PASTNET_RUN_ROOT = "$researchRepo\design\fastmri_brain_pastnet_2p5d\runs\handoff_replay_20261023"
python -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g086_dual_restart60 --eval-only-checkpoint D:\MRI\design\fastmri_brain_pastnet_2p5d\runs\full_pastnet_g086_dual_restart60\checkpoints\pastnet_epoch_best.pth
# ACSI也只能在没有历史同名run的隔离副本中调用该接口。
python -B -m acsinet.run_all --profile full_test115 --eval-only-checkpoint D:\MRI\design\acsinet\runs\full_test115\checkpoints\acsinet_epoch_best.pth
```

PAST数据入口支持`FASTMRI_BRAIN_PASTNET_DATA_ROOT`；[settings.py](../../design/fastmri_brain_pastnet_2p5d/settings.py)默认指向`dataset/fastMRI_brain_T2/processed`，依赖metadata和split，而不是只需NIfTI。Windows脚本中部分Python路径固定D盘；迁移机器须在新副本中记录路径适配，不能改历史代码哈希后继续称原冻结执行。

RASI快速重算命令在[README_NESTED_REPRODUCE.md](../../design/rasinet/README_NESTED_REPRODUCE.md)，`from-precomputed`仍需其atomic/features/outer predictions等CSV，普通Git忽略的`outputs`未必齐全。先取得完整预计算交付再运行；否则不能将空目录、smoke或不全表当原161-examination benchmark。其端到端模式还需所有预测体积和世界坐标匹配。

## 9. Git能提供和不能提供的东西

| 类别 | 本次交付 | 接手者额外取回 |
|---|---|---|
| 代码/协议/已跟踪科研报告 | 同步研究代码快照及新交接入口 | 原论文引用与许可证照来源文件执行 |
| 标准baseline表、full比较CSV、候选判定 | 随Git；原始主表保持字节不变 | 如需全精度逐患者差值，另取底层逐例metrics |
| Git忽略但被文档引用的轻量汇总 | 尽量复制原字节到`handoff_evidence_20261023/source_files`，保留源路径/SHA | 不是完整run，不能据此复现所有图像/统计 |
| 影像、稀疏输入、预测NIfTI/NPZ、cache | 不随普通Git | 原始数据权利、存储位置、处理/修复版本、ID表、affine/header |
| `.pth/.pt`、optimizer/EMA/RNG | 不随Git；提供本地库存与已有包索引 | best/final/last实际文件，传输后逐哈希核对 |
| 逐患者/切片明细、大表、部分目录 | 可能为本地资产；链接指向可用性索引 | 向原维护者取回；宁夏临床资料不可按公开索引直接取得 |
| 当前未见确认队列 | 角色/协议记录 | 沿既有冻结合同管理；本次没有打开效果 |

因此GitHub可用于接手代码、查看结果和准备文稿；完整端到端复现还依赖本地资产。文件索引有路径或哈希不等于下载地址，不能向合作者宣称“一次clone即可复现全部医学结果”。

## 10. 后续做模型：建议的最短研究路径

### A. 以PAST为主模型

1. 冻结G086/G084/G079/G07、MA3JF及其profile，不再在旧test24做结构搜索。完成相同真实观测、患者划分、归一化、有效上下文、budget与checkpoint选择的最小对照协议；旧结果保留为探索。
2. 优先建立同合同强I3Net参考。v2本地I3随机初始化、PAST继承历史权重且loss/累计预算不同，旧的+0.389879不能当匹配结构优越性。核查修复版完整I3参照是否实际completed，再决定新训练，不能只读旧“待full”。
3. 新假设必须有一项能改变结论的主变量与相应同容量/同信息对照；先做能力/机制小检验，再按预写效应、置信区间、困难患者和全部质量守卫决定是否full。原失败路线不通过重新降低门槛被追认为成功。
4. 固定方案后再补2027/9103等训练seed、fastMRI独立患者、IXI及宁夏病例级外部验证；若初始化固定，称适配seed而非完全从头独立训练。所有额外训练在新目录，不能让历史test反复承担确认。
5. 统一效率合同，报告每缺失层/每case、IO是否计入、batch、volume深度、精度、显存峰值及warmup；保留参数/FLOPs定义和预训练累计成本。

### B. 以ACSI为轻量模型

先复核现有IXI115完整结果和3D比较，再测同设备真实吞吐/显存；补fastMRI及宁夏新配置。主目标可设质量–成本Pareto，而非强行胜过I3Net全部质量。ACSI v2.1过度相关/NCC-profile未改善的反例须保留，不用“更平滑”代替解剖正确。若后续想主张临床结构收益，需可靠同空间标注/冻结任务网络与充分任务能力，而非强度阈值proxy。

### C. 机制/任务研究

MIRA外部MSValid84人单配对ΔO确认仍有效；ReMIND/UPENN是发布层上下文跟进，不能当原始独立扫描身份。连续影响的外部可行动预测、等信息ensemble和guard已失败。继续研究应提出超越这些反证的新假设；当前3D任务线先解决完整FOV能力/泛化与强augmentation控制，不在弱任务网络上给SR方法下临床结论。

## 11. 基于现有结果写文章：可用路线与不可越过的证据边界

| 路线 | 已能写的内容 | 必须披露/目前缺口 | 当前写作成熟度 |
|---|---|---|---|
| PAST性能方法稿 | 四锚点rich conditioning、宽MA3、latent/tail/双域消融、fastMRI性能和IXI G07迁移差异 | test24反复开发、训练预算/初始化不等、宁夏自研CV缺失、跨域最强I3仍领先 | 能写完整草稿/技术报告；独立泛化与SOTA论点仍须新证据 |
| ACSI效率稿 | 轻量组预测、模型复杂度、IXI115质量、3D误差比较与负结果 | 没有同设备真实速度和跨域；解剖一致性不胜I3Net | 可写方法与结果初稿，效率主张需实测完成 |
| RASI可靠性/选择稿 | post-hoc分歧、target排除、mask/pooling敏感性、nested选择的正负结果 | 早期all-pixel背景效应；NingXia22series仅8患者；选择/数据泄漏审计；若干优化负迁移 | 有大量现成结果，但必须依据修正后CSV重组，不能直接沿旧摘要数字 |
| MIRA机制/审计稿 | 共享测量误差可见性、有限响应影响、条件协方差、真实同目标控制和MSValid窄外部确认 | 解析控制可有更大效应；内容/几何共变；非校准风险证书；guard/外部预测失败 | 已有较完整内稿与证据链，适合据当前真实边界改写；不等于已投稿/已接收 |
| 任务驱动/动作净收益稿 | 能力、ROI、归一化、增强、full-FOV和资源资格的系统负结果 | 8保留确认未开、同预算净收益无确认、任务泛化不足 | 可整理研究报告；不能宣称成功新方法或临床净收益 |

### 可直接使用但需保留范围的结果表述

- “在既有fastMRI T2开发评估中，PAST G086相对本地I3Net复跑的PSNR高约0.437dB，并改善其余四项核心指标；该评估已多轮用于开发，因此作为探索性结果报告。”
- “ACSI v1在IXI-T2 115例评价中取得29.390dB，使用约0.344M参数；其质量低于I3Net，支持研究轻量质量折中，而非全面优越性。”
- “固定模型对在MSValid84名患者上的发布层上下文切换增加误差可见性；这一窄审计结果不证明原始采集身份的独立因果效应或患者诊断收益。”

不得写：“PAST三域SOTA”“桥接已经超过I3且机制成功”“ACSI解剖最一致”“MIRA低分等于安全”“22名宁夏独立患者”“所有baseline严格官方复现”“参数减少即同倍加速”。

### 现有稿件与图表入口

| 入口 | 使用方法 |
|---|---|
| [CVPR main.tex](../../design/paper/CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.tex) | 当前MIRA框架稿基础，结合后续证据扩展和外部审计更新，不照搬过时结论 |
| [Plan17最终报告](../../design/paper/PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/FINAL_REPORT_ZH.md) | 主张、guard失败、共享协方差与去自比较修正的完整解释 |
| [连续影响大表](../../design/paper/CONTINUOUS_INFLUENCE_EXPANSION/CONTINUOUS_INFLUENCE_BIG_TABLE.md) | 8实现/16单元的最新系统结果，14通过、ACVTT稳定性失败保留 |
| [TMI目录说明](../../design/paper/TMI/README.md) | 对应独立内稿/历史版本，不能假设与CVPR全部同步 |
| [RASI nested修正报告](../../design/rasinet/revision_report_nested_optimization.md) | 用统一支持/归因/外折的修正结论重建稿件表，不拿早期unfair排名做结论 |
| [公共MIRA内部稿](../../innovation/PUBLIC_ONLY_MIRA_MANUSCRIPT_DRAFT_2026-10-01.md) | 后续外部来源与先例边界，仍须结合最终review及新控制 |

建议论文核心表：①同协议主性能表（未完成自研域留NA）；②参数/FLOPs/实测时间及预算；③关键单变量消融；④固定模型的跨域/seed/困难患者；⑤可靠性或3D结构补充。建议图：固定规则选例的轴位/矢状/冠状、共同色标误差图、病例配对差分、质量–成本曲线；用实际数组，不能选最优例掩盖失败。没有数据的图先标待生成，不用合成MRI代替实证。

## 12. RASI/MIRA与后续任务线的特别交接

旧MIRA在MSValid84/479上的预先冻结单配对ΔO为+19.7565个百分点、患者CI[19.3276,20.1605]，84/84同向；这是项目已有外部确认，不能因当前任务线“科学确认0”抹掉。另一方面，MSValid后续60患者连续影响预测未优于精确几何基线，ReMIND同信息ensemble优势区间跨0，部署guard未可靠优于基线；不能以主ΔO正结果替这些失败背书。

当前任务共同初始化两臂各19998updates已完成，2992步匹配增强四臂的开发/已见验证完整FOV也已完成。部分旧handoff中的live/12652仍运行是历史状态。以实际receipt、exit和最终summary为准；高开发拟合/低已见验证只能描述泛化差，不能凭差值判定病因。8名未见确认患者/12series仍关闭，head-only LOPO不能绕过parent task已看过全部开发GT的问题。

RASI已有一项数据一致性问题：旧文字称完整ICASSP benchmark为161 examinations/504组/33672行，但当前`outputs/icassp_full_benchmark/summary.csv`仅236行且cases=2，不能按旧说明给完整主结果作证。早期三队列post-hoc完整汇总和nested修正CSV独立存在；分别核读，不以smoke覆盖旧文或以旧文补造当前缺失产物。

## 13. 接手顺序与交付验收

| 阶段 | 接手者完成的具体产物 | 完成标准 |
|---|---|---|
| 第一次阅读 | 阅读四入口与本文件；复述R1名单、合同差异、停止项 | 能说明G086开发胜出、ACSI轻量价值、为何bridge未晋级 |
| 资产接收 | 影像/split/修复mapping/best-last-EMA/预测/逐例metrics清单 | 对照库存与源SHA，缺项显式列出，不自动从目录名推断完成 |
| 只读复核 | 文档验证、单病例tensor/预测、主表/CSV数值 | 同合同聚合一致，差异附范围/精度与病例原因 |
| 选研究路线 | 固定PAST或ACSI主线，或单独MIRA分析线 | 写主问题、唯一主终点、强对照、预算、晋级/停止与未见评价入口 |
| 写作路线 | 可追溯表/图/claim-evidence map及negative appendix | 每结论能定位原表、协议和checkpoint；草稿不承诺不存在的确认 |
| 新实验 | 新目录、新manifest、新代码标识与实际exit/completion | 运行成功、数值资格和科学门槛分别判定；按预写规则决策 |

若只写现有文章而不新训练，优先整理真实claim、统一各表单位、找回逐例数据和固定模型图、披露所有限制。无法凭排版填补三域/多seed/独立患者确认缺口；保留NA和负结果比补造结果更适合后续科研接力。

## 14. 本次交接核验与维护

本次仅新增筛选/交接/轻量证据快照，更新总汇的阅读入口并保留其完整历史；原`experiment_master_table.md`的SHA-256仍为 `9a4c78ab4e0bfff11152684ea1ba5a7d206f8835e05e2c61d384497a0c485dfe`。未重新训练、未重开test或确认患者、未把本地影像和模型权重放进普通Git。

核验命令为 `python processing/verify_research_handoff.py`；它检查文档链接、表格、UTF-8、快照哈希、关键差值和full配置数量。它是交接完整性检查，不是新的科学复现或医学验证。后续新增实验应更新筛选表、比较CSV、资产索引和相关claim状态；保留旧gate与旧数值，不覆盖失败记录。
