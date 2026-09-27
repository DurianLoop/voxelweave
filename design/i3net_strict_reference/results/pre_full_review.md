# full 前核验：2026-09-17

状态：可交付用户 full，助手未启动正式训练。

1. 官方来源：本地 commit `30be7ba7b214de62a40be5b311867d9f430e6b2e`，两份 vendor 模型源码及官方配置与上游 master 核对，除 CRLF/LF 外相同。源副本 SHA 见 `source_check.json`。
2. 输入与映射：四锚点 256×256 → 13 层，仅取索引 5、6、7。注入 NaN target/cond 不影响输出，包装器也可只传 anchors；观测位置复制在 AMP 输出 dtype 下精确。未用隐藏层归一化。
3. 重计算：前 1、2、8 组与原版 forward 比较，输出逐位一致，所有参数梯度最大绝对差均为 0；完整 23,205,197 参数模型。
4. 真实训练：完整 256² 模型、16 个 train 区间、两轮更新、一个 validation 区间的全部质量指标。每轮 microbatch 8 × 累积 2，未缩小模型。该 smoke 的质量不是模型选择证据。
5. 恢复：连续两轮与第一轮提交后中断、另起进程恢复，模型、Adam、GradScaler、CPU/CUDA RNG 逐位一致；已完成任务再次 `--resume` 不重复训练。
6. 指标：独立加载 smoke best 并重算同一 validation 样本，八个指标差值全部为 0；best/last SHA 与完成凭证匹配。
7. 显存：连续 smoke 18.754/19.598 GiB，恢复 smoke 18.755/19.693 GiB allocated/reserved；保留原始资源探测结果。1/8 checkpoint 较 2/8 多占约 2.58 GiB，微步吞吐仅提高约 4%，选用 2/8。
8. 效率：smoke 权重 forward 16.688 ms/中央缺失层，峰值 0.225783 GiB。Conv/Linear 部分 FLOPs 为 906.985G/区间，**未计 DCT matmul 等，不能称总 FLOPs**。full 结束会重新测量。
9. 正式 PowerShell 入口已用 `-Preflight` 实际运行，确认 train 1360 / val 69、seed 3407、300 轮及全尺寸模型，未创建 full 输出目录。

首次 smoke 在完成 JSON 序列化时发现 NumPy bool 问题，已在本独立包转换为原生 bool；失败目录保留。修正后的 `_v2` smoke、恢复、指标复算及最终源码哈希均通过，不把失败版本计入通过证据。

协议限制：训练从随机初始化开始、原生中央三层 L1、无 EMA；与历史 G086 继承训练不是同预算消融。baseline 没有小样本质量晋级门槛；只依照固定预算和 validation 选 best。不得读取 test 选型。下一步用户运行 README 中的单条 full。
