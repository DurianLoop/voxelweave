# 后续试验依赖与可执行准备

## 先收现有四臂，禁止中途改配方

当前frozen_config明确device=cpu。GPU授权持续有效；最新60c616 total24455/free1394MiB/util91%，不满足已冻结的新GPU阶段≥8192MiB起跑储备。此原因不是权限不足。不迁移、重启或干预session29823及其他PID。

真实terminal exit0后保存ACTUAL_TRAINING_TERMINAL_TOOL.json（保留原工具chunk_id、exit_code、observed_unified_exec_session=29823），再执行原capture_training_terminal.py。它先验证四last2992/11968journal/每患者272曝光及paired母label/geometry。通过才执行原evaluate_matched.py，等待其真实exit0后capture_evaluation_terminal.py→summarize_matched.py。不能拿中间模型先读确认集。

## 普通增强强基线的资格清单

本轮38stresspatch已完成mask/label资格，但未覆盖完整2992训练分布，未读取真实halo MRI，也没有可启动的新2992训练配置。以下是下一阶段的准备，**不是已经执行的训练**。

建议比较同parent/schedule/预算的intensity、intensity+low-pass/resolution degradation、intensity+真实上下文roundtrip；native_reference/raw-PCHIP均保留。坚持当前已认证label/lattice映射、每患者272曝光、last checkpoint、相同crop/flip和优化器初始化。先完整开发schedule资格，不能在4验证患者上选support阈值、尺度或loss。

入口实现必须从父physical cache取真实halo，按crop start/flips及unpadded边界映射；不能只pad当前patch。source_box可能在实际图像域外，box保守超界不等于所有stencil超界；用已独立认证的逐体素正权重支持。几何策略必须GT-free、事先固定，全部患者/series保留。可选的identity/disabled或mask-loss改变增强分布/监督分母，需同策略对照并报告无效比例。原38patch的foreground支持完整不能外推到所有训练patch。

若masked loss，深监督各尺度mask的语义须独立核验；不能随便nearest下采样mask后称完整支持。更不能由input mask推出output只依赖有效输入：卷积扩散和InstanceNorm均须考虑。归一化合成反例已经通过，本轮不修改TaskUNet。可另比较固定ordinary normalization control，但这会改变architecture，须成套matched训练，不可以混入现四臂。

成本需要测source extraction、双插值、mask、缓存/磁盘、CPU/GPU训练以及完整任务推理，记录失败/identity路径和全FOV分割。几何box体素倍数、86.998秒标签诊断或论文设备预算都不是实测训练成本。GPU新阶段用fresh总量查询，不查询/干预其他进程；保留原储备，不安装依赖。

## 具体动作收益假设的严格折外设计

研究问题：合法observed slices/spacing、支持范围、固定模型预测/QC能否在强baseline上预测action前后病灶损害差，并优于按形状QC/cluster/错误成本defer。

开发11患者的所有series按患者归组，任何派生patch、输入和重复series都随患者进同折。若采用5折，固定fold大小3/2/2/2/2；明确这是待冻结候选。每外折task/localization/QC模型仅用其余患者训练，收益头/校准/阈值另用折内cross-fitting。**不得从已见全部11患者GT的19998checkpoint初始化外折任务模型，再声称外折预测独立。**可以用重新训练的同initial模型，或经来源资格的、身份不交叉外部预训练来源，后者目前未取得。

先测动作余量：在折外病人上比较raw/direct task与实际action后完整FOV指标；训练动作损害target可用折内GT，部署特征/动作选择绝不能用missing薄层GT、真病灶ROI、oracle最优action或GT radiomics。特征生成为真实pipeline，定位失败保留。初始优先单个固定action对none/defer，避免未证明的动作可加性；组合动作另测交互。

控制至少包括充分增强task、静态最佳action（仅折内选择）、always、random、强QC/error-cost/defer、预测radiomic cluster/CC过滤及消融“去掉采集可见性”。已有2026集成论文的ranker/固定task权重不是我们的净收益label，但它的强后处理是必比先例。固定病例级/病灶级主要损害及全费用定义，完整患者分母和失败路径都计入；测试方案冻结后8未见确认12series仅打开一次，并独立任务实现复核。当前不运行此确认。

若充分模型没有动作余量，停止收益头方向并保留负结果；若仅高形状QC或PSNR提升、不能改善医学任务，则不写成病灶收益claim。若fold训练资源暂不可用，保存fold/feature/action协议和脚本资格后待fresh GPU，不降能力门槛、不缩患者分母。

## 来源待补

两新增作者稿已经核读，外链supplement、图像像素、最终edited PDF/勘误、作者代码仍未核。VINN多个正文/table不一致、病灶集成weight归一化/OOF映射须查源码后再复现。claustrum外链supporting PDF、供者分折和全atlas是否折内建立仍待取得。VS二值标签不足以忠实构造SynthSeg多组织生成器；合法稠密先验、版本与预算仍缺失。
