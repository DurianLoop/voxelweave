# PAST-Net：训练序列完整性修复实验

**2026-09-23 full 已完成并复核：25.567453 dB，相对旧 control +0.005442 dB，未达到预登记 +0.10 dB 晋级门槛。停止当前候选训练，正确的数据修复保留为后续共同基线。** 详见 [full 复核](results/full_review.md)。下一项是 [共享核小波主干实验](../pastnet_wavelet_trunk/README.md)。

2026-09-23：frame-context full已按预登记停止，仅+0.000426dB，CI跨零，不再运行plain消融。完整报告见 [frame-context复核](../pastnet_frame_context/results/full_review.md)。

本轮回查已知的异常32层体积，发现旧转换将同名AX T2的两个不同SeriesInstanceUID混为一个volume，按重复InstanceNumber交错排序。两个序列像素不同；全部32层已逐像素匹配原DICOM。不同UID不单独证明独立重复采集，本实验只纠正序列身份和物理顺序。

例如旧z=0区间的三个target实际在[0,.5,.5]位置，却标记为[.25,.5,.75]，且来自混合序列。对全部135个train/val原始序列的头审计只发现这一例；test未打开。

独立生成两份各16层的新NIfTI，只重排像素，保留原文件。训练从112series/1360区间变为113series/1356区间，仍111患者；其它训练record与全部23患者69区间validation逐字段不变。原control模型、G086初始化、loss、AdamW/warmup cosine/EMA等保持原方案。

这是**单变量数据修复实验**，不是新架构或SOTA结果。保留错误数据与checkpoint用于追溯，今后数据修复是否正确由UID/位置/像素证据判断，不按PSNR涨跌决定。G086预训练曾见过旧数据，本轮不能宣称全流程干净训练。

以下为已完成实验的历史命令，不需要重跑：

```powershell
Set-Location D:\MRI
powershell -NoProfile -ExecutionPolicy Bypass -File .\design\pastnet_series_integrity\full.ps1 -Seed 3407
```

最多80轮、原min30/patience15，microbatch2×累积8、checkpoint5/10。修复病例完整loss反传峰值19.620GiB allocated /20.295GiB reserved，普通trainer smoke约19.62/20.31GiB。推理模型与control相同。

中断后加 `-Resume`。只跑这一条，不自行加seeds、外部测试或其它模块。完整检查以 [full前核验](results/pre_full_review.md) 和 `results/final_verification.json` 为准；full后代码、协议、入口和修复数据哈希冻结。

模型晋级仍要求相对control至少+0.10dB及全部质量/尾部/效率守卫；通过后再补三seeds并锁定外部评估。报告按完全相同的validation records配对，明确保留两个不同的training manifest哈希，不伪装成同数据架构消融。最终SOTA比较需在修复后的训练集合上建立相应基线。

- [计算前协议](PROTOCOL_ZH.md)
- [运行与恢复](docs/运行指令.md)
- [全部头审计](results/header_audit.json)
- [像素与物理位置映射](results/repair_mapping.json)
- [修复manifest](manifests/fastmri_repaired.json)
