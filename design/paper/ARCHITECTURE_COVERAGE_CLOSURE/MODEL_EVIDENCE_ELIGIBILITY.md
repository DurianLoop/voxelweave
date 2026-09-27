# 模型 × 证据适用性审计

A=重建记录；B=同目标物理相位干预；C=本轮严格 acquired-only 双锚有限响应；D=本轮固定上下文协方差接口。ELIGIBLE 不等于正结果。AVAILABLE BUT NOT YET RUN 不得计为实测支持。

| 模型 | A | B | C | D |
|---|---|---|---|---|
| Linear | ELIGIBLE | ELIGIBLE | AVAILABLE BUT NOT YET RUN | AVAILABLE BUT NOT YET RUN |
| Cubic | ELIGIBLE | ELIGIBLE | INELIGIBLE | INELIGIBLE |
| ACVTT | ELIGIBLE | ELIGIBLE | AVAILABLE BUT NOT YET RUN | AVAILABLE BUT NOT YET RUN |
| Res-SRDiff | ELIGIBLE | ELIGIBLE | INELIGIBLE | INELIGIBLE |
| ArSSR | ELIGIBLE | ELIGIBLE | AVAILABLE BUT NOT YET RUN | AVAILABLE BUT NOT YET RUN |
| CycleINR-style | ELIGIBLE | ELIGIBLE | INELIGIBLE | INELIGIBLE |
| ResUNet | ELIGIBLE | ELIGIBLE | AVAILABLE BUT NOT YET RUN | AVAILABLE BUT NOT YET RUN |
| Pix2Pix-GAN | ELIGIBLE | ELIGIBLE | INELIGIBLE | INELIGIBLE |
| SwinIR | ELIGIBLE | ELIGIBLE | ELIGIBLE | ELIGIBLE |
| SAINT-style | ELIGIBLE | ELIGIBLE | ELIGIBLE | ELIGIBLE |
| I3Net | ELIGIBLE | ELIGIBLE | INELIGIBLE | INELIGIBLE |
| HAT | ELIGIBLE | ELIGIBLE | ELIGIBLE | ELIGIBLE |
| SMamba-UNet | ELIGIBLE | ELIGIBLE | AVAILABLE BUT NOT YET RUN | AVAILABLE BUT NOT YET RUN |

## 逐模型技术依据

### Linear
Linear interpolation at arbitrary physical target fractions; no learned weights.
Pairwise linear map is compatible; no new non-core influence inference authorized.
源代码：`pre/topcow_diffusion/baselines.py`。

### Cubic
Native scipy interp1d cubic on complete regular phase pools, >=4 anchors; not the historical four-point Lagrange estimator.
Exact two-anchor probe triggers native cubic-to-linear fallback, changing the estimator; no synthetic anchors permitted.
源代码：`pre/topcow_diffusion/baselines.py`。

### ACVTT
Two neighboring slices, coarse interpolant and continuous relative-position channel; full phase normalization preserved.
Pair-input interface compatible with fixed acquired scale and per-anchor responses; numerical probe not yet run.
源代码：`baseline/ixi_acvtt_2p5d/train.py`。

### Res-SRDiff
Frozen diffusion sampler consumes linear coarse slices; phase experiment additionally fixes RNG state before both passes.
Unconditional sampler adds fresh Gaussian random draws. The exact acquired-only probe has no frozen internal-noise contract; phase-specific RNG conditioning is not imported into that protocol.
源代码：`baseline/ixi_ressrdiff_2p5d/train.py; baseline/ixi_ressrdiff_2p5d/model.py; external/Res-SRDiff/script/diffusion/gaussian_diffusion.py`。

### ArSSR
Frozen volumetric feature encoder + coordinate MLP permits regular phase0/phase2 pools; retains full-volume extent and normalized coordinates.
The native coordinate wrapper accepts variable volume depth and stride, so a pair-context adapter is technically possible. No exact acquired-only adapter or response experiment has yet been validated; do not count it as measured influence.
源代码：`baseline/ixi_arssr/inference.py`。

### CycleINR-style
Internal ArSSR-derived volume encoder/coordinate model; existing primary phase predictions retained.
Frozen historical probe requires four equally spaced x4 anchors; exact acquired two-anchor context grid is incompatible. Historical stability FAIL is a separate target-informed contract.
源代码：`baseline/ixi_arssr/inference.py; design/paper/ARCHIVE/PLANS/PLAN9_ARCH_GENERALIZATION/UNIFIED_INFLUENCE_PROTOCOL.md`。

### ResUNet
Residual U-Net with neighboring anchors, coarse slice and relative position.
Pair-input interface compatible; no non-core influence experiment added.
源代码：`pre/ixi_diffusion/resunet.py`。

### Pix2Pix-GAN
Generator predicts three x4 intermediate planes from two anchors and phase-local interval coordinate; phase shift preserves x4 output channels.
Frozen generator output channels represent only 1/4,1/2,3/4. Required variable-gap contexts include 2/3,2/5 etc.; remapping channels changes target semantics.
源代码：`baseline/gan_2p5d/inference.py`。

### SwinIR
Existing frozen primary phase arrays and acquired-only responses.
Full acquired-only experiment completed under historical .85 per-stratum gate.
源代码：`baseline/ixi_swinir_2p5d/train.py`。

### SAINT-style
Existing physical-coordinate-correct primary phase arrays; six-channel pair/coordinate estimator.
Exact pair grid compatible via unchanged six-channel interface; physical target coordinate fixed across all contexts. New acquired-only .90 replication retained regardless of outcome.
源代码：`pre/ixi_diffusion/saint.py`。

### I3Net
Frozen stride4 sliding-window model and complete primary phase arrays.
Checkpoint requires four low-resolution slices and fixed stride4 output. Two-anchor variable-gap contexts are not a valid input window; no padding or channel reinterpretation.
源代码：`baseline/ixi_i3net/train.py`。

### HAT
Existing frozen primary phase arrays and acquired-only responses.
Full acquired-only experiment completed under historical .85 per-stratum gate.
源代码：`baseline/ixi_hat_2p5d/train.py`。

### SMamba-UNet
Residual pair/coarse/relative-position wrapper; full acquired phase normalization.
Pair-input interface compatible; no non-core influence experiment added.
源代码：`baseline/ixi_smamba_unet_2p5d/train.py`。

## 计数口径与边界
保留全部 13 个重建实现及 111 个配置；仅22个既有脑队列权重进入本轮接口/推理绑定。原核心 HAT 等可能使用先前固定 profile，不以 master 表较优 profile 替换；模型名覆盖不等于每种历史权重都经机制检验。八个新增模型只作相位敏感性，不构造扩大版跨模型主矩阵。
四个非核心接口（Linear、ACVTT、ResUNet、SMamba-UNet）可形成双锚探针，但本轮不新增其连续影响实验。实际已完成 acquired-only 检验的模型计数，必须与这些未运行接口分开。
I3Net/CycleINR 的本轮 NA 是接口不合格，历史 FAIL 是另一合同；不把未运行写成测得稳定性失败。Cubic 的两锚 fallback 不能冒充 cubic influence。Res-SRDiff 同相位输出随机性由代码事实核对，不采信其类注释中的 deterministic 标签。
NingXia 伦理、同意、脱敏、使用许可和精确 fastMRI release/authorization：NEEDS HUMAN CONFIRMATION。数值实验不解除此投稿阻断。