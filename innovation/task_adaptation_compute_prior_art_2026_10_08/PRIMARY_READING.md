# 新增原文：任务适配与状态策略的已有边界

实际新增两篇独立原文，完整文字29页、视觉9页。提取45页不等于读完45页；[精确阅读范围与SHA](READING_PROVENANCE.json)记录未读页、重复阅读及截断。这里只说明本轮核读的版本，不替最新期刊版或补充材料背书。

## Task adapted reconstruction for inverse problems

Jonas Adler、Sebastian Lunz、Olivier Verdier、Carola-Bibiane Schönlieb、Ozan Öktem；[arXiv 1809.00948v1](https://arxiv.org/abs/1809.00948v1)，2018-08-27。索引另给 DOI 10.1088/1361-6420/ac28ec，但本轮未取期刊最终版。全文33页；完整核读1–5、13–28，共21页；视觉17、20、22、24、26。5页引用的SegNetMRI只是该论文的相关工作，不算我们新读了SegNetMRI原文。

16–18页将分步恢复后任务适配、直接数据到任务，以及恢复与任务共同训练放进同一决策框架。Eq(20)明确写 Ljoint=(1−C)Limage+C Ltask；18页明确任务网训练输入应来自恢复器的输出分布，并可先分别预训练后联合训练。这覆盖“重建损失加分割损失”“修正后再适配分割网”“改成直接从观测输出任务”这些泛称。

25–27页的Proposition1及Corollary2在其条件下说明：若固定表示B保留相关观测信息，直接y和B(y)可有相同任务条件分布。作者明确不以泛称information bottleneck解释联合方法一定更优，可能差异来自架构、训练、稳定性和泛化。这里的定理及其条件是已有理论，不能改名成本项目新证明。也不能把非参数理论等价当成我们的有限容量、插值、归一化、resize和float32流水线实测等价：项目的原始anchor残差和common projection已表明必须核对实际算子是否可逆/丢信息。

19–20页分类是MNIST模拟parallel-beam tomography，512,000 triplets来自约60,000 MNIST entries，作者主动说明并非统计独立。Table1 sequential准确率96.01%，joint C=.5为97.00%，但L2-loss 9.0→9.2；任务提高不表示图像平方误差也提高。22页分割为二维brain CT灰质、模拟30角/183线、0.1%高斯噪声、128×128、100训练triplets加增强、无预训练。这不是100独立MRI患者，不是三维CISS病灶确认。24页的“few milliseconds”也不是我们完整患者费用。

该v1的权重方向存在实际文本冲突：17页Eq(20)及文字说C→1只保留task loss，20页Table1图注却称end-to-end对应C=0；22页方向描述与24页Figure4的C→1 sequential图注也不一致。已视觉核验17/20/22/24确认不是文本提取导致。仅按Eq(20)记录形式，不由这个版本的图注定义我们的训练recipe，也不声称论文整体结果被推翻。若日后复现其具体C曲线，先核最终论文/作者实现。

对项目的行动是保留强任务适配：同observed、同总容量、同初始化/监督/增强和充分优化。native_reference使用额外未部署信息，只能提供能力参照；它与observed路径的差不能填成可部署动作标签。候选若只是同观测的确定性修正，收益必须体现于受控有限预算中的新患者任务端点，不能宣称凭空增加测量信息。

## Tuning-free Plug-and-Play Proximal Algorithm for Inverse Imaging Problems

Kaixuan Wei等；[arXiv 2002.09611v2](https://arxiv.org/abs/2002.09611v2)，2020-11-18。完整文字1–8共8页；9–12只看页首辨认参考文献、不计完整。视觉4–7。索引还返回同作者扩展TFPnP 2012.05703v3和HSI工作2211.15307v2，均只标题/摘要筛查，不计新原文、也不把同工作扩展当独立收益证据。引用的supplemental本輪未取得。

4页状态是PnP-ADMM的(x,z,u)，动作包含离散是否停止、连续denoising strength和penalty parameter，后者由可微环境反传；前者用model-free policy gradient。5页每决策执行m=5次迭代、最多N=6次决策，共30次；奖励Eq(10)为相对当前状态的PSNR增量减η=.05。自然图像监督训练的PSNR标签需要真值，部署策略状态不因此成为真值监督。已有方法直接覆盖“按状态选修正强度”“预测当前动作价值”“收益减费用后停止”；换成MRI、gain head或病灶词汇不能自动建立算法新颖性。

6页denoiser训练87,000 overlapping patches来自400 BSD图像，policy/value训练17,125 PASCAL VOC图像；不是这些数量的MRI患者。6–7页CS-MRI为欠采样Fourier加噪，Medical7七幅图、MICCAI50幅图；本轮所读正文不能据此确定独立患者数。主要报告PSNR，无本项目整患者CISS病灶Dice和未见患者确认。

Table2噪声15、×4：ours 28.42dB/5iter，oracle 28.60dB/30iter；×2 ours30.33超过constant-parameter oracle30.25，文中解释策略允许跨迭代变参数，所以“oracle”只针对其较窄固定参数集合，不是整个合法动作空间上界。不能将5/30写成实际端到端费用比，也不能要求项目超过一个掌握更少行动自由度的“oracle”。

5页Table1的5.65ms是256×256 UNet denoiser GPU耗时，不包含policy、每次proximal、数据IO/传输和患者完整流程。5页η=.05是每决策固定惩罚，单位是PSNR奖励单位，不是实测秒/能耗；本轮所读正文没有全部部署相位费用，所以不能引进这个值替代项目成本。若设置PSNR差特征/阈值，只能开发用；最终label仍是真实完整患者ΔQ。

## 与既有结果结合的可证伪问题

| 可执行候选问题 | 现在能支持什么 | 仍需什么／否定条件 |
|---|---|---|
| 固定合法修正在强任务适配后是否还有病灶净收益 | 本轮真实旧label的连接/负零保留正确；新文说明必须给任务适配强对照 | 两臂final/56FOV/六gates/strict后，三条同observed强适配路径生成新开发label；若无余量就保留负结果，停止学selector |
| observed可用特征能否辨别值得付费的动作 | 17特征已存在，泛称cost/defer/state policy均有先例 | 对全部固定最佳动作、条件双成本/已有defer、DC-based控制，在相同可见信息、容量与总预算下比较；标签生成费用和部署特征费用都计入 |
| 自适应方案是否提供预算优势 | 当前完整action cost未知；新文的iteration proxy不能填空 | 实测完整患者含selector/probe/action/task/postprocess费用；若为了选择已算完所有动作，不能宣称省动作计算 |
| 效应是否延伸到新患者 | 已见4/9的旧linear−PCHIP患者均值为负，不是新确认 | 方法/所有learned components/端点冻结后才8未见/12series；head-only LOPO不称整个pipeline患者外 |

可能最终形成的是针对固定观测MRI恢复的受控经验结果，或在充分适配任务模型下可复现的局部收益机制。**目前两者都未证实**。这些已读先例不报告我们的准确实验组合，但组合差异本身不证明首创；后续仍需直接MRI查新、实际强对照效应和未见确认。
