# 联合适配与静态强控制原文核读

本轮新增两份原文来源：MASC论文和Cartesian MRI博士论文的相关章节。完整读39页正文文字、5页附带封面／摘要尾页／目录，实际视觉核12页；不声称读完189页thesis。原文提取／渲染receipt的false阅读标记保留为生成快照，实际页范围见READING_PROVENANCE.json。

## MASC: Metal-Aware Sampling and Correction via Reinforcement Learning for Accelerated MRI

Zhengyi Lu et al.，[arXiv2602.00348v1](https://arxiv.org/abs/2602.00348v1)，[原PDF](primary_attempt01/masc.pdf)，19页，实际SHA=`c996a22feb8dd0cd8e4fee4e4ebe57cf8d8ce4eabd54ad0a9196d8927d7de1e2`。完整文字1–12、17–19计15页，视觉4、5、7、10、11、12、17、18。13–16参考文献未完整读；未读代码仓库／运行原实现，不把PMLR模板抬头当已核实发表会议信息。

方法：每步新获取一条未采Cartesian phase-encoding line；当前magnitude IFFT和mask进入PPO／MAR pipeline。U-Net预训练以L1+SSIM，后续在策略rollout后用MSE微调，与PPO交替更新。Reward（p5 Eq4）是`100×[Q(gψ(I_{t+1}),I*)−Q(gψ(I_t),I*)]`，`Q=.5 SSIM+.5(1−NMSE)`。策略与恢复器相互适配、以当前恢复状态的质量增量决定动作已有MRI先例。其相似度目标没有病灶Dice／诊断任务效应，不能把MAR恢复叫我们的病灶收益，也不能称本项目首创收益驱动策略。

数据是200个AutoPET **CT/PET subjects**转phantom后模拟TSE MRI／virtual CoCr hip implants；不是200个真实金属植入物MRI患者。每subject36切片；160训练／20验证／20测试，对应5760／720／720，明确报告subject不重叠（p7），但本轮没有核患者ID清单。radiologist验证phantom／simulation也不把模拟变成真实临床采集。模拟3T、TR4050ms、TE32ms、slice3mm、CoCr900ppm；fastMRI knee临床来源图像上另模拟metal artifact、不同implant geometry，不能称真实植入物跨中心临床验证。fastMRI测试患者数／split计数在已读正文中未明确，不补造。

训练p7–8：MAR先100epochs；PPO lr3e-4、MAR lr1e-5，rollout512、PPO每update4epochs、clip.2、entropy.01；RTX5090 32GB。AppendixA p17给每rollout先PPO后MAR的伪代码，停止写“not converged”，没有总joint更新数／精确训练秒数。推断冻结两网，逐线循环到budget耗尽。10×为2初始+18新增线，5×为8+32，不等于相同倍数的完整在线墙时节省；没有policy、MAR、IO、transfer或完整患者费用秒数。

强消融边界：Table2比较clean/metal PPO、只在推断加pretrained frozen MAR及joint MASC。正文说frozen MAR在fully-sampled数据训练、在undersampled数据推断；joint同时改变恢复器训练分布、loss、额外适配和策略所见状态。因此Table2支持联合pipeline优于该frozen/posthoc配置，不单独证明“在线patient-adaptive policy本身”提供增益。已读正文没有“对同一个joint恢复器重新训练的静态policy”或“额外适配预算相同的静态恢复pipeline”控制，不能用这组结果替代我们所需充分任务适配强对照。

论文mean±std和p<.001 paired t-test是作者报告；核读范围没有明确t-test是按20subjects聚合还是720slices等单位，也没有原始配对数据，不能在本轮独立验证p值。不是说其已证伪，只保留统计范围未知。

数值复核见 [CPU结果](table_audit_attempt01/receipt.json)。Table1 MASC10×SSIM=.7224，Random+MAR=.6949，差.0275约3.96%；MSE=.0111，相比Random .0140是20.71%下降。但该指标最强静态对照是Random-LowBias .0131，下降15.27%，不能把20.7%称为对所有端点各自最强静态的收益。PSNR最强静态同样Random-LowBias19.10，MASC19.73提高.63dB。Table2 metal frozen MAR的MSE=.0182，joint下降39.01%，属于另一种对照，不拼接成“对强静态39%”。Table3跨数据的Random-LowBias同时在SSIM／MSE较强，原3.0%／23.1%近似数字对应得上。

## Learning to sample in Cartesian MRI：Chapter5/6

Thomas Sanchez，thesis9981，封面答辩2022-06-03；[arXiv2312.04327v1](https://arxiv.org/abs/2312.04327v1)提交2023-12-07。[实际PDF](thesis_size_verified_attempt02/cartesian_thesis.pdf)189页，实际SHA=`f318edd5dd559c1282a4f935a443fdbaa519aaaf9f1326d695ef3ca9292ed3bb`。来源说明见 [ETag不一致记录](THESIS_BODY_IDENTITY_CLARIFICATION.md)：公开GET长度、完整解析、封面标题／作者／版本匹配通过，ETag SHA匹配未通过；保留下载程序exit1及false receipt，另建本地阅读来源，不称原attempt完整成功。

完整正文读physical60–66（printed47–53）、94–96（81–83）、102–115（89–102），共24页；另完整读physical1、7–10共5页；视觉66、110、112、114。其余正文、数据split细节／AppendicesA1/A2等没有完整读，目录／rg片段不当完整章节阅读。Chapter6脚注提供相关preprint **On the benefits of deep RL in accelerated MRI sampling** 的OpenReview fRb9LBWUo56，本轮未另下载该preprint，不能重复计独立文献。

LBCS是在训练病例上评估动作候选的平均恢复收益，学得非患者自适应的greedy/nested mask sequence；部署直接按序执行。sLBCS以候选subset和共同训练subset减小搜索量（p65–66）。作者特别要求同一轮所有候选用同一个病例subset，否则noise／SNR差异会让候选比较偏向较易病例。配对共同draw、静态greedy序列及budget-aware嵌套路径是既有控制／机制，不是本项目新算法。

Submodular理论限定非负、单调、submodular函数；p63明确nonlinear MRI reconstruction没有submodularity正式证明，p115将其视为conjecture。我们的病灶utility、动作交互、失败和完整cost也不自动满足这些条件；不能套1−1/e保证，不能由单动作增益相加得到joint标签。

Chapter6的核心是pipeline排名反转：crop/crop+resize改变FOV，horizontal/vertical masks、U-Net/cResNet、pretraining mask distribution以及SSIM最终点／轨迹AUC均改变比较。p104–105另提醒magnitude再FFT改变conjugate symmetry、GT与observed分别归一化及GT统计denormalization不能直接作为现实部署操作。这里按作者描述记录原研究问题，未独立读被评论方法的代码来验证这些具体实现。

Table6.2/6.3 p110，c+rhz cResNet：最终25% SSIM，RL−LBCS=−.0006；SSIM-vs-sampling-rate轨迹AUC则+.0015。CPU复核确认两个汇总定义下的报告均值排名严格反转；不是患者显著性反转。AUC这里是恢复质量曲线积分，不是分类ROC AUC。不能在本项目看到结果后换主要端点／预算积分坐标来制造赢家。

Table6.4 p112，DS-DDQN相对LBCS的PSNR sampling-rate AUC差−.251，acceleration-factor AUC差+.179，最终rate差−.559；同一轨迹用1/r坐标会重权高加速早期，不能把不同AUC量纲当直接相同效应。本轮没有获取曲线逐患者点、没有重新做积分、没有独立t-test，只核作者报告的表格算术。

训练成本已给具体对照但不可跨设备外推：p112说Bakker设置sLBCS用A100/20GB资源少于20min，greedy RL每epoch约25min、50epochs；p113另说与原作者通信得DDQN超过20days，sLBCS分布于5 A100约30min。这不是本轮实际测量，也不是同设备完整cost统一账；不得把25×50当已测完整训练墙时，或比较20days与5卡30min直接作本机倍数。

p114已经明确提出：joint training的收益究竟来自更好policy还是双方specialization/curriculum？可在co-trained reconstructor上训练LBCS固定mask，看是否重获co-trained policy表现。这直接覆盖“把同恢复器强静态对照补上”作为研究思路；我们不能将该对照设计本身写成新机制。其主要实证针对当时的pretrained-reconstructor RL，不能由此断言所有未来joint／MRI下游任务策略都无增益。

## 对当前候选的实际影响

新增的强证据不是证明本项目有创新收益，而是进一步压缩宽泛claim：joint/state-quality-gain已有MASC，static-vs-adaptive、pipeline失配及排名反转已有thesis，联合模型的specialization反事实也已经提出。可保留的仍是固定CISS观测、充分任务适配后病灶余量是否存在、完整费用下状态选择是否优于固定最强合法动作与cost/defer/DC控制的MRI经验结果。

新准备 [强静态与适配控制](MATCHED_STATIC_ADAPTATION_PREPARATION.md)沿用旧端点／预算／患者边界，没有修改成功条件，没有执行MRI实验。原能力未通过／raw训练尚未final；旧weak9pair成本null和head不可fit继续保留。读这些原文不会使发表claim自动成立。
