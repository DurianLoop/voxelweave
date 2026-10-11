# 不改变失败门槛的独立定位

重现 stable_reduction_model_cpu_attempt01 的 step0：同初始权重、16³人工输入、三 view、人工 target 和原 AdamW 超参数。只运行两分支各一次人工 CPU 更新，不打开 MRI/GT/parent，不初始化 CUDA，不运行 step1。

绑定原失败记录，逐一核对 54 参数与 162 optimizer 字段的 max error。为每个参数暴露最坏更新坐标、两分支 gradient/state/update，用 NumPy FP64 首步 AdamW 公式独立预测全部参数。保留 parameter > 3e-6 的失败，不调 eps、不钳制梯度、不降低门槛。

结果解释范围只到本人工更新，不能外推到真实 GPU、医学收益或论文 claim。
