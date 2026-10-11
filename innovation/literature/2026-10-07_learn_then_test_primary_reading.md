# Learn then Test：有限策略、多风险与排序的直接已有方法

官方来源：https://arxiv.org/abs/2110.01052 。本地 [原文](source_cache/learn_then_test_primary_2026-10-07/learn_then_test.pdf) 为 arXiv:2110.01052v5，侧栏 2022-09-29；封面日期 October 3, 2022。作者 Anastasios N. Angelopoulos、Stephen Bates、Emmanuel J. Candès、Michael I. Jordan、Lihua Lei。35 个物理 PDF 页。

阅读范围：接续前已完整选读 1–9、11–12 共 11 页；本接续补读 13–15、22–23，并复读 2–6。累计独特完整选读页为 1–9、11–15、22–23，共 16/35 页；不称全篇/全部证明读完。实际 render 并 view_image 核页 4、5、6、14、15，共 5 页。下载/渲染原记录 reading=false/visual=false 保留，实际阅读另存 provenance。

页 2 的 calibration 是 i.i.d. 样本。定义 P(R(T_hat_lambda)<=alpha)>=1-delta：概率对 calibration 抽样而言，不是每病例保证，也不是 CRC 的期望风险保证。无可认证策略时可不返回 RCP；不会凭空认证 fallback。页 3 Theorem 1 将每个固定候选的有效 p-value 和 FWER 检验组合为整个 certified set 的风险保证，无需风险随 lambda 单调。

页 4：同一 certified set 内可用相同 calibration 数据挑选另一性能指标最好的候选，风险保证仍覆盖整个集合。这个许可不允许看 calibration 后另训模型、增添未测试的 grid、改损失定义或把选择后的效用估计当独立验证。Bonferroni 对策略数 N 校正，允许候选 p-value 相互依赖。连续 bounded loss 使用 Hoeffding-Bentkus；这里的 exact binomial 是本合成审计的 binary loss 专门检验，不把任意连续 Dice loss 当 binary。

页 5 Algorithm 1：先验顺序、首个不拒绝即停止；多起点用 delta/|J|。原文明确顺序不可看当前 calibration 数据。页 6 Proposition 6：同一候选多个风险“任一个超标”为 union null，各风险 p-value 取 max，随后跨候选做 FWER。不是 min，也不必简单再乘风险个数。

页 22–23 Appendix D：用额外 graph selection 数据选择 promising path，fresh testing split 才用于固定序列检验；需去除重复候选。这是“学习检验路径”的已有办法。不能把4个反复使用的验证患者切成 series/tiles 后称 fresh independent 数据；本项目11开发/19series、4已见验证/9series、8未见确认/12series的角色继续保留。

页 11–15 的实例分割是 MS-COCO 自然图像、多对象/多类别系统。页 15 记 5000 验证点拆为 3000 calibration /2000 validation、1000次随机拆分，并给50x5x25候选 grid。它不是脑 MRI 结果，不把重复拆分人数相加。页 14 Figure 9 图注说从左至右 coverage/IOU/recall，但实际轴为 Recall/Mean IOU/Mean Coverage；图注 alpha3=.25，页15正文 alpha第三项=.75。保留该原文表述歧义，不自行将某数字当经复现的正确参数，也不据此移植结果。

页 15 说明这些保证是 marginal，不能保证各病灶大小、扫描协议或人群 strata 的风险相同。当前相同患者多series的相关性必须在患者层处理。若要子组保证，须预先定义子组与检验，不能事后挑有利子组称保证。

对本项目的限制：有限非单调策略、多风险安全选择、graph learning、认证集合内优化 utility 均已有直接先例。候选新意只能继续检验充分适配 dense/direct/SR 后的真实可修正余量、observed-only特征对完整患者收益的预测，以及计入全部成本后是否超过强cost/defer/union-greedy/random。LTT 应进入强对照。

[精确排序反例协议](../LTT_ORDERING_COUNTEREXAMPLE_CPU_PROTOCOL_2026-10-07.md) 与 [审计结果](../experiments/ltt_ordering_counterexample_cpu_2026_10_07/attempt01.json)：n8、alpha .3、delta .1、两策略真实错误率 .31；固定先验顺序FWER .05137983744；按同calibration排序再用未校正固定序列FWER .10011978719；Bonferroni此例没有认证。独立整数枚举65536个binary outcome与Fraction81联合计数精确一致。这是已知检验条件反例，不是MRI发现/新理论。
