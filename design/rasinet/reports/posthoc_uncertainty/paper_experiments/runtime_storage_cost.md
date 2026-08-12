# RASI post-hoc runtime / storage cost table

本表记录当前 post-hoc reliability layer 的存储与执行成本属性。它只读取已有预测、GT 和 coarse interpolation，不重新训练模型。

| Profile | Dataset | Cases | Source dirs | Source NIfTI files | Source size GB | Metrics MB | Reports MB | Training needed | GPU needed |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| full_test115 | IXI | 115 | 4 | 2300 | 17.060 | 3.432 | 14.930 | no | no |
| fastmri_full | fastMRI-brain T2 | 24 | 3 | 360 | 1.274 | 0.589 | 0.337 | no | no |
| ningxia_cv | NingXia T2 CV | 22 | 3 | 368 | 4.012 | 0.590 | 0.292 | no | no |

说明：

- `source_size_gb` 是已有 baseline/model output run directories 的总大小，不是本方法新增存储。
- post-hoc 新增产物主要是 CSV、Markdown 和 PNG；相对已有 NIfTI 预测体积很小。
- 若未来加入 TTA variance，GPU/额外推理成本需要单独列入，不应与当前 post-hoc disagreement 混为一谈。
