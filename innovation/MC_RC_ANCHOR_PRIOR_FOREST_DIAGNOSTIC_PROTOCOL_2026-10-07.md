# 观测定位：先验与非线性分类器的固定开发诊断

在新的MRI/标签读取、拟合和评分之前固定。当前目标仍是可发表的MRI净任务收益claim；本诊断用于改善/解释其合法ROI瓶颈，QDA、class balancing、ExtraTrees及现有9通道均为已知方法，不单独作为创新。旧16系列QDA及低覆盖结果保持冻结，不后改。

使用当前19系列/11开发患者完整队列，不按ROI或性能排除。phase0/stride4只读已认证observed-only包；特征沿原feature_plane/normalization：observed 1/99百分位，强度、0.5/2mm高斯、1mm残差/标准差/物理梯度、三RAS相对坐标。没有hidden native MR、GT box/crop或缺层MRI特征。训练仅解码原observed label planes。每held患者的全部系列从本fold训练排除；其observed标签可用于其他fold合法开发监督，不能影响自身参数/采样/阈值/选择。所有19预测包保存后才开始完整GT评分。

固定3模型，不因结果改名：

- `joint_QDA_empirical_prior_19`：在新的19队列按原患者/系列等权全部观测像素矩重新拟合，原shrinkage=.9C+.1diag(C)+1e-4I、真实类先验。它不是旧16模型的同一预测，不能混淆cohort变化。
- `joint_QDA_balanced_prior_19`：**唯一主诊断**，与上者均值/协方差/precision/logdet完全相同，只将决策先验固定为[.5,.5]；LLR≥0。用于隔离先验影响，非正式校准概率。
- `joint_ExtraTrees_balanced_19`：解释性非线性对照；64trees、max_depth16、max_leaf_nodes256、min_samples_leaf5、max_features=sqrt、bootstrap=False、random_state20261007、fit n_jobs4/predict n_jobs1。每series每类最多8192观测像素无放回抽样，PCG64 seed=SHA256('20261007|UID|class')首16hex，排序固定。sample_weight每类在series内等权、训练patient内series等权、10训练patient等权。probability-like score≥.5；不宣称经过校准。与平衡QDA还存在采样和容量差异，不能把差值纯归因非线性。

所有预测anchor masks阈值预先固定；ROI仍两侧anchor并集+原面内2mm，三个内部缺层共享，不沿z扩张、不调半径/阈值、不LCC/后处理、不挑最佳方法。评分保留原foreground≥.99、boundary≥.99、tile32 foreground≥.995、ROI fraction≤.05、tile32 fraction≤.10全部gates，并额外映射当前3D格点/window/batch2费用。主终点为主诊断全19系列gates通过数及“foreground/boundary≥.99且有条件forward省算”的交集；同时报告全部模型、原N/k、空ROI、全batch失效、患者等权Dice/recall/ROI面积/费用。面积不替代3D或真实预算。

完整GT只在全部预测冻结后用于开发评分；没有MRI恢复动作、model task收益或实际推理加速claim。11患者已参与设计，LOPO是开发诊断，不是未见确认；4已见验证/8确认/locked IXI继续不读，旧MIRA/MSValid84确认保留。

MRI环境没有sklearn（preflight19d435 exit1）；固定将scikit-learn1.7.2/joblib1.5.2/threadpoolctl3.6.0仅安装到innovation内任务目录，no-deps/no-compile，不改根环境、environment.yml或.gitignore。包源码/原wheel元数据和文件SHA另存。失败保留，新version/attempt修复；不因依赖缺失把未执行模型记为失败科学结果。

新脚本自身CUDA不可见、BLAS/OMP1、forest fit4 threads、预测1thread、below-normal，RAM/磁盘8GB储备，新阶段文件总上限250MB（含依赖）。准备/拟合/预测/评分总1800秒；独立重放另1800秒。逐plane特征≤100MB、单label slab≤32MB、完整native bool≤256MB。只改innovation，自身审计限制列明metadata/observed/label源；不控制其他PID或原session99542。

独立核验重建observed标签索引/训练membership，独立Cholesky QDA决策与森林leaf-value累加，重跑所有19anchor分类；显式disk、独立GT boundary/原端点及Fraction费用复核。共享SciPy特征提取和sklearn tree traversal可明确登记，不能称独立库或科学确认；任何数值/硬预测差异保存，阳性解释等待核验。
