# 校准、拒绝预测和修正收益的原文碰撞

本次取得三份原文PDF，共38物理页；实际完整选读Guo页1-8、SelectiveNet页1-7、CRC页1-8，共23页，7页实际render并view_image。余下参考文献/附录未完整核读，未复现作者实验。下载时reading_performed=false保持；实际阅读另记provenance。相关原稿分别来自官方PMLR70、PMLR97和arXiv2208.02814v4，不把版本/访问/阅读混为一项。

## Guo、Pleiss、Sun、Weinberger，ICML2017

*On Calibration of Modern Neural Networks*：[官方页](https://proceedings.mlr.press/v70/guo17a.html)。实际所读PMLR会议PDF10页。

页2 Eq1定义置信度为预测正确概率，要求P(correct|confidence=p)=p；页2-3的ECE按bin准确率与平均confidence差加权，页6 Table1使用15bins。它不是缺失层MSE、分割Dice、修正增量收益或被选区域安全保证。目录内此前MRI置信度研究的correlation也不能替代此定义。

页4明确train/validation/test同分布；温度T在validation上用NLL选择，原网络冻结。页6 Eq9对所有类共同用正T缩放logits，argmax不变，因此分类accuracy不变。Table1 CIFAR100/ResNet110的ECE从16.53%到1.26%；页8 Figure4为stochastic-depth模型12.67%到.96%。两个数列不能混用。原文在多个表格有更好其他方法，如Cars/SST等，不能把“常常有效”写成所有数据集最优。

项目影响：温度校准可以成为便宜已知对照，但不会自动产生新病灶能力。正T的二分类sigmoid固定.5也保持logit正负，不过当前FOV流程先patch sigmoid再Gaussian blend，再回native；对每tile先变温度可能经平均改变最终.5二值预测，不能把Guo的argmax不变结论直接推广到这条pipeline。若做校准要冻结位置，保留最终.5任务对照并报告实际输出变化。4已见validation可用于开发温度参数，但不能因此声称独立有限样本临床保证。

## Geifman、El-Yaniv，ICML2019

*SelectiveNet: A Deep Neural Network with an Integrated Reject Option*：[官方页](https://proceedings.mlr.press/v97/geifman19a.html)。实际PDF9页。

页2：coverage=E[g(X)]；selective risk=E[loss*f-selection]/coverage，只评价接受域。页3：主网络有prediction、selection、auxiliary三头，auxiliary对所有训练样本监督，防止仅接受小子集的早期过拟合；coverage约束采用quadratic penalty，联合目标混合系数固定.5。它已覆盖“增加一个selection head”“按coverage学习哪些样本处理”等宽泛机制。其拒绝输出don't know，没有证明另一修正器能修好被拒样本。

页4：需要独立无标签validation对selection score分位数做coverage calibration；coverage校准与带GT风险控制不同。训练target coverage并不必然等于测试coverage，例如CIFAR10 target75%、实际SelectiveNet80.17%、softmax response64.16%。该页文本提取的Hoeffding表达式缺少指数负号，本轮没有另渲染该页核公式，因此不将这一损坏的表达式当已核数值证据；本轮结论只用明确的coverage/risk定义和上述表格。

页5 Table2：CIFAR10 coverage .8时risk .86%对softmax1.05%、MCdropout1.08%。页6 Table3 SVHN .95时SelectiveNet1.40%、softmax1.39%，保留不占优/统计难分的情况。页7 Table5 Concrete回归coverage .8时MSE30.48对35.53，表格relative improvement14.23%。页6叙述中的26.81-30.48%与Table5改善列不一致，本笔记以明确表格数值报告，不把MSE数值误读成相对改善百分比。这些不是MRI任务数据。

项目影响：只在被选tile/患者上Dice更好不能构成完整系统收益。要同时报告所有患者、拒绝比例、拒绝之后实际发生什么、被拒者使用的fallback任务错误、policy成本。保持全部9validation series完整FOV；原8确认留作冻结后独立确认。若换主体网络为SelectiveNet，还需另立充分适配，不能把它当posthoc单阈值完全等价控制。

## Angelopoulos、Bates、Fisch、Lei、Schuster，CRC v4

*Conformal Risk Control*：[官方页](https://arxiv.org/abs/2208.02814)，实际版本v4，2025-06-13，19物理页。**预选协议误写第五作者Zrnic；第一页实际作者Tal Schuster。** 原协议保留，本笔记是明确更正，不按错误作者检索结论。初始发布时间2022不等于所读v4内容均属2022原版。

页2 Eq4：选inf{lambda: n*empiricalRisk/(n+1)+B/(n+1)<=alpha}，空集合fallback=lambda_max。页3 Theorem1要求exchangeable loss functions、loss随lambda非增、right continuity、sup loss<=B，以及几乎必然L_i(lambda_max)<=alpha；保证是对calibration和test共同随机性的**期望risk**，不是每患者conditional安全，也不是95%概率的risk上限。

页5 Proposition1明确非单调loss会破坏直接CRC保证；Corollary1已有**向未来阈值取sup的单调上包络**处理，AppendixA另有渐近方法，本次未完整读附录。因而“发现动作loss非单调”“用包络控制非单调loss”都不能宽称新意。修正支持嵌套、花费递增，并不保证修正后Dice/伤害非增；必须评估真实loss函数或比较原文已有处理。

页5-6的'tumor segmentation'实际为公开**肠道息肉图像**，PraNet、Kvasir/Hyper-Kvasir/CVC/ETIS，校准n1000、评价781图像，1000随机split的meanFNR=.0987/std=.0114、alpha=.1。不是脑MRI/BraTS，也不是本项目4患者能力评价。FNR下降靠扩大预测集合，可伴随FP/体积增加；不同时证明Dice、absRVE或修正净收益。1000随机split不是1000独立患者。

页7-8另有ImageNet hierarchy和QA set-F1例子；QA控制的是候选集合中**最佳**答案F1，不能等同单个分割mask的Dice随阈值单调。预测set越来越大与某个binary mask质量越来越好是不同性质。

## 有限样本检查的实际结论

CPU合成审计真实chunk3d4d86 exit0，独立chunk7afe05 exit0，原图像/任务数据未读。四个observable group各100样本的baseline/action条件risk都精确校准。

| group | baseline risk | action risk | gain |
|---|---:|---:|---:|
| A | .90 | .95 | -.05 |
| B | .60 | .20 | .40 |
| C | .40 | .10 | .30 |
| D | .10 | 0 | .10 |

调用一个group同为100次：最高baseline-risk选A，全400样本错误200变205；两路径成本差选B，200变160；等概率选组的期望错误减少18.75。后者用真实合成条件risk，是oracle/已知cost-sensitive解析控制，不是已训练MRI策略。24排列下gain最大与相对cost最小等价，这仍属此前已读一般defer成本先例。

按baseline高risk依次调用时错误为200、205、165、135、125；调用集合嵌套但loss不单调。这只是一项明确反例，不是CRC算法实测失效率，也不证明当前真实病灶loss一定非单调。

B=1时CRC修正项1/(n+1)：n4为.20、n8为.1111、n11为.08333、n19为.05。零empirical risk也不能使n4/n8通过alpha=.05的**修正不等式**。这不是“小样本CRC永远不能保证”：若lambda_max有事前可证loss<=alpha，empty-set fallback仍可成立，但真实SR/人类defer没有这样的已认证零损失终点。把19series作19独立患者能人为改善表中不等式，却不能满足exchangeability；开发11人、已见验证4人和确认8人也不是本轮随意可用的独立calibration。

## 本轮收窄的新意

校准、拒绝、两路径gain routing、非单调loss包络都已有直接方法先例。剩余值得研究的是：**在同observed源和充分适配任务模型下，真实MRI的可修正余量能否由合法部署特征预测，并在完整患者/实际端到端预算上超越上述强已知控制；若涉及联合动作，超越Dice分式耦合和union-greedy后还剩多少可预测净收益。** 这是待验证问题，当前没有新publication claim。

执行接续见[后续准备](../CALIBRATION_AND_ACTION_GAIN_FOLLOWUP_2026-10-07.md)。

## 校准施加位置的实际补充

本轮随后执行[固定合成位置协议](../CALIBRATION_POSITION_CPU_PROTOCOL_2026-10-07.md)，真实chunk6be8ff exit0。两个tile logits=(2,-10)、权重=(.6,.4)：T1下先sigmoid再融合概率.5284964059342103，为前景；每tile先用T2缩放再融合约.441312，为背景。两tile自身的argmax均没改变。在融合后对最终概率的logit用正T校准，则各T保持最终.5预测。先融合logits是另一个pipeline，T1便与原概率融合不同。

NumPyfloat64和独立Decimal80位解释器最大差2.220446049250313e-16，全部threshold一致，T=.5/1/2/4都保留。只是一个voxel的合成数学检查，非MRI FOV结果、非训练温度参数、非新理论；支持下一轮需要预固定校准位置的实施决定。原生产FOV代码未改。


