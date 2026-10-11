# 内部IN参照控制v2数值实现补充

首版在synthetic batch2×16³同输入自重放失败：三个head概率最大误差2.24709511e-5、1.26659870e-5、2.45403498e-7，二值预测0差异；超过原3e-6门槛。原模块/预检/失败和单独测量记录保留，不能将其写成通过。

新版本不改原数学operator或门槛。将直接计算`gamma*(candidate-mu(reference))/sigma(reference)+beta`改写为数学等价的残差式：`original_IN(reference)+gamma*(candidate-reference)/sigma(reference)`，sigma=sqrt(population_var(reference)+1e-5)。reference_IN直接使用原PyTorch kernel，使零输入差异沿双流逐层精确为零；无相等检测分支、无阈值修补、无替换candidate结果。

除原3项同输入/3head资格外，先用两项非同输入synthetic primitive检查残差式与独立float64 NumPy定义的归一化结果（rtol2e-5、atol3e-6）。此控制验证实际candidate变换，避免只靠零残差恒等性声称实现正确。所有数值观察在断言前保存。

仍先自重放通过再打开001的label-free observed PCHIP/linear首tile，无任务收益端点。首版失败与本补充不能改变checkpoint、输入信息、原任务能力gate或开启验证/确认。
