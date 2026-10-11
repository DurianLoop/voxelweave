# 作者源码核对后的binary loss CPU准备

公开论文直接链接mlyg/unified-focal-loss；按commit411c9c5ce43b2ef847f0903d1b841512ad8d2eee（2022-05-13）读取README和完整loss_functions.py，Git blob与SHA验证。原文件第262行缩进错误，不能原样parse/import；保留原字节、不安装TensorFlow、不运行作者包。

源码的channel0是背景、channel1是前景；Tversky分母tp+δfn+(1−δ)fp，与正文扁平Eq18的系数顺序有出入，按源码记录、不默默交换。FT loss先按每个image的spatial axes统计，再对batch/classes平均，不是本基线跨两个patch合并的single foreground Dice。CE项只对background乘p_foreground^γ，前景项不抑制。FT背景项1−TI，前景项(1−TI)^(1−γ)。weight在代码乘FT，而文字λ常乘CE；.5时相同，其他权重需明确。

实现单logit sigmoid binary adaptation，显式epsilon=1e−7、weight=.5、δ=.6、γ=.5；软label允许[0,1]，用(1−g,g)两class，保留作者per-image/class平均和clip语义。它是新CPU移植准备，不是原Keras训练复现或新loss。

用独立逐image/class NumPy公式核scalar value、24选定logit的central finite-difference梯度；额外空/全前景、极端logit、softlabel、同错误量FP/FN方向。仅合成数值，没有MR、network forward或训练updates，不据toy值推断真实任务收益。通过后才能考虑另写同预算损失能力实验；不改冻结20k基线。
