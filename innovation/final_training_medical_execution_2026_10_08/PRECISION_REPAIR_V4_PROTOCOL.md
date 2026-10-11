# 最后模型坐标精度修复与全部 56 FOV 核验

单病例隔离结果仅支持一个病例的误差来源：生产与 functional 的物理概率场逐位相同，float32 native 映射误差 3.039836883544922e-6；相同物理场采用 Torch float64 坐标映射、最后转换 float32 后，对独立映射误差 4.547473508864641e-13。这不是全队列资格或医学成功。

另建 production V4，仅将最后 physical-to-native 概率插值的输入改为 float64，并将 native 输出明确转为 float32。神经网络、两臂最后19998权重、MR输入与其float32重采样、窗口/权重/融合、阈值0.5、病例集合、患者先聚合、医学六门槛均沿用冻结合同。旧代码和旧结果不修改。不得放宽 3e-6/3e-12 概率门槛或零二值差异要求。

一次新入口逐病例执行 V4 完整生产 FOV、独立 functional FOV/NumPy八角坐标核验、无损预测跨reader重读、独立计数/精确分数患者聚合。共两臂各28series（开发11患者19series，已见验证4患者9series），不是56患者。所有病例执行，不跳过原数值通过病例。记录新概率hash、相对旧二值预测变化及新医学结果；即使数值合格也不得宣称医学门槛合格。GT只在两条完整推理后读取。

不重训、不挑选checkpoint、不读8未见确认患者或locked IXI。V4原型是数值修复，不主张方法创新。单一入口内两条完整实现的比较不等于第三次独立跨进程重跑；来源和实际退出单独绑定。

CPU4/interop1、below-normal，仅此进程；不初始化CUDA或操作其它PID。每次调用resource_guard保留RAM/磁盘各十进制8GB，wall3600秒，本阶段新增保存10MB上限。GPU用户授权仍有效，最新free1394MiB，未达到原8GB启动条件，因此本项继续CPU。新输出用排他创建和原子进度保存，失败完整留存。模型权重和输入/旧结果来源在结束时重新核对。

入口：`verify_precision_repair_all56_v4.py`，实现：`production_probability_mapping_v4.py`。输出：`precision_v4_attempt01/receipt.json` 和56个压缩二值预测。
