# T2/x4 Efficiency Profile

口径：单个 256x256 generated slice 的模型 forward-only；不包含 NIfTI IO、resize、metric 计算或整例循环开销。

| Method | Input | Params(M) | FLOPs(G) | Forward ms | CUDA peak MB | Note |
|---|---|---:|---:|---:|---:|---|
| SAINT-style | 1x6x256x256 | 1.1973 | 35.7606 | 3.0969 | 117.30 | one generated 256x256 slice, model forward only, no NIfTI IO or resize |
| SwinIR-style 2.5D | 1x4x256x256 | 0.2239 | 28.3682 | 4.2980 | 251.23 | one generated 256x256 slice, model forward only, no NIfTI IO or resize |

说明：FLOPs 使用 Conv2d / ConvTranspose2d / Linear hook 估算，attention 中 softmax、matmul 和 normalization 未完全计入，因此 Transformer 的 FLOPs 偏保守；该表主要用于本项目内同脚本横向比较。
