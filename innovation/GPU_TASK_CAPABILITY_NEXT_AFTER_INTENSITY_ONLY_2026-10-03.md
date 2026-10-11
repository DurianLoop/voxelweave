# 下一强任务能力准备：不再只用弱评价器解释MRI重建

当前无自身live训练/评价。GPU已被用户明确允许；固定11开发19series/四已见验证9series/八关闭确认12series，不改角色。无增强与intensity-only两种完整20k都失败，现有981602参数/global8channels/local16channels模型不够作为重建评价器。原MC-RC作者nnU-Net v2约每fold250000更新、五fold及2D/3D集成的阅读记录已存在；当前单seed20k不声称复现作者能力。

| 优先顺序 | 具体可做工作 | 要核的结果和边界 |
|---|---|---|
| 1 | 独立native参考loader的header/UID/RCZ affine、完整MR source像素、label轴/遮罩、observed package层抽取一致性；限定开发/验证，标签可监督，八确认关闭 | 当前已有observed认证可作抽层SHA对照；native完整MR不能走observed部署接口，不能把隐藏统计带入稀疏分支。先准备/认证，不偷换本轮输入合同 |
| 2 | 更充分的3D或较宽2.5D任务基线，对物理context/foreground监督/完整FOV inference分别预检；GPU真实首更新梯度/显存/时间估算后单独冻结架构与预算 | 并非nnU-Net名字或参数量就算强能力，先训练内完整可拟合性，再原四验证门槛。单项loss/增强已知，不作新贡献 |
| 3 | native参照与observed raw PCHIP同执行/同预算/同初权重与patient stream，解耦输入信息上限和任务能力；明确native只是外部参照 | 两输入均弱说明评价器不足，native强/PCHIP弱也不能直接证明SR机制；保留所有域/TP0/空/undefined |
| 4 | 同observed直接任务和采集分辨率随机化强基线，再原6×5输入×训练曝光/统计矩阵 | 容量/总更新/监督/最后checkpoint/阈值/患者权重相同；完整对照后才谈某重建特定残余 |
| 5 | 残余真实且稳定时才开发具体observable政策 | 特征应预测action gain，而非仅预测错误；比较无条件/固定系数/随机/同容量/同预算，旧失败策略不改名重启 |

新native-loader/强3D架构/正式GPU矩阵运行器尚未实现；本文件不拼接虚假的可执行命令。已有可复用部分包括observed-only packages、源case manifests、full-affine metrics、独立label/bincount与NumPy坐标/覆盖重放、GPUfloat32 runtime和梯度预检、完整四验证gate。正在使用的旧代码/协议/结果/失败source SHA保持。

在新的训练source冻结之前，必须明确训练输入是否完整native、observed-only或混合、统计策略、GT只用于训练监督/最终评分、z上下文物理mm、patch采样/面积软标签、所有label/source/code/checkpoint SHA、更新预算和所有资源守卫。GPU可用不代表自动增大实验预算；以新实际资源测量与问题所需证据合理选定，不降低已执行失败attempt的历史门槛。

任何新patient/series效果都是开发验证，四验证此前已用；八確認仅在最终方法/训练/阈值/主端点/聚合冻结后与第二独立训练任务网络一起验证。当前科学确认0，目标active，没有可发表新claim。
