# T2 Through-Plane Interpolation Multi-Scale Table Draft

| Scale | Method | IXI-T2 PSNR | IXI-T2 SSIM | IXI-T2 MAE | IXI-T2 MSE | IXI-T2 NCC | fastMRI-brain-T2 PSNR | fastMRI-brain-T2 SSIM | fastMRI-brain-T2 MAE | fastMRI-brain-T2 MSE | fastMRI-brain-T2 NCC | NingXia-T2 CV PSNR | NingXia-T2 CV SSIM | NingXia-T2 CV MAE | NingXia-T2 CV MSE | NingXia-T2 CV NCC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| x2 | Linear | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| x2 | Cubic | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| x2 | I3Net (2024) | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| x4 | Linear | 26.1722 | 0.8529 | 29.2781 | 6553.8673 | 0.9390 | 19.1133 | 0.5970 | 78.8111 | 23092.0046 | 0.7733 | 22.7335 | 0.6749 | 103.2052 | 42189.1127 | 0.8576 |
| x4 | Cubic | 25.7138 | 0.8422 | 31.1269 | 7217.2979 | 0.9303 | 17.9736 | 0.5332 | 91.9330 | 29740.2642 | 0.7285 | 21.6460 | 0.6184 | 119.4078 | 53313.5368 | 0.8252 |
| x4 | I3Net (2024) | 31.3058 | 0.9285 | 17.5276 | 2565.3177 | 0.9788 | 24.0102 | 0.7921 | 41.0101 | 7755.6546 | 0.9308 | 23.4911 | 0.7208 | 93.5655 | 35725.4805 | 0.8825 |
| x6 | Linear | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| x6 | Cubic | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| x6 | I3Net (2024) | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |

Note: this draft currently targets the I3Net-style multi-scale block: Linear, Cubic, and I3Net over x2/x4/x6. Cells marked pending mean the corresponding run has not generated paper_table.csv or NingXia fold summaries yet.
