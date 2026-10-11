# 公开 GIN 稿、固定作者代码与本项目的创新边界

实际阅读对象为 [arXiv:2111.12525v5](https://arxiv.org/html/2111.12525v5)。七作者与 DOI 10.1109/TMI.2022.3224067 元数据一致，但 arXiv comment 明确这是 early non-peer-reviewed version，期刊 final substantially revised，指向 IEEE 9961940。不能把这份稿、2022-11-28 的作者 commit、TMI final 配置视为同一版本。

正文实际读 0–103 共104个提取块，Algorithm1另补读；主文4张独立数据表已读。13个HTML table包含6个公式布局、重复嵌套数据表，不能报13张实验表。207个math节点是解析数量，不是207条独立完整公式阅读数。References标题104及参考列表不计主文；图像像素、外部supplement、最终期刊全文未读。旧DG-TTA/routing/RUGS阅读不重复计本轮新论文。

作者代码固定 [commit d4d5056](https://github.com/cheng-01037/Causality-Medical-Image-Domain-Generalization/tree/d4d5056ded88951fc3967f8f294f4a12420e13c6)。七文件下载各核Git blob SHA1；README122、configs107、2D GIN96、3D GIN102、trainer379、train script316及AdvBias367，共1489条不同源码行全部静态读完。AdvBias前一部分只读180行，本次补1–169/270–287共187行；重复核读不重复计数。未执行作者仓库。

GIN并非简单随机blend：Gaussian浅卷积四层/隐藏2通道、LeakyReLU、随机alpha混合，并做Frobenius归一化；作者分母实际有1e-5。3D GIN已发布，因此“把GIN搬到3D”不能作为我们的方法贡献。IPA用低频空间变化权重互补混合两个GIN结果，不用GT mask构造前景增强；因而“破背景相关/空间变强度增强/采集不变特征”均已有先例。

作者trainer实际生成三份GIN视图；前两份互补混合，第三份保持GIN。CE+Dice监督第一份，三份预测softmax均值作为KL target，方向KL(mean||each)，默认mean归约且target未detach。本轮独立实现检查在当前Torch实测：attached与detached的loss相同、梯度不同，attached梯度与独立NumPy有限差分相符。不能把该loss直接称forward JS或主文两视图Eq3精确复现；也不从当前环境推断旧Torch行为。原train script每250epoch评价target但未核到直接由target选择checkpoint语句，不凭此指控泄漏，也不把该流程认作本项目独立确认。

AdvBias的kernel helper位于同一文件11–33行；初始化170–235、conv_transpose2d278–283、bilinear align_corners=True上采样288–291、kernel320–332已核。trainer设order2/downscale2；kernel从一个box开始，循环order次增加box factors。该离散构造及最终双线性上采样与主文cubic描述存在实现边界。完整3D IPA field尚未发布/复现；本轮只核互补混合算子，不给未验证的3D场补成功标志。

主文TableIV的GIN→GIN+IPA平均Dice：腹部86.04→86.31，心脏83.83→85.01，前列腺65.10→70.37，器官有取舍；作者讨论源域腹部约−2.0、前列腺约−1.0 Dice points。增强不是无代价保证。其因果模型明确假定acquisition与content独立、跨域content不变；本项目患者/病灶分布变化不自动满足这些假设，合成增强也不自动成为真实物理采集干预。

| 本项目候选 | 本轮判断 | 可证伪的下一步 |
|---|---|---|
| 随机卷积/3D GIN/空间混合本身 | 先例充分，作为强对照 | GIN-only、GIN+IPA、consistency逐项消融；同时匹配曝光和实际总计算预算 |
| 采集信息帮助选择SR/TTA等真实动作 | 保留为研究假设，未确认新颖性或收益 | 在强task基线、实际动作余量和同信息action-risk差/QC/defer/metadata/static/random之上检验患者净收益 |
| 已知切片的锚点、physical-mm条件及风险头 | 原项目及旧计划已包含，不重命名为新贡献 | 在原功能和同信息对照基础上证明额外价值；g=L(a0)-L(a)与risk差等价，不能靠head命名创新 |
| 保持舍入的局部依赖插值 | 已有可复现实现加速结果，当前属实验基础设施 | 完整新schedule资格和全费用；所测12配对约10.19倍不当临床收益或整个训练wall |

下一步顺序为强普通task能力→真实动作完整FOV收益/全费用→患者cold-init cross-fitting→冻定模型/动作/端点/预算→独立确认。含全部11开发GT的19998 parent只作开发能力诊断。11开发患者19series全保留；4已见验证9series不能当新确认；8未见确认12series及lockedIXI关闭。当前无可发表且独立确认的claim，目标保持active。
