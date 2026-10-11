# VS-SEG：原确认方案已被源级反证，任务级 CPU 路径可运行

目前仍未达成可发表 claim。新证据关闭了一个无效实验方向，并建立了后续独立病灶任务验证所需的模型、名单和 CPU 路径。当前终端训练没有收到本轮启动、停止、重启或修改命令；新模型执行均明确在 CPU 上，CUDA 初始化被禁止且结果记录为 false。

原 [VS-SEG 确认方案](VS_SEG_THIN3D_MODEL_CONFIRMATION_PROTOCOL_2026-10-01.md)要求至少 100 名完成患者，每人四层目标，且每个余数 1/3 至少三层合格病灶切片。首批在 14 例后中止，仅一例完成；不能把这 14 例当队列确认结果。

**源级上界已独立复核。** [第一种非像素审计](experiments/vs_seg_nonpixel_target_upper_bound_2026-10-01.json)以 RTSTRUCT 的 SOP 引用与物理轮廓格点映射出层序，允许所有相位、层序正反和可能的边缘平移，并忽略 64 像素/支持域等门槛；239 例明确首结构最多 95 例可能满足目标数，144 例连这一放宽条件也不满足。35 例重复或缺失的 Skull 引用已通过物理格点处理，而非丢弃。另两例首结构名为 Men，语义未核清；一例 VS-SEG-133 不在当前 NBIA T2 清单中。

[独立复核](experiments/vs_seg_target_bound_independent_2026-10-02.json)逐一核验全部 242 个 RTSTRUCT ZIP 的既有 SHA-256、患者身份和首 ROI，以轴向轮廓的物理 z 坐标计算模 4 层数。它连四锚点的边缘限制也取消，允许全部相位和方向，并包含 Men 与 VS-SEG-133；仍只有 **96/242** 例可能满足每个余数至少三层。未知/失败为零，前一审计的可行例全部在该更宽上界内。因此原 >=100 人门槛在此版本、清单和目标规则下不可达；即使修复标签名称和浮点误排除也不能通过。这个结果只适用于当前具体协议，不能宣称公开 MRI 研究普遍无效。

**标签规则有作者代码依据，名称语义仍须谨慎。** 固定作者 Git 树为 `33410a2d44e3f57b4df1c3ed005e6d40c0824aa6`，[代码及六例原始轮廓档案](literature/source_cache/vs_seg_author_code_2026-10-01/index.json)可复查。`data_conversion.py` 按 JSON 结构顺序构建分割，默认仅导出 index 0；BIDS 转换脚本明写 “only export the first structure, the tumour”。这支持按作者首结构选取，不能由此声称作者逐一定义了 AN、Rt AN 或 Men 的缩写。六例 JSON 与 RTSTRUCT 的首结构名称一致，但两种轮廓的条数/几何可不同。小写名称不能继续以精确 TV 的规则静默排除，也不能追溯改写旧协议为阳性。

**第 10 例并非实际层距不合格。** [非像素 DICOM 头复核](experiments/vs_seg_010_header_spacing_check_2026-10-01.json)给出 80 个 3D 对象、层厚 1.5 mm、物理层距中位数 1.5 mm，最大变化约 6×10⁻¹³ mm。旧脚本第一步长为 `1.500000000000007`，严格 `<=1.5` 比较触发误排除。旧失败原样保存；后续新协议应对厚度和间距明确采用例如 0.0001 mm 的数值容差，不改写历史记录。

**官方任务模型与独立名单已取得。** [源级方案](VS_SEG_TASK_MODEL_SOURCE_GATE_PLAN_2026-10-02.md)、[源代码/Zenodo 元数据](literature/source_cache/vs_seg_task_model_sources_2026-10-02/index.json)、[权重与日志审计方案](VS_SEG_TASK_CHECKPOINT_LOG_AUDIT_PLAN_2026-10-02.md)及[发布档案](literature/source_cache/vs_seg_t2_release_logs_2026-10-02/index.json)固定了 DOI `10.5281/zenodo.6323472` 的 T2 模型。ZIP 为 35,275,354 字节，官方 MD5 `a13b58405481b5cbf30771e39499b829` 校验通过，许可 CC BY 4.0。最佳权重 SHA-256 为 `9105ad78fed0561bb04a82e660eed6083c3d182fc43642bc332f68a272ede0a7`。

[逐名单复核](literature/source_cache/vs_seg_t2_release_logs_2026-10-02/split_verification.json)显示，训练日志、测试日志和固定 Git CSV 的 176/20/46 人列表完全一致。46 名测试患者都在当前 242 人映射及 241 人 NBIA T2 清单中，且与已尝试的前 14 例零重叠。45 例为 CISS、1 例为 TSE；不能把两序列的表现当同一分布。旧四目标放宽规则最多覆盖其中 22 人，说明继续该选择规则会失去超过一半的独立任务患者。发布日志原生 T2 平均 Dice `0.9066144 ± 0.0362898` 是作者既有结果，不是本项目新结果。

**CPU 软件验证已经实际运行。** [兼容性方案](VS_SEG_CPU_COMPATIBILITY_PROBE_PLAN_2026-10-02.md)和[依赖来源](literature/source_cache/vs_seg_cpu_compat_sources_2026-10-02/index.json)把作者未改动网络代码及官方 MONAI 0.4.0 wheel 隔离在 innovation/tools，未安装到用户 MRI 环境。首次导入因 Python 3.12 移除 FileFinder.find_module 失败；只在探针进程中将该旧导入 API 交由 importlib.import_module，未改卷积、注意力或权重键。小输入[第二次尝试](experiments/vs_seg_cpu_compatibility_probe/attempt_02.json)严格加载 3,453,012 个参数，32×32×8 重复前向差为零。官方大小[第三次尝试](experiments/vs_seg_cpu_compatibility_probe/attempt_03.json)在 384×384×64 上单线程前向约 10.37 秒，峰值驻留约 5.91 GB，全部参数在 CPU，CUDA 未初始化；只降低了探针自身进程优先级。

[原生影像预检协议](VS_SEG_001_NATIVE_TASK_PREFLIGHT_PROTOCOL_2026-10-02.md)固定使用已看过、且属于作者训练集的 VS-SEG-001。[实际结果](experiments/vs_seg_001_native_task_preflight/attempt_01.json)验证 DICOM P/L/S 到 R/A/S 的轴交换/翻转，没有空间插值；原版全图 NormalizeIntensity 和 Gaussian 384×384×64 滑窗在 CPU 上约 24.77 秒完成。对 7,505 体素的 RTSTRUCT 平面 TV 参考，预测 7,531 体素，TP/FP/FN=7,210/321/295，Dice `0.9590317`。这只证明实现能运行，病例曾参与分割训练，且没有测试任何重建条件，不能作为独立病灶效果或原论文基线复现。

**原始掩膜门槛确有实质差异。** 该例作者原始 JSON 有 14 条轮廓，距最近 T2 原生平面的最大偏差 `0.5997195 mm`；RTSTRUCT 是 13 条已插值到 T2 平面的轮廓。没有把原始 JSON 强行投到最近层。源论文说明 GammaPlan 的插值可能使首尾整层消失，原始 JSON+SlicerRT 才是训练用掩膜；论文报告两转换方式在 T2 的 Dice 为 97.6±2.2%。正式任务级检验必须解决原始掩膜转换及边界敏感性，不能把本次 0.959 与作者 0.907 直接相减。MONAI 的旧多维列表索引还出现弃用警告，当前输出形状正确；后续需验证 tuple 索引移植与原实现一致。

本轮创新判断及可执行后续见 [下一项任务研究准备](VS_SEG_FULL_VOLUME_TASK_STUDY_PREPARATION_2026-10-02.md)，五篇来源论文复核及既有任务先例见 [阅读矩阵](literature/2026-10-02_vs_seg_source_task_reading_matrix.md)。目标仍保持 active，不以软件预检通过代替发表门槛。
