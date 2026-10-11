# 实际带标签 MC-RC 来源的下一步准备

这是在当前 487 行目录/2023 标签 ZIP 事实下保存的准备方案。不是已取得 71 名合格患者，也不意味着下述下载已经执行。当前标签缺失、legacy UID crosswalk 缺口和首跑失败均保留。

## 固定候选集与下一批

以现有 [可用性全表](experiments/mc_rc_native_t2_label_gate/geometry_availability_attempt_01.json)为入口：PatientID 前缀 `VS-MC-RC-`、SeriesDescription 前缀 `_T2_` 且 `availability=available`；使用精确 SeriesUID 联结 API/CSV/ZIP。候选 71 人/159 系列，排除全部 58 名共享 VS-SEG 患者。预选 001/002/003 全部归来源预检/后续开发，所有时间点整体处理。

下一批取排除这三人后按官方 PatientID 排序的前三人：**VS-MC-RC-004/005/006**，纳入其全部八条有实际标签的 T2 系列，包含 description 已标 MPR 的系列以透明报告拒绝，不按 spacing、病灶大小或效果筛选。API 合计 ImageCount=701、FileSize=385,990,404 bytes，FileSize 不是实际 ZIP 传输量。

[准备脚本](experiments/prepare_mc_rc_labelled_native_expansion.py)只使用已存来源生成 [固定候选/批次 JSON](experiments/mc_rc_native_t2_label_gate/labelled_native_expansion_preparation.json)，不访问网络、不解码 MR 或新标签。JSON 明确 `prepared_not_executed`，源/API/方案 hash 一并保存。

## 执行前仍需独立合同

真正扩展读取前另写有界合同，复用现有公开 getImage endpoint，最多两条下载线程、无自动重试，每请求保存 provenance；建议该八系列合计上限 500MB，实际 transfer 超上限则记录 partial/失败、保留固定分母，不按成功病例改名单。只使用已认证官方标签 ZIP，不猜 2026 标签地址。此处不是启动下载的记录。

几何沿用全部 IPP 拟合、0.02mm residual、0.05mm label 角点误差，仅整数轴置换/翻转；逐对象核身份、ORIGINAL/DERIVED、3D/缺字段、orientation/spacing、名义层厚与多帧等。将本轮修正作为新实现版本，先保存新版本 hash。独立实现重新读取原 ZIP，不能只比布尔值。派生和缺字段为拒绝/pending，不以注册修复放行。

全部 159 系列的完整审计也须另定资源预算与不可变名单，不能从当前八条外推全库。若实际合格规模不足，报告真实规模，不凑 100 人。

## 方法探索和确认资格

四条已通过系列仅有头/标签预检。读取 MR pixel_array 前，另冻结模型、灰度归一化、物理/模拟观测方式、缺层phase、完整体积分母、任务模型权重及训练名单、候选动作/计算预算和病灶端点；先核开发 oracle 是否存在可用空间，再讨论训练收益头。

所有患者多时间点整体分组；采用完整患者缺层分母和患者等权，不让扫描次数增加患者权重。源预检/开发患者不得变为新方法未见确认。资格审计可以先做，性能标签不可参与确认患者筛选；开发/校准/确认名单在性能读取前冻结，并核既有 IXI/VS-SEG 及任务模型训练独立性。

未满足真实观测算子/独立噪声条件前，不将跨时间点用作 Noise2Noise/Rep2Rep 重复监督；病灶可能随时间变化，协议/物理 PSF也可能改变。空残余不强行用 Dice，另报告误检与假阳性体积，标签协议与派生 provenance 保持单独记录。
