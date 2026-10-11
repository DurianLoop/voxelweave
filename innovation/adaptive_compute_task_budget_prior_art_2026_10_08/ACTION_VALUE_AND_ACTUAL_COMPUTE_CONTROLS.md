# 当前项目下一步：先量余量，再选择计算

这是本轮原文核读后的研究准备，不是已执行医学实验，不替换原冻结协议、预算、阈值、分组或runner。

## 已有证据为何限制创新表述

[匹配anchor诊断](../MC_RC_MATCHED_ANCHOR_ORACLE_RESULT_2026-10-08.md)中的annotation oracle覆盖99.9649%前景和99.9229%边界、条件forward省算57.6985%，但它使用真实observed标签，不是部署定位；balanced QDA条件省算只有16.7439%，原全部几何gates0/19。ROI很小仍可触及所有重叠batch，不能用面积比例冒充速度。

[费用场景](../MC_RC_MATCHED_ORACLE_BUDGET_RESULT_2026-10-08.md)的balanced QDA A5完整患者等权比1.028456773，B5才.857047311；A/B实际流程分母必须事前固定。两者尚未计定位/生成/transfer/任务等费用，不能挑B或pooled宣称加速。[特征实测](../DEPLOYMENT_FEATURE_COST_RESULT_2026-10-08.md)全19series cold child23.8487972秒，显式生产相位19.377979001只是子集。此次没有重读医学数组或重测这些结果。

因此，本轮不再把泛化ACT/MoE或“边界处多算”列为主要创新。先问：共同初始化、同容量充分适配后，真实合法动作是否还有可恢复病灶收益？如果没有可重复余量，新增value头和动态网络没有推进依据。

## 两个依次验证的假设

H1（恢复余量，先执行）：固定observed CISS的强raw-pchip任务基线经过足够适配后，至少有事前定义的合法局部动作，在开发患者完整FOV中产生稳定的Δ病灶任务增量，同时满足原漏检/体积/合法性约束。native参考用于诊断信息和模型能力，有限网络经验结果不是理论Bayes上界。GT定位oracle只诊断余量，不能当部署policy。

H2（选择价值，仅H1有余量后）：用部署可取得的observed特征预测真实action收益，和已实测的affected-window成本一起选择有限预算动作，相对最强静态、risk/error、不做动作/defer、random和cost-only对照，完整患者收益—实际成本曲线更好。所有策略给相同训练标签曝光、参数/适配机会、动作集、预览机会和预算。规则/预算不能根据已见验证或未见确认调优。

候选可发表句式仅作为待证伪草稿：在已声明CISS稀疏观测与患者分布中，经充分适配之后，病灶action收益预测能够在完整实际成本预算下获得优于匹配强控制的任务收益。未获数据支持前不能写“提出首个”或“显著提升/加速”。

若H1失败：保留完整失败、患者伤害和能力诊断；可继续研究“图像重建增益在任务充分适配后是否消失”的限定结论，但需要事前实用等价margin和患者级区间；单队列11患者/一个弱网络/不显著p值不构成普遍无效性证明。此处不补造margin或自动打开外部/确认数据。

## 本轮补充的实现与成本控制

| 控制 | 执行时需要的证据 | 推翻候选的结果 |
|---|---|---|
| dense-after-mask对真正跳算 | 最终权重、相同完整FOV输入上 dense/cached/真正选择执行的logits、硬预测、任务端点与实际执行次数；注意力/重叠窗口/global context依赖按真实实现处理 | 选择图只掩码输出，kernel执行量没减或输出等价失败 |
| 成本完整分母 | 定位、baseline、所有preview action、失败action、router、生成、DC、传输、缓存/合并、任务forward/后处理全计；CPU/GPU异步以实际流程的wall time为主，分相位避免重复相加 | 优势只在漏算共享初始化/preview/定位时成立 |
| ACT收敛与停止 | 若使用循环修正，验证实际T轨迹和非线性映射；继续保持原合法观测约束 | 只凭ρ(A)<1或几张halting图声称全局保证 |
| 硬路由训练 | 若采用hard top-k，静态检查有无gate amplitude/STE/gather，记录hard assignment与soft mass分别的利用率 | 模型只有balance loss在训练router、无task梯度；专家饥饿未被发现 |
| 同信息曝光强静态 | 最佳固定动作/循环深度与策略从同开发折选；充分任务适配和训练信息对齐；active acquisition不混进固定观测动作 | 给静态同等监督或更新机会后优势消失 |
| 完整任务安全性 | 原full/missing Dice、recall、FP/FN、signed/absRVE和伤害患者逐一保存；患者内全部series合并，患者等权，空值不删 | 只有局部ROI、过滤层、pooled或PSNR好，漏检/患者伤害超原规则 |

不为本轮另写合成资格测试或重做已有software入口。医学链按已授权既有入口走：原native/raw两臂各19998的final与真实exit0、历史/权重来源冻结 → 56完整FOV全部六能力gates和独立strict退出 → 三observed臂真实19series资源 → 冻结充分适配预算/runner → 固定合法action的真实余量与全部成本 → 匹配强控制 → 全组件冻结后8未见患者/12series一次确认。当前11患者/19series开发、4/9已见验证、8/12确认和locked IXI边界保持。

最新 GPU free1394MiB，原训练仍live，所以本轮没有启动新医学GPU实验。GPU授权已经有效，后续满足既定8,000,000,000 bytes启动储备和科学前置条件即可执行，不需要再次询问许可。原两臂总39996更新/30h合同不修改。
