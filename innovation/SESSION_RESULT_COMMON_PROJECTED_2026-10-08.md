# 本轮入口：共同投影控制与任务效益边界

19开发系列／11患者的共同投影输入已实现，并通过全系列生产和精度明确的独立v2核验。新的direct与旧direct完整输入19/19逐位相同，availability与旧资格相同；后续可复用该数据臂，加入共同投影dense-PCHIP解释插值/投影顺序。没有新增神经训练或MRI任务效果。

- [实现、19系列结果与保留的原失败](COMMON_PROJECTED_OBSERVED_INPUT_RESULT_2026-10-08.md)
- [后续同容量任务矩阵、调用接口和启动依赖](COMMON_PROJECTED_TASK_FACTOR_PREPARATION_2026-10-08.md)
- [两篇感知/失真/码率原文：10文字页、4视觉页；未读范围明确](literature/2026-10-08_distortion_perception_primary_reading.md)
- [可见对话](SESSION_VISIBLE_DIALOGUE_COMMON_PROJECTED_2026-10-08.md)、[交接资料](SESSION_IMPORTED_HANDOFF_COMMON_PROJECTED_2026-10-08.md)、[工具与资源账本](SESSION_EXECUTION_LEDGER_COMMON_PROJECTED_2026-10-08.json)、[冻结清单](literature/common_projected_stage_manifest_2026-10-08.json)

原v1独立gate在第4个observed包失败，3系列完成，保留原source/attempt及exit=1。另存v2沿用atol/rtol=3e-5，显式后端float32坐标；完整Hermite和抽样插值通过，原ideal双精度门槛9系列/30样点失败仍记录，没有回填v1。新observed包加载42次=19+4+19，唯一19系列；native/GT/验证/确认/lockedIXI数组、神经/GPUforward、训练更新0，不包含原live训练。新/旧direct本开发范围exact不外推其他grid/backend，更不证明两种最终编码严格信息等价。

原session99542仍live，最新已观测native15543/new15444/cumulative35133.23273809999s，无terminal。GPU已授权但free1394MiB，不满足新增作业8GB预留；原训练不迁移、不重启。真实完整训练exit0/两臂冻结后才原56FOV/全部6gates/独立strict。此次未读中间模型效益，未打开8确认/12series、已见验证或lockedIXI；旧MIRA/MSValid84保留，根.gitignore/environment.yml哈希不变。

本阶段为实质progress；goal active，尚未达到可发表MRI收益claim。rank/像素误差/感知分布/自监督风险不能替代强任务基线上的患者配对净收益和完整实测预算确认。
