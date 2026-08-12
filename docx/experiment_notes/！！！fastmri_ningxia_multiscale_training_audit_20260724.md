# ！！！fastMRI / NingXia x2 x4 x6 训练与完整性审计（2026-07-24）

## 先看结论

- fastMRI-brain-T2 expanded 的 x2 / x4 / x6：主表中的 26 个 x2/x6 表格行均已有完整测试评估；x4 已在主表原三数据集表中完整记录。没有缺失的测试结果需要补跑。
- NingXia-T2 的 x4：历史 `baseline/ningxia_t2_*_cv/runs` 中的已纳入主表结果均已完成 8-fold 汇总。
- NingXia-T2 的 x2/x6：I3Net、HAT、SMamba 与 ACVTT 均已补齐为完整 8-fold；当前不再有常规 x2/x6 CV 训练缺口。
- 30 个 epoch 的日志不能单独证明“已完全拟合”或“未拟合”。本审计以验证集最优 epoch 是否贴近预算上限作为筛查条件，而不是把训练损失下降当成泛化改善。所有需要补齐的缺失结果优先于任何延长训练。

## 审计口径

1. **完整**：`fold_xx/<profile>/metrics/summary_metrics.csv` 存在，且该尺度 8 个 fold 都完整。
2. **半完成 / 未完成**：只有目录、checkpoint 或部分中间文件，而没有上述 summary；这类结果不进入均值，不进入主表结论。
3. **预算边界候选**：训练跑到 30 epoch 且最优 `val_loss` 在 epoch 28 或 29。它提示“30 轮可能不够”，但不是未拟合的证据；只有 60 轮续训后验证曲线仍改善，才能在论文内部说明原预算偏短。
4. **早停完成**：训练历史小于 30 epoch、但 summary 完整。这是 patience 触发的正常完成，不应为了凑满 30 轮而直接重跑。

## 当前完成状态

| 优先级 | 方法 / 尺度 | 当前状态 | 处理方式 |
|---|---|---|---|
| NingXia 常规 x2 / x6 CV | 训练与汇总均已完成 | 已更新主表。 |
| NingXia Res-SRDiff x2 90 epoch | 训练与汇总均已完成 | 已作为收敛诊断更新主表。 |
| fastMRI 60 epoch 收敛敏感性 | SwinIR x2、ACVTT x6、Res-SRDiff x2 均已完成 | 已作为收敛敏感性更新主表。 |

当前清单中不再有待执行训练命令；本文件保留审计口径与结果解释。

### 60 epoch 重训范围说明

- fastMRI：SwinIR x2、ACVTT x6、Res-SRDiff x2 的 60-epoch 重训均已完成，结果已写入主表收敛敏感性附表；其余训练日志没有足够强的持续下降证据，未启动重训。
- NingXia：常规 x2/x6、x2/x4/x6 的 60-epoch 组、Res-SRDiff x2 的 90-epoch 收敛诊断及相应汇总均已完成，故均已从命令区移除。
- 不列入 60 epoch 重训：I3Net（验证早停，不是边界耗尽）、GAN（对抗训练需单独的稳定性诊断）、已完成 fastMRI HAT x4 `full_extend60`、以及没有达到“至少半数 fold 或单次 fastMRI 运行在 epoch 28--29 最优”筛查条件的组合。

`full_extend60` / `full_x2_extend60` / `full_x6_extend60` 已写入相关 baseline 配置，统一为 `epochs=60`、`patience=12`、独立 run directory、从头训练；它们是重训敏感性实验，不覆盖当前主表的固定 30-epoch 结果。HAT x4 使用原有 `full_60_scratch`，因为原 `full_extend60` 是仅针对 fastMRI 历史 x4 run 的 warm-start profile。

`full_x2_extend90` 的 NingXia Res-SRDiff x2 收敛诊断已完成：`epochs=90`、`patience=16`、独立 run directory、从头训练。PSNR 从 60-epoch 的 22.6714 升至 23.5044，但仍明显低于同协议下的强确定性方法，支持将不足归因于扩散任务适配/标定，而不是继续增加 epoch。

## 30 epoch 边界审计：建议做“60 轮续训敏感性实验”

以下项目**不是缺失**，都已有完整评估。这里采用更严格的筛选：最后 8 个 validation loss 必须仍有清晰的整体下降，且末段没有明显平台或反弹；仅“最优 epoch=28/29”不再构成重训理由。

| 数据集 / 尺度 | 候选 | 日志证据 | 建议优先级 |
|---|---|---|---|
| fastMRI x2 | SwinIR、Res-SRDiff | 最后 8 个 val loss 分别下降 6.88%、7.23%；均已完成 60-epoch 独立重训 | 结果已写入主表敏感性附表。 |
| fastMRI x6 | ACVTT | 最后 8 个 val loss 下降 3.27%，末轮为最低点；已完成 60-epoch 独立重训 | 结果已写入主表敏感性附表。 |
| fastMRI 其余候选 | HAT、SAINT、SMamba、CycleINR、ArSSR、其余尺度 | 改善不足 2% 或末段波动/反弹，不能证明被 30 epoch 截断 | 不重训。 |
| NingXia x2 / x4 / x6 | 已完成的 60-epoch 组 | 已有完整 8-fold 结果与汇总 | 从命令区移除。 |
| NingXia x2 | Res-SRDiff | 60 epoch 的 8-fold 平均末段下降 14.78%，中位数下降 2.73%，4/8 fold 下降超过 2% | 唯一进入 90-epoch 收敛诊断的组合。 |

### 暂不建议因“30 轮”重训的完成项

- I3Net：fastMRI x2 在 epoch 17 早停、x6 最优 epoch 23；NingXia x2 的已完成 6 fold 均在更早 epoch 触发早停。这说明当前学习率/耐心组合已在验证集停止改善，不能简单用“加轮数”解释为欠拟合。
- Pix2Pix-GAN：fastMRI x2 17 epoch、x6 27 epoch 早停；NingXia 多数 fold 也早停。GAN 的对抗损失不宜用“再训 30 轮”机械处理，应独立看 visual QC 和生成器损失。
- Res-SRDiff 的 NingXia x2：虽然 8/8 fold 都在 epoch 28--29 取得最低验证损失，但最终指标显著低于 classical baseline（PSNR 15.3187）。这更像适配/强度标定问题，不应继续加训；这不影响保留 fastMRI x2 的独立收敛检查。
- ArSSR / CycleINR：除非论文需要同算力敏感性附录，否则不作为继续调参方向。

## 关于 60 轮命令的边界

当前大多数 baseline 的公开适配脚本只定义了 `full` / `full_x2` / `full_x6` 这三个 30-epoch profile，且没有通用 optimizer-state resume。因此不能把 `--profile full_x2` 再执行一次称为“续训”：那会从头重训并覆盖 checkpoint，既浪费资源，也不满足敏感性实验的含义。

fastMRI HAT x4 的 `full_extend60` 已从 `full` best checkpoint warm-start 训练过 30 个额外 epoch，主表 x4 已使用该结果。其余 P1 的独立 `*_extend60` profile 已实现为新的 60-epoch run directory；完成后的命令已从本清单移除。

## 写论文时如何表述

- 主文只报告每个方法按预先固定的训练预算和早停策略得到的 best-validation checkpoint；不需要为每个 baseline 罗列完整逐 epoch 曲线。
- 训练设置中应写明：最大 epoch=30、以 validation loss 选 checkpoint、patience=8（部分模型/扩展 profile 另行注明）。
- 对所有 P0 缺失项，在完整 8-fold 结果出现前保持 `pending`，不要用 6-fold 或 1-fold 数字参与排名。
- 如执行 P1，补充材料中报告 30 -> 60 epoch 的验证曲线和最终测试变化即可。若改善很小，可反向支撑“30 epoch 足以得到稳定比较”；若改善显著，则主表统一采用已固定的扩展预算并透明说明。
