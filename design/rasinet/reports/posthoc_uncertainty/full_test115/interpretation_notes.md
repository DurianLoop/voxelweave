# full_test115 RASI post-hoc interpretation notes

## 1. 主 proxy 决策

当前主 proxy 采用 `baseline_disagreement`。

理由：

- 在四个已有强方法上，`baseline_disagreement` 的 pixel error-uncertainty correlation 都高于 residual proxy。
- 在 nonzero/masked 区域上，`baseline_disagreement` 仍保持正相关：
  - SwinIR: `0.4711`
  - HAT: `0.4628`
  - ACSI: `0.4037`
  - I3Net: `0.3068`
- failure detection AUROC 稳定在 `0.9822-0.9871`。
- 它不依赖重新训练，因此符合 Design 3 当前的低算力 post-hoc 路线。

## 2. residual proxy 定位

`residual_linear` 和 `residual_cubic` 不作为主 proxy，只作为 sanity / ablation。

理由：

- residual proxy 的 pixel corr 普遍低于 `baseline_disagreement`。
- residual proxy 的 pixel/slice 分歧 case 更多，稳定性较弱。
- residual proxy 仍有意义：它能说明“偏离 coarse interpolation 的区域”与真实误差存在一定关系，但不足以支撑主故事。

## 3. 推荐主张

推荐主张：

> Existing interpolation models can be equipped with a low-cost post-hoc reliability signal. Without retraining the reconstruction networks, baseline disagreement provides a failure-aware uncertainty proxy that correlates with reconstruction error and helps identify high-risk cases.

中文表述：

> 不重新训练重建模型的情况下，可以为已有强插值方法外挂一个低成本的 post-hoc 可信性信号。多模型预测分歧与真实重建误差保持正相关，并能帮助发现高风险失败 case。

## 4. 不建议的主张

不建议写：

- RASI-Net beats SOTA。
- 该方法提出了新的最强重建网络。
- uncertainty 是严格校准的概率不确定性。
- linear/cubic 是主要对手。

这些说法都不符合当前证据。

## 5. 必须报告的限制

- `baseline_disagreement` 不是概率校准 uncertainty，只是 post-hoc proxy。
- 如果多个模型同时犯相似错误，disagreement 可能低估风险。
- 全像素 correlation 会被背景区域抬高；主文应优先报告 nonzero/masked 版本。
- 当前 full_test115 是 IXI 内部验证，还不能替代 fastMRI 或 NingXia 的跨数据集证据。
- failure detection 的 top-k 定义依赖 MAE 排名；后续可补充 SSIM/结构一致性失败定义。

## 6. 建议放入论文的表格顺序

1. Main reliability table: nonzero/masked correlation under `baseline_disagreement`。
2. Failure detection table: AUROC / AUPRC / top-k recall。
3. Proxy ablation table: disagreement vs residual-linear vs residual-cubic。
4. Visual QC: high-risk/high-error、low-risk/low-error、mismatch cases。

## 7. 下一步

优先推进：

- fastMRI-brain T2 post-hoc 重复验证。
- NingXia CV post-hoc 重复验证。
- TTA variance 只在运行时间可控时添加，不应阻塞当前可靠性主线。
