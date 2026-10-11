# 首真实病例的损失公式误差归因

在真实资格首case0/native_reference/step0已失败之后，保持失败文件不变。使用frozen_config同一个开发病例、原crop/母GT、journal里实际记录的3套GIN参数逐位反解，而非另抽seed。另用同一CPU functional graph/同一3view logits，分别计算原production deep-supervision+attached KL与独立softplus/xlogy loss，以两次autograd.grad获取全部54梯度。CPU的独立loss必须逐位复现原资格CPU loss值。

随后各自冷初始化副本，赋予对应实际梯度，只做一次真实CPU AdamW，记录两种loss的概率（同一个logits所以相同）、loss、全部梯度、全部参数和moment差。独立loss这一AdamW后model/state hash必须逐位复现原资格CPU step0记录，证明复用相同输入/随机参数/计算结果。仅两个新的诊断CPU更新、0GPU更新；不推进剩余病例，不改变失败gate，仍不是正式训练或医学收益。

对原CPU/GPU比较最差参数的位置，读取原journal两侧实际梯度和更新；记录新两种CPU公式在该位置梯度差、是否改变符号、两侧AdamW实际参数。仅解释已测坐标，不把未测算子归因给某一conv/IN，也不以参数差自动推断临床差。保持3e-6所有原gate不变；本试验诊断结果无论正负完整保存，不以loss标量相同证明梯度相同。

CPU1/interop1/below-normal、RAM/disk8GB、prep7MB/FOV20MB/other22.8MB预算，wall180s，CUDA不初始化，确认集/lockedIXI关闭，不安装/委派/改原进程。
