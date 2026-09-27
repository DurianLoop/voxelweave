# HAT / SMamba 证据交接包 — 2026-09-16

已找回 fastMRI n=24、NingXia 全 8-fold 的原始 CSV、训练 history、manifest 和普通 val-loss best checkpoint；历史五项数值全部可由 CSV 复算至四位小数一致。独立 IXI n=25 结果未找到。**按本次要求，没有 FORMAL_COMPLETE 结果，两种方法目前均不能进入三个数据集的统一正式主表。**

| Method | fastMRI | IXI n=25 | NingXia 8-fold | NingXia 4-fold | Training seed | Evidence status |
| --- | --- | --- | --- | --- | --- | --- |
| HAT | INVALID | MISSING | INVALID | INVALID | unknown/unrecorded | 原始证据已找回；strict-val 不合规 |
| SMamba | INVALID | MISSING | INVALID | INVALID | unknown/unrecorded | 原始证据已找回；strict-val 不合规 |


INVALID 表示不符合本次 strict friend-protocol，**不表示 CSV 损坏或数值伪造**。所有已审计 best checkpoint 的 epoch 和 best_val_loss 均匹配普通滑窗验证 history 的最小 loss；其验证过程使用密集体积归一化和滑动相位，不是严格 x4 sparse validation。见 [审计报告](AUDIT_REPORT.md)、[checkpoint 审计](checkpoint_audit.csv)。

指定四折可以计算，数据在 `HAT/NingXia_4fold_exploratory/` 和 `SMamba/NingXia_4fold_exploratory/`：

Post-hoc exploratory subset only.
Not a replacement for the formal 8-fold result.

其中源运行本身也不满足 strict-val 选模要求。

包内包含 21 个体积较小的原始 best checkpoint 副本：fastMRI 2 个、NingXia 16 个、IXI n=115 排除区 2 个、HAT fastMRI 60-epoch 另一个 profile 1 个。这些均为 **ordinary validation best，不是 strict best**。未复制 final checkpoint、MRI 图像体积或大型模型输出。

原始 checkpoint 均保持在本机：

- `D:\MRI\baseline\fastmri_brain_hat_2p5d\runs\full\checkpoints\hat_epoch_best.pth`
- `D:\MRI\baseline\fastmri_brain_smamba_unet_2p5d\runs\full\checkpoints\smamba_unet_epoch_best.pth`
- `D:\MRI\baseline\ningxia_t2_hat_2p5d_cv\runs\fold_00` 至 `fold_07` 下的 `full\checkpoints\hat_epoch_best.pth`
- `D:\MRI\baseline\ningxia_t2_smamba_unet_2p5d_cv\runs\fold_00` 至 `fold_07` 下的 `full\checkpoints\smamba_unet_epoch_best.pth`
- IXI n=115 和 HAT `full_extend60` 的逐个绝对路径、大小、SHA-256 均见 [checkpoint_audit.csv](checkpoint_audit.csv)；其他候选 checkpoint 见 [source_file_inventory.csv](source_file_inventory.csv)。

主要文件：

- `AUDIT_REPORT.md`：判定依据、协议核验、数值差异、搜索限制。
- `evidence_matrix.csv`、`seed_audit.csv`：8 行方法×数据集矩阵及种子证据。
- `source_file_inventory.csv`：源文件绝对路径、大小、SHA-256、复制去向。
- `sha256_manifest.csv`：包内文件 SHA-256；不包含自身，避免递归自校验。
- `missing_items.md`、`rerun_recommendations.md`：缺失项和需要授权后才能执行的最小任务。
- `historical_value_comparison.csv`：附件 20 项历史数值逐项对照。
- `run_candidate_audit.csv`：97 个发现的 run，记录其他 scale/profile 的排除原因。
- `run_level_audit.csv`、`numeric_consistency_checks.csv`、`validation_checks.csv`：21 个重点 run、105 项均值复算、756 项一致性检查。
- `search_scope.json`、`content_search_summary.json`：搜索范围和不可读临时目录，不将这些范围声称为已完整读取。
- `scripts/`：只读源审计、报告和打包代码；不会启动训练或推理。

原始数据、结果、论文主表和代码均未修改。本次只做既有文件审计、复制、CSV 聚合和打包；没有重新训练、推理或从 NIfTI 像素重新执行 metrics。当前源码哈希证明本次审计看到的源码，不能追溯证明历史训练运行时的 commit。历史 manifest 内迁移前的路径原样保留，当前位置由 inventory 映射。
