# dMRI不确定性原文与项目下一步

新读公开稿[Uncertainty Quantification in Deep Learning for Safer Neuroimage Enhancement](https://arxiv.org/html/1907.13418v1)，固定1907.13418v1（2019-07-31）。九位作者顺序与DOI [10.1016/j.neuroimage.2020.117366](https://doi.org/10.1016/j.neuroimage.2020.117366)一致，但题名不同；未核期刊final全文，不冒充最终版本。HTML455653bytes，SHA7c6d332766e4fbc7bc1625a3ff011a1be42bd24f79a99c34fe813db8649fc255。实际读139提取块（正文、公式、图注、三数据表），参考文献列表、图像像素、外部supplement和作者代码未读。获取及阅读来源另行登记；2017会议稿1705.00664v2仅索引，不计第二篇全文。

## 它已经做过的事

两条3D-ESPCN分别估计均值与对角协方差，heteroscedastic Gaussian NLL训练；variational dropout用于两网所有卷积层，近似参数后验。式13、15–19按全方差定律将图像不确定性传播到任意可测且有有限矩的下游函数g，再分内在与参数部分。MD/FA就是实际例子。因此“SR不确定性+下游量”“内在/参数分解解释失败”已有直接原始先例，不是当前新点。

Fig9不是泛指病灶安全：以MD重建RMSE<1.5e-4为safe真值，safe是正类，risky是负类；用全部16训练患者的foreground voxels选最大F1阈值，再用于未见HCP/Lifespan。作者所报Lifespan识别96% risky预测是这个体素误差任务，不能读成96%病灶检出或零漏检。讨论130明确更临床相关的成功/失败定义与定量病理验证仍待做。

讨论131已经提出按低不确定性区域覆盖原低分辨率图、高风险区域abstain，以及按参数不确定性进行active learning；并指出新增label可能需要额外扫描。这覆盖“置信度决定SR/保留原图/拒绝”宽思路。讨论128的“参数高→多训练数据；内在高→承认难度/拒绝”也是既有提议，作者限定估计充分准确；不是我们可直接采用的因果诊断。

## 原实验范围与可移植限制

| 实际设计 | 对当前MRI任务的约束 |
| --- | --- |
| 16 HCP训练患者；从原DWI做r立方mean blur，再拟合DT/MAP，再抽每r体素；测试×2三轴 | 不是本项目CISS单轴point删层×4，不替代slice-profile/前向模型资格 |
| 50%训练patch对作validation，200epochs/Adam/batch12，按val MSE选best | 不是患者隔离的校准或LOPO，不能把这个配方认作我们的充分任务训练 |
| 16未见HCP及10 Lifespan用于重建比较；后者年龄/协议同时变 | OOD为联合分布变化，不识别采集协议单独因果 |
| per-subject foreground均值/std；MAP训练分布0.1%/99.9% clip | 支持mask的合法部署来源需核，不可把隐藏native missing pixels用于本项目统计 |
| 推断通常200MC；传播分解200参数×10内在样本 | 需包含两网络/全部采样与派生量费用；均值网的快速数字不是完整UQ成本 |
| Prisma两healthy adults两分辨率扫描，Fig7示例tractography，分辨率/配准不完全相同 | 没有本项目paired病灶Dice/recall或临床工作流省时证据 |
| Glioma/MS临床图无高分辨率重建真值，MS图有neurologist病灶标注 | Fig12是warning/定性观察，没有定量漏检/过分割/体积损害证明 |

正文有值得保留的版本差异：MAP在82/Table1为22coefficients，87写21channels；正文93称各方法10个训练重复，Table3 caption称5；Lifespan重建比较93为10患者，而Fig9caption114写16。登记实际文本，不自行统一为最有利计数。

## 对强对照最有用的结果

Table2的HCP DTI interior：baseline6.212，hetero6.135，joint(II)6.116；exterior：baseline13.609，hetero15.469（更差），pure variational(I)13.412，joint(II)13.622。不能把“组合不确定性”概括为所有区域都最佳。Table3的MAP HCP interior2.285→hetero1.998→joint(I)1.951，但exterior9.316→hetero11.294，同样变差。

作者101/126直接解释：inverse variance加权会减少高不确定区域的拟合资源，可能忽视困难但重要结构。对当前已有严重漏检的024，不能把UQ权重当无条件改善；若后续引入，需同预算deterministic、hetero、variational、joint四控制，同时保留FN/FP/recall/precision和signed/abs体积损害。该论文只是动机和既有基线，不证明我们网络失败由该机制造成。

当前TaskUNet3D没有已训练的Bayesian参数/variance head，不能把重复同一确定性forward、现有空间增强四臂差异或人工加noise直接称此论文posterior。

## 一个实际实现准备检验

原HTML式20/21按字面在全部嵌套样本恒为1、T200/J10时给parameter=-19/81、intrinsic=1/9、total=-10/81，而方差应为0。float64数组与Fraction独立精确算术一致，实际fe41d8 exit0；[结果](constant_variance_attempt02/receipt.json)保留原MathML alttext。只说明这个公开HTML版本的字面式不能直接移植；未核PDF、期刊final或作者实现，不能宣称其医学结果因此无效。首跑9a62a3将左/右两侧六math节点误当三节点，断言失败且未产生结果；原脚本保留，独立v2按明确右侧ID选取三式后成功。

正文38的“高MSE低uncertainty”文字也与inverse variance及后文解释不同；保留差异。后续实现先核固定作者版、独立推导方差估计与有限样本性质，不盲抄。经验分布ddof0分解恒定检验通过，并不自动给总体分解无偏性或校准保证。

## 创新假设进一步收窄

当前只保留待证伪假设：充分任务模型及普通分辨率/支持增强后，在同一合法observed输入下，**采集信息是否能提高对具体SR动作的病灶净收益预测**，并在全费用与漏检/过分割约束下优于同信息同容量QC/error及action-conditioned posterior risk差。

为每患者/动作使用真实paired损害差L(baseline)-L(action)，纳入每动作失败、fallback、defer及全费用。图像方差、下游量方差或病灶“严重程度”不是这个差的替代真值。对照必须有去采集特征、metadata-only、同容量QC/error、动作条件风险差，以及static/random/always-action/defer。Bayesian期望效用规则本身是已有方法，不把该定义声称首创。

下一顺序：先四模型76开发完整终态/原capture/全部36已见验证比较；能力仍弱先补普通task，开发高验证弱先查泛化和常规增强。35904强度资格全量真正结束后才考虑六普通增强臂。当前1394MiB GPU空闲及储备之外约15MB磁盘不能容纳六final约33.73MB payload；不改用户训练，不删历史。准备冷初始化严格患者fold；见过全部11GT的parent不能作为LOPO外折初始化。8未见确认12series与lockedIXI继续关闭，尚无独立确认发表claim，goal active。
