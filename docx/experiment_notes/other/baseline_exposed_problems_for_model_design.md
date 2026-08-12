# Baseline 暴露问题与自研模型设计备忘录

更新日期：2026-06-19

本文档用于进入自研模型阶段前，系统整理当前 T2 / x4 through-plane interpolation 主线中各类 baseline 已经暴露出的共性问题、可能原因、可转化的模型设计点，以及后续验证实验。目标不是再重复主表，而是把已有实验现象转换成“为什么需要一个新模型”和“新模型应该解决什么”的研发依据。

当前主线口径：

```text
Modality: T2
Scale: x4 through-plane interpolation
Input: sparse through-plane slices
Output: dense/interpolated intermediate slices
Main metrics: PSNR / SSIM / MAE / MSE / NCC
Main table: docx/experiment/experiment_master_table.md
Datasets: IXI-T2, fastMRI-brain-T2 expanded, NingXia-T2 case-level 8-fold CV
```

## 1. 一句话结论

当前 baselines 共同暴露的问题是：T2 x4 through-plane interpolation 不能只看成普通 2D 超分，也不能只靠连续坐标表达或更大的 Transformer。它同时需要：

- 强但受控的 interpolation prior。
- 相邻 sparse slices 的空间条件建模。
- offset / phase 感知。
- z 向解剖连续性。
- 对不同数据集强度、shape、slice depth 的鲁棒性。
- 对局部结构区域的保真，而不是只优化全图平均指标。
- 可接受的训练和显存成本。

因此，自研模型最有价值的方向不是“堆一个更大的通用 SR 网络”，而是做一个面向 through-plane synthesis 的轻量结构感知 residual 模型。

## 2. 当前主表证据快照

只摘最关键的 PSNR 趋势，完整指标仍以主表为准。

| Method | IXI-T2 n=25 PSNR | fastMRI-T2 n=24 PSNR | NingXia-T2 8-fold PSNR | 当前定位 |
|---|---:|---:|---:|---|
| Linear | 26.1113 | 19.1133 | 22.7335 | 强传统下限，尤其 IXI 上不弱。 |
| Cubic | 25.6655 | 17.9736 | 21.6460 | 经常低于 Linear，说明高阶平滑不一定适合。 |
| ArSSR-style | 27.1894 | 20.3143 | 23.1634 | INR published baseline，已补齐但非第一梯队。 |
| CycleINR-style | 26.1120 | 20.3156 | 22.9009 | INR published baseline，整体提升有限。 |
| ResUNet residual | 27.4698 | 22.2549 | 23.3816 | 内部 CNN residual baseline，稳定但不够强。 |
| SwinIR-style 2.5D | 28.7582 | 22.3615 | 23.9513 | 通用 Transformer SR 强基线，NingXia 均值最强。 |
| SAINT-style | 28.7980 | 23.2605 | 23.8350 | spatially-aware slice conditioning 强，fastMRI 很强。 |
| I3Net | 31.0386 | 24.0102 | 23.4911 | published medical slice synthesis 最关键 baseline；IXI/fastMRI 最强，NingXia 不占优。 |

这个表暴露出一个重要事实：没有单个 baseline 在三个数据集上稳定统治。I3Net 在 IXI 和 fastMRI 很强，但 NingXia 不如 SwinIR/SAINT；SwinIR 在 NingXia 最强，但 fastMRI 弱于 SAINT/I3Net；SAINT fastMRI 很强，但 IXI 上不如 I3Net。这个“不一致”正是自研模型的切入点。

### 2.1 三数据集全指标证据

下面把当前主线最关键的全指标均值集中放在这里，便于后面把问题和模型设计点挂到具体数据上。指标方向为：PSNR/SSIM/NCC 越高越好，MAE/MSE 越低越好。

#### IXI-T2 test n=25

| Method | Cases | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|
| Linear | 25 | 26.1113 | 0.8588 | 34.6798 | 7643.7916 | 0.9318 |
| Cubic | 25 | 25.6655 | 0.8486 | 36.9456 | 8472.9004 | 0.9215 |
| ArSSR-style | 25 | 27.1894 | 0.8825 | 30.0435 | 6130.4423 | 0.9474 |
| CycleINR-style | 25 | 26.1120 | 0.8587 | 34.6777 | 7643.8680 | 0.9318 |
| ResUNet residual | 25 | 27.4698 | 0.8874 | 29.3855 | 5680.4368 | 0.9508 |
| SwinIR-style 2.5D | 25 | 28.7582 | 0.9060 | 25.6723 | 4585.3369 | 0.9618 |
| SAINT-style | 25 | 28.7980 | 0.9027 | 26.1536 | 4552.2339 | 0.9622 |
| I3Net | 25 | 31.0386 | 0.9278 | 20.5964 | 2994.9736 | 0.9736 |

数据解读：

- I3Net 相对 Linear：PSNR +4.9273，SSIM +0.0690，MAE -14.0834，MSE -4648.8180，NCC +0.0418。
- SAINT 相对 Linear：PSNR +2.6867，SSIM +0.0439，MAE -8.5262，MSE -3091.5577，NCC +0.0304。
- SwinIR 相对 Linear：PSNR +2.6469，SSIM +0.0472，MAE -9.0075，MSE -3058.4547，NCC +0.0300。
- CycleINR 几乎贴着 Linear：PSNR 26.1120 vs 26.1113，说明 INR 若没有足够强的图像条件，很容易退化到接近插值。

#### IXI-T2 full test n=115 I3Net 复核

| Method | Cases | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|
| Linear | 115 | 26.1722 | 0.8529 | 29.2781 | 6553.8673 | 0.9390 |
| Cubic | 115 | 25.7138 | 0.8422 | 31.1269 | 7217.2979 | 0.9303 |
| I3Net | 115 | 30.7526 | 0.9231 | 18.5089 | 2858.7057 | 0.9771 |

paired wins：

- I3Net vs Linear：PSNR 115/115，SSIM 115/115，MAE 115/115，MSE 115/115，NCC 115/115。
- I3Net vs Cubic：PSNR 115/115，SSIM 115/115，MAE 115/115，MSE 115/115，NCC 115/115。

这说明任务匹配的 medical slice synthesis architecture 确实有效，不是 n=25 子集偶然结果。

#### fastMRI-brain-T2 expanded test n=24

| Method | Cases | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|
| Linear | 24 | 19.1133 | 0.5970 | 78.8111 | 23092.0046 | 0.7733 |
| Cubic | 24 | 17.9736 | 0.5332 | 91.9330 | 29740.2642 | 0.7285 |
| ArSSR-style | 24 | 20.3143 | 0.6575 | 65.9931 | 17745.8948 | 0.8301 |
| CycleINR-style | 24 | 20.3156 | 0.6577 | 66.0985 | 17743.2358 | 0.8302 |
| ResUNet residual | 24 | 22.2549 | 0.7374 | 53.5705 | 11842.8147 | 0.8955 |
| SwinIR-style 2.5D | 24 | 22.3615 | 0.7455 | 52.0221 | 11591.7882 | 0.8974 |
| HAT-style 2.5D | 24 | 22.7858 | 0.7536 | 49.6702 | 10454.4878 | 0.9079 |
| SMamba-UNet/Mamba-style | 24 | 22.7322 | 0.7618 | 49.4487 | 10826.4468 | 0.9051 |
| SAINT-style | 24 | 23.2605 | 0.7705 | 46.4417 | 9347.6662 | 0.9177 |
| I3Net | 24 | 24.0102 | 0.7921 | 41.0101 | 7755.6546 | 0.9308 |

数据解读：

- I3Net 相对 Linear：PSNR +4.8969，SSIM +0.1951，MAE -37.8010，MSE -15336.3500，NCC +0.1575。
- SAINT 相对 Linear：PSNR +4.1472，SSIM +0.1735，MAE -32.3694，MSE -13744.3384，NCC +0.1444。
- SwinIR 相对 Linear：PSNR +3.2482，SSIM +0.1485，MAE -26.7890，MSE -11500.2164，NCC +0.1241。
- HAT 相对 Linear：PSNR +3.6725，SSIM +0.1566，MAE -29.1409，MSE -12637.5168，NCC +0.1346。
- SMamba 相对 Linear：PSNR +3.6189，SSIM +0.1648，MAE -29.3624，MSE -12265.5578，NCC +0.1318。

paired wins：

- I3Net vs Linear：五个主指标均为 24/24 wins。
- I3Net vs SAINT：五个主指标均为 24/24 wins。
- SAINT vs SwinIR：五个主指标均为 24/24 wins。
- HAT vs SwinIR：五个主指标均为 24/24 wins。
- SMamba vs SwinIR：五个主指标均为 24/24 wins。

这组结果很关键：HAT/SMamba 这类更新或更强通用架构确实能超过 SwinIR，但仍低于 SAINT/I3Net。也就是说，自研模型不能只靠“换更强通用 SR backbone”，还必须解决 medical slice synthesis 的条件建模问题。

#### NingXia-T2 case-level 8-fold CV

| Method | Folds | Test series | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|---:|
| Linear | 8 | 22 | 22.7335 | 0.6749 | 103.2052 | 42189.1127 | 0.8576 |
| Cubic | 8 | 22 | 21.6460 | 0.6184 | 119.4078 | 53313.5368 | 0.8252 |
| ArSSR-style | 8 | 22 | 23.1634 | 0.7091 | 96.4890 | 38343.9409 | 0.8708 |
| CycleINR-style | 8 | 22 | 22.9009 | 0.6935 | 101.0990 | 40735.3568 | 0.8625 |
| ResUNet residual | 8 | 22 | 23.3816 | 0.7209 | 97.0409 | 36316.2290 | 0.8785 |
| I3Net | 8 | 22 | 23.4911 | 0.7208 | 93.5655 | 35725.4805 | 0.8825 |
| SAINT-style | 8 | 22 | 23.8350 | 0.7422 | 89.4140 | 32992.9496 | 0.8905 |
| SwinIR-style 2.5D | 8 | 22 | 23.9513 | 0.7525 | 85.9679 | 32030.5455 | 0.8930 |

数据解读：

- SwinIR 相对 Linear：PSNR +1.2178，SSIM +0.0776，MAE -17.2373，MSE -10158.5672，NCC +0.0354。
- SAINT 相对 Linear：PSNR +1.1015，SSIM +0.0673，MAE -13.7912，MSE -9196.1631，NCC +0.0329。
- I3Net 相对 Linear：PSNR +0.7576，SSIM +0.0459，MAE -9.6397，MSE -6463.6322，NCC +0.0249。

paired wins：

- I3Net vs Linear：PSNR 20/22，SSIM 20/22，MAE 20/22，MSE 20/22，NCC 21/22。
- SwinIR vs SAINT：PSNR 16/22，SSIM 22/22，MAE 20/22，MSE 16/22，NCC 15/22。
- SwinIR vs I3Net：PSNR 21/22，SSIM 22/22，MAE 21/22，MSE 21/22，NCC 22/22。
- SAINT vs I3Net：PSNR 20/22，SSIM 22/22，MAE 21/22，MSE 20/22，NCC 22/22。

NingXia 这组结果最能暴露跨域问题：I3Net 在 IXI/fastMRI 极强，但到临床小样本 CV 上不如 SwinIR/SAINT。这说明“任务匹配”还不等于“跨域鲁棒”。

### 2.2 视觉 QC 数据支撑

SAINT vs SwinIR 的 visual QC 已选出 fastMRI 和 NingXia 代表病例，面板位于：

```text
docx/experiment_notes/visual_qc/saint_vs_swinir/
```

代表切片数据：

| Dataset | Label | Case | Slice | SAINT PSNR | SwinIR PSNR | SAINT-SwinIR PSNR | SAINT SSIM | SwinIR SSIM | SAINT grad-MAE | SwinIR grad-MAE |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| fastMRI | small_gap | 103098218097_ax_t2 | 2 | 23.0489 | 22.9028 | +0.1461 | 0.7710 | 0.7617 | 43.4638 | 43.6371 |
| fastMRI | median_gap | 108917069439_ax_t2 | 2 | 24.2436 | 23.2717 | +0.9719 | 0.8024 | 0.7721 | 41.0607 | 41.9316 |
| fastMRI | large_gap | 110005080074_ax_t2 | 2 | 25.3419 | 23.8493 | +1.4926 | 0.8394 | 0.8080 | 24.9699 | 25.8614 |
| NingXia | saint_better | NX001_ce72161303f3 | 15 | 24.0366 | 23.8912 | +0.1454 | 0.7295 | 0.7301 | 36.5361 | 36.9111 |
| NingXia | near_tie | NX006_539c16575ab2 | 9 | 20.2233 | 20.3101 | -0.0868 | 0.6812 | 0.6963 | 53.5782 | 53.8809 |
| NingXia | swinir_better | NX007_4fc7b295b09b | 2 | 25.8983 | 26.4744 | -0.5761 | 0.7761 | 0.8098 | 43.0336 | 42.5823 |

视觉结论：

- fastMRI 中，SAINT 对 SwinIR 的优势从小差距到大差距都存在，large gap 病例 PSNR 高 +1.4926，SSIM 高 +0.0314，gradient MAE 也更低。
- NingXia 中，SAINT 和 SwinIR 的优劣更混合；SwinIR better 病例中 PSNR 高 +0.5761，SSIM 高 +0.0336，gradient MAE 也更低。
- 因此，自研模型不能只追全局 PSNR，还要看局部边界、脑室、脑沟、outer boundary、亮结构等区域。

### 2.3 效率与样本规模数据支撑

训练规模：

| Dataset | Train cases | Val cases | Train samples | Val samples | batch=8 steps/epoch |
|---|---:|---:|---:|---:|---:|
| IXI-T2 full/full_test115 | 404 | 58 | 153195 | 22086 | 19150 |
| fastMRI-brain-T2 full | 112 | 24 | 4080 | 864 | 510 |

IXI 的训练样本数约为 fastMRI 的 37.55 倍。任何自研模型如果太重，IXI full 都会成为主要瓶颈。

前向效率 profiling：

| Method | Params | FLOPs(G) | Forward ms | Peak CUDA memory |
|---|---:|---:|---:|---:|
| SAINT-style | 1.1973M | 35.7606 | 3.0969 ms | 117.30 MB |
| SwinIR-style 2.5D | 0.2239M | 28.3682 | 4.2980 ms | 251.23 MB |

效率解读：

- SAINT 参数更多，但当前实现下 forward 更快、peak memory 更低。
- SwinIR 参数更少，但 attention/窗口实现带来更高 peak memory。
- 因此，参数量不是唯一效率指标；自研模型必须同时报告 Params、FLOPs、forward time、peak CUDA memory。

## 3. Baseline 家族逐项暴露问题

### 3.1 Linear / Cubic

已知现象：

- Linear 是很强的非学习下限，尤其 IXI 上并不弱。
- Cubic 多数情况下低于 Linear。
- 这说明 MRI T2 through-plane 插值不是“越平滑越好”，高阶插值可能改变强度分布或引入不合适的局部过冲。

暴露问题：

- 直接生成完整 slice 容易浪费模型容量，因为大部分低频结构 Linear 已经能提供。
- 如果模型只学平滑，会贴近 Linear 而很难显著增益。
- 如果模型追求锐化，可能破坏 MRI 强度真实性。

模型启发：

- 自研模型应优先采用 coarse-to-fine residual 口径。
- 输入保留 `linear coarse`，输出预测 `residual`。
- residual 应偏向结构区域，而不是全图无差别修正。

可验证 ablation：

- `without linear coarse`：只用左右 sparse slices 预测。
- `direct prediction` vs `residual prediction`。
- residual clipping / residual scaling 是否提升 NingXia 稳定性。

### 3.2 ResUNet residual

已知现象：

- ResUNet residual 明显强于 Linear/Cubic。
- 但在 fastMRI 和 NingXia 上通常低于 SwinIR/SAINT/I3Net。

暴露问题：

- CNN residual 学局部纹理和低层结构有效，但跨 slice 的全局结构推断不足。
- U-Net skip connection 容易保留 coarse 形态，但对相邻 slice 的空间错位、形变和拓扑变化建模有限。
- 单纯扩大 CNN 通道数未必解决 through-plane 几何问题。

模型启发：

- CNN 可以作为局部细节编码器，但不应是唯一核心。
- 需要加入 cross-slice fusion、phase embedding、轻量 attention 或序列模块。
- 局部 encoder 与跨层融合模块分工：CNN 管局部结构，fusion 模块管左右 slice 的变化趋势。

### 3.3 ArSSR-style / CycleINR-style

已知现象：

- ArSSR 和 CycleINR 已作为 INR published baseline 横向补齐。
- CycleINR 在 IXI 基本接近 Linear，在 fastMRI/NingXia 也不进入第一梯队。
- ArSSR 在 NingXia 比 Linear 有提升，但仍明显低于 SwinIR/SAINT/I3Net 第一梯队。

暴露问题：

- 连续坐标表达本身不是瓶颈。
- 如果图像条件弱，INR 容易变成平滑插值器。
- 本任务的核心是缺失中间 slice 的解剖结构推断，而不是单纯拟合坐标函数。

模型启发：

- 不建议把 pure INR 作为自研模型主路线。
- 如果用 implicit 表达，更适合作为 offset-aware residual head。
- 坐标或 phase 输入应服务于局部结构修正，而不是代替强图像特征。

可验证 ablation：

- 在 residual decoder 末端加入 coordinate/phase MLP，看是否提升 offset=1/4、2/4、3/4 的一致性。
- 比较 pure convolution residual head 与 phase-conditioned implicit residual head。

### 3.4 SwinIR-style 2.5D

已知现象：

- IXI 和 fastMRI 都明显强于传统插值、ResUNet、INR。
- NingXia 8-fold CV 平均指标当前最强。
- fastMRI 上弱于 SAINT 和 I3Net。

暴露问题：

- 通用 2D Transformer SR prior 有价值，尤其对局部纹理和边界。
- 但 SwinIR-style 不天然理解 x4 sparse acquisition 的相位关系。
- 它更像强 restoration backbone，而不是专门的 medical slice synthesis 模型。

模型启发：

- 可以吸收窗口注意力或局部窗口 token mixing。
- 必须显式加入相邻 slice 条件和 offset/phase。
- 不应只是“把 SwinIR 换成 HAT”，否则创新点会被看成通用 SR 迁移。

可验证 ablation：

- SwinIR-like backbone + phase embedding。
- SwinIR-like backbone + spatially-aware left/right gating。
- 去掉或保留 linear coarse 的差异。

### 3.5 SAINT-style

已知现象：

- fastMRI 上非常强，此前为最强 baseline，I3Net 加入后仍是第一梯队。
- NingXia 上紧跟 SwinIR。
- visual QC 显示 fastMRI 中 SAINT 的优势常出现在脑室、脑沟、高对比外边界。

暴露问题：

- 相邻 slice 的 spatially-aware conditioning 很关键。
- 只做单张 2D restoration 不够，左右 anchor slice 之间的空间关系需要显式建模。
- fastMRI 这种传统插值明显下降的数据集上，空间条件建模收益更大。

模型启发：

- 自研模型应有 explicit left/right slice fusion。
- 融合不能只是通道 concat，最好是位置相关或结构相关的 adaptive gating。
- phase/offset 应影响左右 slice 的权重，例如 offset=1/4 时更靠近左侧 anchor，offset=3/4 时更靠近右侧 anchor。

可以考虑的模块：

```text
left feature, right feature, coarse feature, phase embedding
        -> spatially adaptive gate
        -> fused feature
        -> residual decoder
```

### 3.6 I3Net

已知现象：

- I3Net 是当前最任务匹配的 published medical slice synthesis baseline。
- IXI-T2 n=115：I3Net 对 Linear/Cubic 在 115/115 cases 上全指标胜出。
- fastMRI：I3Net 对 Linear 24/24 cases 全指标胜出，也是当前 fastMRI 最强。
- NingXia：I3Net 明显优于传统插值和多数中等 baseline，但不如 SwinIR/SAINT。

暴露问题：

- inter-/intra-slice window 是有效的。
- 但任务匹配不等于跨域鲁棒，NingXia 暴露了临床小样本和强度/shape 分布差异。
- I3Net-like 大窗口可能更依赖训练域的 slice continuity 和采集分布。

模型启发：

- 可以借鉴 multi-slice window / inter-intra 建模思想。
- 但需要更强 domain robustness，例如强度自适应、轻量化、结构约束。
- 不宜只复刻 I3Net 形态，应明确解决其 NingXia 不占优的问题。

可验证 ablation：

- 2-slice anchors vs 4-slice anchors。
- 单 slice residual output vs window output。
- 加入 domain/contrast normalization 后 NingXia fold 稳定性是否提升。

### 3.7 HAT-style / SMamba-style

已知现象：

- HAT mini 强于 SwinIR mini，值得扩展。
- SMamba/Mamba-style 有 2024+ 架构意义，但当前 screening 不显示明显超越 SwinIR。
- full 训练显存和耗时压力较大。

暴露问题：

- 更新架构本身不是充分贡献。
- 重型 attention 或状态空间模块若没有任务特化，可能只是提高成本。
- 训练成本会影响实验可完成性和论文可复现性。

模型启发：

- 如果用 Mamba/attention，应作为轻量 token mixing 或 z-direction modeling 模块，而不是整网堆叠。
- 重点是解释“为什么这个模块解决 through-plane 问题”。
- 自研模型必须报告效率，否则容易被质疑只是用更大模型换指标。

## 4. 共性问题归纳

### 4.1 问题 A：强下限导致“普通学习模型”容易只学到平滑

Linear 已经提供很强低频形态。模型如果没有明确结构目标，很容易学成一个平滑修正器。

具体表现：

- INR 线整体增益有限。
- CycleINR 在 IXI 接近 Linear。
- ResUNet 虽有提升，但不进入最强梯队。

可改进方向：

- residual prediction。
- structure-weighted residual。
- edge/gradient-aware loss。
- 高频区域自适应增强，但限制 hallucination。

### 4.2 问题 B：offset/phase 是任务变量，不是普通输入噪声

x4 中间层不是同一个任务：

```text
offset=1/4: 更接近左 anchor
offset=2/4: 居中
offset=3/4: 更接近右 anchor
```

如果模型没有显式 phase 信息，就只能从图像中隐式猜测目标位置。

可改进方向：

- phase embedding。
- phase-conditioned normalization。
- phase-conditioned left/right gate。
- 对三个 offset 分别统计指标，检查是否某个 offset 明显弱。

建议后续增加的诊断：

| 诊断项 | 目的 |
|---|---|
| offset=1/4 PSNR/SSIM | 看靠近左 anchor 的预测是否更容易。 |
| offset=2/4 PSNR/SSIM | 看最难的中间位置是否被充分建模。 |
| offset=3/4 PSNR/SSIM | 看模型是否左右对称。 |
| left-right flip consistency | 检查输入左右翻转后预测是否一致。 |

### 4.3 问题 C：左右 slice 融合不能只是 concat

SAINT 和 I3Net 的结果说明，相邻 slices 的关系非常重要。简单 concat 只能把信息交给后续卷积自己学，可能不足以处理结构位移。

可改进方向：

- spatially adaptive gate。
- cross-attention between left/right slices。
- deformable or correlation-based alignment。
- phase-conditioned interpolation of features。

一个轻量设计草案：

```text
F_l = Encoder(left)
F_r = Encoder(right)
F_c = Encoder(linear coarse)
p = PhaseEmbedding(offset)

G_l, G_r = Gate(F_l, F_r, F_c, p)
F = G_l * F_l + G_r * F_r + F_c
residual = Decoder(F, p)
output = coarse + residual
```

### 4.4 问题 D：局部视觉结构与平均指标存在错位

visual QC 已经显示，差异常集中在：

- ventricles。
- sulci。
- outer brain boundary。
- bright structures。
- high-contrast edge。

全图 PSNR/MAE 会被大量背景和低频区域稀释。模型如果只优化全图平均 loss，可能对这些关键局部结构不够敏感。

可改进方向：

- gradient-weighted L1。
- Laplacian / Sobel edge loss。
- structure mask weighting。
- local SSIM 或 patch-level contrast loss。
- residual 只在结构区域加强，平滑区域保持保守。

注意事项：

- MRI 不能鼓励 hallucination。
- 高频 loss 应该约束为“贴近 GT 的边界恢复”，不是凭空造纹理。
- 需要 visual QC 支撑，不能只报边缘指标。

### 4.5 问题 E：跨数据集鲁棒性不足

IXI、fastMRI、NingXia 的分布差异明显：

| 数据集 | 特点 | 暴露风险 |
|---|---|---|
| IXI | 相对干净，depth 深，传统插值强 | 容易高估模型在干净数据上的表现。 |
| fastMRI | public complex brain T2，depth 较短，Linear 下降明显 | 能体现学习模型收益，但样本数实际比 IXI 少很多。 |
| NingXia | 本地临床外部验证，8 cases / 22 series，shape/强度差异更大 | 小样本 CV，fold 方差和 domain shift 更明显。 |

可改进方向：

- instance-level normalization。
- contrast-invariant feature。
- intensity residual scaling。
- training augmentation：强度缩放、bias field、noise、轻微 blur/sharpness。
- 小样本临床数据上避免过大模型。

### 4.6 问题 F：sliding sample 与严格 x4 acquisition grid 的口径差异

当前一些 baseline 的 single-slice 样本构造使用 sliding：

```python
for z in range(0, depth - stride):
    for offset in range(1, stride):
        items.append((path, z, offset, depth))
```

严格 x4 acquisition grid 更接近：

```python
for z in range(0, depth - stride, stride):
    for offset in range(1, stride):
        items.append((path, z, offset, depth))
```

这不是 train/test 泄露，因为 split 已经在 volume/case 层面完成。但 sliding 会引入 phase augmentation，使训练看到更多非全局 sparse phase 的组合。

可改进方向：

- 自研模型训练先沿用当前主表口径，保证横向公平。
- 额外做 phase-aligned ablation，证明严格 acquisition grid 下也有效。
- 在论文中把 sliding 解释为 phase augmentation，而不是偷偷混淆任务。

### 4.7 问题 G：训练效率会约束模型路线

IXI full train samples = 153195，batch=8 时每轮约 19150 step。fastMRI train samples = 4080，每轮约 510 step。IXI full 很容易成为训练瓶颈。

可改进方向：

- 轻量 residual model。
- 尽量 2.5D，而不是 full 3D heavy model。
- 少量 attention / Mamba 放在瓶颈层或 fusion 层。
- 报告 Params / FLOPs / inference time / GPU memory。

不建议：

- 一上来堆完整 HAT 级重模型。
- 直接上 diffusion full training。
- 依赖 shared GPU memory 才能跑通的设计。

## 5. 自研模型可以主打的设计目标

建议把自研模型目标写成五个关键词：

```text
Residual
Phase-aware
Spatially-adaptive
Structure-preserving
Domain-robust
```

对应关系：

| 关键词 | 解决的问题 | 具体实现方向 |
|---|---|---|
| Residual | Linear 下限强，直接生成不稳 | `output = linear_coarse + residual` |
| Phase-aware | offset=1/4,2/4,3/4 是不同任务 | phase embedding / FiLM / conditional norm |
| Spatially-adaptive | 左右 slice 贡献随位置和结构变化 | left-right adaptive gate / cross-attention |
| Structure-preserving | 局部边界和脑结构容易被平均指标掩盖 | edge loss / gradient-weighted residual / visual QC |
| Domain-robust | NingXia 小样本临床外部验证不稳定 | instance normalization / contrast augmentation / residual scaling |

## 6. 一个推荐的第一版模型框架

第一版自研模型建议不要过重，先做一个清晰、可解释、可 ablation 的结构。

### 6.1 输入

对每个目标 missing slice，输入：

```text
left sparse slice:      L
right sparse slice:     R
linear coarse slice:    C
relative phase map:     P, value in {1/4, 2/4, 3/4}
optional difference:    D = R - L
optional gradients:     grad(C), grad(L), grad(R)
```

最小输入版本：

```text
[L, R, C, P]
```

增强输入版本：

```text
[L, R, C, R-L, |R-L|, grad(C), P]
```

### 6.2 主体结构

推荐结构：

```text
Input preparation
    L, R, C, P

Shared local encoder
    E_l = Enc(L)
    E_r = Enc(R)
    E_c = Enc(C)

Phase-aware fusion
    p = PhaseEmbedding(P)
    G_l, G_r, G_c = SpatialGate(E_l, E_r, E_c, p)
    F = G_l * E_l + G_r * E_r + G_c * E_c

Lightweight context mixer
    F' = SmallWindowAttention(F) or LightweightMamba(F) or ConvNeXtBlock(F)

Residual decoder
    res = Dec(F', p)
    out = C + alpha * res
```

这里 `alpha` 可以是固定值，也可以是可学习的 residual scale。这样能避免模型过度改变 coarse 强度。

### 6.3 可选模块

| 模块 | 目的 | 风险 |
|---|---|---|
| phase-conditioned FiLM | 让不同 offset 使用不同特征调制 | 过强可能导致 offset 过拟合。 |
| left/right spatial gate | 学习每个像素更信任左 slice 还是右 slice | gate 可视化需要检查，否则可能退化。 |
| small window attention | 增强局部结构建模 | 显存增加。 |
| lightweight Mamba block | 提供长程 token mixing 和 2024+ 架构元素 | 如果没有任务解释，容易变成堆新模块。 |
| edge-aware residual head | 强化边界区域 | 需避免 hallucination。 |
| uncertainty/confidence head | 估计哪里需要大 residual | 训练和解释更复杂。 |

## 7. Loss 设计建议

基础 loss：

```text
L_main = L1(out, gt)
```

建议组合：

```text
L = L1(out, gt)
  + lambda_grad * L1(grad(out), grad(gt))
  + lambda_res * smooth_or_bound(residual)
  + lambda_z * z_consistency
```

可选项解释：

| Loss | 作用 | 注意 |
|---|---|---|
| L1 | 稳定，适合强度回归 | 主 loss。 |
| MSE | 提升 PSNR 相关性 | 可能更偏平滑。 |
| Gradient loss | 强化边界和局部结构 | 权重不能太大。 |
| SSIM loss | 强化结构相似性 | 与 PSNR/MAE 可能有 trade-off。 |
| Residual regularization | 防止过度修改 coarse | 对 NingXia 稳定性可能有用。 |
| Z-consistency | 约束 slice 间连续变化 | 需要 batch/window 支持。 |

第一版建议：

```text
L = L1 + 0.05 * gradient_L1 + 0.001 * residual_L2
```

后续再做 loss ablation，不要一开始叠太多。

## 8. 必做 ablation 设计

为了让自研模型能写成论文，建议从第一版就把 ablation 设计好。

| Ablation | 对应 claim | 预期观察 |
|---|---|---|
| Direct output vs residual output | residual prior 是否必要 | residual 应更稳，尤其 IXI/NingXia。 |
| Without phase embedding | phase-aware 是否有效 | offset=1/4/3/4 或中间 offset 指标下降。 |
| Concat fusion vs spatial gate | 自适应左右融合是否有效 | fastMRI 边界和 NingXia fold 稳定性提升。 |
| Without linear coarse | interpolation prior 是否关键 | PSNR/MAE 下降，训练更慢。 |
| Without gradient loss | 结构约束是否有效 | visual QC 边界更平，SSIM/局部指标下降。 |
| Light mixer type: Conv / Attention / Mamba | 哪种上下文建模最划算 | 找性能/效率最优点。 |
| Sliding vs phase-aligned training | phase augmentation 是否影响口径 | 严格 x4 grid 下仍要有收益。 |
| Full model vs small model | 容量是否过度 | NingXia 小样本可能更偏好轻量模型。 |

## 9. 诊断指标建议

主表仍只放 PSNR / SSIM / MAE / MSE / NCC。但研发阶段建议额外记录：

| 诊断 | 用途 |
|---|---|
| per-offset metrics | 判断 1/4、2/4、3/4 哪个最难。 |
| per-case wins | 避免均值被少数 case 拉高。 |
| per-fold NingXia metrics | 检查小样本临床稳定性。 |
| residual magnitude | 看模型是否过度修改 Linear。 |
| gradient MAE | 对应边界/结构保真。 |
| inference time | 控制效率。 |
| peak CUDA memory | 控制可复现性。 |
| Params / FLOPs | 证明不是单纯堆模型。 |

建议研发日志每次记录：

```text
dataset
profile
train_samples
batch_size
grad_accum_steps
effective_batch_size
best_val_loss
test metrics
per-offset metrics
params
inference time
peak memory
```

## 10. 论文叙事可以怎么写

不建议叙事：

```text
现有方法都不好，所以我们提出一个更大模型。
```

因为 I3Net、SAINT、SwinIR 都已经很强。

更建议叙事：

```text
现有方法各自解决了 T2 x4 through-plane interpolation 的一部分问题：传统插值提供强低频先验，通用 SR Transformer 擅长局部恢复，SAINT/I3Net 证明相邻 slice 条件很重要，INR 提供连续位置建模但图像条件不足。然而这些方法没有同时处理 offset/phase 感知、空间自适应左右融合、结构区域保真、跨数据集强度鲁棒性和可接受效率。为此，我们设计一个轻量 phase-aware spatial residual model。
```

可以形成的 contribution 草案：

1. 提出一个面向 T2 x4 through-plane interpolation 的 phase-aware residual synthesis framework。
2. 设计 spatially adaptive left-right slice fusion，在不同 offset 和局部结构区域自适应利用相邻 sparse slices。
3. 引入 structure-aware residual refinement，在保持 Linear coarse 强先验的同时改善边界和局部解剖结构。
4. 在 IXI、fastMRI-brain-T2 expanded、NingXia case-level CV 上与 Linear/Cubic、INR、CNN、Transformer、SAINT/I3Net 等 baselines 系统比较。
5. 补充效率和 visual QC，证明模型不是用不可接受成本换取指标。

## 11. 第一阶段实验计划

建议按以下顺序搓模型，避免一开始做太大。

### Stage 0: 代码骨架

目标：

- 新建一个自研模型 package。
- 复用现有 data / metric / paper_table 口径。
- 先跑 IXI smoke，确认输入输出和指标链路正确。

最低标准：

- 能跑通 `smoke`。
- 输出 shape 正确。
- Linear/Cubic baseline 同步输出。
- 指标文件能生成。

### Stage 1: Residual baseline

模型：

```text
[L, R, C, P] -> small CNN -> residual -> C + residual
```

目标：

- 证明 residual 口径有效。
- 与 ResUNet / SwinIR mini 对比。

### Stage 2: Phase-aware fusion

加入：

- phase embedding。
- left/right/coarse spatial gate。

目标：

- 看 per-offset 指标是否提升。
- 看 fastMRI 上是否更接近 SAINT/I3Net。

### Stage 3: Structure-aware loss

加入：

- gradient loss。
- residual regularization。

目标：

- 看 visual QC 的边界是否改善。
- 避免只提升 PSNR 但结构变差。

### Stage 4: Lightweight context mixer

尝试：

- ConvNeXt-style block。
- small window attention。
- lightweight Mamba block。

目标：

- 在性能和效率之间找最优点。
- 不优先追求最大模型。

### Stage 5: 三数据集 full

进入条件：

- IXI smoke/mini 稳定。
- IXI full_test115 有明确增益。
- fastMRI full 至少接近 SAINT/I3Net 或明显超过 SwinIR/ResUNet。

然后再跑 NingXia 8-fold CV。

## 12. 当前最推荐的第一版模型定义

第一版可以暂命名为：

```text
Phase-Aware Spatial Residual Network
```

最小可实现版本：

```text
Input:  L, R, C, P
Encoder: shared lightweight CNN
Fusion: phase-conditioned spatial gate
Mixer:  2-4 residual blocks
Head:   residual prediction
Output: C + residual_scale * residual
Loss:   L1 + gradient_L1 + small residual regularization
```

这个版本的优点：

- 和 Linear/Cubic 的差异清楚：不是直接插值，而是结构残差修正。
- 和 ResUNet 的差异清楚：有 phase-aware left/right fusion。
- 和 SwinIR/HAT 的差异清楚：不是通用 SR，而是 x4 through-plane 专用。
- 和 SAINT/I3Net 的差异清楚：更轻量，强调 residual 和 domain robustness。
- 和 INR 的差异清楚：连续 phase 只是条件，不把坐标表达当作唯一核心。

## 13. 需要避免的坑

| 坑 | 为什么危险 | 建议 |
|---|---|---|
| 一上来堆大模型 | IXI full 成本太高，NingXia 小样本可能不稳 | 先轻量模型 + ablation。 |
| 只看 PSNR | 可能边界变平或局部结构差 | 加 visual QC 和 gradient MAE。 |
| 不区分 offset | 三个 missing positions 难度不同 | 做 per-offset metrics。 |
| 忽略 Linear 强先验 | 模型可能学成平滑器 | residual + coarse input。 |
| 把 sliding 当严格 acquisition | 论文口径容易被质疑 | 明确 phase augmentation，补 phase-aligned ablation。 |
| 只在 IXI 上调 | IXI 干净，可能过拟合开发集 | fastMRI 和 NingXia 必须保留。 |
| 只说用了 Mamba/Transformer | 架构名不是贡献 | 必须绑定 through-plane 问题解释。 |

## 14. 可直接作为模型设计 checklist

开始写代码前逐项确认：

- [ ] 是否保留 Linear coarse 作为输入。
- [ ] 是否采用 residual output。
- [ ] 是否显式输入 phase / offset。
- [ ] 是否区分 left/right anchor 的贡献。
- [ ] 是否有局部结构增强机制。
- [ ] 是否有防止 residual 过大的约束。
- [ ] 是否能输出 per-offset metrics。
- [ ] 是否能记录 Params / FLOPs / inference time / peak memory。
- [ ] 是否能先 IXI smoke/mini，再 IXI full_test115，再 fastMRI/NingXia。
- [ ] 是否有足够 ablation 支撑每个创新点。

## 15. 证据到模型动作的对应矩阵

这一节把上面的数据证据压缩成可以直接指导建模的决策表。

| 数据证据 | 暴露问题 | 模型动作 |
|---|---|---|
| IXI n=25 Linear PSNR 26.1113，CycleINR 26.1120，几乎持平 | 弱条件 INR 容易退化到插值水平 | 不把 pure INR 作为主线；若用坐标，只作为 phase-aware residual head。 |
| Cubic 在三数据集均低于 Linear：IXI 25.6655 vs 26.1113，fastMRI 17.9736 vs 19.1133，NingXia 21.6460 vs 22.7335 | 高阶平滑/过冲不适合 MRI T2 强度结构 | 避免盲目锐化；使用 residual scaling / residual regularization。 |
| I3Net 在 IXI n=115 对 Linear/Cubic 五指标 115/115 wins | medical slice synthesis 的任务匹配非常有效 | 借鉴 inter-/intra-slice、window 或 cross-slice fusion 思路。 |
| I3Net 在 fastMRI 对 SAINT 五指标 24/24 wins，且 PSNR 24.0102 | 多 slice / task-matched published baseline 是当前最强 fastMRI 证据 | 自研模型不能只做通用 SR backbone，需要显式 slice synthesis 条件。 |
| I3Net 在 NingXia 低于 SwinIR/SAINT，SwinIR vs I3Net 五指标最多 22/22 wins | 任务匹配不等于跨域鲁棒 | 加 domain-robust normalization、contrast augmentation、轻量容量控制。 |
| SwinIR 在 NingXia 均值最强，PSNR 23.9513 / SSIM 0.7525 | 通用 Transformer 的局部恢复和结构保持仍有价值 | 可吸收 small window attention 或局部 token mixing，但需任务特化。 |
| SAINT 在 fastMRI 对 SwinIR 五指标 24/24 wins | spatially-aware adjacent-slice conditioning 很关键 | 设计 phase-conditioned left/right spatial gate。 |
| HAT/SMamba fastMRI 都五指标 24/24 胜 SwinIR，但仍低于 SAINT/I3Net | 新 backbone 有用，但不是充分条件 | attention/Mamba 只作为轻量 mixer，不把“新架构名”当核心创新。 |
| visual QC fastMRI large gap：SAINT 比 SwinIR PSNR +1.4926、SSIM +0.0314、grad-MAE 更低 | 局部边界/脑沟/脑室区域决定实际视觉差异 | 加 gradient-aware loss、structure-weighted residual、visual QC。 |
| NingXia visual QC 中存在 saint_better、near_tie、swinir_better 三类 | 临床外部数据 case-specific 差异强 | 保留 per-fold/per-case 分析，避免只看均值。 |
| IXI train samples 153195，fastMRI 4080，差 37.55 倍 | 模型训练成本会决定实验能不能完成 | 第一版必须轻量；报告效率；不要一开始堆大模型。 |
| SAINT 参数 1.1973M 但 peak 117MB，SwinIR 参数 0.2239M 但 peak 251MB | 参数少不等于显存低或速度快 | 设计时同时优化实现和内存，不能只报参数量。 |

## 16. 第一版模型的量化目标

为了避免“搓模型”时没有停靠点，建议给第一版自研模型设几个可量化目标。

### 16.1 IXI-T2 阶段目标

最低目标：

- smoke/mini 能稳定超过 Linear 和 Cubic。
- full_test115 至少明显超过 SwinIR/SAINT 以外的中等 baseline。
- per-offset 指标不能出现某一个 offset 明显崩掉。

理想目标：

- 接近 I3Net n=115 的趋势，至少证明 residual + phase-aware fusion 对 Linear 是全 cases 稳定收益。
- 如果短期追不上 I3Net，也要用 ablation 证明设计点有效，例如 phase gate、residual、gradient loss 各自有增益。

### 16.2 fastMRI 阶段目标

最低目标：

- 超过 SwinIR-style 2.5D 的 22.3615 PSNR。
- 至少接近 HAT/SMamba 当前 fastMRI full 水平：HAT PSNR 22.7858，SMamba PSNR 22.7322。

较强目标：

- 接近 SAINT 的 23.2605 PSNR。
- 如果能超过 SAINT，就具备非常强的主表增量。

高目标：

- 接近 I3Net 的 24.0102 PSNR。
- fastMRI 是最能体现 learning-based 方法收益的数据集，因此这里的提升最有论文说服力。

### 16.3 NingXia 阶段目标

最低目标：

- 明确超过 Linear：PSNR > 22.7335，SSIM > 0.6749，MAE < 103.2052。
- 不只看均值，至少多数 test series 上赢 Linear。

较强目标：

- 超过 I3Net：PSNR > 23.4911，SSIM > 0.7208，MAE < 93.5655。
- 这说明不仅 task-matched，而且比 I3Net 更适合临床外部小样本。

高目标：

- 接近或超过 SwinIR/SAINT 第一梯队：SwinIR PSNR 23.9513，SAINT PSNR 23.8350。
- 如果 NingXia 能同时接近 SwinIR，fastMRI 接近 SAINT/I3Net，就可以支撑“跨数据集稳定”的核心 claim。

### 16.4 效率目标

第一版模型建议控制在：

```text
Params: <= 1-2M
Forward peak CUDA memory: 尽量不高于 SwinIR 当前 251 MB
Forward time: 尽量接近 SAINT/SwinIR 的 3-5 ms 量级
Training: batch_size=8, grad_accum_steps=3 不使用 shared GPU memory
```

这不是硬性论文标准，但能约束模型别变成不可训练的超大模型。

## 17. 研发阶段建议新增的结果文件

为了让后续自研模型的证据链更完整，建议新 package 从一开始就输出这些文件：

| 文件 | 内容 | 目的 |
|---|---|---|
| `metrics/summary_metrics.csv` | 主五指标均值 | 进入主表候选。 |
| `metrics/per_case_metrics.csv` | 每个 case 的主指标 | 做 paired wins。 |
| `metrics/per_offset_metrics.csv` | offset=1/4,2/4,3/4 分组指标 | 支撑 phase-aware claim。 |
| `metrics/residual_stats.csv` | residual mean/std/max/percentile | 证明没有过度修改 Linear。 |
| `metrics/gradient_metrics.csv` | gradient MAE / edge-region MAE | 支撑 structure-preserving claim。 |
| `metrics/complexity.json` | Params / FLOPs | 支撑效率 claim。 |
| `metrics/runtime.json` | forward time / peak CUDA memory | 支撑可复现和效率。 |
| `metrics/ablation_table.md` | 消融结果汇总 | 写论文方便。 |
| `visual_qc/selected_cases.csv` | 自动选 small/median/large gap cases | 保持视觉分析统一。 |

如果这些从第一天就打通，后面不会出现“模型跑完了，但证据链缺一块”的麻烦。
