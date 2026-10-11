# Native 参照认证第二次尝试

第一次实际 exit 1：前两系列完成，第三系列完整 native MR 已读，读取 label 时因 NIfTI scaling 产生 float64 全体积 >256MB 而触发单数组上限。失败记录保留在 experiments/mc_rc_true_native_reference_2026_10_07/attempt_01.json；原脚本和被其 SHA 绑定的 loader 不修改。

第二次改变只涉及标签内存方式：源标签逐 4 张 slab（每块 <=32MB）核对有限/二值并转为 bool，最终 bool 体积仍 <=256MB；随后原 transpose/flip 和 foreground/shape 核验不变。完整 MR 像素来源、allowed patients、所有物理/observed SHA 门槛及预算不改。新 wrapper、入口、结果单独保存，失败不能计入成功系列数。
