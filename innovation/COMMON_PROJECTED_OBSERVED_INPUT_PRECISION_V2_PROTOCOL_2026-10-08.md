# 独立核验 v2：区分后端坐标精度和理想坐标误差

[原协议](COMMON_PROJECTED_OBSERVED_INPUT_PROTOCOL_2026-10-08.md)、原 19 系列生产结果和[独立失败 attempt01](experiments/common_projected_observed_independent_2026_10_08/attempt01.json)保持原文件。原独立作业真实 exit=1，3 系列通过、4 observed 包已加载，第 4 包的 sampled_bilinear_all_anchors 检查失败，max absolute difference=3.9674332792838385e-5。原 atol=rtol=3e-5 门槛未通过，不能记为原协议全通过。

执行失败后仅阅读已安装 Torch 的 `ATen/native/UpSample.h`：scale 由 scalar_t(input_size)/output_size 得到，source index 为 scale*(dst+scalar_t(.5))−scalar_t(.5)；`ATen/OpMathType.h` 的 float opmath 仍为 float。原独立核验用 float64 的几何坐标，故把 float32 坐标量化与四角加权实现误差混在了同一门槛。此解释需要新核验验证，尚不将其当已证结论。冻结这两个 header 的字节副本及 SHA，记录本机 Torch 版本。

v2 不改输入模块、原生产结果、观测统计、source、抽样坐标、样点数量、Hermite 算法、训练或任何 task endpoint，不放宽 atol/rtol。另存源码、执行前 preregistration、新输出目录。重新加载同一 19 个开发 observed 包，不读取医学标签/原 native/验证/确认。

- 同库全数组 SHA 重放、完整 NumPy Hermite/linear/tail 数学核验保持原定义及门槛。
- 2D bilinear、z-only 和 raw direct sampled 数值核验，显式以 NumPy float32 重建 scale/source coordinate、clip、floor/neighbor，四角加权用 float64 累加以隔离 accumulation error；门槛仍 atol=rtol=3e-5。这核 float32 坐标下的算子数值实现，不声称等同理想实数坐标或 bitwise 运算。
- 原 float64 pixel-center bilinear 路径仍对全部预定样点计算，保存原 3e-5 门槛失败数、max error、worst ratio 和失败样点坐标/anchor。它作为理想坐标数值差异诊断保留，不再混作后端实现 gate。对照记录 float32 和 float64 source coordinates 的最大差。
- 原第 4 包的失败来源只有在 v2 的预定相同样点上确认原 float64 检查仍失败、float32 算子检查通过，才写为坐标精度差异得到解释。即使如此，原失败仍成立，不将 v2 结果回填 v1。

新核验版本由可审查的文本变换从 v1 生成，生成器、版本源码、header snapshots、原失败结果、原生产结果都先绑定。新作业最多1200s、CPU1/interop1/BLAS1、CUDA不可见、below-normal、RAM/disk各8GB预留，20MB阶段预算不变。追加原19生产+4原独立失败加载；预计 v2再19，总42实际 observed 包加载（hash byte IO不算数组加载）。神经/GPU forward、训练更新0。

本项是失败后的数值核验修正，不是根据分割效果改方法或选择 MRI 结果；尚无任务效益。原训练99542不动；旧 direct absolute failure不以本次浮点诊断覆盖。goal active。
