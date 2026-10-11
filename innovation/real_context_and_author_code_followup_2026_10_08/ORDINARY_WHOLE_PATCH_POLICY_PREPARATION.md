# 全 patch 支持候选政策（只准备，不启动训练）

本协议准备一个普通增强基线；它不是创新算法或已经观察到的病灶改善。本阶段全 5984 候选几何检查仍须真正 terminal exit0，加独立进程重放全部 2992 母 label / crop / pivot 的资格后才能分析分布。不能从当前部分日志推测最终支持比例。

候选规则固定为：原采样决定的每一个 enabled 非 identity primitive，仅当所有 1048576 target 体素的 unpadded-domain 正权重支持均通过既有阈值 `1-1e-9` 时执行 image roundtrip；否则该 patch 使用原 identity image。整个母 label、患者、series、采样曝光、loss 分母和原 intensity 处理均保留。对照臂重放相同 primitive 和 eligibility 记录，但不执行 roundtrip。该 eligibility 不读取新的 GT、损害或预测：只使用既有合法训练 geometry、physical domain 和插值支持。但 forced-FG crop/pivot 本来是训练 GT 定位的，不能将这份记录称为部署 GT-free 定位证据。

采用整个 patch 的资格，避免宣称“只要有效 loss 区域输入支持足够，InstanceNorm 输出就不受无效输入影响”。fallback 身份臂本身可能含原始 cache padding，因此承诺仅是未通过资格的新增 roundtrip 不执行，不能保证整个母输入都具有真实采集支持。所有 identity/失败/不执行均计入完整分母。domain 仍是 unpadded resampled image，不能称每格点真实观测。

资格收齐后，`analyze_whole_patch_eligibility.py` 只读取已完成 journal / audit，按患者、series、forced-FG、active、实际尺度和旋转汇总可执行数，并生成每个 step/patch 的 deterministic decision 文件及其 SHA。不读影像/GT/checkpoint、不评分损害，不安装依赖。该分析**不增加候选支持字段重算**；独立 Torch/SciPy mask 资格来自原 qualifier，母 batch 独立重放来自 terminal audit。

在新训练前仍有必须完成的事项：对所有可执行 geometry 认证真实 MRI roundtrip 及完整 intensity 管线；本阶段 76 stress fields 不覆盖完整 2992 schedule。需冻结实际 eligible 数和患者覆盖、测完整 forward/backward / cache / support 成本、确认 GPU 8192MiB 储备、同 parent / last checkpoint / schedule / optimizer / 更新数、对 native_reference 与 raw-PCHIP 都保留 matched 控制。若几乎无 active 可执行，保留资格和阴性结论，不放宽支持阈值或按 GT 选 patch。low-pass/resolution-only 控制另需明确实现及完整 source 支持资格，不能以这份 gate 偷换已完成。

原四臂 session29823 recipe 保持。它的单次 spatial 改 image 和 label，不能把当前 image-only 往返资格当作该臂效果或支持审计；四臂最终 all-last2992 后原六医学门槛、36 production +36 functional 完整 FOV 评价仍是下一医学依赖。8 未见确认患者/12series与 lockedIXI 不打开。
