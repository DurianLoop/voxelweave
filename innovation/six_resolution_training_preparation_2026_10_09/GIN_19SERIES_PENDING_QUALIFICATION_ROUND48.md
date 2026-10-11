# 三视图强对照的真实医学资格准备，尚未执行

本轮人工完整图通过 CPU 卸载，两步全参数与优化器状态相同，不能替代真实医学资格。下面的 manifest 只读取已冻结 metadata，不加载 MRI/GT，不开始训练；它保留原 11 开发患者 / 19series / 两种输入，不把人工 target 换名为医学实验。GIN-only consistency 是已有强对照；IPA 场仍独立 pending。

病例、两个采样步骤、几何和母 GT hash 复用 development_optimizer_coverage_2026_10_09/coverage_attempt01/frozen_config.json 的全部19行。每个 case 两个 original scheduled step，batch_rng(19998+step)，原 sample_batch 的训练采样/flip/基本强度变换。允许原训练的前景采样，但不允许用 GT 生成 GIN/IPA 混合场。GT 仍是同一 physical_label 的母标签，核全部 voxel 和两输入共享 label SHA。只改变输入强度，不改坐标/label。GIN 后三视图第1 view 用原深监督 loss，三 view 最终 head softmax([0,z])，attached KL(mean||each)、element mean；qualification lambda=0.1，不把它当临床最优选择。

每个 case×kind 重置为共同 cold-init seed20261009，原完整 batch2/patch64×128×128。三个 view 参数 seed=480000+case×100+optimizer_step_index×10+view_index，两个输入 kind 用同一参数抽样。记录完整具体随机卷积参数/hash、输入/输出/hash和 Frobenius 归一化。严格 LOPO 以后也必须 fold cold-init；含全部开发GT的19998 parent不能充当该资格的训练外起点。

首先资格检查共38个 case×kind，两个实际连续 optimizer step。GPU 使用已通过的 builtin save_on_cpu 完整 attached graph；相同输入/参数/target 的独立 CPU functional FP32 计算图作数值参考（完整 loss、全部概率和梯度），独立 NumPy AdamW 检查更新/一阶二阶矩，全部 gate3e-6；坐标3e-12、二值零差。恢复具体CPU参考梯度实现之前不得把单纯GPU hooks内容比较改称CPU算术资格。两个 step 的全参数、moment、step、序列化/恢复、target 不变均需核对。遇到不合格保留全部 prefix/错误/资源，停止该实现资格，不挑病例、不放宽 gate。

最低完整分母：GPU实际 optimizer updates76、至少228个 whole-model forward，228个CPU参考 whole-model forward，两设备所有 checkpoint recomputation、两步152 patch母标签核对（38×2×2）均计费。这里是未来预算数量，不是本轮已执行数量。完整计算图 backward 每个step一次；不能把 block recomputation当新的患者/whole-model forward。报告 GPU 与CPU参考、GIN参数生成/卷积/归一化、三view loss、offload传输、CPU/RAM、梯度/状态捕获、hash、保存/核验总 elapsed。独立参考的诊断成本不能偷算成部署时间，也不能隐去。

仍需实现：独立CPU可微 functional reference、完整19series数据/母GT绑定的 runner、两步和所有费用journal，以及以首病例实际成本估计整个资格wall/储存后另冻可执行协议。当前只有协议与metadata manifest；本轮不启动这个医学作业，也不称 runner 已完成。沿用CPU1/interop1/below-normal、磁盘/RAM8GB、GPU启动8192MiB、allocator min(10%,2.4GB/total)、peak2.5GB/runtimefree4GB、FP32/TF32off/deterministic。新资格需要在当前prep7MB/FOV20MB/other22.8MB预算内，或另做完整预算；不增加磁盘、压缩/删除历史或降低保留量来启动。

正式强对照仍须 basic / GIN-only / GIN+IPA / +consistency 同曝光及同完整计算预算两套比较，模型/GT/患者/schedule/endpoint一致。完整35904和full38资格仍各自pending，六臂预算104156359bytes未降低。模型能力必须通过患者先均值 fullDice≥.70、missingDice≥.65、recall≥.70、absRVE≤.50、每患者 full/missing Dice>0、无series零TP；本轮不运行或打开8未见确认12series/lockedIXI，4已见验证不作新确认。
