# 两篇原始正文：全视野定位、小结构分割与分辨率

本批三查询各筛查六条题名，共 18 行（含重复），选取下列两篇原始研究的公开 JATS 正文。新增正文实际读完 50+122=172 个文字块，包含标题、表格、图注与重复表格文字；不是 172 个独立实验。没有新增 PDF、图像视觉复核或单独补充材料阅读。获取时点记录保持不变，阅读完成另列 [阅读证据](source_cache/global_local_task_fulltexts_2026-10-03/reading_provenance.json)。作者实验未独立复现。

| 论文 | 原始公开来源 | 本项目要排除的宽创新说法 |
|---|---|---|
| Automatic Segmentation of Vestibular Schwannoma From MRI Using Two Cascaded Deep Learning Networks，2025，DOI 10.1002/lary.31979 | [PMC11903922](https://pmc.ncbi.nlm.nih.gov/articles/PMC11903922/)，[正文文字](source_cache/global_local_task_fulltexts_2026-10-03/vs_cascade_maintext.txt) | VS 两阶段 CNN、初始 mask/encoder feature 指导细化、空间 attention 已有直接先例 |
| Automated olfactory bulb segmentation on high resolutional T2-weighted MRI，2021，DOI 10.1016/j.neuroimage.2021.118464 | [PMC8473894](https://pmc.ncbi.nlm.nih.gov/articles/PMC8473894/)，[正文文字](source_cache/global_local_task_fulltexts_2026-10-03/olfactory_maintext.txt) | 全视野粗定位→高分辨率局部小结构分割、2.5D 邻层输入、分辨率迁移和体积与重叠分离均有先例 |

## VS 两级网络：直接近邻，但不能套用其部署能力

正文块 2/4/14/16：第一级输出 mask 和 encoder features；第二级结合原图、初始预测和特征作细化，attention 将两级 encoder features 结合。作者比较 2D、2.5D、3D，分别处理 T1/T2。我们的全 FOV/local 基线属于既有路线的能力检查，不能因为加粗定位或 local branch 宣称新架构。

块 6/9：公共 242 患者、484 T1/T2 图像，155/39/48 训练/验证/测试；内部 96 患者、497 可见肿瘤切面，72/16/8。内部先选肿瘤可见切面，并按最大标注 mask 的矩形包围框裁剪；公共数据截取 centered on tumor mass 的 100×100×50 mm box。正文没有证明该中心可在无标签的完整 FOV 部署中获得。不能将 cropped ROI 的分数当作全视野定位能力，也不能抄成我们的输入合同。

结果表 II/III 与块 27–43：公共 T2 的 3D Dice .81→.82，但内部 T2 2D Dice .55→.51、HD95 32.03→32.14 mm。attention 的次要指标也有取舍：公共 2D T2 RVE 22.77→27.47%，2.5D T2 RVE 49.21→51.50%，2.5D T1 HD95 5.58→6.49 mm。不能从部分 Dice 改善改写为每种架构、模态和端点都改善。

块 9/45：100 epochs、不同维度的 batch、交叉验证与参数增加都影响比较。提取正文的“over 2°ø”存在编码错误，不恢复成未经核对的准确参数倍数。本文不提供我们的同容量/同观测/同更新预算证明。

## 嗅球：预测定位可部署，但体积、空间与分辨率不能混算

块 8–45：357 训练、203 内部测试；先在约 1.6 mm 全视野训练定位，再以预测 centroid 在 .8 mm 输入上截取 96³ ROI；定位训练监督来自人工左右 OB centroid，推断中心来自网络预测。这和上篇 GT 所决定的 crop 不同。多层邻片、多视图和四组模型最终集成共 12 个网络，不能和我们单模型同容量对照混为一谈。

块 53：作者明确说明 volume similarity 可以达到最大而空间 overlap 为零。这直接覆盖了我们上轮“体积很近但位置分错”的宽规律；本项目那个单病例是已有现象的失败诊断，不构成首创。作者 AVD 用两个方向平均距离的最大值，我们用 pooled 双向六邻接表面 ASSD，定义不同，不直接比较数字。

块 68–85，表 2/3：AttFastSurferCNN 集成 Dice 约 .8525，FastSurferCNN 约 .8506；AVD 后者略优，attention 并非所有指标都更好。集成相对单模型 Dice 大致 .8469–.8482 有小幅增益。每组多次随机初始化、按验证选权重；块 70/71 明述最终定位模型按 test-set 三指标总排名选入 pipeline。这个选择会使同一 test-set 不能承担完全未用于选择的最终确认，不能照搬成我们的保留患者规则。

块 94–101：无可见 OB 12 例中仅一半预测完全空，其余仍有少量体素。作者要求极小体积检查，并揭示 Dice 与体积的关联。109 同次 session 两种 T2 协议的稳定性集合，在视觉检查后排除 7 例，剩 102；ICC .897、VS .889，但体积仍有显著协议差异。稳定性不等于空间准确性，缺少配准时不计算同人跨序列 Dice。我们的正标签筛选队列不能声称已经验证无肿瘤特异性。

块 103–108：30 HCP 外部患者，.7 mm 原生分辨率，作者为 .7/.8 mm 两个网格分别人工标注。A：先重采样 .8，再把最终标签放回 .7；B：直接 .7 推断；C：.8 上推断并在 .8 标签评分。A 表现最低、B 通常好于 A，C 最好，但 C 的评分网格/人工参考已变，不能作为同一原生 gold standard 的严格配对增益。作者把 A 的下降解释为标签上采样伪影；这不等于我们概率回原生后阈值的操作已被证实有害。我们的空间重采样必须保留概率与阈值顺序对照。

块 111–119：推荐 full-head 输入、视觉检查小体积与控制 MRI sequence，作者也指出可通过重新训练/更强 scaling augmentation 适应分辨率。不能把本项目“直接分割或分辨率随机化”称为新概念；这些是必须比较的强基线。

## 已有 MC-RC 作者论文补读（不计新增正文）

DOI [10.3389/fncom.2024.1365727](https://doi.org/10.3389/fncom.2024.1365727)，PMC11111906；本轮补读旧缓存块 39–50、64–69、74，共 19 块，原始来源和 [旧阅读](2026-10-02_cobrai_crossmoda_mc_rc_reading.md)保留。

作者采用 nnU-Net v2，nonzero crop、z-score、median spacing resampling；1000 epochs×250 minibatches 即每 fold 250,000 updates，batch 2，并作五折和 2D/3D 集成。我们此前导入的 SC-GK 2.5D 权重、4000 步小网络及本次 20,000 步全 FOV/local 基线都不是该能力的复现。

表 2：在 MC-RC T2 上 MC-RC-trained（291 训练图/72 测试图）mean Dice 85.0±15.6%；SC-GK-trained（196 图）仅 16.5±31.9%；combined 85.2±14.1%。表 3 的跨域 SC-GK T2 median Dice 为 0，作者明报完全漏检和 undefined/∞。训练图/时点数不是独立患者数，不能外推我们 11 训练人。块 69 的无残留病例另作评价，不能用我们只含合格正标签的队列替代。

## 对下一实验的约束

1. 先证明不用 GT crop 的全 FOV 任务能力；预写四患者门槛、冻结最后 checkpoint，保留所有系列。
2. 能力通过后再作训练曝光、统计、输入重建的公平矩阵，加入直接分割/随机分辨率强对照，不能将适应本身当创新。
3. 只有适应后仍存在一致的缺层边界/漏检残差，才推进可观测的局部修正。候选必须优于 raw PCHIP，同时控制同容量、同 observed、同预算，守住 anchors/tail 与体积端点。
4. 先独立核坐标、训练身份、预测和指标；最后新方法需在八名未开效果的保留患者确认，并用第二独立训练任务网络复查。当前科学确认为 0，没有可发表的新 claim。
