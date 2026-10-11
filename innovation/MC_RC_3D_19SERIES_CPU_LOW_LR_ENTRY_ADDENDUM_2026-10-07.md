# 全开发 series CPU 资格的可执行接续绑定

这是 [原资格条件](MC_RC_3D_19SERIES_CPU_QUALIFICATION_PREPARATION_2026-10-07.md) 的具体入口，低 LR 两臂效果未打开时准备。它不是正式强能力训练。入口 `experiments/qualify_mc_rc_3d_19series_cpu_low_lr_2026_10_07.py`，独立无更新核验 `experiments/verify_mc_rc_3d_19series_cpu_low_lr_2026_10_07.py`。

来源明确绑定当前 low_lr 两臂最后 1024 checkpoint。启动前必须：主训练/独立重放实际 exit0、complete、errors=[]；两臂全部原拟合 gate 通过；module/functional/生产坐标 replay 通过；float32 生产与 NumPy 坐标两臂严格 <=3e-6 且 0 阈值差异；独立 float64 通过。实际退出状态必须由本次 observed-exit receipt 给出，不从 JSON complete 推测进程退出。若不满足，本入口保持准备，不运行、不改门槛。

从已有固定 metadata 中只选择 development 的 11 患者/19 series；fixed_cases 会校验验证的既有元数据清单，但不加载验证 MRI/GT、不计算验证效果。按患者排序、各患者 UID 排序后，以 SeedSequence(20261007) 分配独立 series 置换和患者排序随机流。轮数为患者内最多 series 数，每轮每患者一次，患者内置换列表按轮循环；预期 33 步/臂，但由固定数据计算后冻结。两臂共享完整事前流。每 batch 的原 FG/background-center clamp、三轴 flip、强度增强采用 SeedSequence([20261007, step])，两臂 GT/primitive 逐项一致。新增 augmentation 或对齐方案均不加入。

每臂依次缓存 image+float32 label，读已认证 native/PCHIP 和原 native 监督；不向磁盘写体积缓存。使用原 sample_batch、模型、三尺度 BCE+Dice；从各自单 001 最后模型出发，新 AdamW lr=.001、weight_decay=.0001，仅测资源/有限梯度，最终权重 SHA 记录后丢弃，不保存新 checkpoint、不评分，不累计为正式更新。

4 intra-op/1 interop、自身 below-normal、无 CUDA；逐 cache/逐 batch guard，RAM/磁盘各留 8GB、总墙钟 <=1200s、输出 <5MB。分开记录 cache、sample/hash、forward/loss、backward、有限梯度检查、optimizer.step 和真实整步时间，首两步标为 warmup，median/max 明确区分。需要全部计划更新、19 series 全覆盖、患者均衡、两臂流/GT/primitive 完全一致、首步 encoder/decoder/ups/heads 梯度非零、所有参数梯度有限。

本资格不进行 19 series 完整 FOV 推断；其 1139 tiles 的真实推断成本另作 bounded 无评分计时，在写正式训练预算前测量。不能仅根据本资格纯更新中位数忽略该成本。若两臂低 LR 拟合不通过，当前资源资格也不被偷偷改成诊断。所有失败保留，四验证/八确认保持关闭，可发表 claim 仍未确认。
