# 本轮接续阅读与创新探索总览

本轮内容、代码、论文原文、运行结果、失败、图片及对话全部存于 `D:\MRI\innovation`。GPU已经获得授权；最新总量仍约1394MiB空闲，未满足完整GPU实验的8GB启动门槛。只查询设备总量，未操作用户训练进程。目标仍active，没有独立确认的可发表claim。

## 阅读与排重

接续CPU阶段已核读5篇3D/损失论文；本次新增IN、AdaIN、GroupNorm3篇原始PDF，共33页可提取正文/表格/图注/参考文献，三页关键公式已渲染视觉核读。合计本接续研究链8篇；此前nnU-Net两篇另计，不重复算新增。Generalised Dice的三张SVG数值表仍未视觉读，保留限制。

“换3D/context/loss/采样/soft-GT/norm”都有先例。AdaIN与本控制的精确operator不同已写清，但该差异不自动构成创新或MRI收益。[3篇内部统计原文报告](literature/2026-10-07_feature_normalization_primary_reading.md)。

## 新增可执行探索

| 阶段 | CPU参数更新 | native完整训练FOV Dice | PCHIP完整训练FOV Dice | 状态 |
|---|---:|---:|---:|---|
| 原全网络、两个固定crop | 1024（继承完成） | 0.351453 | 0.256330 | 独立重放/四增强变体诊断已完成，两臂失败 |
| 固定骨干、bias/full-head四分支 | 4096（新增） | full-head0.590714 | full-head0.372671 | 训练crop可过0.9，全部原完整gate失败 |
| 固定骨干、16tile head两分支 | 2048（新增） | 0.678448 | 0.475659 | 覆盖后改善，仍不满足原门槛 |

六个新增分支共6144次输出参数更新，均单线程CPU、CUDA未初始化；不能包装成一个模型累计7168次训练或19series强任务模型。全部checkpoint/每步记录/四域/empty/undefined保留，模块与functional两种实现的完整FOV预测一致；两张新科学图已实际视觉检查。

[局部head全部结果](MC_RC_3D_FROZEN_FEATURE_HEAD_FIT_RESULT_2026-10-07.md)、[全tile全部结果](MC_RC_3D_ALL_TILE_HEAD_FIT_RESULT_2026-10-07.md)。

内部PCHIP参照IN控制已实现，非同输入primitive与float64 NumPy对齐，三项同输入/三个head重放均0概率/阈值差异。只读一份authenticated observed NPZ，原MR ZIP/NIfTI/GT读取阻断；单个弱checkpoint首tile输出差异不能称改善/损害。[实现预检及两次失败](MC_RC_3D_REFERENCE_IN_PREFLIGHT_RESULT_2026-10-07.md)。

开发标签网格往返19series/11患者完成。患者均值Dice0.96783554，18/19过诊断gate；微小011 Dice0.87741935，保留失败。原float32概率数值门槛14/19过，但全部19二值预测与独立坐标一致；独立float64坐标19/19核对通过，不改判float32失败。001标签往返0.983284高于任务模型0.678448，仍需充分任务拟合。标签参考不是连续预测的数学上界。[完整标签诊断](MC_RC_3D_LABEL_ROUNDTRIP_RESULT_2026-10-07.md)。

## 保留的创新方向

优先研究：充分任务适配后，仅从同一真实观测信息预测具体缺层修正动作的任务收益，并在完整FOV超过强PCHIP与直接任务。SafeRestore/MoEDiff/误差头等先例须公平比较；没有稳定残余则停止正方向。

次级机制方向：在合格任务网络里固定PCHIP内部统计，区分内容改变与统计反馈。模块已准备，科学有效性与新颖性仍未确认。011的标签网格限制是必要训练/评价控制，不能当单独的新方法。

下一步先完成真实GPU资源/数值/速度资格，再冻结19series充分骨干优化/context覆盖配方；四已见验证全部原门槛通过后才公平矩阵，最后才八确认及第二独立训练网络。[候选边界和GPU入口](INNOVATION_NEXT_AFTER_HEAD_CONTEXT_2026-10-07.md)。

所有旧失败/门槛/数据角色保留，八确认未开、科学确认0。旧阶段283个证据文件将在本阶段归档入口逐个重新核SHA；新原文、source、checkpoint、结果、相对链接和视觉登记均独立归档，旧manifest不覆盖。
