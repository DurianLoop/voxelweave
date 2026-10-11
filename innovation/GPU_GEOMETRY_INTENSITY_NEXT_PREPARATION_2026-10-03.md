# 下一GPU能力阶段的具体准备

**本文件原动态内容现为历史：25991/97494/67623/84382均已经实际exit0。** 单intensity_only20k、全20000训练核验、新37评价/111plane均完成；四验证full Dice .222203、仍5/6gate失败。当前没有自身live任务，新的[强任务准备](GPU_TASK_CAPABILITY_NEXT_AFTER_INTENSITY_ONLY_2026-10-03.md)和[最新判断](INNOVATION_DECISION_AFTER_INTENSITY_ONLY_2026-10-03.md)覆盖下文“待实现/待poll”。两个80k资源失败仍保留、四因素未完成、不重启。

前置新无增强20k与GPU37完整评价/111plane核验均实际结束；原四验证gate失败。当前允许GPU，根环境/.gitignore和用户终端训练不操作。四因素首[GPU协议](MC_RC_GPU_GEOMETRY_INTENSITY_FACTORIAL_PROTOCOL_2026-10-03.md)/[运行器](experiments/run_mc_rc_gpu_geometry_intensity_factorial.py)的session52790已实际exit1：10updates、总80k投影5456.296秒>3600资源gate。新[执行协议](MC_RC_GPU_FACTORIAL_ATTEMPT02_RUNTIME_PROTOCOL_2026-10-03.md)/[全GPU运行器](experiments/run_mc_rc_gpu_geometry_intensity_factorial_attempt02.py)的session33664也已实际exit1：10updates、3672.063秒>3600，两个失败完整保留，不重启。全GPU数值预检通过，context误差2.98e-7、梯度7.28e-12、loss1.19e-7。

当前另立[单配方20k能力协议](MC_RC_INTENSITY_ONLY_GPU_CAPABILITY_PROTOCOL_2026-10-03.md)/[运行器](experiments/run_mc_rc_intensity_only_gpu_capability.py)，session25991，intensity_only单臂、保持初权重/采样/监督/原loss与budget20000/最后权重/.5；首10总20k投影≤1800秒。它是有界能力探索，不冒充完整四因素或精确CPU/GPU控制。动态输出会变，不能以历史SHA判断最终完成。

| 工作 | 已实现/已实际运行 | 尚须做 |
|---|---|---|
| partial输入 | 仅几何/仅强度接口、608原流、1216新输入/整patch通过；零前向 | 多患者20kstream的全量认证，不能用608替代 |
| GPU运行库 | synthetic分支CPU/GPU误差预检及重复一致；同训练checkpoint六plane mask0差 | GPU训练反传/首10真实更新耗时由新运行器实际输出取得，不能从推理预检推定 |
| 四因素公平训练 | 四臂同GPU/同初权重/seed/流/原patch支撑的运行器已实现，两次资源预检失败保留 | 完整80k仍未完成，不能报告因素因果；需独立规划资源，不续用失败权重 |
| 有界intensity_only单配方 | 全GPU实现已另立20k协议并启动25991；复用认证kernel预检 | 只poll25991直到实际exit，不重启；全20000新partial输入与权重verifier/37评价/111plane尚须实现 |
| 新完整评价 | 复用原37条件、每臂111plane的具体规格 | 四臂148预测/444plane新binding/evaluator/verifier尚未编写/未运行；不拼虚假的可运行命令 |
| 创新比较 | strong raw PCHIP、直接任务/分辨率随机化和native/6×5规格 | 能力证据充分后才实施。CPU旧两臂只是历史对照，不等于GPU精确因素控制 |

四验证020/022/024/025仍是已见开发验证；八确认030/029/019/028/031/026/027/015不开效果。训练内拟合门槛和四验证门槛不能混用，single-seed因素差异不作群体因果/显著性。

若首10真实更新预计总80k>3600秒或资源/非有限检查失败，保留完整失败JSON/traceback/已经发生的updates；另立新attempt，只在原进程实际结束后处理，不降低正在运行的资源门槛。GPU不足不枚举/杀其他进程。每实际draw输入SHA和primitive对应认证旧CPUstream，关闭因素不改变采样。

全80k verifier计划用原sampler与冻结metadata、独立tensor assembly/编号plane映射/最后checkpoint认证；primitive生成与context/torch库共享须披露。每预测独立原label轴/bincount/full-affine物理距离、3完整plane同架构重放；这仍不是第二独立训练网络。最终患者确认必须是方法/端点冻结后的独立工作。
