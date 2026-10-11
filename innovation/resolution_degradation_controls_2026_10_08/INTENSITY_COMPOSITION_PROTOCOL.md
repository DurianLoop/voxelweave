# 原强度管线对新分辨率输入的误差传播检查

必须先观察真实228MRI资格terminal exit0，再读其完整receipt和SHA。本检查重放同11开发/19series/两输入/两stress母patch/三模式，228字段，完整GT/cache/母crop绑定同前阶段；CPU1/低优先级/wall1800秒/stage5MB/磁盘RAM8GB不改。不并发运行本stage第二CPU检查，不安装依赖，不接触验证或确认像素。

重读现有adaptation_paired_pilot/augmentation.py（本轮1f4505）确认gamma依赖整个patch min/max/mean/std，bias再noise。对独立Torch/SciPy重建的两份新MRI输入，执行**同一个已冻结生产强度函数**及旧stress记录的相同primitives和noise_seed，测既有3e-6阈值下最终输入误差是否被放大。这个检查是组合误差传播，不是独立重新实现gamma/bias/noise，也不等于全5984完整强度分布已认证。新真实MRI值、label和所有启用参数保留，不根据结果删病例。

分辨率算子自身padding不变的资格，只适用于强度函数之前。gamma的统计依赖可使padding位置的数值也发生改变，不能声称最终神经网输入的padding仍与identity逐位相等；支持mask不是任务输出安全证书。记录失败字段和实际最大误差，若超过3e-6则阻止新的完整资格/训练，保留原源，不降低门槛。六医学能力和概率/坐标/二值门槛仍保持。
