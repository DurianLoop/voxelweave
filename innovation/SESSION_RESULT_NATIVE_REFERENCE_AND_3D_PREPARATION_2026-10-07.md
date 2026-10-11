# MRI 创新探索：本阶段实际结果

尚未达成可发表且独立确认的 claim，目标继续 active。本阶段完成真实 native MR 参照、标准3D候选的输入/监督/推断资格及两篇论文核读；GPU拟合因实际显存不足在初始化之前退出，没有GPU训练结果。原失败任务能力门槛、八确认关闭和旧反证不变。

| 实际完成事项 | 证据范围 | 含义 |
|---|---|---|
| 完整 native MR 参照 | 固定28系列，1993原生层，461,967,360 MR像素逐层逐值核对，等量native标签体素由affine坐标重放 | 完整MR来源/坐标/观测层抽取一致，不等于分割能力 |
| observed 一致性 | 全28完整MR抽 z=0,4,...，与原package SHA/数值/SOP/顺序一致；八确认角色均在IO前拒绝 | native参考与旧稀疏接口没有混淆 |
| 双输入物理预检 | 28×2=56输入，11,256实际MR插值采样点独立核对，326,194,800物理标签体素全值核对 | MR是采样核验，不能称全体physical MR逐值重放；所有系列前景>0，最少76 |
| 坐标误差 | native DICOM角点最大约0.010024mm；3D中心world误差最大8.64e-14mm；插值误差最大6.69e-5 | 在冻结几何/数值门槛内 |
| 稀疏来源隔离 | 28系列把MR zip/header/label路径及hash改为不存在/无效，拒绝full-native及label readers后仍生成相同输入 | 同observed构造不需要隐藏MR/监督标签 |
| 实际尺寸CPU预检 | native/PCHIP各1更新；batch2×1×64×128×128；8,388,608输入/目标值独立NumPy patch重放，所有encoder/decoder/up/head有限非零梯度 | 可执行性和监督路径通过，2个CPU更新不是训练拟合或验证结果 |
| 原始论文阅读 | arXiv1809.10486及2404.09556v1，157提取文字块，正文/主表/附表文字已读 | 排除配置、尺度、预算混杂造成的假创新；未核原图像素/作者代码/复现 |

3D候选为1,401,363参数，四级16/32/64/128，InstanceNorm/LeakyReLU、标准deep supervision，名义.5mm重采样、32×64×64mm patch、full-FOV半窗Gaussian平均。不是nnU-Net自动规划器复现，也尚未资格化为充分任务适配的强基线。小原生slab的padding、有限视野和患者/序列异质性仍须真实拟合和完整原四验证门槛检查。

本阶段具体发现与修复：源label scaling使全体积float64超过单数组256MB，已改为<=32MB slab；36→58最近邻标签在半格tie处，Torch选26而精确中心坐标选27，出现120voxel差异。改用有理坐标等价的整数nearest标签版本；独立Fraction oracle全28重放通过。两个首轮失败原源码/协议/result全部保留，新尝试单独目录。这些可靠性修复不称新论文贡献。

GPU实际观测2026-10-07T02:22:58Z：总25,642,926,080字节，空闲1,461,714,944字节，util91%。新拟合pilot启动门槛8GB，执行记录为resource_deferred、0 updates、CUDA uninitialized；入口外层PowerShell工具exit1（Python逻辑返回3表示资源延后），没有运行任务可等待。CPU、native、隔离核验也均实际结束。未枚举/修改用户PID，未打开用户终端训练、根环境、.gitignore或locked IXI test。

该GPUpilot已冻结为native/PCHIP同observed stats/初始权重/固定patch/监督的各512更新诊断，总1024更新、最后checkpoint、同阈值。协议和可执行入口具备；它只用一个开发系列，哪怕通过也不能替代19系列正式训练、四验证能力门槛、公平矩阵和八保留确认。

下一步依赖：先新的GPU totals观测满足8GB，再按同冻结协议使用新的attempt02，不覆盖attempt01资源延后记录。真实梯度/peak/投影合格后完成两臂512更新和训练系列完整FOV拟合；若不合格保留失败、设计新版本。然后决定正式19系列的充分任务基线架构/预算并冻结，用原四验证所有分母和gate；能力充分之后再native/6×5公平矩阵、同observed直接任务/分辨率随机化。只有稳定可观测可修正残余成立，才设计预测action gain的修正；冻结最终方法后才打开八确认与第二独立任务网络。

精确问题仍是：同observed信息/统计/监督/容量/预算、充分任务适配后，能否修正缺层病灶残余并优于强raw PCHIP及直接任务适配。当前尚无正答案，不通过弱评价器、重复使用四验证或更换问题来制造发表claim。

主要入口：[native认证](experiments/mc_rc_true_native_reference_attempt02_2026_10_07/attempt_01.json)、[独立全部源重放](experiments/mc_rc_true_native_reference_attempt02_2026_10_07/independent_all28_pixels_and_labels_2026_10_07.json)、[3D输入预检](experiments/mc_rc_3d_baseline_inputs_attempt02_2026_10_07/attempt_01.json)、[实际CPU batch](experiments/mc_rc_3d_real_batch_cpu_2026_10_07/attempt_01.json)、[稀疏隔离](experiments/mc_rc_3d_sparse_source_isolation_2026_10_07/attempt_01.json)、[GPU延后记录](experiments/mc_rc_3d_gpu_fit_pilot_2026_10_07_attempt01/attempt_01.json)、[GPUpilot协议](MC_RC_3D_GPU_FIT_PILOT_PROTOCOL_2026-10-07.md)、[论文阅读](literature/2026-10-07_strong_task_baseline_fulltext_reading.md)。
