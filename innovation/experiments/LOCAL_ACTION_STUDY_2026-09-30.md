# 固定修正动作的局部收益与结构代价：CPU 开发性诊断

本记录使用旧 fastMRI 同合同 control 与已停止的 orientation 分支，23 名历史 validation 患者、207 张缺失层。所有模型前向都在 CPU float32 完成；旧报告由 GPU autocast 得出，因此逐层 PSNR 的最大绝对差为 control 0.00815 dB、orientation 0.00445 dB。两个 checkpoint、数据 manifest、旧 CSV 的 SHA-256 写在[完整推理汇总](local_oracle_full_val23/summary.json)和[成对数组登记](local_oracle_paired_arrays_val23/manifest.json)。大数组在 `local_oracle_paired_arrays_val23/paired_predictions.npz`，只作本地开发材料，不含 test。

## 1. 行动空间有多大

在每张缺失层上固定 `b=control`、`r=orientation`，候选输出为 `b+alpha*(r-b)`。最佳全局 `alpha=0.70` 在同一验证集上从 0.01 网格乐观选择；整层真值 oracle 用 MSE 二次式求 `alpha`；局部真值 oracle 对 32×32 patch、步长 16 求 `alpha`，以正值 Hann 窗重组后按完整图像评分。

| 输出 | 患者等权 PSNR dB | MAE | SSIM | HD95 强度代理 |
|---|---:|---:|---:|---:|
| 原 control | 25.56147 | 0.024630 | 0.835089 | 5.40895 |
| 原 orientation | 25.65622 | 0.024606 | 0.834672 | 5.58205 |
| 同集最佳固定混合 | 25.67698 | 0.024484 | 0.835633 | 5.55633 |
| 整层真值连续混合 | 25.70912 | 0.024414 | 0.835949 | 5.52768 |
| patch 真值连续混合 | 25.82512 | 0.024077 | 0.838164 | 5.46025 |

patch oracle 相对最佳固定混合 +0.14815 dB，23/23 患者 PSNR 改善，说明此**固定动作对**确有空间异质性。但它读取目标像素；相对原 control 的 HD95 代理仍差 +0.05130，故不能将 +0.26365 dB PSNR 称为通过质量守卫的结果。病例级/逐层二选一 oracle 见[前次 CPU 诊断](CPU_RESULTS_2026-09-30.md)，其动作集合不同。

## 2. 从可观测量能找回多少

先用完整图像 MSE 的代数关系重建每层 `m=mean[(r-b)(y-b)]` 和 `d=mean[(r-b)^2]`，与已输出的整层 oracle 权重核对。在只对选择器留一患者的弱诊断中，phase、物理间隔、z 位置与模型分歧的整层 ridge 权重相对留一患者固定混合仅 +0.00742 dB；详见[整层 JSON](scalar_selector_diagnostic.json)。

再用局部可观测特征（phase、间隔、patch 位置、base 均值/纹理、两模型局部差值与梯度）预测 patch 权重，按同一窗重组并评分完整切片。留一患者 ridge 相对留一患者固定混合为 25.68950 vs 25.67568 dB，即 +0.01382 dB，20/23 患者 PSNR 更好；HD95 代理为 5.56294 vs 5.55720，略差。详见[patch JSON](patch_selector_diagnostic.json)。这里的“留一”只排除了当前患者的选择器标签；两个基础模型的 checkpoint 原本就用这些验证患者开发选择，不能声称整条链 OOF。

## 3. 真值幅度和结构守卫的冲突

将真值 patch oracle 相对 base 的增量再乘统一 `beta∈{0,0.1,...,1}`，重新计算完整图像指标。[幅度前沿](oracle_guard_frontier.json)显示：严格要求全部群体均值质量代理方向不退时，最大网格点为 `beta=0.1`、PSNR +0.03586 dB；`beta=0.2` 的 PSNR +0.06977 dB，但 HD95 代理由 5.40895 增至 5.41286；`beta=0.3` PSNR +0.10165 dB 时 HD95 进一步退化。这里的严格符号筛选只是开发性检查，不是原晋级协议的完整统计/效率门槛，也不是所有空间动作的上限。

若用真值**按患者**选 `beta` 并要求该患者的 SSIM、MAE、MSE、NCC、Dice/HD95 强度代理和 tail10 MSE 均不退，[患者真值 oracle](patient_guard_oracle.json)平均可得 +0.13747 dB；5/23 人只能保留 base，11/23 人至少 +0.10 dB。bootstrap 区间 [0.08647, 0.19403] dB 仅描述这批已开发患者。患者级真值选择仍不可部署。

最后用患者预测分歧、base 图像统计和物理间隔，以留一患者 ridge 预测保守 `beta`，但仍**使用真值 patch oracle**作为被放大的图像。[患者风险诊断](patient_risk_selector_diagnostic.json)为 +0.10241 dB，相对 base 的 HD95 代理仍差约 +0.00381，仅 11/23 人通过逐患者严格守卫。这个试验不能证明部署风险控制有效；它反而显示即使给出不可用的真值 patch 修正，简单患者特征也未可靠识别需要回退者。

## 当前决定与下一步

### 修复版 control / wavelet3 的同口径复核

为避免把结构代价归咎于旧 orientation 一对模型，又在相同 repaired fastMRI manifest、两个已完成 checkpoint 上按相同 CPU 协议运行 23 名患者、207 张缺失层。[完整结果](repaired_wavelet_oracle_full_val23/summary.json)的 CPU PSNR 与历史 GPU autocast 最大逐层绝对差分别约 0.00609 / 0.00431 dB。

| 输出 | 患者等权 PSNR dB | HD95 强度代理 |
|---|---:|---:|
| repaired control | 25.56683 | 5.34478 |
| 固定 wavelet3 / 同集最佳固定混合 `alpha=1` | 25.58459 | 5.29257 |
| 整层真值连续混合 | 25.58659 | 5.29360 |
| 32×32 patch 真值混合 | 25.60110 | 5.29880 |

patch 真值 oracle 相对固定 wavelet3 仅 +0.01651 dB；23/23 患者有 0.01017–0.02436 dB 的微小 PSNR 改善，但仅 7/23 人 HD95 代理改善，群体 HD95 也比固定 wavelet3 差约 +0.00623。这不是值得训练选择器的额外空间。它同样只说明此固定动作对与所测 patch/幅度范围，不是所有可学习修正的上限。修复版配对与旧 orientation 配对的数值不可交叉混合。

当前证据不支持用旧 orientation 动作直接训练大型 gate 或宣称“安全选择性修正”。它有局部 oracle 空间，但简单可观测特征只回收约 0.014 dB，结构代理守卫和真实可部署性仍未解决；修复版 wavelet 动作的 oracle 额外空间又太小。不能把这两个结果解释为所有修正动作、不同 patch 定义或新模型的理论上限。

下一轮不宜继续在同一验证患者上无界更换既有专家；优先审计项目现有测量影响论文的核心 claim，并准备独立的观测模型失配证伪试验。后者需要可信薄层参考和改变的真实/模拟 profile，且必须区分输入中心间距与输出层响应。最终正向 claim 仍需完整学习链的患者隔离、独立确认、匹配预算强基线与原项目完整层评价。GPU 上现有 IXI wavelet 训练继续由原终端控制，本轮没有修改它。

可复算入口：[成对推理及 oracle](local_correction_oracle.py)、[整层选择](scalar_selector_diagnostic.py)、[patch 选择](patch_selector_diagnostic.py)、[幅度前沿](oracle_guard_frontier.py)、[患者真值幅度](patient_guard_oracle.py)、[患者幅度预测](patient_risk_selector_diagnostic.py)。
