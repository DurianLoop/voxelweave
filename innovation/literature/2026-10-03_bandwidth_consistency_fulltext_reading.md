# 本轮三篇正文：重采样损失、下游量化和层间一致性的直接先例

实际取得并重点核读3篇经DOI身份核对的公开JATS正文，新增PDF为0。五查询返回18题名记录、17不同规范化题名；这不是18篇全文阅读。重点证据块、原始XML和哈希见[阅读登记](source_cache/bandwidth_consistency_fulltexts_2026-10-03/reading_provenance.json)，索引返回见[获取记录](source_cache/bandwidth_consistency_search_2026-10-03/attempt_01.json)。只读相关正文/展平公式、表格、图注，没有视觉核图或补充材料，也没有复现作者训练或采集实验。

## Lazy Resampling

*Lazy Resampling: Fast and information preserving preprocessing for deep learning*，2024，DOI [10.1016/j.cmpb.2024.108422](https://doi.org/10.1016/j.cmpb.2024.108422)。[本地正文](source_cache/bandwidth_consistency_fulltexts_2026-10-03/lazy_resampling_maintext.txt)。核心块0024、0028–0029、0034–0042、0074、0091–0095、0101–0103、0109–0116、0121–0132、0138、0141–0155。

方法将空间变换描述累积为pending operations，尽可能组合成一次resample。需要图像值的非lazy变换、采样模式或dtype不兼容时，必须执行中间resample；不能声称任意数据依赖非线性操作都能无损合并。作者专门保留flip/90°等准确tensor操作，避免把数学上可消去的变换也强行插值。当前grid变换与noise的lazy链还有实现限制。

MSD脑肿瘤有484已标注体积，四对比已重采样1mm，并非原始薄层采集；hippocampus有263已标注T1 MPRAGE。forward/roundtrip实验与任务训练分开：标签nearest-neighbor roundtrip的whole/tumour-core/enhancing Dice从.694/.520/.598变成lazy的.911/.819/.871。那是标签信息退化实验，不能当网络的预测Dice。

任务部分固定相同初始权重、采样顺序、随机增强和学习日程，残差UNet在5fold运行，brain注明每fold75、hippocampus每fold52。正文没有解释brain每fold75与484总标签的具体筛选映射，不能自行补成484全参与任务训练。作者累计25对成功训练，披露不稳定种子/运行问题；报告的是best validation scores，不能改称完全独立test表现。表3的mean validation Dice为brain .7400→.7522、hippocampus .8954→.9135；配对t作者p<1e−9，未由本项目复现。

熵结果只能说明作者选定的256bin边缘强度分布统计；单一Shannon entropy高低不是对解剖信息损失的完备证明。本文已经直接覆盖“减少多次重采样、降低图像/标签失配并改善分割训练”，本项目不能用这种宽主张命名创新。其lazy composition不直接解决值依赖PCHIP与空间平均交换问题；我们的raw PCHIP仍是必需强对照，不能只比传统pipeline。

## 真实2D/3D配对MRI下的量化形态学

*Machine learning-based reconstruction of 2D MRI for quantitative morphometry in epilepsy*，2025，DOI [10.1162/imag.a.997](https://doi.org/10.1162/imag.a.997)。[本地正文](source_cache/bandwidth_consistency_fulltexts_2026-10-03/epilepsy_morphometry_maintext.txt)。重点块0042–0044、0048、0051、0058–0063、0066、0069、0073、0079、0084、0088–0095、0107–0128。

实际分析112人：31药物敏感IGE、42药物抵抗IGE和39对照；最初33名敏感IGE的2人排除不能继续计最终114。GE MR750同scanner、同session获得3D T1-FSPGR-PURE（.9×.9×1mm）与2D T1-FLAIR（.4×3×.4mm）。这是真实配对采集，却同时改变sequence/contrast，不能隔离成纯粹through-plane分辨率因果实验。

作者比较未处理2D、NiBabel conform且HD-BET skull-strip的res-T1、SynthSR生成1mm MP-RAGE、DL+DiReCT，并比较FreeSurfer recon-all与recon-all-clinical。res-T1不是只改interpolation核，已经包含其他处理；FSL subcortical分支还有N4、BET、MNI注册和run_first_all。3D-T1分割是silver standard，不是ex-vivo或肿瘤人工真值。174区域需合并/删除部分atlas定义，再rigid注册并最近邻映射到3D参考，Dice受这条评估链影响。

表1的RA cortical Dice为未处理2D .69、res .70、SynthSR .58；cortical-volume ICC .80/.80/.61，thickness ICC .56/.58/.24。高低并非所有下游量一同变化；RC显著降低某些thickness离群，其他ICC/DSC并未一概改善。正文0077的若干括号数值与表1的z-score列一致，虽然段落称ICC，不能将−.38等抄成ICC；本笔记用表1有标头的值。

作者对shape采用5000permutation和TFCE，但不在不同结构/图像类型之间做整体多重检验修正。“false positive/negative”按3D silver-standard显著图定义，不能当经病理证实的临床错误；一个图像type不显著也不是证明无效应。作者明确披露res-T1的run_first_all注册错误可能贡献所谓false positives（0120），DL+DiReCT并不宣称适用于这种各向异性输入（0114），不能把本结果作为该模型原用途失败的证明。

对MRI项目：下游量化的负效应、未经处理基线可能更好和模型输入暴露都已有直接证据。值得借鉴的是跨输入×跨任务pipeline矩阵和完整失败披露。本45CISS不能凭冻结模型Dice把重建变化直接称临床伤害；更需要把网络暴露、全volume归一化与真实局部解剖变化分开。

## 动态声道：清晰度、SNR和层间一致性取舍

*Super-Resolved Dynamic 3D Reconstruction of the Vocal Tract during Natural Speech*，2023，DOI [10.3390/jimaging9100233](https://doi.org/10.3390/jimaging9100233)。[正文](source_cache/bandwidth_consistency_fulltexts_2026-10-03/vocal_tract_maintext.txt)。核心块0010、0014–0017、0020–0021、0030、0035–0039、0049–0056、0060–0067、0081。

只有2名志愿者，radial 2D FLASH、1.6×1.6mm面内/8mm厚层，多个1.6mm偏移的重叠采集，通过音频PCA/DTW和nose ROI刚体注册后求解带blur/downsample/shift的逆问题。不是本项目从同一次3D CISS中四层抽取的观测合同。两个speech protocol分别用于两个不同人，protocol与个体混杂，不能视为同人随机交叉验证；每人1500多重建图像也不能等同1500独立患者。

Tikhonov/Beltrami参数在少量图像上选；作者报告Beltrami清晰度高于Tikhonov，但两者仍低于原2D，SNR则反向：S1原2D76.3、Tikhonov95.0、Beltrami81.0，S2为47.1/58.5/55.7。Canny边缘沿slice曲线拟合的残差S降低用于量化slice smoothness；这不是病灶保真指标，也不等于bandwidth均匀。作者关于自动segmentation只是潜力/未来工作，没有实际Dice验证（0063–0067），不能补造下游分割成功。

它已经覆盖用空间regularization改善层间连续性同时损失清晰度；本项目不能把“一致性与清晰度取舍”当宽首创。它没有直接检验observed-preserving稀疏合同中的面内梯度能量相位模式，也没有相同缺层数组/只改变anchors的对照。

## 对当前项目的具体决策

| 候选说法 | 直接先例/本项目反证 | 本轮动作 |
| --- | --- | --- |
| 减少重复插值有利分割 | Lazy Resampling、VINNA已经直接覆盖 | 强对照与相关工作，放弃宽首创 |
| SR图像指标改善不保证任务收益 | 形态学及既有任务论文直接覆盖；原HAT负向主张已被项目反证 | 原claim继续停止，不能换标签/基线挽救 |
| order差可用作简单部署风险信号 | 本轮全45固定order_rms、180旧数组/6规则/5000随机复核后失败 | 停止固定候选，保留CSV与全部反例 |
| anchors清晰/缺层经面内处理造成相位差 | 当前是待测具体解释，本文献不提供相同控制的证实；未找到不代表首创 | 固定45无神经解析诊断，四条件2×2，先证明缺层逐位相同 |
| 相位差导致冻结任务损失 | 尚无只改anchors的任务结果，全volume归一化亦可能改变缺层网络输入 | 只准备另合同的任务/归一化控制，不提前写Dice或临床结论 |

科学独立确认患者仍为0，尚无可发表且独立确认的新方法claim。新正文只是收紧空间，不能用已取论文数或软件复核代替这个目标。
