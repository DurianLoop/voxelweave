# 有界单配方GPU能力探索：仅强度增强20k

前述四臂80k资源规划两次已实际结束并保留失败：52790首10平均.06820370秒/投影5456.296秒；33664全GPU实现首10平均.04590079秒/投影3672.063秒，均超过原3600秒门槛。两次各只发生10更新，不算完整因素实验，不从这20更新得出模型效果。全GPUkernel输入/梯度/同loss预检已通过。

这次不是第三次偷偷放宽80k门槛，而是单独开发问题：保留无增强配方的空间支撑/方向，加回原强度scale/shift，能否改善已见四验证能力。只训练**intensity_only一个新GPU模型，固定20000更新**；完整四因素仍未完成。选择基于已见开发失败，是能力探索，不是确认试验。旧CPU配方不是精确同设备因果控制，所有比较只作描述。

继承981602参数/seed20261004/相同初权重、11开发19series真实observed-only raw PCHIP/observed_shared、physical输入/原生标签监督/外生patient与series/z/patch流、BCE+Dice+.5global/AdamW/cosine/最后checkpoint/.5。intensity_only已608draw预检；正式20000全部输入SHA/primitive对应认证旧CPU训练流，后续须全20000独立tensor reference、源patch和最终checkpoint核验。

GPU按attempt02同full GPU kernels；sample/context/physical image/label/area resize仍CPU冻结生成，同float32 CPUgrid原值传GPU作grid_sample，不加AMP/TF32。复用并认证已通过的attempt02 kernel预检，不重复合成测试；CUDAgrid backward仍不保证bitwise重复。每步loss/梯度非有限停止，单线程/below-normal/15GB磁盘/8GB内存、GPU allocator10%/peak2.5GB/free4GB保持。首10真实updates的**总20000投影≤1800秒**；按更小工作量独立估时，不借单臂预算冒充80k四因素完成。

前一两任务实际exit后才启动；新目录intensity_only_gpu_capability，全部从初权重重建，不续用失败权重。新20k及完整核验完成前验证模型前向0。之后另写37条件19开发+18四验证新binding/evaluator/verifier，111plane，沿原能力门槛与所有空/undefined，任何效果失败保留；当前这些新入口尚需实现。八确认/第二任务网络仍未启用，科学确认0。
