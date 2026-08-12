# T2 x2/x4/x6 through-plane interpolation 扩展计划

## 目标

把当前 T2 x4 through-plane interpolation 主线扩展到 x2 / x4 / x6 三个倍率，并最终整理成类似 I3Net 论文的大表。当前先接入最稳的一批：

- Linear
- Cubic
- I3Net (2024)

这三项的意义是先把多倍率 protocol、数据切分、评估和表格结构跑通。I3Net 本身就是 medical slice interpolation / through-plane synthesis 方法，x2 / x4 / x6 都有明确的窗口定义，最适合作为多倍率扩展的第一批。

## 当前已完成的代码改动

1. IXI I3Net 增加 `full_test115_x2` 和 `full_test115_x6`。
2. fastMRI I3Net 增加 `full_x2` 和 `full_x6`。
3. NingXia case-level CV runner 允许 `full_x2` 和 `full_x6`。
4. I3Net checkpoint、manifest、paper table 的 condition / source / FLOPs 描述已经从硬编码 x4 改为按 `profile.stride` 动态生成。
5. 新增多倍率汇总脚本：
   `processing.build_multiscale_table`

生成的大表草稿位置：

`docx/experiment_notes/multiscale_x2_x4_x6_i3net_table.md`

## 多倍率窗口定义

I3Net 的输入窗口固定为 4 个 sparse slices，输出 HR 窗口长度由倍率决定：

| Scale | Sparse input slices | HR target slices | 中间待合成切片数 |
|---|---:|---:|---:|
| x2 | 4 | 7 | 3 |
| x4 | 4 | 13 | 9 |
| x6 | 4 | 19 | 15 |

因此 x2 / x4 / x6 不能共用同一个 I3Net checkpoint。每个倍率都应该单独训练、单独评估、单独入表。

## 推荐执行顺序

第一阶段只跑 I3Net + Linear/Cubic，先得到三数据集 x2/x4/x6 的大表骨架。

IXI-T2 使用 `full_test115_x2/full_test115_x6`，保持你现在要求的 test n=115。fastMRI 使用全量 test。NingXia 使用 8-fold case-level CV。

第二阶段再决定是否把 HAT / SwinIR / SAINT / SMamba 等强 baseline 扩到 x2/x6。建议只扩论文最需要的强方法，不建议把所有历史弱 baseline 都乘上 x2/x6，因为训练成本会变成原来的数倍，而且论文价值不一定增加。

## 运行后刷新大表草稿

任意一个倍率或数据集跑完后，都可以执行：

```powershell
Set-Location D:\MRI
D:\conda\envs\MRI\python.exe -B -m processing.build_multiscale_table
```

脚本会保留还没跑完的单元格为 `pending`，不会误填。

## 入主表策略

`experiment_master_table.md` 当前仍建议保留 x4 主表，避免主表突然过宽。x2/x4/x6 的超大表建议先放在 experiment notes 中，等三倍率补齐后，再作为论文 supplementary 或新增 multi-scale comparison table。

