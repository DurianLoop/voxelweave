# Direction update after TTA experiments

日期：2026-07-10

## 当前判断

TTA variance 已经在 fastMRI、IXI、NingXia 三套数据上完成 SwinIR 实验。结果显示它是有价值的辅助 proxy，但不适合作为主 proxy：

- slice-level correlation 明显强于 `baseline_disagreement`。
- pixel-level correlation 在三套数据上均弱于 `baseline_disagreement`。
- risk-coverage 不稳定优于 `baseline_disagreement`。
- failure detection 在 NingXia 有增益，但 fastMRI 已饱和，IXI 基本持平。

因此论文主线应继续使用 `baseline_disagreement` 作为 main post-hoc reliability signal，TTA variance 放入 proxy ablation / supplementary。

## 接下来优先做

1. 生成论文主表：main reliability、failure detection、proxy ablation、runtime/storage cost。
2. 生成论文主图：risk-coverage、masked vs all-pixel correlation、proxy ablation、visual QC。
3. 写 paper outline，明确题目、贡献、实验结构和主结论。
4. 写 reviewer attack list 和 response notes。
5. 只有当主表或 reviewer notes 暴露硬缺口时，再补 learned uncertainty head 或 I3Net TTA。

## 暂不优先做

- 不启动 full learned uncertainty head training。
- 不重新训练完整 RASI-Net reconstruction model。
- 不继续为了“更多实验”盲目扩展 proxy；新增实验必须服务于论文主张或 reviewer 风险。
