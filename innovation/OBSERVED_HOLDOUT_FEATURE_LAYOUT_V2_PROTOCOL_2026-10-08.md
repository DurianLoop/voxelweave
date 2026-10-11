# 独立统计重放v2：显式复现生产的retained C-order copy

[原协议](OBSERVED_HOLDOUT_FEATURE_PROTOCOL_2026-10-08.md)、生产19系列/38fold结果、原独立attempt01/源码保留。生产真实exit0（aad9d0）；独立真实exit1（628031），2完整series、5fold通过、3包已加载，在第三系列fold1的retained_statistics严格相等断言失败。不是神经任务收益失败，也不回填原独立为成功。

源码差异：生产先 `a[:,:,kept].copy()` 再计算float64 mean/std；原独立在fancy-index结果 `a[:,:,kept]` 上直接归约。两者的数组内存排列不同，mean/std的浮点归约顺序可能不同。需要新版本复现失败统计，并检查统一布局后全19成功，才将失败归因此差异。

v2只在独立统计函数开始用 `np.array(a,copy=True,order='C')`，明确重放原生产复制操作。不改producer/module、fold、source、metadata、预测、评分或atol/rtol=3e-5；评分仍严格相等，患者聚合1e-12容差仍不变。旧原layout mean/std仍各fold复算，保存逐字段差异；第三series/fold1必须再次与原记录不相等，C-copy后严格相等。另以float64分块二次中心矩/fsum核数学统计，记录最大误差，预定atol=rtol=1e-12；这只核mean/std定义，不要求不同归约顺序bitwise相同。

另存generated source、prereg、output directory，执行前绑定original fail result/source、原production、两个protocol以及生成器。实际总包加载预计19生产+3原独立+19v2=41；counterfactual检查生产38、原独立5、v2预计38，全部计数分开。新作业CPU1/interop1/BLAS1、below-normal、CUDA不可见、1200s、RAM/disk8GB、stage20MB不变；GT/native/验证/确认/lockedIXI/模型/神经/训练0。

布局差异不说明源信息泄漏，也不解释旧direct absolute任务失败；保留所有失败、不调观察误差来制造收益。后续特征仍须配对MRI动作任务端点与完整费用才能判断有用，goal active。
