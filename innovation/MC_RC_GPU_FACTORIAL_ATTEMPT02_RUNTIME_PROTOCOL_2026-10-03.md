# 第一次GPU因素资源失败后的新执行实现

原session52790已实际exit1，原attempt完整保留。10真实none updates均匹配原primitive/输入SHA，global/local56/44参数有梯度；首10平均.06820370秒，总80k投影5456.296秒>3600，按预写资源gate停止。不是训练效果失败，没有四臂checkpoint或新验证效果；不能把它记为完整80k。

新attempt02只改计算执行：physical输入重建/context/resize/labels/采样和example SHA仍在原CPU冻结实现；global/local网络、global context grid_sample以及同segmentation_loss放GPU，减少训练中GPU→CPU→GPU及反传往返。坐标grid仍在CPU按原float32公式生成后原值传GPU，不改变patch位置/尺度。这个新执行的训练权重不能与原CPU权重宣称逐值等价；所有四臂统一新执行。

启动前另做无患者、无标签文件的synthetic GPU grid_sample versus CPU reference预检：固定非方形fullshape、首/中/末位置，context值max误差≤5e-5，有限双向梯度；合成CPU/GPU segmentation_loss误差≤5e-5。该预检无optimizer updates，不证明实际训练效果。cuDNN deterministic/无AMP/TF32保持；CUDA grid_sample backward可能使用非确定累加，不承诺整体训练bitwise可重复。单seed只作能力开发，完整checkpoint/实际输入SHA仍保存供实现复核。

四臂/顺序/同GPU/981602参数/seed/初权重/训练患者和series流/原patch支撑/监督/loss配方/AdamW/cosine/每臂20k/最后checkpoint/.5及八确认关闭全部沿原协议。**首10真实更新的80k总投影≤3600秒门槛保持**；再失败则保留新attempt，不反复降低门槛或偷偷换预算。每次都从初始权重重建，不续用失败10更新的权重。

输出新目录mc_rc_gpu_geometry_intensity_factorial_attempt02，不覆盖原目录；只在首attempt真实exit之后运行。四臂全80k认证与148预测/444plane仍需新实现，当前无新能力结果。旧CPU无增强20k和GPU37/111结果保持。
