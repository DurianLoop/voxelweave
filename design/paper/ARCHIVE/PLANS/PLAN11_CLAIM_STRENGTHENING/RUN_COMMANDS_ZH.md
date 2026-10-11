# Plan 11 运行指令

更新时间：2026-08-27

以下命令均在 PowerShell 中运行。三项实验共享冻结协议 `PROTOCOL.md`，正式 IXI 任务使用同一个后缀 `full` 和 `--resume`，因此可以逐模型运行、失败后续跑，并在每次完成后重新汇总已经完成的模型。

## 0. 环境

```powershell
Set-Location D:\MRI
$env:PYTHONPATH = "D:\MRI\pre;D:\MRI\baseline;D:\MRI\design;D:\MRI"
D:\conda\envs\MRI\python.exe -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

## 1. 同模型 ×4→×2 受益预测

正式运行（fastMRI + NingXia，13 个同模型配对，5,000 次簇 bootstrap）：

```powershell
D:\conda\envs\MRI\python.exe -B .\design\paper\PLAN11_CLAIM_STRENGTHENING\scripts\p11_same_model_benefit.py --bootstrap 5000
```

该命令已经在 2026-08-27 成功运行。无后缀的正式输出位于 `outputs\p11_same_model_benefit_*`。

## 2. IXI 五架构 clean shared/disjoint 复制

### 2.1 一例冒烟测试

五个模型都会执行 checkpoint-wrapper-历史 phase-0 输出复现门控。CycleINR 一例约需 2 分钟，其余四个合计约 20 秒（当前机器实测，仅供估时）。

```powershell
D:\conda\envs\MRI\python.exe -B .\design\paper\PLAN11_CLAIM_STRENGTHENING\scripts\p11_ixi_five_arch_clean.py --models hat swinir i3net saint cycleinr --max-cases 1 --targets-per-case 5 --bootstrap 20 --device cuda --suffix smoke_manual
```

### 2.2 正式 115 例运行（推荐：逐模型、可续跑）

五条命令必须使用相同的 `--suffix full --resume`。每条结束后，汇总文件会包含该后缀下所有已经完成的模型。

```powershell
D:\conda\envs\MRI\python.exe -B .\design\paper\PLAN11_CLAIM_STRENGTHENING\scripts\p11_ixi_five_arch_clean.py --models hat --targets-per-case 5 --bootstrap 5000 --device cuda --suffix full --resume
```

```powershell
D:\conda\envs\MRI\python.exe -B .\design\paper\PLAN11_CLAIM_STRENGTHENING\scripts\p11_ixi_five_arch_clean.py --models swinir --targets-per-case 5 --bootstrap 5000 --device cuda --suffix full --resume
```

```powershell
D:\conda\envs\MRI\python.exe -B .\design\paper\PLAN11_CLAIM_STRENGTHENING\scripts\p11_ixi_five_arch_clean.py --models i3net --targets-per-case 5 --bootstrap 5000 --device cuda --suffix full --resume
```

```powershell
D:\conda\envs\MRI\python.exe -B .\design\paper\PLAN11_CLAIM_STRENGTHENING\scripts\p11_ixi_five_arch_clean.py --models saint --targets-per-case 5 --bootstrap 5000 --device cuda --suffix full --resume
```

```powershell
D:\conda\envs\MRI\python.exe -B .\design\paper\PLAN11_CLAIM_STRENGTHENING\scripts\p11_ixi_five_arch_clean.py --models cycleinr --targets-per-case 5 --bootstrap 5000 --device cuda --suffix full --resume
```

CycleINR 当前实测约 119 秒/例，115 例粗略估计约 3.8 小时；其他模型显著更快。不要添加 `--skip-wrapper-validation`，除非仅用于定位技术故障，且这类结果不能进入正式证据。

### 2.3 正式运行后的门控检查

```powershell
Import-Csv .\design\paper\PLAN11_CLAIM_STRENGTHENING\outputs\p11_ixi_wrapper_reproduction_full.csv | Format-Table model,case,mae,max_abs,tolerance,pass -AutoSize
```

```powershell
Import-Csv .\design\paper\PLAN11_CLAIM_STRENGTHENING\outputs\p11_ixi_clean_per_plane_full.csv | Group-Object model,condition | Select-Object Name,Count
```

预期：5 个 wrapper 均为 `pass=True`；每个模型每个 condition 应有 `115 × 5 = 575` 行。若病例中断，直接重跑对应模型的同一条 `--resume` 命令。

## 3. matched-geometry identity-swap

必须在第 2 节的五模型正式输出完成后运行：

```powershell
D:\conda\envs\MRI\python.exe -B .\design\paper\PLAN11_CLAIM_STRENGTHENING\scripts\p11_matched_geometry_identity.py --input-suffix full --output-suffix full --bootstrap 5000
```

检查每个模型是否保留了两个镜像 residue class，并同时查看方向效应：

```powershell
Import-Csv .\design\paper\PLAN11_CLAIM_STRENGTHENING\outputs\p11_identity_swap_model_summary_full.csv | Format-Table model,cases_with_both_mirror_classes,median_balanced_observable_gain,gain_ci_low,gain_ci_high,median_residue1_minus_residue3,orientation_warning -AutoSize
```

## 4. 关键输出

- `p11_same_model_benefit_summary.json`：×4→×2 正式汇总。
- `p11_same_model_benefit_correlations.csv`：每个数据集、模型、分数的相关与区间。
- `p11_ixi_wrapper_reproduction_full.csv`：五架构复现门控。
- `p11_ixi_clean_per_plane_full.csv`：IXI 原始目标平面级结果。
- `p11_ixi_clean_model_summary_full.csv`：IXI 模型级 clustered-bootstrap 汇总。
- `p11_identity_swap_balanced_per_case_full.csv`：镜像 residue 平衡后的病例级效应。
- `p11_identity_swap_model_summary_full.csv`：identity-swap 模型级区间与方向警告。

正式解释必须保留所有符合协议的模型和结果方向；`smoke_*` 文件只验证实现，不用于论文 claim。
