# 时间增量推理：接续两篇原文的选择协议

新增选择 Habibian 等 *Skip-Convolutions for Efficient Video Processing*（CVPR2021）和 Parger 等 *MotionDeltaCNN: Sparse CNN Inference of Frame Differences in Moving Camera Videos with Spherical Buffers and Padded Convolutions*（ICCV2023）。现有正文阅读报告没有登记这两篇，已有 DeltaCNN/SIGE/DeepCache 的阅读不重复计数。

目的：核对连续视频中的 learned gate、状态更新/冷启动与相机运动补偿，判断这些已有技术能否直接支持“多个 MRI 修正候选共享缓存”及其速度/任务保持。两篇从 CVF 会议题名目录公开 GET 定位；获取官方 landing/PDF，核首页身份，再逐页文本阅读方法、实验和限制，渲染关键方法/结果页。下载与提取不计已读；补充材料和作者代码若未核读要明示。

固定只公开 GET，最多两并发、每响应32MB/25秒、输出100MB；沿用当前脚本禁用失效代理，不改系统代理。所有新文件写在 innovation。现有训练 session99542 和用户终端进程继续运行，新实验仍遵守既定资源合同。

新成本审计已有生产结果但尚待独立核验。已有 joint_QDA 低覆盖是旧结果，此次新增仅为其当前3D窗口成本；不把“稀疏但错误的ROI”构造成功。文献结论同样不代替真实 MRI 差分、模型端点或实际总耗时。
