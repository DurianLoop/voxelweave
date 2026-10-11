# 新增输出层/context证据后的创新候选与执行顺序

没有已独立确认的可发表claim。原45 CISS的宽SR损害说法已被反证，addback/QDA/线性策略失败保留；本项没有改比较对象/分母/阈值救旧假设。新增3篇IN/AdaIN/GN原始PDF33页及公式核读，加接续CPU阶段原5篇，共8篇；此前nnU-Net两篇另计，不能重复计新增。

## 现在证据能支持什么

| 对照 | native完整训练FOV Dice | PCHIP完整训练FOV Dice | 实际含义 |
|---|---:|---:|---|
| 原全网络两个固定crop、512更新 | 0.351453 | 0.256330 | 两臂精确训练crop也未过0.9，任务能力不足 |
| 固定骨干、同两个crop、17参数head各1024更新 | 0.590714 | 0.372671 | crop达到0.943708/0.907710，说明局部特征可利用；完整FOV仍弱 |
| 固定同骨干、16个推断tile、17参数head各1024更新 | 0.678448 | 0.475659 | 覆盖与聚合域改变后改善，仍不满足原完整拟合gate |

native也是失败，所以这些差距不能作为SR损害任务的科学确认。17参数只改主head，全部52项其他state保持；实现核验通过而任务gate失败，二者分别记录。原1024次全网络、4096次局部head及2048次全tile head分别计数，不包装成7168次同一网络持续优化。八确认和本项四验证仍未开。

## 优先候选：强任务适配后的动作收益预测

精确假设保持：部署只用同一真实观测层，预测具体缺层修正动作对病灶任务的paired收益，完整FOV超过充分适配PCHIP和同observed直接任务。SafeRestore已有候选动作与风险、MoEDiff已有区域专家，误差头/任务指导也已有先例；独立差异应由信息合同、可辨识收益和公平实证给出，不能只改成非线性网络或模块命名。

前置：11开发/19series充分训练native能力参照、raw PCHIP、同observed直接任务、resolution randomization。相同监督/初权重/患者流/容量/总计算预算；native只是训练/能力上限参照，不是稀疏部署输入。原4已见验证/9series的全部能力gate通过，全部full/anchors/missing/tail、漏检/FP、体积/表面端点和空/undefined保留。未出现稳定可修正残余就停止正方向；不能开启八确认或换网络寻找有利分数。

## 第二候选：内容与内部统计反馈的控制

新模块已实现并通过数值预检：PCHIP参考流独立逐层推进，candidate使用参考均值/方差。三项同输入自重放全部概率/阈值0差异，两个非同输入primitive核对float64 NumPy通过。只用authenticated observed NPZ；原MR ZIP和NIfTI/GT读取屏蔽。v1数值失败和v2 ZIP守卫失败保留。

与AdaIN不同的operator定义已写清，但“参考统计”不是新颖性已确认。当前只有弱checkpoint单个无GT首tile的输出敏感性，没有有益/有害方向证据。将来用合格checkpoint和全部预写case/domain检查ordinary/reference-statistics，保持相同tile plan、容量和两流额外计算预算；差值是这个具体干预的效果，不是可加的全网统计因果百分比。

## 最短后续顺序

1. 完成开发标签网格往返对照，区分hard GT重采样/回映与任务模型能力限制。原生产float32和独立float64坐标两路全部保留，不选有利链；标签参照不是连续预测性能的数学上界。
2. 核验GPU当前totals。只有新的free>=8,000,000,000bytes，才执行已准备的新完整GPU资格入口；原4GB运行、2.5GB peak、float32、3600秒门槛保持。tiny合成FP32误差约1.8e-6，但整次预检未通过、BF16未测，不算GPU完整资格。
3. 按真实GPU实测资源/时间，再冻结新的骨干充分优化与context/采样覆盖开发配方。可考虑已知学习率/更新量/主head初始化或norm配置控制；不得只用单crop或冻结特征改善代替全19充分适配。CPU实测全骨干单臂20k约20小时，不未经估时启动两臂20k长训练。
4. 原4验证能力通过后再做公平矩阵；具体收益标签与策略只在开发患者构造。最终方法/端点/阈值冻结后才8确认及第二独立训练任务网络；小样本不预保证发表。

已准备GPU命令（只在fresh totals过门槛时执行；attempt02还未启动）：

```powershell
nvidia-smi --query-gpu=timestamp,name,memory.total,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits
& 'D:\conda\envs\MRI\python.exe' -X utf8 -B 'D:\MRI\innovation\experiments\run_mc_rc_3d_gpu_fit_pilot_totals_v2_2026_10_07.py' --attempt 02
```

最近totals空闲1394MiB，不能用CUDA另一个接口报告的约23GB替代共享物理显存读数。不枚举或操作用户训练进程，不更改根环境或.gitignore。完整19series正式schedule仍待资源资格后冻结，不把此候选计划说成已训练模型。

详细证据：[局部head](MC_RC_3D_FROZEN_FEATURE_HEAD_FIT_RESULT_2026-10-07.md)、[全tile head](MC_RC_3D_ALL_TILE_HEAD_FIT_RESULT_2026-10-07.md)、[内部统计资格](MC_RC_3D_REFERENCE_IN_PREFLIGHT_RESULT_2026-10-07.md)、[3篇原文排重](literature/2026-10-07_feature_normalization_primary_reading.md)。
