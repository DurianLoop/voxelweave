# 独立新数值版本：双精度归约、FP32存储/卷积的人工资格

ROUND50显示仅改变参考norm精度，不能假定与原FP32 production完整Adam状态一致；旧失败不改。本轮另建实验模型StableReductionTaskUNet3D，保持54参数名/shape、FP32参数与输入、卷积/反卷积/池化/head及AdamW。production norm改用torch.var_mean(input.double(),unbiased=False)、FP64 affine后回FP32；独立CPU functional reference仍用明确centered均值/平方均值norm v2。两者都是新的高精度归约版本，不能冒称原TaskUNet算子逐位不变或原正式六臂资格已通过。

为减少不同但数学等价loss表达的FP32归约差，两个分支的BCE/Dice/attached mean-target KL只在loss中将logits升float64、归约float64。输出和传回参数的grad仍FP32。production BCEWithLogits/kl_div与independent softplus/xlogy表达独立；仍原deep weights4/7,2/7,1/7、consistency.1、KL(mean||each)和默认element mean，target不detach。数学目标不改变，舍入版本改变；不靠eps/lr/小梯度截断强迫通过。

先CPU人工shape(2,1,16,16,16)、seed初值20261009/输入49/target501/GIN480000–480002、3view、两步；每步所有54梯度/参数、162Adam字段、全部3heads/prob/完整二值判断、loss检查。全部maxerror≤3e-6、binary差0，首失败停；两分支各2更新为最大4人工CPU更新（发生多少逐项记录），不运行MRI/GT/parent。

另检查14norm参数/eps与目标nearest-exact独立索引，生产FP64norm和旧NumPy数学检查关联仅说明数学参照，不重复运行已通过的局部检查。独立完整loss v1作为高精度输入公式使用，逐步完整state绑定；任何失败旧代码不修改、另版修正scope明确。

仅人工CPU全通过后，允许另版GPU人工16³两步对独立CPU参考；用户GPU授权已具备。启动aggregate free≥8192MiB（不枚举PID），allocator min(10%,2.4GB/total)、peak≤2.5GB/runtimefree≥4GB，FP32conv/TF32off/deterministic、CPU1/interop1/below-normal、wall180秒、RAM/disk8GB及所有cap不变。GPU人工通过也不能当完整19series/full38/35904或医疗gate；真实资格须单独保留完整scope和allheads/两步/费用。当前先准备并执行CPU，GPU计划需真实结果和fresh资源再决定。
