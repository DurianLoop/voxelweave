# 直接先例补读：dStripe与STRESS

本批实际取得并重点核读2篇新的DOI匹配公开JATS正文，新增PDF为0。原XML、展平正文及实际证据块见[阅读登记](source_cache/phase_direct_neighbour_fulltexts_2026-10-03/reading_provenance.json)。没有复现作者实验、视觉核图或读取supplement。追加三查询返回24条题名记录，两个dStripe版本和两个stomach论文版本不能重复计研究；索引条目不是全文数。

## dStripe：频率约束与slice artefact已有直接方法

*dStripe: Slice artefact correction in diffusion MRI via constrained neural network*，2021，DOI [10.1016/j.media.2021.102255](https://doi.org/10.1016/j.media.2021.102255)。[正文](source_cache/phase_direct_neighbour_fulltexts_2026-10-03/dstripe_maintext.txt)。关键块0011–0016、0026–0034、0040–0048、0051–0065、0068–0090、0102–0106、0114–0129、0140–0153。

它不是直接生成一个任意新MRI体积，而是学习可检查的乘性纠正field。网络保持slice轴分辨率，面内pooling到16×16，再在log-field上面内low-pass、z方向high-pass，约束强度范围，输出field乘回原信号。它明确要保留面内局部contrast，同时去除slice artefact。频率约束、限制修正自由度、可观察的修改field以及跨层一致性不能再作为本项目宽首创。

数据为dHCP multi-shell dMRI：1.5×1.5×3mm，overlap1.5mm，interleave3/shift2，multiband4；原k-space先重建1.5mm各向同性。20训练scans与44评估scans不重叠；32名38–42weeks/质量>20th percentile患者用于population-template，不能将template结果外推到全部质量/年龄。作者另用两名Philips product sequence babies检验迁移，并披露只有66unique volumes时从头训练不稳定，不能简化成“任意小数据均稳健”。

原scanner slice-space和motion-corrected anatomical-space两条控制通过固定motion、slice weights和SHARD basis来区别。作者明确写“这不能证明artefact起源，只比较各空间给定框架下的纠正潜力”（0106）。源空间forward投影及后续SVR会改变局部细节、花费更高；field在anatomical-space平滑并不等于源空间平滑。对本项目，改变anchors的控制也必须保留这一解释边界。

作者特别提醒真实解剖through-plane差异比artefact大1–2数量级，不能直接优化SD作为stripe指标（0044–0046）。其评估为through-plane SD、DTI/MT-CSD fit residuals、跨人模板variance与field bias，未测本项目肿瘤Dice。population平均变化小也不是逐人组织保真保证；corpus callosum邻域变化是否解剖偏差，作者明确保留歧义（0140）。正文限制包括乘性field不能处理跨层unmixing、没有显式tissue依赖等。

SURE部分（0068）先陈述additive同方差Gaussian与weak differentiability的标准条件；实际loss（0076–0079）使用模拟相关乘性slice modulation、绝对值divergence penalty及校准perturbations，不能直接引用标准等式声称本项目动作风险无偏。这与既有[风险假设CPU审计](../RISK_ACTION_ASSUMPTION_CPU_RESULT_2026-10-02.md)一致：需要实际满足noise/observation/mask条件，不能借论文名称替代验证。

训练到推断还改了frequency filter，累积field每轮重新投影约束，处理interpolation artifacts和brain-mask边缘泄漏。rawarray observed-preserving不是它的合同：它本来就修改acquired signal。不能拿其成功直接证实我们的“保持anchors产生带宽相位差”；但它已经构成任何“频率约束slice一致性方法”的强先例。

## STRESS：interleaved SSR与冻结下游任务已有先例

*STRESS: Super-Resolution for Dynamic Fetal MRI using Self-Supervised Learning*，MICCAI2021，DOI [10.1007/978-3-030-87234-2_19](https://doi.org/10.1007/978-3-030-87234-2_19)。[正文](source_cache/phase_direct_neighbour_fulltexts_2026-10-03/stress_maintext.txt)。重点0008、0011、0014–0020、0022–0033、0038–0039。

它把原始各向异性dynamic frames先插值、交换高分辨率x轴与z轴，再模拟interleaved acquisition以产生LR/HR训练对。输入含目标帧及相邻时间帧，EDSR16residual blocks/64channels，L1；可选blind-spot先去噪再生成training target。SMORE对照使用相同网络容量与训练hyperparameters，不能只把更大模型当新slice约束的收益。

合成实验使用21–38GA的已重建1mm CRL atlas，叠加77个运动轨迹×10时间段，共13,860样本；test GA与train/validation不同，但这些不是13,860独立胎儿。真实in-utero EPI共111volumetric time series，92训练/19测试，3×3×3mm、NI2，再每帧移除半数slice变NI4。正文以series分配，不明确patient去重，不能补成111独立患者或声称无共享患者泄漏。

真实评估的reference是被移除的NI2原始层，未获得完全motion-free高分辨率3D真值；可用于该删层合同，不能变成真实薄层reference。更直接相关的是它已经实际将所有SR结果送入相同pretrained fetal keypoint detector，比较15landmark的PCK，并报告STRESS最好（0029–0030）；“冻结下游task验证slice SR”已有直接先例。JATS图注没有给PCK精确数值，本笔记不从图注补造数字。

作者的时序interleave是不同采集时刻，原static3D CISS抽层不是这种temporal条件；不能把邻时帧context搬到本项目而声称新信息来源。推断代码描述对完整重建frame再应用网络，且启用BDN时acquired slices也去噪，并不承诺原anchors逐位不变。表2最后一列标头重复σ3%，而方法文字说1/3/5%，展平表存在标头歧义，本笔记不把最后列独断标成5%结果。

## 新意进一步收窄

| 候选 | 此次直接先例 | 当前可做的更具体工作 |
| --- | --- | --- |
| frequency约束、保持面内contrast、修正slice pattern | dStripe已有网络、loss、field限制及跨人评估 | 不能宽称新方法；区分乘性intensity artefact与本合同的空间blur phase差 |
| interleaved observation/SSR/时序context | STRESS与SMORE已有直接方案 | 本static数据无time context，不能借用temporal证据 |
| 用冻结下游网络评价slice SR | STRESS实际pretrained keypoint实验 | 当前冻结分割响应不能宽称首创，仍需任务/归一化控制 |
| 保持missing数组、只干预anchors，固定task normalization | 本两文未给相同控制；有限查新未足以证明新颖 | 正在运行固定3人12forward开发机制pilot；不把其改变anchors条件当observed-preserving SR |

本阶段共新增5篇重点正文，前3篇与本2篇分别有独立获取/阅读记录，未重计既有论文。当前没有科学独立确认的新claim；需要新的未见患者及第二/适配任务模型，不能用论文数替代。
