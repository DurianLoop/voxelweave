# 配对收益预测与 learning-to-defer 的直接方法碰撞

实际核读两篇正确来源的原文可提取文字：Mozannar/Sontag 的正式 PMLR 119 会议 PDF **12 物理页**；Madras/Pitassi/Zemel 的 arXiv:1711.06664v3 **20 物理页**（含文内 Appendix A-I、参考文献、图表可提取文字）。关键方法页面实际渲染/view_image：前者 4、8；后者 3。未完整检查所有图像像素、未运行作者训练。Mozannar 43 页最新 arXiv 版本超原页数预算，原失败保留；会议 PDF 引用的额外 Appendix B/C 未另取，不能声称已核其完整证明。初次错误 Madras ID 1711.06646 是物理论文，不计相关论文阅读。

原始文件及提取位于 `source_cache/learning_to_defer_primary_attempt02_2026-10-07`，题名页核对与更正见 [来源记录](2026-10-07_learning_to_defer_route_correction.md)。下载时 actual_reading=false 不回改，后续 provenance 单独记录实际阅读。这两篇本次新增原文 **2 篇**，不回写上一冻结阶段的计数。

## 确认的直接先例

Madras 等，*Predict Responsibly: Improving Fairness and Accuracy by Learning to Defer*，[arXiv 官方页](https://arxiv.org/abs/1711.06664)，NeurIPS 2018，所读版本 v3（2018-09-07）。

- 物理页3，Eq2/3：系统在模型预测与固定外部决策器预测之间选择，优化 `(1-s)*model loss+s*DM loss`。正文明确 gate 预测“哪一方在该样本的损失更低”，并非只表达自身不确定性。固定外部决策器可为人或 proprietary black-box。
- 页4/5：恒定外部成本下退化为普通 rejection；自身不确定但外部决策器更差时，应保留自身预测。这个例子直接覆盖“误差高不等于修正收益高”的一般动机。
- 页6/7：post-hoc 两阈值 gate 和依赖 X 的神经 gate；Concrete relaxation、可阻断 gate 向基础预测器的梯度、测试 π>.5。添加 learned gate 或 gain head 本身不是新方法。
- 页8/9/16/17：COMPAS、Heritage Health，外部决策器为带额外信息/偏差/人为噪声的模拟神经网络；不是 MRI 恢复或真实放射医师试验。每设置5次运行，图中 Pareto front 和超参数 sweep 不是一个事前固定部署点。Appendix D 写1000阈值组合在一半名义 test 上选择、另一半评价；本项目不照搬这种角色命名，开发调参/最终确认应清楚独立。
- 页17/18：公平正则并不满足页4原定理形式，作者用实验补充；不能把正文理论泛化为所有复杂约束保证。

Mozannar/Sontag，*Consistent Estimators for Learning to Defer to an Expert*，[PMLR119 官方页](https://proceedings.mlr.press/v119/mozannar20b.html)，ICML 2020，7076-7087。

- 页2/3：Eq1 是任意 classifier/expert cost 的系统风险；可含动作调用成本 c(x)。将 deferral 纳入动作集合做 cost-sensitive learning。Proposition1 的加权交叉熵构造适用于一般有限随机成本，不局限于 0-1。
- 页3/4：重点 0-1 理论的 Bayes gate 比较最佳分类正确率与 `P(Y=M|X)`；Eq6 的附加输出可在仅有训练专家样本下学习 defer。不能把这个分类一致性定理直接称作 voxel Dice 或病灶安全保证。
- 页4/5：单独拟合基础预测器后再比较两方置信度，在无限容量等理想条件下可一致，但有限容量会因缺乏联合适配而失效；另指出一种 mixture loss 不一致。论文没有说所有 two-stage 策略必定失败，更没有否定真实强基线。
- 页6：CIFAR 基础网故意减小容量/取消增强以展示固定模型下机制；这不符合本项目充分适配强基础网的要求，不能用其增益幅度预测本项目空间。
- 页7/8：CIFAR10H 人类标签、专家正确率预测与补全已有；表2 system accuracy 的策略 coverage 不同（例如51.67与79.48），不是相同预算比较。CheXpert 使用合成专家，按 support devices 标签设正确率 p/q；80/10/10 患者隔离，不能称真实专家临床验证。
- 页8/9：CheXpert 的 coverage 阈值来自未标记 test score 分位数，曲线报告多个预算点和最大 AUC；它未用 test GT 选这些分位数，但属于整队列相对预算策略。若本项目声称逐个上线部署，应开发上冻结阈值或明示队列预算合同，不能使用确认 GT 调阈值。

## 对当前“收益头”候选的实质降级

若有限动作 a 只根据 observed O 生成预测 `f_a(O)`，训练时可用 GT 算每动作成本 `C_a(O,Y)`，则策略目标就是

`min_pi E[C_pi(O)(O,Y)]`，最优动作是 `argmin_a E[C_a | O]`。

相对于固定动作0的收益 `G_a=C_0-C_a`，取最大条件期望收益与取最小条件期望成本完全等价。这是已有 cost-sensitive/defer 的实例，不是本项目新定理。将全体积 Dice 作为每例成本仍可定义这个有限动作问题；仅因 Dice 是比值并不能躲开一般成本先例。若动作逐区域选择，局部图像修正会经当前 IN/上下文影响区域外任务预测，单动作标签不能未经验证直接相加，此时需评价实际联合系统；这个条件也不自动产生新颖性。

因此，**“首次学习具体修正的任务收益”“收益头优于自身风险头”“自动选择两个恢复输出”不能直接作为方法首创**。此前 SafeRestore/MoEDiff 也保持。当前候选应降级为待检验的 MRI 科学问题：充分任务适配后，同 observed/监督/容量/总预算条件下，病灶收益相关的策略是否还有稳定、独立可确认的剩余改善；若只是移植已知 gate，即使有效，也需诚实定位为应用或机制结果。

## 后续必须增加的对照/记录

1. 普通误差头之外，加入 **两路径成本/错误率头** 与已有 cost-sensitive/defer gate；同特征、容量、开发监督和总预算。仅与单一路径 uncertainty 比较太弱。
2. 固定评估器条件与联合优化任务预测器条件分开。若策略获得额外适配预算，同 observed 直接任务和 PCHIP 任务网也获得同预算；教师、候选重建和动作 GT 打分成本计入。
3. 学收益大小的条件期望与二分类 `gain>0` 标签目标不同；用哪一个应事前定义，不因测试胜负换解释。全体积主端点与局部 surrogate 需实际联合策略验证，不用训练 oracle 作部署效用。
4. 所有学习/动作标签角色按患者隔离。跨系列同患者不能作为独立折；任务评估器在该患者上拟合所得标签需明确标记开发内训练标签。若要声称标签的泛化效用，可预备患者外 fold 的标签生成，但 fold 训练/强能力成本需实测，尚未执行。
5. 四已见验证只用于能力/开发选择，八确认待策略/模型/阈值/主端点冻结后才打开；确认样本很小，需诚实报全部患者差值、区间和失败，不把多次阈值/模型试验称独立确认。

本批原文反而削弱了候选的算法新颖性，不能因批量阅读增加而宣布 claim 已形成。现阶段先完成已有低 LR 基础任务资格，若充分适配后残余消失则停止收益头方向，不用改名或挑病例补救。
