# T2 x4 插值实验的 GPU 运行效率说明

更新日期：2026-06-18

本文档解释三个问题：

1. 为什么 fastMRI 跑得明显比 IXI 快。
2. Windows 任务管理器里 GPU 页面各个组件大致是什么意思。
3. 在不改变实验口径的前提下，如何调整 batch 参数，让训练尽量高效。

## 1. 为什么 fastMRI 比 IXI 快很多

主要原因不是 fastMRI 用了更轻的模型。当前 HAT / SMamba 的 full 配置里，模型宽度、epoch 数、stride 和有效 batch 都是一样的。真正差异在于训练样本数。

当前已核验的样本数如下，配置为 `stride=4`、`batch_size=8`：

| 数据集 / profile | 训练 3D cases | 验证 3D cases | 训练 2D samples | 验证 2D samples | 每轮 micro-step |
|---|---:|---:|---:|---:|---:|
| IXI-T2 full / full_test115 | 404 | 58 | 153195 | 22086 | 19150 |
| fastMRI-brain-T2 full | 112 | 24 | 4080 | 864 | 510 |

也就是说，IXI 的训练样本数大约是 fastMRI 的：

```text
153195 / 4080 = 37.55 倍
```

在相同 `batch_size=8` 下，IXI 每个 epoch 需要做约 19150 次 forward/backward micro-step，而 fastMRI 只需要约 510 次。因此 fastMRI 显得快很多是正常的。

### 为什么 3D volume 数量不是唯一决定因素

fastMRI 有 160 个 3D T2 volumes，看起来不少；但这些 volumes 的 through-plane depth 很短，大部分是 16 层。IXI 的 T2 volume 通常 z-depth 更深，所以切出来的 2D interpolation samples 多很多。

当前 single-slice interpolation dataset 的样本生成逻辑是：

```python
for z in range(0, depth - stride):
    for offset in range(1, stride):
        items.append((path, z, offset, depth))
```

当 `stride=4` 时，每个 anchor 位置会产生 3 个目标层：

```text
z+1, z+2, z+3
```

一个 depth 为 `D` 的 volume，当前 sliding 口径下产生的训练样本数是：

```text
(D - 4) * 3
```

例子：

| Volume depth | 每个 volume 的 2D samples |
|---:|---:|
| 16 | 36 |
| 32 | 84 |
| 130 | 378 |

所以 fastMRI 虽然有 160 个 3D volumes，但因为 depth 普遍短，总训练样本数只有 4080。IXI 的训练 cases 更多，且 z-depth 更深，所以训练样本数达到 153195。

## 2. 任务管理器里各项是什么意思

Windows 任务管理器的 GPU 页面会把很多不同概念放在一起。对 PyTorch 训练来说，重点看下面这些。

| 项目 | 大致含义 | 对当前实验怎么理解 |
|---|---|---|
| CPU | 主机端计算，包括 Python、DataLoader、NIfTI 读取、resize、进程调度等 | 如果 CPU 接近 100%，但 GPU 很低，说明可能是数据读取或预处理卡住了 GPU。 |
| 内存 | 系统内存，也就是 RAM，不是显存 | RAM 用得多不一定有问题；但如果接近满载，Windows 会换页到硬盘，训练会明显变慢。 |
| 磁盘 | SSD 读写 | 训练阶段如果磁盘长期很高，可能是 NIfTI 读取或输出写入成为瓶颈。 |
| Wi-Fi | 网络流量 | 当前本地训练基本无关。 |
| GPU 0 | NVIDIA 独立显卡 | 这是 PyTorch CUDA 训练真正使用的 GPU。 |
| GPU 1 | AMD 集成显卡 | 一般不参与当前 CUDA 训练。 |
| 3D | Windows WDDM 里的 GPU engine 视图；CUDA 计算经常会显示在这里 | 可以当作粗略活跃度参考，但不是精确的 CUDA / tensor core 利用率。更建议用 `nvidia-smi` 看。 |
| Copy | GPU 拷贝引擎，通常表示 CPU/GPU 或 GPU/GPU 间的数据传输 | 如果 Copy 长期很高，可能是数据搬运瓶颈。当前实验通常接近 0。 |
| Video Encode / Decode | 视频编码 / 解码硬件 | MRI 训练无关。 |
| 专用 GPU 内存 | NVIDIA 显卡物理显存，本机可用约 23.5 GB | 这是最重要的显存指标。希望用得高，但不能顶满。 |
| 共享 GPU 内存 | GPU 借用系统 RAM，当作“慢显存”使用 | 这比真实显存慢很多。训练时应尽量接近 0。 |
| GPU 内存 | 专用显存 + 共享显存的总和 | 这个数看起来可以很大，但如果增长来自共享显存，训练效率会变差。 |

你截图里的状态大致是：

```text
专用 GPU 内存：17.3 / 23.5 GB
共享 GPU 内存：0.1 / 62.8 GB
3D 利用率：约 36%
```

这是比较健康的状态：专用显存用上了，但没有顶满；共享显存几乎没有被用到。

需要注意的是，`3D=36%` 不等于 CUDA 只用了 36%。Windows 任务管理器不是 PyTorch 最准确的监控工具。看训练状态更推荐：

```powershell
nvidia-smi -l 2
```

或者更详细一点：

```powershell
nvidia-smi --query-gpu=timestamp,utilization.gpu,memory.used,memory.total,power.draw,temperature.gpu --format=csv -l 5
```

## 3. 什么状态算效率比较高

对当前 HAT / SMamba 2.5D 训练来说，比较理想的状态是：

| 指标 | 好状态 | 坏状态 |
|---|---|---|
| 专用 GPU 内存 | 较高但没顶满；本机 23.5 GB 显存下，大约 18-22.5 GB 比较合理 | 长期顶满，或者在上限附近剧烈波动 |
| 共享 GPU 内存 | 接近 0，最好低于 0.3-0.5 GB | 明显上涨，尤其是超过 1 GB |
| GPU 利用率 | 在 `nvidia-smi` 中比较稳定且较高 | 很低，同时 CPU 或磁盘很忙 |
| 功耗 | 训练时较高且稳定 | 很低、断断续续，说明 GPU 经常在等数据 |
| CPU | 中等使用即可 | CPU 接近 100%，GPU 等待 |
| 磁盘 | 低到中等 | 长时间高读写 |
| step time | warmup 后稳定 | 大幅随机波动 |

最差的情况不是“显存没用满”，而是：

```text
专用显存顶满 + 共享 GPU 内存上涨 + step time 明显变慢
```

这说明 Windows 开始把 GPU 需要的数据溢出到系统内存。这样可能不会立刻 CUDA OOM，但训练会非常慢，而且不稳定。对我们的实验来说，这种状态应该视为 batch 过大。

## 4. 哪些参数能调，哪些不能调

为了保证结果能进入主表，full 实验中这些口径不要改：

| 参数 | 固定口径 |
|---|---|
| Train split | 完整 train set |
| Val split | 完整 val set |
| Test split | 完整目标 test set，例如 IXI 用 `full_test115` |
| Epochs | 30 |
| 模型宽度 | `embed_dim=48`, `depths=(2,2,2)`, `num_heads=(3,3,3)` |
| 任务定义 | T2, x4 through-plane interpolation |

可以安全调整的是效率参数：

| 参数 | 含义 | 是否可调 | 原则 |
|---|---|---|---|
| `batch_size` | 每次 forward/backward 实际喂给 GPU 的 micro-batch | 可以 | 尽量增大到显存利用较高，但共享显存仍接近 0。 |
| `grad_accum_steps` | 累积多少个 micro-batch 后再做一次 optimizer step | 可以 | 配合 `batch_size` 调整，让有效 batch 保持一致。 |
| `num_workers` | DataLoader 子进程数 | 当前不建议调 | Windows 上之前遇到过 multiprocessing 权限/worker 问题，当前保持 `0`。 |

有效 batch 的计算是：

```text
effective_batch_size = batch_size * grad_accum_steps
```

当前 full 设置是：

```text
batch_size = 8
grad_accum_steps = 3
effective_batch_size = 24
```

这样相当于保持原来的优化口径不变，但比 `batch_size=4` 少一半 micro-step。

## 5. batch 参数怎么调

当前机器的 NVIDIA 显卡专用显存约 23.5 GB。HAT / SMamba full 训练建议按下面表格调。

| 设置 | 有效 batch | 预期表现 | 适用情况 |
|---|---:|---|---|
| `batch_size=4`, `grad_accum_steps=6` | 24 | 非常稳，但 micro-step 数约为 batch 8 的 2 倍 | batch 8 不稳定时的保守回退 |
| `batch_size=6`, `grad_accum_steps=4` | 24 | 中间档 | batch 8 使用共享显存或 OOM 时使用 |
| `batch_size=8`, `grad_accum_steps=3` | 24 | 当前推荐默认值 | 2026-06-18 检查后的主推荐 |
| `batch_size=12`, `grad_accum_steps=2` | 24 | 如果能稳定放下，是更快的整齐配置 | 只有在 batch 8 明显低于 18-20 GB 且共享显存接近 0 时才试 |

不要因为 Windows 没有立刻 OOM 就盲目加 batch。只要共享 GPU 内存明显上涨，训练就已经不高效了。

## 6. 当前推荐配置

HAT / SMamba full 训练当前推荐：

```text
batch_size=8
grad_accum_steps=3
effective_batch_size=24
num_workers=0
```

这个设置已经应用到：

| 包 | Profile |
|---|---|
| `ixi_hat_2p5d` | `full`, `full_test115` |
| `ixi_smamba_unet_2p5d` | `full`, `full_test115` |
| `fastmri_brain_hat_2p5d` | `full` |
| `fastmri_brain_smamba_unet_2p5d` | `full` |

如果运行时出现：

```text
专用 GPU 内存 > 22.5 GB
共享 GPU 内存持续 > 0.5-1.0 GB
或者 CUDA out of memory
```

就降到：

```text
batch_size=6
grad_accum_steps=4
```

如果运行时出现：

```text
专用 GPU 内存 < 18-20 GB
共享 GPU 内存接近 0
step time 稳定
```

可以测试：

```text
batch_size=12
grad_accum_steps=2
```

但必须先确认第一个 epoch 稳定，且共享显存没有明显上涨。

## 7. 如何公平比较 IXI 和 fastMRI 的耗时

不要直接用“总耗时”判断哪个数据集更慢，应该把总耗时拆成：

```text
总耗时 ≈ epochs * ceil(train_samples / batch_size) * seconds_per_step
```

在 `batch_size=8` 下：

| 数据集 | 训练 samples | 每轮 step | 30 轮 micro-step |
|---|---:|---:|---:|
| IXI-T2 | 153195 | 19150 | 574500 |
| fastMRI-brain-T2 | 4080 | 510 | 15300 |

所以即使 IXI 和 fastMRI 每一步一样快，IXI 也会因为 step 数多很多而耗时明显更长。

以后汇报训练速度或判断某个实验是否“太慢”时，建议同时记录：

```text
dataset
train_samples
batch_size
grad_accum_steps
effective_batch_size
steps_per_epoch
seconds_per_epoch
```

否则很容易把数据集规模差异误读成代码效率差异。

