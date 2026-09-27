# 主表与权重对应清单

日期：2026-09-20。每项指标按照主表显示精度核对。
NingXia 每行目录下包含 fold_00 至 fold_07 八份权重，详细文件及 SHA256 见 checkpoint_index.csv。
训练与评估目录分别记录；eval-only 不能误用评估目录中的其他权重。

| ID | 表格分区 | 数据集 | 倍率 | 方法 | 训练 profile | 权重数 | 训练目录 | 说明 |
|---|---|---|---|---|---|---:|---|---|
| R001 | main_x4 | IXI | x4 | Linear (Classical) | `-` | 0 | `-` | 非学习插值，无模型权重 |
| R002 | main_x4 | fastMRI | x4 | Linear (Classical) | `-` | 0 | `-` | 非学习插值，无模型权重 |
| R003 | main_x4 | NingXia | x4 | Linear (Classical) | `-` | 0 | `-` | 非学习插值，无模型权重 |
| R004 | main_x4 | IXI | x4 | Cubic (Classical) | `-` | 0 | `-` | 非学习插值，无模型权重 |
| R005 | main_x4 | fastMRI | x4 | Cubic (Classical) | `-` | 0 | `-` | 非学习插值，无模型权重 |
| R006 | main_x4 | NingXia | x4 | Cubic (Classical) | `-` | 0 | `-` | 非学习插值，无模型权重 |
| R007 | main_x4 | IXI | x4 | ACVTT (2025) | `full_test115_b64` | 1 | `baseline/ixi_acvtt_2p5d/runs/full_test115_b64` | 五指标来源匹配 |
| R008 | main_x4 | fastMRI | x4 | ACVTT (2025) | `full_tiny` | 1 | `baseline/fastmri_brain_acvtt_2p5d/runs/full_tiny` | 五指标来源匹配 |
| R009 | main_x4 | NingXia | x4 | ACVTT (2025) | `full_tiny` | 8 | `baseline/ningxia_t2_acvtt_2p5d_cv/runs/fold_07/full_tiny` | 五指标来源匹配 |
| R010 | main_x4 | IXI | x4 | Res-SRDiff (2025) | `full_test115` | 1 | `baseline/ixi_ressrdiff_2p5d/runs/full_test115` | 五指标来源匹配 |
| R011 | main_x4 | fastMRI | x4 | Res-SRDiff (2025) | `full_tiny` | 1 | `baseline/fastmri_brain_ressrdiff_2p5d/runs/full_tiny` | 五指标来源匹配 |
| R012 | main_x4 | NingXia | x4 | Res-SRDiff (2025) | `full_tiny` | 8 | `baseline/ningxia_t2_ressrdiff_2p5d_cv/runs/fold_07/full_tiny` | 五指标来源匹配 |
| R013 | main_x4 | IXI | x4 | ArSSR (2021) | `full` | 1 | `baseline/ixi_arssr/runs/full` | 五指标来源匹配；复用 full best 做 n=115 测试 |
| R014 | main_x4 | fastMRI | x4 | ArSSR (2021) | `full` | 1 | `baseline/fastmri_brain_arssr/runs/full` | 五指标来源匹配 |
| R015 | main_x4 | NingXia | x4 | ArSSR (2021) | `full` | 8 | `baseline/ningxia_t2_arssr_cv/runs/fold_07/full` | 五指标来源匹配 |
| R016 | main_x4 | IXI | x4 | CycleINR (2024) | `full` | 1 | `baseline/ixi_cycleinr/runs/full` | 五指标来源匹配；复用 full best 做 n=115 测试 |
| R017 | main_x4 | fastMRI | x4 | CycleINR (2024) | `full` | 1 | `baseline/fastmri_brain_cycleinr/runs/full` | 五指标来源匹配 |
| R018 | main_x4 | NingXia | x4 | CycleINR (2024) | `full` | 8 | `baseline/ningxia_t2_cycleinr_cv/runs/fold_07/full` | 五指标来源匹配 |
| R019 | main_x4 | IXI | x4 | ResUNet residual (Internal) | `resunet_full_t2` | 1 | `pre/ixi_diffusion/runs/resunet_full_t2` | 五指标来源匹配；复用 full best 做 n=115 测试 |
| R020 | main_x4 | fastMRI | x4 | ResUNet residual (Internal) | `full` | 1 | `baseline/fastmri_brain_t2_resunet/runs/full` | 五指标来源匹配 |
| R021 | main_x4 | NingXia | x4 | ResUNet residual (Internal) | `full` | 8 | `baseline/ningxia_t2_resunet_cv/runs/fold_07/full` | 五指标来源匹配 |
| R022 | main_x4 | IXI | x4 | Pix2Pix-GAN 2.5D (2017) | `full_test115_b64` | 1 | `baseline/ixi_gan_2p5d/runs/full_test115_b64` | 五指标来源匹配 |
| R023 | main_x4 | fastMRI | x4 | Pix2Pix-GAN 2.5D (2017) | `full` | 1 | `baseline/fastmri_brain_gan_2p5d/runs/full` | 五指标来源匹配 |
| R024 | main_x4 | NingXia | x4 | Pix2Pix-GAN 2.5D (2017) | `full` | 8 | `baseline/ningxia_t2_gan_2p5d_cv/runs/fold_07/full` | 五指标来源匹配 |
| R025 | main_x4 | IXI | x4 | SwinIR 2.5D (2021) | `full` | 1 | `baseline/ixi_swinir_2p5d/runs/full` | 五指标来源匹配；复用 full best 做 n=115 测试 |
| R026 | main_x4 | fastMRI | x4 | SwinIR 2.5D (2021) | `full_audit` | 1 | `baseline/fastmri_brain_swinir_2p5d/runs/full_audit` | 五指标来源匹配 |
| R027 | main_x4 | NingXia | x4 | SwinIR 2.5D (2021) | `full` | 8 | `baseline/ningxia_t2_swinir_2p5d_cv/runs/fold_07/full` | 五指标来源匹配 |
| R028 | main_x4 | IXI | x4 | SAINT (2020) | `saint_full_t2` | 1 | `pre/ixi_diffusion/runs/saint_full_t2` | 五指标来源匹配；复用 full best 做 n=115 测试 |
| R029 | main_x4 | fastMRI | x4 | SAINT (2020) | `full` | 1 | `baseline/fastmri_brain_t2_saint_expanded/runs/full` | 五指标来源匹配 |
| R030 | main_x4 | NingXia | x4 | SAINT (2020) | `full` | 8 | `baseline/ningxia_t2_saint_cv/runs/fold_07/full` | 五指标来源匹配 |
| R031 | main_x4 | IXI | x4 | I3Net (2024) | `full_test115_stable` | 1 | `baseline/ixi_i3net/runs/full_test115_stable` | 五指标来源匹配 |
| R032 | main_x4 | fastMRI | x4 | I3Net (2024) | `full` | 1 | `baseline/fastmri_brain_i3net/runs/full` | 五指标来源匹配 |
| R033 | main_x4 | NingXia | x4 | I3Net (2024) | `full` | 8 | `baseline/ningxia_t2_i3net_cv/runs/fold_07/full` | 五指标来源匹配 |
| R034 | main_x4 | IXI | x4 | HAT 2.5D (2023) | `full_test115` | 1 | `baseline/ixi_hat_2p5d/runs/full_test115` | 五指标来源匹配 |
| R035 | main_x4 | fastMRI | x4 | HAT 2.5D (2023) | `full_extend60` | 1 | `baseline/fastmri_brain_hat_2p5d/runs/full_extend60` | 五指标来源匹配 |
| R036 | main_x4 | NingXia | x4 | HAT 2.5D (2023) | `full` | 8 | `baseline/ningxia_t2_hat_2p5d_cv/runs/fold_07/full` | 五指标来源匹配 |
| R037 | main_x4 | IXI | x4 | SMamba-UNet 2.5D (2024+) | `full_test115` | 1 | `baseline/ixi_smamba_unet_2p5d/runs/full_test115` | 五指标来源匹配 |
| R038 | main_x4 | fastMRI | x4 | SMamba-UNet 2.5D (2024+) | `full` | 1 | `baseline/fastmri_brain_smamba_unet_2p5d/runs/full` | 五指标来源匹配 |
| R039 | main_x4 | NingXia | x4 | SMamba-UNet 2.5D (2024+) | `full` | 8 | `baseline/ningxia_t2_smamba_unet_2p5d_cv/runs/fold_07/full` | 五指标来源匹配 |
| R040 | pastnet_development | fastMRI | x4 | PAST-Net G079 tail-aware | `full_pastnet_g079_tail_aware160` | 1 | `design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g079_tail_aware160` | 五指标来源匹配 |
| R041 | pastnet_development | fastMRI | x4 | PAST-Net G081 PhaseFlow | `full_pastnet_g081_phase_flow140` | 1 | `design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g081_phase_flow140` | 五指标来源匹配 |
| R042 | pastnet_development | fastMRI | x4 | PAST-Net G082 Fourier-INR | `full_pastnet_g082_coord_inr160` | 1 | `design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g082_coord_inr160` | 五指标来源匹配 |
| R043 | pastnet_development | fastMRI | x4 | PAST-Net G083 Unrolled | `full_pastnet_g083_unrolled160` | 1 | `design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g083_unrolled160` | 五指标来源匹配 |
| R044 | pastnet_development | fastMRI | x4 | PAST-Net G084 Dual-domain | `full_pastnet_g084_dual_domain140` | 1 | `design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g084_dual_domain140` | 五指标来源匹配 |
| R045 | pastnet_development | fastMRI | x4 | PAST-Net G085 Volumetric U-Net | `full_pastnet_g085_volumetric180` | 1 | `design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g085_volumetric180` | 五指标来源匹配 |
| R046 | pastnet_development | fastMRI | x4 | PAST-Net G086 Dual-domain restart | `full_pastnet_g086_dual_restart60` | 1 | `design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g086_dual_restart60` | 五指标来源匹配 |
| R047 | pastnet_development | fastMRI | x4 | PAST-Net G087 Sparse-window | `full_pastnet_g087_sparse_window200` | 1 | `design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g087_sparse_window200` | 五指标来源匹配 |
| R048 | pastnet_development | fastMRI | x4 | PAST-Net G088 Sparse-window + Flow | `full_pastnet_g088_sparse_flow200` | 1 | `design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g088_sparse_flow200` | 五指标来源匹配 |
| R049 | pastnet_development | fastMRI | x4 | PAST-Net G089 Sparse-window + FFT | `full_pastnet_g089_sparse_dual200` | 1 | `design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g089_sparse_dual200` | 五指标来源匹配 |
| R050 | pastnet_development | fastMRI | x4 | PAST-Net G090 Sparse-window hybrid | `full_pastnet_g090_sparse_hybrid220` | 1 | `design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g090_sparse_hybrid220` | 五指标来源匹配 |
| R051 | fastmri_multiscale | fastMRI | x2 | Linear (Classical) | `-` | 0 | `-` | 非学习插值，无模型权重 |
| R052 | fastmri_multiscale | fastMRI | x2 | Cubic (Classical) | `-` | 0 | `-` | 非学习插值，无模型权重 |
| R053 | fastmri_multiscale | fastMRI | x2 | ResUNet residual (Internal) | `full_x2` | 1 | `baseline/fastmri_brain_saint/runs/full_x2` | 五指标来源匹配 |
| R054 | fastmri_multiscale | fastMRI | x2 | ACVTT (2025) | `full_x2` | 1 | `baseline/fastmri_brain_acvtt_2p5d/runs/full_x2` | 五指标来源匹配 |
| R055 | fastmri_multiscale | fastMRI | x2 | Res-SRDiff (2025) | `full_x2` | 1 | `baseline/fastmri_brain_ressrdiff_2p5d/runs/full_x2` | 五指标来源匹配 |
| R056 | fastmri_multiscale | fastMRI | x2 | ArSSR (2021) | `full_x2` | 1 | `baseline/fastmri_brain_arssr/runs/full_x2` | 五指标来源匹配 |
| R057 | fastmri_multiscale | fastMRI | x2 | CycleINR (2024) | `full_x2` | 1 | `baseline/fastmri_brain_cycleinr/runs/full_x2` | 五指标来源匹配 |
| R058 | fastmri_multiscale | fastMRI | x2 | Pix2Pix-GAN 2.5D (2017) | `full_x2` | 1 | `baseline/fastmri_brain_gan_2p5d/runs/full_x2` | 五指标来源匹配 |
| R059 | fastmri_multiscale | fastMRI | x2 | SwinIR 2.5D (2021) | `full_x2` | 1 | `baseline/fastmri_brain_swinir_2p5d/runs/full_x2` | 五指标来源匹配 |
| R060 | fastmri_multiscale | fastMRI | x2 | SAINT (2020) | `full_x2` | 1 | `baseline/fastmri_brain_saint/runs/full_x2` | SAINT 指标来自既有预测恢复审计；共享目录配置可能属于 ResUNet |
| R061 | fastmri_multiscale | fastMRI | x2 | I3Net (2024) | `full_x2` | 1 | `baseline/fastmri_brain_i3net/runs/full_x2` | 五指标来源匹配 |
| R062 | fastmri_multiscale | fastMRI | x2 | HAT 2.5D (2023) | `full_x2` | 1 | `baseline/fastmri_brain_hat_2p5d/runs/full_x2` | 五指标来源匹配 |
| R063 | fastmri_multiscale | fastMRI | x2 | SMamba-UNet 2.5D (2024+) | `full_x2` | 1 | `baseline/fastmri_brain_smamba_unet_2p5d/runs/full_x2` | 五指标来源匹配 |
| R064 | fastmri_multiscale | fastMRI | x6 | Linear (Classical) | `-` | 0 | `-` | 非学习插值，无模型权重 |
| R065 | fastmri_multiscale | fastMRI | x6 | Cubic (Classical) | `-` | 0 | `-` | 非学习插值，无模型权重 |
| R066 | fastmri_multiscale | fastMRI | x6 | ResUNet residual (Internal) | `full_x6` | 1 | `baseline/fastmri_brain_saint/runs/full_x6` | 五指标来源匹配 |
| R067 | fastmri_multiscale | fastMRI | x6 | ACVTT (2025) | `full_x6` | 1 | `baseline/fastmri_brain_acvtt_2p5d/runs/full_x6` | 五指标来源匹配 |
| R068 | fastmri_multiscale | fastMRI | x6 | Res-SRDiff (2025) | `full_x6` | 1 | `baseline/fastmri_brain_ressrdiff_2p5d/runs/full_x6` | 五指标来源匹配 |
| R069 | fastmri_multiscale | fastMRI | x6 | ArSSR (2021) | `full_x6` | 1 | `baseline/fastmri_brain_arssr/runs/full_x6` | 五指标来源匹配 |
| R070 | fastmri_multiscale | fastMRI | x6 | CycleINR (2024) | `full_x6` | 1 | `baseline/fastmri_brain_cycleinr/runs/full_x6` | 五指标来源匹配 |
| R071 | fastmri_multiscale | fastMRI | x6 | Pix2Pix-GAN 2.5D (2017) | `full_x6` | 1 | `baseline/fastmri_brain_gan_2p5d/runs/full_x6` | 五指标来源匹配 |
| R072 | fastmri_multiscale | fastMRI | x6 | SwinIR 2.5D (2021) | `full_x6` | 1 | `baseline/fastmri_brain_swinir_2p5d/runs/full_x6` | 五指标来源匹配 |
| R073 | fastmri_multiscale | fastMRI | x6 | SAINT (2020) | `full_x6` | 1 | `baseline/fastmri_brain_saint/runs/full_x6` | SAINT 指标来自既有预测恢复审计；共享目录配置可能属于 ResUNet |
| R074 | fastmri_multiscale | fastMRI | x6 | I3Net (2024) | `full_x6` | 1 | `baseline/fastmri_brain_i3net/runs/full_x6` | 五指标来源匹配 |
| R075 | fastmri_multiscale | fastMRI | x6 | HAT 2.5D (2023) | `full_x6` | 1 | `baseline/fastmri_brain_hat_2p5d/runs/full_x6` | 五指标来源匹配 |
| R076 | fastmri_multiscale | fastMRI | x6 | SMamba-UNet 2.5D (2024+) | `full_x6` | 1 | `baseline/fastmri_brain_smamba_unet_2p5d/runs/full_x6` | 五指标来源匹配 |
| R077 | ningxia_multiscale | NingXia | x2 | Linear (Classical) | `-` | 0 | `-` | 非学习插值，无模型权重 |
| R078 | ningxia_multiscale | NingXia | x2 | Cubic (Classical) | `-` | 0 | `-` | 非学习插值，无模型权重 |
| R079 | ningxia_multiscale | NingXia | x2 | ResUNet residual (Internal) | `full_x2` | 8 | `baseline/ningxia_t2_resunet_cv_root_results_202607/runs/fold_07/full_x2` | 五指标来源匹配 |
| R080 | ningxia_multiscale | NingXia | x2 | ACVTT (2025) | `full_x2` | 8 | `baseline/ningxia_t2_acvtt_2p5d_cv_root_results_202607/runs/fold_07/full_x2` | 五指标来源匹配 |
| R081 | ningxia_multiscale | NingXia | x2 | Res-SRDiff (2025) | `full_x2` | 8 | `baseline/ningxia_t2_ressrdiff_2p5d_cv_root_results_202607/runs/fold_07/full_x2` | 五指标来源匹配 |
| R082 | ningxia_multiscale | NingXia | x2 | ArSSR (2021) | `full_x2` | 8 | `baseline/ningxia_t2_arssr_cv_root_results_202607/runs/fold_07/full_x2` | 五指标来源匹配 |
| R083 | ningxia_multiscale | NingXia | x2 | CycleINR (2024) | `full_x2` | 8 | `baseline/ningxia_t2_cycleinr_cv_root_results_202607/runs/fold_07/full_x2` | 五指标来源匹配 |
| R084 | ningxia_multiscale | NingXia | x2 | Pix2Pix-GAN 2.5D (2017) | `full_x2` | 8 | `baseline/ningxia_t2_gan_2p5d_cv_root_results_202607/runs/fold_07/full_x2` | 五指标来源匹配 |
| R085 | ningxia_multiscale | NingXia | x2 | SwinIR 2.5D (2021) | `full_x2` | 8 | `baseline/ningxia_t2_swinir_2p5d_cv_root_results_202607/runs/fold_07/full_x2` | 五指标来源匹配 |
| R086 | ningxia_multiscale | NingXia | x2 | SAINT (2020) | `full_x2` | 8 | `baseline/ningxia_t2_saint_cv_root_results_202607/runs/fold_07/full_x2` | 五指标来源匹配 |
| R087 | ningxia_multiscale | NingXia | x2 | I3Net (2024) | `full_x2` | 8 | `baseline/ningxia_t2_i3net_cv_root_results_202607/runs/fold_07/full_x2` | 五指标来源匹配 |
| R088 | ningxia_multiscale | NingXia | x2 | HAT 2.5D (2023) | `full_x2` | 8 | `baseline/ningxia_t2_hat_2p5d_cv_root_results_202607/runs/fold_07/full_x2` | 五指标来源匹配 |
| R089 | ningxia_multiscale | NingXia | x2 | SMamba-UNet 2.5D (2024+) | `full_x2` | 8 | `baseline/ningxia_t2_smamba_unet_2p5d_cv_root_results_202607/runs/fold_07/full_x2` | 五指标来源匹配 |
| R090 | ningxia_multiscale | NingXia | x6 | Linear (Classical) | `-` | 0 | `-` | 非学习插值，无模型权重 |
| R091 | ningxia_multiscale | NingXia | x6 | Cubic (Classical) | `-` | 0 | `-` | 非学习插值，无模型权重 |
| R092 | ningxia_multiscale | NingXia | x6 | ResUNet residual (Internal) | `full_x6` | 8 | `baseline/ningxia_t2_resunet_cv_root_results_202607/runs/fold_07/full_x6` | 五指标来源匹配 |
| R093 | ningxia_multiscale | NingXia | x6 | ACVTT (2025) | `full_x6` | 8 | `baseline/ningxia_t2_acvtt_2p5d_cv_root_results_202607/runs/fold_07/full_x6` | 五指标来源匹配 |
| R094 | ningxia_multiscale | NingXia | x6 | Res-SRDiff (2025) | `full_x6` | 8 | `baseline/ningxia_t2_ressrdiff_2p5d_cv_root_results_202607/runs/fold_07/full_x6` | 五指标来源匹配 |
| R095 | ningxia_multiscale | NingXia | x6 | ArSSR (2021) | `full_x6` | 8 | `baseline/ningxia_t2_arssr_cv_root_results_202607/runs/fold_07/full_x6` | 五指标来源匹配 |
| R096 | ningxia_multiscale | NingXia | x6 | CycleINR (2024) | `full_x6` | 8 | `baseline/ningxia_t2_cycleinr_cv_root_results_202607/runs/fold_07/full_x6` | 五指标来源匹配 |
| R097 | ningxia_multiscale | NingXia | x6 | Pix2Pix-GAN 2.5D (2017) | `full_x6` | 8 | `baseline/ningxia_t2_gan_2p5d_cv_root_results_202607/runs/fold_07/full_x6` | 五指标来源匹配 |
| R098 | ningxia_multiscale | NingXia | x6 | SwinIR 2.5D (2021) | `full_x6` | 8 | `baseline/ningxia_t2_swinir_2p5d_cv_root_results_202607/runs/fold_07/full_x6` | 五指标来源匹配 |
| R099 | ningxia_multiscale | NingXia | x6 | SAINT (2020) | `full_x6` | 8 | `baseline/ningxia_t2_saint_cv_root_results_202607/runs/fold_07/full_x6` | 五指标来源匹配 |
| R100 | ningxia_multiscale | NingXia | x6 | I3Net (2024) | `full_x6` | 8 | `baseline/ningxia_t2_i3net_cv_root_results_202607/runs/fold_07/full_x6` | 五指标来源匹配 |
| R101 | ningxia_multiscale | NingXia | x6 | HAT 2.5D (2023) | `full_x6` | 8 | `baseline/ningxia_t2_hat_2p5d_cv_root_results_202607/runs/fold_07/full_x6` | 五指标来源匹配 |
| R102 | ningxia_multiscale | NingXia | x6 | SMamba-UNet 2.5D (2024+) | `full_x6` | 8 | `baseline/ningxia_t2_smamba_unet_2p5d_cv_root_results_202607/runs/fold_07/full_x6` | 五指标来源匹配 |
| R103 | ningxia_60 | NingXia | x4 | ArSSR (2021) | `full_extend60` | 8 | `baseline/ningxia_t2_arssr_cv_root_results_202607/runs/fold_07/full_extend60` | 五指标来源匹配 |
| R104 | ningxia_60 | NingXia | x4 | ResUNet residual (Internal) | `full_extend60` | 8 | `baseline/ningxia_t2_resunet_cv_root_results_202607/runs/fold_07/full_extend60` | 五指标来源匹配 |
| R105 | ningxia_60 | NingXia | x4 | SAINT (2020) | `full_extend60` | 8 | `baseline/ningxia_t2_saint_cv_root_results_202607/runs/fold_07/full_extend60` | 五指标来源匹配 |
| R106 | ningxia_60 | NingXia | x4 | SMamba-UNet 2.5D (2024+) | `full_extend60` | 8 | `baseline/ningxia_t2_smamba_unet_2p5d_cv_root_results_202607/runs/fold_07/full_extend60` | 五指标来源匹配 |
| R107 | ningxia_60 | NingXia | x4 | SwinIR 2.5D (2021) | `full_extend60` | 8 | `baseline/ningxia_t2_swinir_2p5d_cv_root_results_202607/runs/fold_07/full_extend60` | 五指标来源匹配 |
| R108 | ningxia_60 | NingXia | x2 | CycleINR (2024) | `full_x2_extend60` | 8 | `baseline/ningxia_t2_cycleinr_cv_root_results_202607/runs/fold_07/full_x2_extend60` | 五指标来源匹配 |
| R109 | ningxia_60 | NingXia | x2 | HAT 2.5D (2023) | `full_x2_extend60` | 8 | `baseline/ningxia_t2_hat_2p5d_cv_root_results_202607/runs/fold_07/full_x2_extend60` | 五指标来源匹配 |
| R110 | ningxia_60 | NingXia | x2 | Res-SRDiff (2025) | `full_x2_extend60` | 8 | `baseline/ningxia_t2_ressrdiff_2p5d_cv_root_results_202607/runs/fold_07/full_x2_extend60` | 五指标来源匹配 |
| R111 | ningxia_60 | NingXia | x2 | SAINT (2020) | `full_x2_extend60` | 8 | `baseline/ningxia_t2_saint_cv_root_results_202607/runs/fold_07/full_x2_extend60` | 五指标来源匹配 |
| R112 | ningxia_60 | NingXia | x2 | SMamba-UNet 2.5D (2024+) | `full_x2_extend60` | 8 | `baseline/ningxia_t2_smamba_unet_2p5d_cv_root_results_202607/runs/fold_07/full_x2_extend60` | 五指标来源匹配 |
| R113 | ningxia_60 | NingXia | x2 | SwinIR 2.5D (2021) | `full_x2_extend60` | 8 | `baseline/ningxia_t2_swinir_2p5d_cv_root_results_202607/runs/fold_07/full_x2_extend60` | 五指标来源匹配 |
| R114 | ningxia_60 | NingXia | x6 | ArSSR (2021) | `full_x6_extend60` | 8 | `baseline/ningxia_t2_arssr_cv_root_results_202607/runs/fold_07/full_x6_extend60` | 五指标来源匹配 |
| R115 | ningxia_60 | NingXia | x6 | CycleINR (2024) | `full_x6_extend60` | 8 | `baseline/ningxia_t2_cycleinr_cv_root_results_202607/runs/fold_07/full_x6_extend60` | 五指标来源匹配 |
| R116 | ningxia_60 | NingXia | x6 | Res-SRDiff (2025) | `full_x6_extend60` | 8 | `baseline/ningxia_t2_ressrdiff_2p5d_cv_root_results_202607/runs/fold_07/full_x6_extend60` | 五指标来源匹配 |
| R117 | ningxia_60 | NingXia | x6 | ResUNet residual (Internal) | `full_x6_extend60` | 8 | `baseline/ningxia_t2_resunet_cv_root_results_202607/runs/fold_07/full_x6_extend60` | 五指标来源匹配 |
| R118 | ningxia_60 | NingXia | x6 | SwinIR 2.5D (2021) | `full_x6_extend60` | 8 | `baseline/ningxia_t2_swinir_2p5d_cv_root_results_202607/runs/fold_07/full_x6_extend60` | 五指标来源匹配 |
| R119 | ningxia_90 | NingXia | x2 | Res-SRDiff (2025), 90 epoch | `full_x2_extend90` | 8 | `baseline/ningxia_t2_ressrdiff_2p5d_cv_root_results_202607/runs/fold_07/full_x2_extend90` | 五指标来源匹配 |
| R120 | fastmri_60 | fastMRI | x2 | SwinIR 2.5D (2021), 60 epoch | `full_x2_extend60` | 1 | `baseline/fastmri_brain_swinir_2p5d_root_results_202607/runs/full_x2_extend60` | 五指标来源匹配 |
| R121 | fastmri_60 | fastMRI | x6 | ACVTT (2025), 60 epoch | `full_x6_extend60` | 1 | `baseline/fastmri_brain_acvtt_2p5d_root_results_202607/runs/full_x6_extend60` | 五指标来源匹配 |
| R122 | fastmri_60 | fastMRI | x2 | Res-SRDiff (2025), 60 epoch | `full_x2_extend60` | 1 | `baseline/fastmri_brain_ressrdiff_2p5d_root_results_202607/runs/full_x2_extend60` | 五指标来源匹配 |
