# learned RASI uncertainty 辅助 ablation 说明

来源：`rasinet/runs/mini/metrics/summary_reliability.csv`

该结果来自早期训练型 RASI-Net mini profile，只包含 5 个 IXI case。它不能作为当前 Design 3 主证据，只能说明 learned uncertainty head 在小样本筛查中具备可行性。

## mini 结果

| Profile | Cases | Pixel Err-U corr | Slice Err-U corr | Risk-AURC | MAE@50% low-U | Failure AUROC | Top-k recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| IXI mini | 5 | 0.6532 | 0.8215 | 8.9841 | 1.8911 | 1.0000 | 1.0000 |

## 解释

- learned RASI uncertainty 在 mini 上能和误差对应，但样本太少，不能外推到 full_test115 / fastMRI / NingXia。
- 当前主线仍是 post-hoc reliability：`baseline_disagreement` 已经在 IXI、fastMRI、NingXia 上形成跨数据集证据。
- 如果后续要把 learned RASI 写进论文，应作为 appendix 或 ablation，而不是主方法。

## 当前决策

- 不启动 full RASI-Net training。
- 不把 learned RASI mini 结果写入主表。
- 保留该结果作为“learned uncertainty 可行，但当前证据不足”的补充说明。
