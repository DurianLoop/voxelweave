# 接续拟合最后模型的独立核验

在两臂最后 checkpoint 生成前准备核验入口。只有主训练实际 exit0、complete=true、2048 次更新和无 errors 时执行，不读取中途模型评分。

核验两臂完整 1024 history、同一冻结随机 tile stream、每 batch 真实 GT 计数与所有16tile每轮覆盖、全部原/最后 SHA、骨干和所有 head 参数变更；通过 module/functional 两种前向实现核对固定训练crop三个head，原crop gate及完整FOV四域按独立 contingency table 计数重算。

生产 float32 坐标映射与独立 NumPy float64 中心坐标映射比较仍用 3e-6 最大概率差和0二值差异，不掩盖失败。既有标签往返证明两种坐标精度可能超过此数值差；因此另行保存 NumPy 与 Torch float64 坐标参照的比较。两条数值结果分开登记，float64 通过不改判 float32 门槛。任何二值预测差异完整报告，不能挑数值链救科学端点。

所有端点以原生产 .5 预测为准。独立核验通过不等于原拟合gate通过，更不等于原4验证能力、SR新方法收益或发表claim。CPU最多4线程/1interop，自身below-normal；RAM/磁盘各留8GB，无CUDA。
