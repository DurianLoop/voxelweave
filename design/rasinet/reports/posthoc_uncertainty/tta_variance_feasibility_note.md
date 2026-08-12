# TTA variance proxy feasibility note

状态：暂缓，未运行。

原因：

- TTA variance 需要对同一个模型做多次增强推理，例如 flip / transpose / intensity perturbation 后再 inverse-transform。
- 当前已完成的 IXI、fastMRI、NingXia post-hoc 证据都只读取已有预测，不占 GPU；TTA 会改变资源假设。
- 现有 baseline disagreement 已经在三个数据集上形成正相关证据，TTA 不应阻塞当前可靠性主线。

如果后续要补 TTA，建议只选一个代表模型和一个数据集：

1. 模型：I3Net 或 SwinIR。
2. 数据集：先选 IXI full_test115 或 fastMRI 24 cases。
3. TTA transforms：
   - original
   - left-right flip
   - anterior-posterior flip
   - both flips
4. Proxy：
   - `U_tta = std(pred_original, pred_flip_lr_inv, pred_flip_ap_inv, pred_flip_both_inv)`
5. 报告方式：
   - 只作为 ablation，与 `baseline_disagreement` 比较。
   - 如果 TTA 不明显优于 baseline disagreement，不进入主文。

当前决策：

- 不在本轮运行 TTA。
- 保留为后续可选增强实验。
