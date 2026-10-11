# 开发监督规模与采样诊断（无模型前向）

在 20,000 步训练仍进行、验证模型效果未读时预写。只使用已证明的 11 开发人/19 系列原生标签和 case spacing；不加载 MR、checkpoint 或验证/确认标签。本次既有训练配置不调整。

每系列按同一物理平面 shape 与 area label resize，用该 shape 的全零 placeholder MRI，调用原冻结 training_example 32 次。seed 固定 20261006，每系列 seed 再加其固定清单序号；训练调用涉及同样的 z、flip、rot90、强度变换与 foreground/local 位置随机数，因此可描述既有采样的监督分布。每系列等数量诊断不能冒充本次训练的实际 patient-uniform 轨迹。

记录原生前景总量/体积占比、物理 soft label mass、32 次 z 的正/负比例、全 FOV256 与两个 local128 target 的 positive mass/positive pixel ratio，保留每次 target hash。汇总先患者内等权系列，再患者等权；不给验证模型效果或真实梯度结论。此诊断不计训练 update，不计 neural forward。19 系列、608 采样都必须保留。

CPU 单线程，只降低自身优先级，磁盘≥15 GB/内存≥8 GB。逐系列处理，不建立第二个重训练 cache。输出仅 JSON 和来源 SHA，失败不覆盖。
