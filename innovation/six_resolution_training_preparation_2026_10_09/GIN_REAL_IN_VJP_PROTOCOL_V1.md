# 卷积之后 InstanceNorm 的局部反向隔离

前一 v1 局部卷积诊断已真实 exit0：同一输入/同一 cotangent 只换卷积 backend 不改变最差坐标符号，换 cotangent 则改变；整层 gradient 两设备分别逐位复现。现在只新增一个独立诊断版本，不编辑已执行文件。

复用同一病例、三视图、母 GT、cold-init 和损失。CPU/GPU完整图各3 forward、1 backward、optimizer0；在 decoders.2.layers.3 的输出和 decoders.2.layers.4 的输出同时记录 cotangent。将 IN 的输入来源、上游 cotangent 来源及 IN backend 做2×2×2隔离，每组合三视图，总CPU12/GPU12局部 IN VJP。原设备原输入原上游的局部 dx 必须逐位复现完整图 conv-output cotangent，保存比较统计。用 float64 NumPy population-variance、eps1e-5 和解析 IN 导数独立检查完整 dx；再用 float64交叉相关将 dx 映射到原最差卷积权重坐标，减少下一层卷积归约差干扰。

不以其他设备的反向公式代替 production；不修改优化器、norm、阈值、患者选择、确认集。记录的是该坐标的归因；即使发现 IN backend 的影响，也不推断其解释其他层、其他病例或临床效益。资源沿 local VJP v1全部限制及剩余预算算法，wall600秒、receipt180KB；中间数组只在内存。
