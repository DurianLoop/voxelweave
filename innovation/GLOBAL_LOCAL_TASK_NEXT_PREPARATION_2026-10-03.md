# 能力验证之后的创新候选与后续实验准备

本文件在当前固定训练完成前准备，不用验证效果倒推本次架构、阈值或预算。实际能力结论以最终报告为准。新论文三篇、334 文字块，旧 MC-RC 补读 19 块：VS cascade、嗅球、Unified Focal Loss 均是能力/对照先例，不能用其组合宣称创新。

当前角色与 6×5 条件、预算公平和启动门槛另存 [机器可读准备](experiments/global_local_fair_matrix_followup_preparation_2026-10-03.json)。这是在旧规格上更新已合格角色的准备，不是矩阵已执行或新预算已冻结。

完整失败结果现在已取得；下一 CPU 工作具体细化为 [冻结模型的开发可拟合性诊断准备](MC_RC_FROZEN_GLOBAL_LOCAL_DEVELOPMENT_DIAGNOSIS_NEXT_PLAN_2026-10-03.md)，先查19训练输入的完整FOV表现，避免仅用前景patch判断能力。新入口尚未编写，该诊断未执行。

| 工作项 | 可执行入口/现有准备 | 如何否证，何时启用 |
|---|---|---|
| 当前能力基线 | 最后 20,000 checkpoint；九系列×两输入；完整 native grid 和固定 .5；独立计数/距离与 54 plane 重放 | 先过原写 full/missing/recall/体积/漏检门槛；失败停止作重建评价器 |
| 若能力失败：定位可拟合性与优化 | 19 开发标签的 608 次无前向采样诊断已实现；新 loss 正文记录前景/背景取舍和实现歧义 | 先写新协议，用既有开发患者、同架构单病例拟合；不得拿验证患者训练，再宣布验证；loss/采样对照同初始化、draws、budget、endpoint，不事后改门槛 |
| 若能力通过：原生能力控制 | 稀疏接口已逐案证明；native 完整 MR 还需单独 loader 与数据证明 | 另写仅开发/验证的 native 控制协议；完整输入不能混进稀疏分支；若原生仍失败，不能解释 SR 缺层收益 |
| 训练曝光×统计×输入矩阵 | 已有原 3训练曝光×2统计×5输入规格；新全视野模型可用作相同容量基础 | 随机初权重、patient draw/augmentation、总更新和最后 checkpoint 公平；matched raw PCHIP 保留；native/raw/mixed×observed_shared/full_own 各 condition 完整报告 |
| 直接分割与随机分辨率 | Soft spinal/DRIPS/SynthSeg 等直接先例及当前物理上下文实现 | 同 observed 信息和监督预算，不拿额外模态/GT crop/多模型集成作同容量；若直接任务已够好，复杂重建收益需重新证明 |
| 可观测局部修正：仍是假设 | 只有真实 observed 强度、位置/物理 spacing、已有预测的不确定性可作输入；不读取隐藏 MR 统计或 GT ROI | 先证实适应后仍有可修复缺层残余；对照 PCHIP、固定系数、无条件、同容量 task-loss、随机策略，守住边界/漏检/体积及 anchors/tail |
| 最终确认 | 固定 030/029/019/028/031/026/027/015 八保留人、十二合格系列 | 方法/阈值/训练身份/端点冻结后才开；患者聚合与患者 bootstrap，全部病例；第二独立训练任务网络的一致证据，而非本轮同架构重放 |

尚未执行的正式矩阵、native 控制、loss 对照、具体修正和八患者科学确认都不写成完成。GPU 仍占用；新 GPU 任务不启动，不操作用户终端训练。没有可发表且独立确认的 claim，研究目标保持 active。

后续可运行的实现入口是本轮 evaluator/独立 verifier；已完成目录使用 exist_ok=False 防覆盖，不能原地重跑当新复制。正式矩阵和 native loader 尚不是可直接运行入口，需先具体实现和单独输入核验。
