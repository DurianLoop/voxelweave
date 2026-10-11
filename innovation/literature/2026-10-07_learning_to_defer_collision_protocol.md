# 收益选择与 learning-to-defer 的原文碰撞准备

在低 LR 效果尚未打开时预选两篇公开方法原文，依据机制而不是性能结果：Mozannar/Sontag 2020，Consistent Estimators for Learning to Defer to an Expert（arXiv:2006.01862）；Madras 等 2018，Predict Responsibly: Improving Fairness and Accuracy by Learning to Defer（arXiv:1711.06646）。题名/作者必须在实际取得 PDF 后核对；标识与题名不匹配时不能沿用预期叙述。

问题：如果缺层修正候选经过同一个任务网络后就是若干可计算预测器，那么基于 observed 预测其任务损失差并决定采取哪个动作，在方法层面可能是已有 defer/routing 的实例。需要核对已有损失、可见信息、训练监督、专家正确率估计、预算与风险边界。它们不是 MRI 临床验证，不能把分类一致性理论直接搬到 Dice 比值或病灶体积。

只使用公开 arXiv PDF/正式公开 proceedings 路由，单请求 <=25s、每文 <=20MB、每文 <=40 物理页；所有响应/提取/SHA/失败留存。取得和阅读分开登记；未核全文不计新增原文。没有 MRI/GT 加载、训练或 GPU 初始化。
