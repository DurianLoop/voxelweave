# 连续影响大表扩展

本轮由用户授权在上一轮停止边界之外继续测更多模型。新增固定范围：Linear、ACVTT、ResUNet、SMamba-UNet、ArSSR；复用 HAT、SwinIR、SAINT 的原观察，完整展示 13 模型。

执行状态见 [RUNNING_STATUS.md](RUNNING_STATUS.md)，冻结规则见 [PROTOCOL.md](PROTOCOL.md)。状态表由 `scripts/status.py` 根据真实输出更新，不将尚未完成的模型填成失败或成功。

完整实验计划为 2,085 个新增目标响应文件（5 模型 × 139 检查 × 3 目标），每个文件保留所有上下文/幅度/锚/扰动场。当前有其他 GPU 任务，因此推理预计需要数小时。代码不会停止其他任务、减少已冻结病例数量或选择更有利模型。

`scripts/analyze.py --watch` 在每个模型/队列完整时从原始响应独立重算；全部计划任务完成或记录技术失败后才生成新家族区间。随后 `scripts/publish.py` 生成大表、全部次要端点、图表与论文草稿，编译、版面复核和入口交付是后续独立步骤。

`original_snapshot/manuscript/` 为原稿快照。生成/重建成功前，`revised_manuscript` 内 PDF 是旧稿工作副本，不能视作新实验交付。原 canonical CVPR 与 TMI 在本轮最终验收前保持不变。
