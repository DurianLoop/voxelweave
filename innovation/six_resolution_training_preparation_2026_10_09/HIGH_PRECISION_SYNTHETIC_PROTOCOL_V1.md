# 新数值分支的人工资格探索

依据 stable_reduction 的失败与独立 Adam 定位，新建 high_precision 分支。保留全部 54 个 FP32 参数、FP32 optimizer state、同一初始权重和 AdamW 超参数；卷积、反卷积、归一化、激活、中间张量、输出 logits 与 loss 运算使用 FP64，输入人工 view 仍为原 FP32。此分支不是原 FP32 production，也不是正式六臂 runner。

production 用模块图及 FP64 var_mean；独立 CPU reference 用显式 functional 图及中心化方差公式。原 16³、三 view、两步、相同初始化/输入/target、54 参数与 162 state 字段、全部输出概率及 binary 校验不变。绝对数值门槛仍为 3e-6，binary 为 0；不改变 eps、学习率、损失定义，不钳制近零梯度。

每个分支最多两次人工 CPU optimizer update。未通过则原样保存失败；通过也只说明人工 CPU 算术关系。允许后续单独准备人工 GPU/CPU 检查，必须先通过本协议、另冻资源与版本合同；不因此跳过真实全图/19-series资格，不打开确认患者或 locked IXI。

FP64 会增加内存与计算成本，未来真实分辨率必须重新预估并实测；原 FP32 预算和模型资格不能继承。CPU1/interop1/below-normal、8GB RAM/disk reserve 与目录 cap 不变。
