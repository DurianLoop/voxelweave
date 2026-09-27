# T2 x4 统一实验主表

后续主表只维护本文件。上部为论文主线候选表：**T2 模态、x4 through-plane interpolation**；文件末尾另追加 fastMRI-brain-T2 expanded 与 NingXia-T2 的 x2/x6 多尺度汇总。

表格格式参考 I3Net 论文大表：方法放在左侧，数据集横向展开，每个数据集下展示同一组指标。当前主表只放训练阶段核心指标：

```text
PSNR / SSIM / MAE / MSE / NCC
```

RMSE / NMSE / NRMSE / SNLI / LPIPS / Params / FLOPs / inference time / GPU memory 等作为扩展指标，后续进入论文候选后再单独整理。

<table>
  <thead>
    <tr>
      <th rowspan="2">Scale</th>
      <th rowspan="2">Method</th>
      <th colspan="5">IXI-T2<br>test n=115</th>
      <th colspan="5">fastMRI-brain-T2 expanded<br>test n=24</th>
      <th colspan="5">NingXia-T2 case-level CV<br>8 folds</th>
    </tr>
    <tr>
      <th>PSNR</th><th>SSIM</th><th>MAE</th><th>MSE</th><th>NCC</th>
      <th>PSNR</th><th>SSIM</th><th>MAE</th><th>MSE</th><th>NCC</th>
      <th>PSNR</th><th>SSIM</th><th>MAE</th><th>MSE</th><th>NCC</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="13">x4</td>
      <td>Linear (Classical)</td>
      <td>26.1722</td><td>0.8529</td><td>29.2781</td><td>6553.8673</td><td>0.9390</td>
      <td>19.1133</td><td>0.5970</td><td>78.8111</td><td>23092.0046</td><td>0.7733</td>
      <td>22.7335</td><td>0.6749</td><td>103.2052</td><td>42189.1127</td><td>0.8576</td>
    </tr>
    <tr>
      <td>Cubic (Classical)</td>
      <td>25.7138</td><td>0.8422</td><td>31.1269</td><td>7217.2979</td><td>0.9303</td>
      <td>17.9736</td><td>0.5332</td><td>91.9330</td><td>29740.2642</td><td>0.7285</td>
      <td>21.6460</td><td>0.6184</td><td>119.4078</td><td>53313.5368</td><td>0.8252</td>
    </tr>
    <tr>
      <td>ACVTT (2025)</td>
      <td>27.3431</td><td>0.8822</td><td>25.5217</td><td>5206.8325</td><td>0.9557</td>
      <td>20.1941</td><td>0.6624</td><td>71.5480</td><td>18286.6190</td><td>0.8320</td>
      <td>23.4735</td><td>0.7281</td><td>95.4376</td><td>35779.4840</td><td>0.8804</td>
    </tr>
    <tr>
      <td>Res-SRDiff (2025)</td>
      <td>28.0441</td><td>0.8821</td><td>24.1938</td><td>4664.4129</td><td>0.9611</td>
      <td>21.6727</td><td>0.6909</td><td>56.3371</td><td>13095.4191</td><td>0.8814</td>
      <td>21.1538</td><td>0.5538</td><td>153.0213</td><td>66533.1526</td><td>0.8207</td>
    </tr>
    <tr>
      <td>ArSSR (2021)</td>
      <td>27.2467</td><td>0.8773</td><td>25.5509</td><td>5267.3658</td><td>0.9533</td>
      <td>20.3143</td><td>0.6575</td><td>65.9931</td><td>17745.8948</td><td>0.8301</td>
      <td>23.1634</td><td>0.7091</td><td>96.4890</td><td>38343.9409</td><td>0.8708</td>
    </tr>
    <tr>
      <td>CycleINR (2024)</td>
      <td>26.1728</td><td>0.8527</td><td>29.2765</td><td>6553.8469</td><td>0.9390</td>
      <td>20.3156</td><td>0.6577</td><td>66.0985</td><td>17743.2358</td><td>0.8302</td>
      <td>22.9009</td><td>0.6935</td><td>101.0990</td><td>40735.3568</td><td>0.8625</td>
    </tr>
    <tr>
      <td>ResUNet residual (Internal)</td>
      <td>27.4611</td><td>0.8812</td><td>25.2395</td><td>4985.4989</td><td>0.9552</td>
      <td>22.2549</td><td>0.7374</td><td>53.5705</td><td>11842.8147</td><td>0.8955</td>
      <td>23.3816</td><td>0.7209</td><td>97.0409</td><td>36316.2290</td><td>0.8785</td>
    </tr>
    <tr>
      <td>Pix2Pix-GAN 2.5D (2017)</td>
      <td>27.1070</td><td>0.8506</td><td>27.0202</td><td>5372.2668</td><td>0.9538</td>
      <td>21.9090</td><td>0.7294</td><td>53.2622</td><td>12485.1668</td><td>0.8915</td>
      <td>22.4530</td><td>0.7112</td><td>105.8119</td><td>46398.6707</td><td>0.8552</td>
    </tr>
    <tr>
      <td>SwinIR 2.5D (2021)</td>
      <td>28.6485</td><td>0.8997</td><td>22.4556</td><td>4137.5109</td><td>0.9658</td>
      <td>22.3578</td><td>0.7494</td><td>50.8733</td><td>11636.3791</td><td>0.8977</td>
      <td><strong>23.9513</strong></td><td><strong>0.7525</strong></td><td><strong>85.9679</strong></td><td><strong>32030.5455</strong></td><td>0.8930</td>
    </tr>
    <tr>
      <td>SAINT (2020)</td>
      <td>28.6677</td><td>0.8970</td><td>22.8365</td><td>4128.0151</td><td>0.9660</td>
      <td>23.2605</td><td>0.7705</td><td>46.4417</td><td>9347.6662</td><td>0.9177</td>
      <td>23.8350</td><td>0.7422</td><td>89.4140</td><td>32992.9496</td><td>0.8905</td>
    </tr>
    <tr>
      <td>I3Net (2024)</td>
      <td><strong>31.3058</strong></td><td><strong>0.9285</strong></td><td><strong>17.5276</strong></td><td><strong>2565.3177</strong></td><td><strong>0.9788</strong></td>
      <td><strong>24.0102</strong></td><td><strong>0.7921</strong></td><td><strong>41.0101</strong></td><td><strong>7755.6546</strong></td><td><strong>0.9308</strong></td>
      <td>23.4911</td><td>0.7208</td><td>93.5655</td><td>35725.4805</td><td>0.8825</td>
    </tr>
    <tr>
      <td>HAT 2.5D (2023)</td>
      <td>28.7249</td><td>0.9016</td><td>22.2500</td><td>4088.7422</td><td>0.9663</td>
      <td>23.0894</td><td>0.7688</td><td>47.2467</td><td>9773.1765</td><td>0.9138</td>
      <td>23.9499</td><td>0.7519</td><td>86.1449</td><td>32226.9860</td><td><strong>0.8933</strong></td>
    </tr>
    <tr>
      <td>SMamba-UNet 2.5D (2024+)</td>
      <td>29.3536</td><td>0.9077</td><td>21.1352</td><td>3691.2381</td><td>0.9699</td>
      <td>22.7322</td><td>0.7618</td><td>49.4487</td><td>10826.4468</td><td>0.9051</td>
      <td>23.9126</td><td>0.7500</td><td>86.8152</td><td>32498.3175</td><td>0.8917</td>
    </tr>
  </tbody>
</table>

Note: IXI-T2 已统一补齐为 test n=115；其中 `ArSSR` / `CycleINR` / `ResUNet residual` / `SwinIR 2.5D` / `SAINT` 是复用既有 full best checkpoint 的 eval-only n=115 评估，`I3Net` 使用 `full_test115_stable` 稳定重训结果，`ACVTT` 使用 IXI `full_test115_b64` 与 fastMRI/NingXia `full_tiny` 官方代码适配结果，`Res-SRDiff` 使用 IXI `full_test115` 与 fastMRI/NingXia `full_tiny` 官方扩散核心适配结果。IXI-GAN 训练 best epoch=0 后早停，仅作为 inherited GAN 弱基线记录。

## PAST-Net fastMRI x4 开发轨迹（尚未进入三数据集主表）

以下版本目前只完成 fastMRI test n=24，不能替代上方三数据集统一结果。待候选结构固定后再原样迁移 IXI/NingXia。

| Method | PSNR | SSIM | MAE | MSE | NCC | 状态 |
|---|---:|---:|---:|---:|---:|---|
| PAST-Net G079 tail-aware | 24.4032 | .8060 | 38.4845 | 7239.4437 | .9365 | 前一阶段参考 |
| PAST-Net G081 PhaseFlow | 24.4187 | .8066 | 38.4218 | 7216.4669 | .9367 | 小幅正结果 |
| PAST-Net G082 Fourier-INR | 24.4121 | .8062 | 38.4562 | 7223.0122 | .9366 | 停止 |
| PAST-Net G083 Unrolled | 24.4091 | .8062 | 38.4639 | 7231.3298 | .9365 | 停止 |
| **PAST-Net G084 Dual-domain** | **24.4423** | **.8073** | **38.3100** | **7173.3934** | **.9371** | 当前fastMRI开发最优 |
| PAST-Net G085 Volumetric U-Net | 24.4085 | .8061 | 38.4578 | 7230.7852 | .9365 | 停止 |
| **PAST-Net G086 Dual-domain restart** | **24.4470** | **.8075** | **38.2894** | **7165.7872** | **.9371** | 当前fastMRI开发最优；停止续训 |
| PAST-Net G087 Sparse-window | 24.0859 | .7903 | 40.8068 | 7737.2032 | .9318 | 停止独立窗口路线 |
| PAST-Net G088 Sparse-window + Flow | 24.0638 | .7895 | 40.9240 | 7742.8106 | .9316 | 停止 |
| PAST-Net G089 Sparse-window + FFT | 24.1089 | .7910 | 40.7628 | 7686.0198 | .9323 | 组内最佳但未晋级 |
| PAST-Net G090 Sparse-window hybrid | 24.0497 | .7890 | 41.0388 | 7764.1283 | .9316 | 停止 |

## 数据集定位

| Dataset | 当前定位 | 说明 |
|---|---|---|
| IXI-T2 | 主开发 / 内部 benchmark | 当前主表已统一为 test n=115。数据相对干净，Linear/Cubic 已经较强，适合快速筛模型，但不能单独证明泛化。 |
| fastMRI-brain-T2 expanded | 公开复杂 brain T2 验证集 | 160 NIfTI；train/val/test = 112/24/24；传统插值明显下降，更能体现学习模型收益。 |
| NingXia-T2 case-level CV | 本地外部临床验证 | 8 cases / 22 T2 series；当前采用 8-fold 病例级交叉验证，优先报告 fold mean。 |

## 方法定位

| Method | 当前定位 |
|---|---|
| Linear / Cubic (Classical) | 非学习基线，所有主表必须保留。 |
| ACVTT (2025) | 近期公开代码 slice-interpolation baseline；当前已完成 IXI-T2、fastMRI-brain-T2 expanded 与 NingXia-T2 8-fold CV。 |
| Res-SRDiff (2025) | 近期公开代码 diffusion MRI SR / refinement baseline；当前已完成 IXI-T2、fastMRI-brain-T2 expanded 与 NingXia-T2 8-fold CV，作为扩散模型适配到 coarse-to-target slice refinement 的对照。 |
| ArSSR (2021) | published INR baseline 的本地复现，已完成三个主表数据集。 |
| CycleINR (2024) | published INR baseline 的本地复现，已完成三个主表数据集，但当前不是强 baseline。 |
| ResUNet residual (Internal) | 内部 CNN residual baseline，不写成严格复现某篇论文。 |
| Pix2Pix-GAN 2.5D (2017) | 师兄早期 pix2pix/GAN 路线迁移到当前 T2/x4 protocol；IXI-T2 full_test115_b64、fastMRI-brain-T2 expanded 与 NingXia-T2 8-fold CV 已完成。IXI-GAN best epoch=0 后早停，主要作为 inherited GAN 弱基线。 |
| SwinIR 2.5D (2021) | 通用 Transformer SR baseline 的 2.5D 适配，当前为第一梯队对照之一。 |
| SAINT (2020) | spatially aware adjacent-slice conditioning baseline，当前与 SwinIR 一起作为强对照。 |
| I3Net (2024) | medical slice synthesis published baseline；三数据集已完成，IXI-T2 和 fastMRI-brain-T2 expanded 当前最强，NingXia 中上但低于 SwinIR / HAT / SAINT。 |
| HAT 2.5D (2023) | HAT 通用 SR Transformer 强基线的 2.5D 本地适配；IXI-T2 full_test115、fastMRI-brain-T2 expanded 与 NingXia-T2 8-fold CV 已完成。 |
| SMamba-UNet 2.5D (2024+) | Mamba 系医学 / 图像复原新架构对照；IXI-T2 full_test115、fastMRI-brain-T2 expanded 与 NingXia-T2 8-fold CV 已完成。 |

## 当前结论

1. `I3Net` 是当前最重要的 published medical slice synthesis baseline；在 IXI-T2 test n=115 和 fastMRI-brain-T2 expanded test n=24 上均为当前最强。
2. `ACVTT` 在 IXI-T2 test n=115 上略强于 ArSSR / CycleINR / Linear / Cubic，但明显弱于 SwinIR / HAT / SMamba / I3Net；因此适合作为近期公开代码 slice-interpolation 对照，而不是第一梯队方法。
3. `Res-SRDiff` 在 IXI-T2 test n=115 和 fastMRI-brain-T2 expanded 上高于 Linear / Cubic / ACVTT / ArSSR / CycleINR 等弱基线，但仍低于 SwinIR / SAINT / HAT / SMamba / I3Net；在 NingXia-T2 8-fold CV 上弱于 Linear / Cubic / ACVTT，说明直接扩散 refinement 适配到小样本外部临床 CV 时不稳定。
4. `SwinIR 2.5D` 在 NingXia-T2 8-fold CV 上的 PSNR / SSIM / MAE / MSE 略优，`HAT 2.5D` 的 NCC 最高，二者非常接近。
5. `HAT 2.5D` 的 fastMRI 结果已使用 `full_extend60` 更新，较原 full 结果明显提升，但仍低于 I3Net 和 SAINT。
6. `SMamba-UNet 2.5D` 已完成三数据集；IXI 上强于 SwinIR / HAT / SAINT，NingXia 上接近 SwinIR / HAT / SAINT，但没有超过当前第一梯队。
7. `Pix2Pix-GAN 2.5D` 已完成 IXI-T2 full_test115_b64、fastMRI-brain-T2 expanded 和 NingXia-T2 8-fold CV，当前整体弱于 HAT / SwinIR / SAINT / I3Net；IXI-GAN best epoch=0 后早停，因此不作为强对照，只作为 inherited GAN 弱基线。
8. `ArSSR` 与 `CycleINR` 已补齐三数据集横向结果，适合作为 INR 类 published baseline 对照，但目前不作为优先调参方向。
9. `ResUNet residual` 只作为 internal baseline，不能写成严格论文复现。

## fastMRI-brain-T2 expanded 多尺度补充（test n=24）

以下为与 x4 主表相同的病例划分和指标实现下的 x2/x6 结果。`pending` 表示 checkpoint 已训练但尚未完成评估，或该尺度的训练配置无有效验证窗口；这些单元格不参与当前结论。

| Scale | Method | PSNR | SSIM | MAE | MSE | NCC |
|---|---|---:|---:|---:|---:|---:|
| x2 | Linear (Classical) | 21.6348 | 0.7030 | 53.9754 | 11591.9388 | 0.8732 |
| x2 | Cubic (Classical) | 20.3321 | 0.6363 | 64.1081 | 15236.6373 | 0.8370 |
| x2 | ResUNet residual (Internal) | 24.1700 | 0.7913 | 39.7905 | 6909.6572 | 0.9338 |
| x2 | ACVTT (2025) | 21.7910 | 0.7110 | 53.4000 | 11160.0709 | 0.8783 |
| x2 | Res-SRDiff (2025) | 22.4766 | 0.6511 | 50.3378 | 9901.7857 | 0.9034 |
| x2 | ArSSR (2021) | 23.1137 | 0.7613 | 43.5812 | 8391.3334 | 0.9140 |
| x2 | CycleINR (2024) | 23.0957 | 0.7593 | 43.7063 | 8411.5115 | 0.9132 |
| x2 | Pix2Pix-GAN 2.5D (2017) | 26.0734 | 0.8302 | 31.2304 | 4584.5238 | 0.9565 |
| x2 | SwinIR 2.5D (2021) | 24.8716 | 0.8153 | 35.9392 | 5990.3711 | 0.9428 |
| x2 | SAINT (2020) | 24.4308 | 0.7809 | 39.6861 | 6749.7212 | 0.9373 |
| x2 | I3Net (2024) | 27.7711 | 0.8670 | 25.3325 | 3113.5377 | 0.9700 |
| x2 | HAT 2.5D (2023) | 24.6475 | 0.8106 | 37.2729 | 6225.7429 | 0.9409 |
| x2 | SMamba-UNet 2.5D (2024+) | 24.6548 | 0.8077 | 37.1110 | 6361.0863 | 0.9401 |
| x6 | Linear (Classical) | 18.2648 | 0.5595 | 88.2647 | 28258.4309 | 0.7215 |
| x6 | Cubic (Classical) | 18.2648 | 0.5595 | 88.2647 | 28258.4309 | 0.7215 |
| x6 | ResUNet residual (Internal) | 22.1434 | 0.7375 | 53.8609 | 12277.0333 | 0.8921 |
| x6 | ACVTT (2025) | 19.8309 | 0.6601 | 72.4367 | 20031.3896 | 0.8120 |
| x6 | Res-SRDiff (2025) | 21.2529 | 0.6791 | 59.4388 | 14747.2531 | 0.8702 |
| x6 | ArSSR (2021) | 19.4214 | 0.6156 | 74.9270 | 21914.5364 | 0.7872 |
| x6 | CycleINR (2024) | 19.3873 | 0.6158 | 74.9017 | 22086.6021 | 0.7854 |
| x6 | Pix2Pix-GAN 2.5D (2017) | 21.6510 | 0.7250 | 54.8359 | 13567.5373 | 0.8828 |
| x6 | SwinIR 2.5D (2021) | 21.8398 | 0.7305 | 56.4490 | 13267.8010 | 0.8840 |
| x6 | SAINT (2020) | 22.3172 | 0.7466 | 52.5303 | 11683.3596 | 0.8979 |
| x6 | I3Net (2024) | 22.8308 | 0.7617 | 47.0732 | 10309.8900 | 0.9088 |
| x6 | HAT 2.5D (2023) | 21.8230 | 0.7313 | 55.7775 | 13341.4608 | 0.8829 |
| x6 | SMamba-UNet 2.5D (2024+) | 21.9153 | 0.7313 | 56.5002 | 13166.6662 | 0.8848 |

fastMRI-brain-T2 expanded 的 x2/x6 表格行现已全部完成（26/26，均为 test n=24）。I3Net x6 使用适配 fastMRI 深度 16 数据的 3 张锚点 / 13 张 HR 切片配置；其余方法保持各自已记录的多尺度训练与评价协议。

## NingXia-T2 多尺度补充（8-fold case-level CV）

下表使用病例级 8-fold CV；每个数字是 8 个 fold 的 fold-level mean 再取平均。仅在对应尺度的 8/8 fold 均已生成 `summary_metrics.csv` 时报告数值。`pending (k/8)` 表示已完成 `k` 个 fold，不能作为完整 CV 结果参与横向结论。

| Scale | Method | PSNR | SSIM | MAE | MSE | NCC |
|---|---|---:|---:|---:|---:|---:|
| x2 | Linear (Classical) | 24.9741 | 0.7264 | 78.5349 | 27551.4768 | 0.9112 |
| x2 | Cubic (Classical) | 24.1081 | 0.6767 | 89.5215 | 33708.1987 | 0.8952 |
| x2 | ResUNet residual (Internal) | 25.2629 | 0.7478 | 76.6937 | 25684.3115 | 0.9170 |
| x2 | ACVTT (2025) | 25.3139 | 0.7518 | 76.2396 | 25631.8031 | 0.9180 |
| x2 | Res-SRDiff (2025) | 15.3187 | 0.2945 | 440.6059 | 311894.3839 | 0.8320 |
| x2 | ArSSR (2021) | 25.1538 | 0.7427 | 76.6719 | 26571.4634 | 0.9146 |
| x2 | CycleINR (2024) | 25.1538 | 0.7427 | 76.6723 | 26571.4525 | 0.9146 |
| x2 | Pix2Pix-GAN 2.5D (2017) | 25.2116 | 0.7543 | 74.8168 | 25448.9329 | 0.9169 |
| x2 | SwinIR 2.5D (2021) | 25.5845 | 0.7651 | 73.1350 | 24249.0709 | 0.9226 |
| x2 | SAINT (2020) | 25.3398 | 0.7535 | 75.9435 | 25247.7430 | 0.9191 |
| x2 | I3Net (2024) | 25.7679 | 0.7574 | 70.8835 | 23483.9767 | 0.9265 |
| x2 | HAT 2.5D (2023) | 25.8489 | 0.7738 | 70.0441 | 22767.1915 | 0.9276 |
| x2 | SMamba-UNet 2.5D (2024+) | 25.4409 | 0.7603 | 74.6767 | 24857.0321 | 0.9201 |
| x6 | Linear (Classical) | 21.7375 | 0.6509 | 118.6269 | 53812.4881 | 0.8146 |
| x6 | Cubic (Classical) | 21.6523 | 0.6483 | 119.6982 | 54616.6079 | 0.8118 |
| x6 | ResUNet residual (Internal) | 22.7683 | 0.7143 | 104.7535 | 42861.1183 | 0.8551 |
| x6 | ACVTT (2025) | 22.6160 | 0.7126 | 108.2221 | 44622.4723 | 0.8490 |
| x6 | Res-SRDiff (2025) | 20.4586 | 0.5616 | 156.7453 | 75246.6372 | 0.7890 |
| x6 | ArSSR (2021) | 22.3530 | 0.7007 | 108.1897 | 47147.2527 | 0.8389 |
| x6 | CycleINR (2024) | 21.8961 | 0.6728 | 116.1079 | 52220.1671 | 0.8214 |
| x6 | Pix2Pix-GAN 2.5D (2017) | 21.1353 | 0.6662 | 129.1480 | 61058.8712 | 0.8005 |
| x6 | SwinIR 2.5D (2021) | 22.9792 | 0.7362 | 98.5621 | 40916.0806 | 0.8624 |
| x6 | SAINT (2020) | 22.7341 | 0.7233 | 106.0398 | 44729.0092 | 0.8562 |
| x6 | I3Net (2024) | 22.3951 | 0.6940 | 111.4996 | 46546.2263 | 0.8452 |
| x6 | HAT 2.5D (2023) | 23.0110 | 0.7361 | 98.5351 | 40588.4310 | 0.8635 |
| x6 | SMamba-UNet 2.5D (2024+) | 22.9507 | 0.7336 | 100.4715 | 41414.3824 | 0.8611 |

NingXia 的 x2/x6 运行目录位于仓库根目录的 `ningxia_t2_*_cv/runs`，与历史 x4 的 `baseline/ningxia_t2_*_cv/runs` 分开保存。上述标准预算 x2/x6 已全部完成 8-fold CV（无 pending）。

## NingXia-T2 60-Epoch 收敛敏感性（补充，不替代主排名）

以下是已经完成的 60-epoch 独立重训。它们与标准 30-epoch 表使用相同病例级 CV、指标实现和测试 fold，但训练预算不同，故仅用于说明收敛敏感性，**不替换上方标准预算主表数值**。

| Scale | Method | PSNR | SSIM | MAE | MSE | NCC |
|---|---|---:|---:|---:|---:|---:|
| x4 | ArSSR (2021) | 23.4566 | 0.7241 | 91.8598 | 36115.4376 | 0.8793 |
| x4 | ResUNet residual (Internal) | 23.7562 | 0.7379 | 90.5450 | 33771.8800 | 0.8876 |
| x4 | SAINT (2020) | 23.8388 | 0.7473 | 88.1769 | 33105.9966 | 0.8909 |
| x4 | SMamba-UNet 2.5D (2024+) | 24.0160 | 0.7542 | 84.8084 | 31545.2244 | 0.8947 |
| x4 | SwinIR 2.5D (2021) | 24.0370 | 0.7573 | 83.8378 | 31317.4826 | 0.8946 |
| x2 | CycleINR (2024) | 25.1538 | 0.7427 | 76.6723 | 26571.4690 | 0.9146 |
| x2 | HAT 2.5D (2023) | 26.1387 | 0.7853 | 66.2919 | 21520.2802 | 0.9321 |
| x2 | Res-SRDiff (2025) | 22.6714 | 0.5619 | 140.4503 | 56206.7760 | 0.8894 |
| x2 | SAINT (2020) | 25.6706 | 0.7677 | 72.4046 | 23699.0011 | 0.9245 |
| x2 | SMamba-UNet 2.5D (2024+) | 25.9101 | 0.7813 | 68.4655 | 22757.3826 | 0.9281 |
| x2 | SwinIR 2.5D (2021) | 26.0556 | 0.7821 | 67.3308 | 21930.8546 | 0.9310 |
| x6 | ArSSR (2021) | 22.4720 | 0.7020 | 106.4477 | 46384.2568 | 0.8423 |
| x6 | CycleINR (2024) | 22.1578 | 0.6886 | 111.6263 | 49569.1804 | 0.8335 |
| x6 | Res-SRDiff (2025) | 20.8328 | 0.6008 | 139.9794 | 62636.9837 | 0.7782 |
| x6 | ResUNet residual (Internal) | 22.9161 | 0.7281 | 100.4640 | 41591.4635 | 0.8610 |
| x6 | SwinIR 2.5D (2021) | 23.0201 | 0.7392 | 97.7710 | 40687.7343 | 0.8637 |

### NingXia Res-SRDiff x2 90-Epoch 诊断

| Scale | Method | PSNR | SSIM | MAE | MSE | NCC |
|---|---|---:|---:|---:|---:|---:|
| x2 | Res-SRDiff (2025), 90 epoch | 23.5044 | 0.6178 | 118.2457 | 43546.3681 | 0.8924 |

Res-SRDiff x2 的 90-epoch 收敛诊断已完成 8-fold。它相对 60-epoch 的 PSNR（22.6714）有所提升，但仍显著低于同协议下的强确定性方法；因此该行仅作为扩散适配的训练预算诊断，不替换标准预算主排名。

## fastMRI-brain-T2 60-Epoch 收敛敏感性（补充，不替代主排名）

以下三项是训练日志显示在 30 轮末仍有明确下降趋势后完成的独立 60-epoch 重训。它们保持相同 train/val/test 划分（test n=24）与指标实现，但训练预算不同，因此仅用于说明收敛敏感性。

| Scale | Method | PSNR | SSIM | MAE | MSE | NCC |
|---|---|---:|---:|---:|---:|---:|
| x2 | SwinIR 2.5D (2021), 60 epoch | 25.4180 | 0.8274 | 33.7890 | 5326.9072 | 0.9500 |
| x6 | ACVTT (2025), 60 epoch | 20.0269 | 0.6677 | 70.9050 | 19173.6891 | 0.8211 |
| x2 | Res-SRDiff (2025), 60 epoch | 24.0661 | 0.7540 | 40.8709 | 7086.3766 | 0.9320 |

其中 SwinIR x2 与 Res-SRDiff x2 相比各自标准 30-epoch 结果均有提升；ACVTT x6 的 60-epoch 结果低于其标准预算结果，说明该设置并未从更长训练中获益。三项均不替换上方统一标准预算主表数值。
