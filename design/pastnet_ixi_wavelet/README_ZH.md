# 小波主干版：IXI 训练与锁定评估

用户已选择兼顾质量的小波主干 wavelet3。此次方案是从现有 fastMRI 最佳小波权重出发，在 IXI-T2 上训练，再与现有 IXI I3Net 进行同口径比较；不是直接零样本迁移。完整约定见 [PROTOCOL_ZH.md](PROTOCOL_ZH.md)。旧代码、旧 checkpoint 不修改。

## 第一步：用户运行训练 FULL

在 PowerShell 中执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\MRI\design\pastnet_ixi_wavelet\full.ps1 -Seed 3407
```

固定 404 train / 58 validation / 115 test，T2、x4、256×256；每轮抽取 4,000 个训练区间，最多 80 轮，最少 30 轮后按 validation patience=15 停止。仅由 validation 选择 best。启动后先评估初始化权重的完整 validation 并建立缓存，因此第一条 epoch 日志之前会等待较久。首轮时间还包括首次读取训练数据；缓存后速度才有代表性。缓存预计占约 16 GB（train+val），test 另约 4 GB。

microbatch=2，累积 8 次，有效 batch=16，10 个主干块中 5 个使用 activation checkpoint。GPU 应独占；不要同时运行另一个训练任务。正式配置 smoke 实测峰值 allocated 20.71 GiB、reserved 21.39 GiB。

输出：`runs/full_wavelet3_ixi_seed3407/`。终端记录：`logs/train_*.txt`。`completion.json` 的 completed=true 才表示完整训练完成。

如训练在已生成 `last.pth` 后意外中断，保留同一目录与代码，执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\MRI\design\pastnet_ixi_wavelet\full.ps1 -Seed 3407 -Resume
```

恢复点是上一完整 epoch，当前未提交 epoch 会重跑。首次 epoch 提交前的中断、验证结果写入期间的中断，应先交由助手检查文件一致性，不要删除已有结果或自行修改 manifest。AMP 溢出记录位于 `results/amp_*.jsonl`。

## 第二步：训练完成并审计后，单独运行 TEST

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\MRI\design\pastnet_ixi_wavelet\test.ps1 -Seed 3407
```

入口拒绝未完成训练、smoke 权重、代码/数据哈希变化以及已有输出目录。先写入候选与 I3Net 权重锁，再读取 115 个 test 病例。该命令不重新训练。输出位于 `results/test115_seed3407/`，包含逐层、逐患者指标、配对 bootstrap、困难四分位与推理耗时/显存。

双方使用 observed-only min/max、256×256、仅缺失层评分、逐患者等权聚合。I3Net 保留完整 4→13 滑窗及逐窗口 clamp(0,1)，PAST 也使用相同输出范围约束。Dice/HD95 是强度阈值代理，不是组织分割指标。旧主表 31.3058 dB 来自另一套 native-volume 评分，不能与此处新分数直接相减。

## 解释结果

单 seed 首先回答“这个固定候选在本次协议下是否超过现有 I3Net 权重”。PSNR 配对置信区间下界 >0、质量守卫不退化且患者胜率 ≥60%，才视为有希望的综合结果。现有两模型的预训练、训练归一化和预算不同，此次并非严格匹配训练条件的架构排名；超过 I3Net 也不能单独证明新的 SOTA。

最终确认需要固定方案后补齐 2027、9103 两个 IXI 训练 seed，使用相同训练入口的 `-Seed` 参数。三次均来自同一固定 fastMRI 初始化，衡量 IXI 微调随机性。此时不得根据已见 test 结果修改架构或超参数。当前先运行 3407，后续根据训练审计推进；不自动批量启动。

## 助手已完成的验证

- 预处理缓存与原始 v2 数据路径逐 tensor 完全一致；患者划分不重叠。
- epoch 抽样可复现、不放回且全部使用 z=0,4,… 真实模拟观测网格。
- 把 target 替换为 NaN 不改变模型输出。
- I3Net 严格加载既有权重，两个相邻窗口的裁剪/融合与旧网络独立实现最大误差为 0。
- 使用 full 的 batch/累积/显存配置完成训练 smoke；评估 smoke 只使用 validation。
- `full.ps1 -Preflight` 已通过，未启动 FULL。

首次无裁剪评估是一次失败的协议诊断，保留在 `results/smoke_evaluation/`，不可当作候选胜出证据。正式修正版在 `results/smoke_evaluation_final/`。所有 smoke 分数均不是 IXI 正式结果，也不用于调整候选结构。

## 2026-10-03 已完成结果

IXI full seed3407 已完成 80 轮，锁定 validation best epoch80 后，助手完成了全部 115 名 test 患者、每方法 11,001 张缺失层的评估及独立复算。**小波版没有超过 I3Net：31.7358 vs 33.8452 dB，差值 −2.1094 dB，配对95% CI [−2.2689,−1.9487]；3/115 患者胜出，八项质量指标全部落后。**

完整结果见 [RESULTS_ZH.md](RESULTS_ZH.md)。测试目录已经存在，不应再次运行同一 test 命令或删除结果后重测。当前候选未通过综合门槠，不作为最终候选启动三 seed 确认；后续创新需要重新在 validation 建立证据，不能据此轮 test 调参择优。上方“未启动 FULL”等文字描述的是 2026-09-28 的准备阶段，最新状态以本节为准。
