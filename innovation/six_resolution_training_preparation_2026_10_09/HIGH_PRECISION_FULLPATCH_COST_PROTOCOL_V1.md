# 真正训练 patch 的人工资源探索

前置：high_precision GPU attempt04 两步通过，independent_round51_audit_attempt02 完成，原 strict3e-6/binary0 保留。仅探索新 v2 数值分支在原 patch (2,1,64,128,128) 下顺序三 view 的全图资源成本。

固定初始权重 seed20261009；人工输入 seed991，GIN seed801/802/803；人工椭球 target（不加载医学标注），同 supervised+0.1 attached consensus loss、原 AdamW 超参数。最多1次人工 GPU 更新，无 CPU全模型重跑、不保存权重、不计算医学指标。

这次是成本测试，没有独立 CPU 全尺寸对照，成功也不赋予完整数值资格。若在 allocator<=min(10%,2.4GB/total) 下 OOM，原样记录 stage、已开始与完成的 forward、是否实际更新；不重试同配置、不放宽门槛、不动其它进程。GPU start8192MiB/peak2.5GB/runtimefree4GB、CPU1/interop1/below-normal、RAM/disk8GB reserve、wall360s、目录cap不变。
