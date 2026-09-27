# 最终投稿准备：冻结与事后敏感性协议

日期：2026-09-12。此文件在本轮任何敏感性结果计算前写入；freeze.json 绑定其 SHA-256 与原始数组。既有主要结果不能因本轮结果而改写。新输出仅写本目录，核验后更新已另行快照的 CVPR 稿件。TMI 不在本轮范围。

## A. 已冻结的主要证据

上一轮 FINAL_SCIENTIFIC_STRENGTHENING 的协议、全部最终 CSV、报告卡、现行主文和完整补充材料保持独立快照。所有复现使用的预测/目标/掩膜数组逐文件重新哈希，原址保全而不复制约 86 GiB 数组；另外绑定原始 acquired-support NIfTI 和定性图数组。保护是内容哈希绑定，不宣称操作系统写保护。任务结束再验证。

主要 cross-architecture 实验不变：139 examinations、五个既有模型、每数据集全部20有向异模型对、已选定五个目标、A0/B0 与同一 A0/B2、原 target-1% support。既有 acquired-only 与 Proposition-1 实验、失败结果、稳定性门槛不改变。

## B. 新增事后敏感性（非预注册主要检验）

所有分析只读取已冻结预测，不训练、不推理、不选新分数。连续 O = ||A-B||²/[2(||A-y||²+||B-y||²)]，先以 float64 做差。每目标同一支持区域用于两个条件；先平均目标，再平均 examination。每数据集使用相同的5000次 examination 抽样（fastMRI seed 19001；IXI 19002），全20对共同重采样。对每个数据集/支持区域/几何端点分别计算20对 max-standardized-deviation 双侧 simultaneous 95% CI；不宣称跨全部敏感性总体校正。

支持区域仅三种：(1) 原冻结 target-1% mask；(2) 最近两个 bracketing phase-0 acquired anchors 的 foreground union，每张 abs(x)>1% max(abs(x))，严格复用 PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/PROTOCOL.md 第13行既有合同；不使用目标、其他phase或新阈值；(3) 全图所有模型 A0/B0/B2 和目标共同有限像素。不有限值不隐蔽插补。记录像素数与几何有效性。输出 shared O、disjoint O、ΔO、每对CI、等权家族均值CI、相对于原支持区域的20对 Spearman排序及最大名次移动；排序相关<.9或最大移动>=5名标记实质变化（仅描述）。

几何分析在原 target mask 上进行：(a) residue1和residue3各自 examination 内目标均值；(b) 两个 residue 均值等权；(c) residue1减residue3的 mirror difference，仿照历史 identity-swap 的反射类比较，使用均值以保持新实验原估计量一致；这不是重新镜像图像推理或精确因果交换。(d) 最近左右 acquired anchors 的距离多重集在两个phase均为{1,3}的所有目标，按两个 residue 等权。另列更严格四邻锚全支持 {-7,-3,1,5}/{-5,-1,3,7} 上的反射平衡；必须每phase至少两个左/右锚，且 examination 含两个residue，否则NA，禁止边界补锚。所有筛选只依赖索引几何。不得把 orientation CI 包含0解释为几何等价证明。

家族分析：原 target mask 的20对等权均值/中位数、每次排除一种架构涉及的全部有向对（余12对）的均值/中位数。重采样同一批 examinations，并在每个bootstrap内部重新计算 pair-family mean/median；报告描述性percentile CI，保持模型对依赖。不可称20个独立重复。

原始 clean same-model 图重新表达：只用既有 shared/disjoint 都有效的成对目标键，采用原预测1% mask、历史 float32 subtraction 合同；目标先在 examination/model 内平均，模型等权，再 series 在 patient 内平均，patient等权（NingXia8）。统一报告local O/ΔO和shared S=1-O；三cohort分别患者/检查bootstrap，seed19003/19004/19005。旧 pooled-plane 排名和stable-wrong移至补充，原数值保留。

## C. 编辑变动

重新组织图2、图3和报告卡；题名选择依赖而非无限推广影响探针；摘要最多两个定量重点；结论区分architecture diversity与evidence diversity。清理读者可见内部Plan措辞；保留全部负结果及协议修订。引用和伦理逐项核查，缺失批准、同意或来源一律标 NEEDS HUMAN CONFIRMATION，不补造编号。全部新敏感性与复现结果进入补充和证据矩阵。

## 终止条件

完成支持/几何/家族分析、论文重排、引用伦理审计、原数组独立复现、LaTeX与视觉检查后停止科学探索。没有新增数据、架构、阈值或评分搜索。不得从这组回顾性资料量化接收概率。
