# 可观测特征如何连接真实动作收益：后续可执行准备

已有[19行series特征表](experiments/observed_holdout_feature_table_2026_10_08.json)及[完整结果](OBSERVED_HOLDOUT_FEATURE_RESULT_2026-10-08.md)。heldout两fold使用合法observed：17个有限数值特征包含实际层距、retained间距、anchor与heldout数、r/c、pixel数、linear／PCHIP MSE／MAE及retained统计范围。表中病灶任务标签、动作收益和完整成本均为null，不制造监督。表按patient及series UID连接，series UID／patient标识仅用于分组／连接，不能充当预测特征。

## 待检验claim及为何仍有可能

待检验：同raw观测、同动作集合、同充分适配任务网和同完整实测预算下，预测某个动作的患者病灶净收益，比选择最高恢复误差／风险更有效。误差不一定可修正；信号不可预测、背景和稀有结构可能贡献不同，动作又有交互。这个区别由已读文献与旧项目失败提出，**尚未获得MRI效应量，未完成直接MRI查新，未证明可发表或独创**。

这一轮实际完成的是先mask特征依赖资格和real观测负结果。Noise2Void／Noise2Same、PCHIP、J-invariance、先mask、成本路由、cross-fitting及误差与收益区别都不是单独创新。不要把整理成新名字代替强控制下的实测增量。

## 执行依赖与作业顺序

继续原live99542，真实final exit0且两个最终模型冻结前，不做中间模型任务收益选择；不重启／迁移或修改原训练配方。原两臂各19998／总39996、30h、CPU4／interop1、float32、AdamW lr/wd=.0001及资源合同沿用。模型结束后按原顺序：真实退出receipt→原56完整FOV→全部6能力gates→独立strict。旧absolute失败不以本次布局差异解释或覆盖。

若这组强任务基线有资格，再实施[同信息同容量矩阵](COMMON_PROJECTED_TASK_FACTOR_PREPARATION_2026-10-08.md)：legacy dense两通道、direct两通道、common projected dense两通道；direct与共同投影direct输入19/19逐位相同，不重复训练。原一通道native信息较多、raw-PCHIP一通道容量不同，两者仍按原用途报告，不能与这组三臂混为同信息同容量控制。

任务训练／推理及动作成本的具体执行合同必须另冻源码、checkpoint、初始化、augmentation、GT几何、预算和输出目录；本准备不授权回改已冻结方案。用户已允许GPU，无需重问；新增作业先核8GB余量，当前1394MiB不足。CPU资格主体总时间108.4670518s包含IO／counterfactual／核验，不是部署特征时间，更不是全部动作成本；需另行benchmark真实生产路径。

## 真实标签表的连接合同

每条未来标签必须具备：patient、series集合、baseline／任务网checkpoint SHA、输入分支与source SHA、当前动作状态、候选动作定义、完整患者FOV端点Q_before及Q_after、差Q_after−Q_before、全部系列合并的当前累计与增量实测成本、精确预算、失败／defer状态。Q与正负方向沿用原预先指定的病灶端点；不在看到结果后换指标、ROI、阈值或患者集合。不得以本表observed MSE、训练loss、GT ROI误差或一个patch的分数填Q。

只在开发11患者／19series生成监督。整患者cross-fitting，各heldout患者的全部series、动作、相邻patch、增强和重复case都属于同fold；特征标准化／head fitting／阈值选择只用训练患者。11患者较小，先检验可修正余量及控制强度，不以像素数或81次核验增加样本量。缺失／负收益／零收益／失败／超预算都保留，不只收成功动作。

定义动作状态后，联合／连续动作从当前状态重新测ΔQ及incremental cost，重叠区域以实际union和共享实现计费。禁止把单动作ΔQ相加或静态N+m*k外推。对每种cached／full／新布局都检查最终输出、硬预测和完整FOV；费用流程A/B沿既有事先合同。

## 最小比较与判定

| 比较 | 需匹配的信息与预算 | 能排除的解释 |
|---|---|---|
| utility head vs observed error head | 同可观测特征、head容量、整患者split、动作集合及总预算 | 仅高误差排序即可 |
| utility head vs task risk／uncertainty head | 同任务状态信息、head容量和成本范围 | 仅高风险区域即可 |
| fixed best legal action／no action／defer | 开发内合法选定，定位与生成费用都计入 | 方法只是一个有效固定动作或总花费更高 |
| cost-only、预算随机、union-aware greedy | 同总预算、随机规则冻结、当前状态动作成本 | 收益来自费用偏好或已知贪心 |
| legacy dense vs direct vs common projected dense | 同raw source、两通道、初始化／监督／适配／augmentation | 投影顺序／容量／训练不足造成优势 |

若开发内强适配后仍无稳定的可修正病灶余量，不训练一个收益头去“找出”不存在的空间，归档受控负结果。若有配对净收益，先冻结方法、特征、网络、指标、阈值、checkpoint、动作与预算，再8确认患者／12series及第二任务网。已见验证4／9不改名新确认，lockedIXI关闭；旧MIRA／MSValid84保留。fresh calibration只约束正式风险保证，不给普通经验论文额外门槛。

## 定向补读队列

先补Noise2Same官方Supplemental的Theorem1／2证明，以识别normalization与target依赖条件；不把它当病灶证据。再取得并核读主PDF引用[18]“Leveraging self-supervised denoising for image segmentation”（2020），以及更直接的MRI slice acquisition／task-aware recovery／adaptive acquisition论文，对齐观测集合、任务网适配和完整成本。以上只是队列，不计已读或已确认原创。全部新增attempt与结果另存innovation，不覆盖旧材料。
