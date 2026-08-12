# Table 2. Main Reliability Results

Main proxy: baseline disagreement. Each metric cell is the per-method mean; CI columns report bootstrap 95% confidence intervals.

| Dataset | Method | Cases | Pixel Corr | Pixel Corr 95% CI | Nonzero Corr | Nonzero Corr 95% CI | Slice Corr | Risk AURC | MAE@50% low-U |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IXI T2 | I3Net | 115 | 0.502 | [0.498, 0.506] | 0.307 | [0.300, 0.313] | 0.357 | 3.925 | 1.423 |
| IXI T2 | HAT | 115 | 0.609 | [0.605, 0.614] | 0.463 | [0.456, 0.469] | 0.458 | 4.468 | 1.525 |
| IXI T2 | SwinIR | 115 | 0.615 | [0.610, 0.620] | 0.471 | [0.464, 0.478] | 0.457 | 4.492 | 1.525 |
| IXI T2 | ACSI | 115 | 0.567 | [0.563, 0.570] | 0.404 | [0.398, 0.410] | 0.418 | 4.295 | 1.455 |
| fastMRI-brain T2 | I3Net | 24 | 0.414 | [0.394, 0.433] | 0.235 | [0.203, 0.269] | 0.346 | 13.623 | 7.104 |
| fastMRI-brain T2 | HAT | 24 | 0.489 | [0.465, 0.515] | 0.318 | [0.279, 0.353] | 0.285 | 15.414 | 7.466 |
| fastMRI-brain T2 | SwinIR | 24 | 0.512 | [0.484, 0.542] | 0.350 | [0.313, 0.390] | 0.294 | 15.616 | 7.313 |
| NingXia T2 CV | I3Net | 22 | 0.486 | [0.459, 0.514] | 0.314 | [0.289, 0.335] | 0.356 | 32.882 | 26.135 |
| NingXia T2 CV | HAT | 22 | 0.458 | [0.432, 0.484] | 0.290 | [0.266, 0.311] | 0.267 | 30.445 | 24.553 |
| NingXia T2 CV | SwinIR | 22 | 0.456 | [0.429, 0.481] | 0.289 | [0.264, 0.309] | 0.276 | 30.295 | 24.473 |
