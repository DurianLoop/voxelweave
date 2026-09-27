# 最小补齐建议（未执行；训练需要后续明确授权）

现有文件能补齐历史证据，但不能通过改 checkpoint 文件名把 ordinary-val 变成 strict-val。

1. 先完成一次共享代码工作：建立真正的 sparse-input x4 strict validation、generated-only 正式 metrics、按预先固定验证指标选 best，并保存完整配置/训练 seed/代码 SHA/环境/数据 split/strict history/checkpoint SHA/final-test manifest。保留模型源身份；SMamba surrogate 若继续使用必须明确命名，若要声称官方模型则先提供并审查真实实现。不要自行写另一种近似模型冒充。
2. 现有重点 run 只留普通 best/final，不能重建整个历史 strict 选模过程。基于目前证据，建议两方法各补 fastMRI 1、IXI n=25 1、NingXia 8：合计 **20 个训练+strict-val 周期**，各自结束只对 strict best 执行一次 final-test，另 **20 个测试任务**。按一个训练与其测试组成完整 run 计为 **20 个 run**；按阶段计 **40 个任务**，不包括实现修复、身份核验和只读汇总。
3. NingXia 指定四折无需额外训练：从未来合规 8-fold 中按固定 fold_01/03/04/06 等权汇总，2 个纯汇总任务。完整 8-fold 永远保留。
4. 如果之后找到真正的 strict 运行/完整逐 epoch 候选和可靠记录，先审计再减少上述数量。禁止把现存 final 当作正式 checkpoint，也不能按 test 数值从不同 profile/seed/epoch 中挑选。

预计训练时长不作无依据估算：原始多 run 的硬件/环境未锁定，模型身份也需先明确。20 个 run 是目前可审计证据下的补齐预算，不是已执行任务。

## 当前可直接运行的只读核验命令

```powershell
Set-Location 'D:\MRI'
$auditRoot = 'D:\MRI\handoff_hat_smamba_evidence_2026-09-16'
Import-Csv -LiteralPath (Join-Path $auditRoot 'evidence_matrix.csv') |
    Select-Object method,dataset,status,training_seed
Import-Csv -LiteralPath (Join-Path $auditRoot 'checkpoint_audit.csv') |
    Select-Object method,checkpoint,epoch,selection
Import-Csv -LiteralPath (Join-Path $auditRoot 'recomputed_summaries.csv') |
    Select-Object method,dataset,folds,series,psnr,ssim,mae,mse,ncc
```

## 后续训练命令的真实限制

当前这份仓库没有可证明符合本次协议的 HAT/SMamba strict runner，也没有 `--strict-val` 或 `--best-strict` 这类现成开关。不能给出一个看似可运行却不存在的正式训练命令。现存入口是：

- IXI：`ixi_hat_2p5d.run_all` / `ixi_smamba_unet_2p5d.run_all`，`--profile full` 才是 test n=25；`full_test115` 是 n=115。
- fastMRI：`fastmri_brain_hat_2p5d.run_all` / `fastmri_brain_smamba_unet_2p5d.run_all`，`--profile full`。
- NingXia：`processing.run_ningxia_case_cv --profile full --models hat smamba`，fold_00 至 fold_07。

这些入口目前使用普通 validation，而且 run_all 会清理输出目录，**不能作为本次正式补跑命令直接执行**。已复制原脚本供实现时参考，没有运行它们。IXI 入口当前还有固定输出目录，必须先为新 run 实现独立 output root，不得沿用旧目录。

修复实现后建议采用以下执行接口（接口规格/命令模板，**当前尚未实现，禁止直接运行**）：

```text
<reviewed_strict_runner> --method <hat_style|smamba_verified_or_explicit_style>
  --dataset <fastmri|ixi|ningxia> --scale 4
  --split-manifest <frozen train/val/test manifest>
  --test-count <24|25|one fold's complete series>
  --seed <predeclared training seed>
  --checkpoint-selection strict-val
  --normalization sparse-minmax --generated-only
  --metrics-file D:/MRI/pre/topcow_diffusion/metrics.py
  --output <NEW_EMPTY_RUN_DIRECTORY>
```

上述是建议接口，不是声称仓库已有命令。真实实现、来源审查、独立输出路径及实际参数核验完成后，再给出可执行正式命令并等待训练授权；本次审计没有修改任何 baseline 代码。
