# Pix2Pix/GAN-style 2.5D 三数据集接入记录

日期：2026-06-29

## 背景

师兄早期的 x4 GAN 代码位于：

```text
D:/MRI/pre/v4
D:/MRI/pre/topcow_gan
```

这条线此前只在 TopCaw / TopCoW 早期血管数据线上完整跑过，没有在当前主线三数据集上运行过。历史 TopCaw full 结果显示 GAN v4 优于 linear / cubic，但那不是当前 T2 x4 through-plane 主表协议。

## 本次改动

新增共享 GAN baseline 包：

```text
gan_2p5d/
```

新增数据集入口：

```text
ixi_gan_2p5d/
fastmri_brain_gan_2p5d/
```

NingXia 通过 `processing.run_ningxia_case_cv` 调用 `fastmri_brain_gan_2p5d.run_all`，每个 fold 使用环境变量切换 data root 和 run root。

## 方法口径

方法名：

```text
Pix2Pix/GAN-style 2.5D
```

主表 method id：

```text
gan_2p5d
```

输入：

```text
left sparse slice + right sparse slice + global z position + relative positions 0.25 / 0.50 / 0.75
```

输出：

```text
一次生成 x4 间隔内的 3 张中间切片
```

和师兄旧代码一致保留：

- motion estimator
- warping coarse prediction
- U-Net generator refinement
- PatchGAN discriminator
- adversarial loss + L1 + coarse + gradient + flow smoothness

和旧 TopCaw 协议不同：

- 不再使用 TopCaw 固定 staging。
- 数据 split 改为当前三数据集主线 split。
- 评估指标只看主表五项：PSNR / SSIM / MAE / MSE / NCC。
- NingXia 使用 8-fold case-level CV。

## 已完成 smoke 验证

### IXI-T2 smoke

命令：

```powershell
Set-Location D:\MRI
$env:PYTHONPATH='D:\MRI'
D:\conda\envs\MRI\python.exe -B -m ixi_gan_2p5d.run_all --profile smoke
D:\conda\envs\MRI\python.exe -B -m ixi_gan_2p5d.paper_table --profile smoke
```

状态：通过。

输出：

```text
D:/MRI/ixi_gan_2p5d/runs/smoke
```

### fastMRI-brain-T2 smoke

命令：

```powershell
Set-Location D:\MRI
$env:PYTHONPATH='D:\MRI'
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_gan_2p5d.run_all --profile smoke
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_gan_2p5d.paper_table --profile smoke
```

状态：通过。

输出：

```text
D:/MRI/fastmri_brain_gan_2p5d/runs/smoke
```

### NingXia-T2 fold_00 smoke

命令：

```powershell
Set-Location D:\MRI
$env:PYTHONPATH='D:\MRI'
D:\conda\envs\MRI\python.exe -B -m processing.run_ningxia_case_cv --profile smoke --models gan --fold-limit 1 --force
D:\conda\envs\MRI\python.exe -B -m processing.summarize_case_cv --profile smoke --include-gan --out-dir docx\experiment_notes\other --title "NingXia-T2 GAN Smoke CV"
```

状态：通过。

输出：

```text
D:/MRI/ningxia_t2_gan_2p5d_cv/runs/fold_00/smoke
D:/MRI/docx/experiment_notes/other/ningxia_case_cv_summary.md
```

## 注意

smoke 只训练 1 epoch，且 case 数很少，不能作为模型质量判断，也不能写入主表。

正式进入大表的条件：

1. IXI 使用 `full_test115`。
2. fastMRI 使用 `full`。
3. NingXia 使用完整 8-fold `full`。
4. 三者均生成 `summary_metrics.csv` 和 `paper_table.csv` / CV summary。
5. 只把 full 口径结果写入 `docx/experiment/experiment_master_table.md`。

## Full 运行指令

IXI-T2：

```powershell
Set-Location D:\MRI
$env:PYTHONPATH='D:\MRI'
D:\conda\envs\MRI\python.exe -B -m ixi_gan_2p5d.run_all --profile full_test115
D:\conda\envs\MRI\python.exe -B -m ixi_gan_2p5d.paper_table --profile full_test115
```

fastMRI-brain-T2：

```powershell
Set-Location D:\MRI
$env:PYTHONPATH='D:\MRI'
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_gan_2p5d.run_all --profile full
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_gan_2p5d.paper_table --profile full
```

NingXia-T2 8-fold CV：

```powershell
Set-Location D:\MRI
$env:PYTHONPATH='D:\MRI'
D:\conda\envs\MRI\python.exe -B -m processing.run_ningxia_case_cv --profile full --models gan
D:\conda\envs\MRI\python.exe -B -m processing.summarize_case_cv --profile full --include-gan
```

## 下一步

GAN full 跑完后，和 deterministic baselines 对比它是否出现以下现象：

- 视觉更锐但 PSNR / MAE 不占优。
- SSIM 或 NCC 对数据集敏感。
- NingXia case-level CV 方差较大。
- 对结构边界有局部改善但整体 fidelity 不稳定。

这些现象可以作为后续任务专用 diffusion-refine / proposed model 的动机。
