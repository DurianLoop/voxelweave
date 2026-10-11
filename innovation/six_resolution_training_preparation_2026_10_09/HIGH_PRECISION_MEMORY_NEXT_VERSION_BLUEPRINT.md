# 全patch成本失败后的具体准备

已执行来源：probe_high_precision_fullpatch_cost_v1.py；实际c4be7c exit1/no session；首路forward未完成、0optimizer update。下一版本不得更改该失败文件、扩大2.4GB allocator、减小正式patch后冒充原尺寸通过，或修改其他进程。

下一步先暴露首路forward的layer、仅本进程allocated/reserved与张量shape，明确峰值来自何处；源码另版本，独立receipt。若首路forward已超限，仅offload后两路view不够，必须解决单图内部峰值。

可试结构：将FP64归一化前向与解析VJP包进新的自定义autograd版本，减少中心化、乘法和仿射操作同时存活的大临时张量；输入/中间保存使用独立版本activation recomputation或CPU offload。保存的FP64输入和梯度不能被量化，affine参数/AdamW仍FP32，eps/loss不变。先验证输出、dx、dgamma、dbeta对显式FP64独立公式，随机/常量/近常量/稀疏支持输入，原3e-6 gate；再做多步有限差分，不复用曾失败的最大h作为唯一资格。

层次顺序：算子数学 -> checkpoint/offload前向与VJP -> 同16³三view两步54param/162state -> 严格deterministic GPU/CPU -> 原64x128x128完整人工图在相同cap -> 全尺寸独立对照和19series费用/病例资格。每层都有新版本source binding与真实终态，前层失败不启动后层。

可行性尚未知；完整人工GPU/CPU成功也只是工程数值证据，不是发表claim。所有医学数据/外部权重/确认患者保持按原冻结合同的pending状态。
