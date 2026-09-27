# full前复核：可以交付E1指令

2026-09-15，助手完成以下工作；没有自动启动full。

## 设计和能力

新增路径与已停止LACV、线性频率读出独立，不使用其权重。相对G086，直接扩大query可访问的锚点空间对应支持，保留锚点身份到非线性读出。global/local相同1,048,019参数，新增55,840参数；后续只用候选位置mask对照支持范围。

注册的4训练区间、96步、冻结旧G086、新路径AdamW=.001、原完整loss的能力检查通过：MSE下降15.3205%，MAE同步下降。没有按validation调步数或学习率，没有保存临时权重。这是小样本训练能力，不是full结果或泛化收益。

## 合同和执行

- 零投影输出与原G086逐位一致，target不读，metadata变化不影响本新路径；无效特征不能进入新路径。
- global远距离value变化对中心query有可测影响.005290；local相同位置影响严格为0。SDPA与独立显式矩阵计算一致。
- 相同seed两臂所有参数初始化相同。顺序反转两次的输入合同通过。
- global/local真实trainer各1轮smoke通过，完整loss反向传播梯度有限；global已完成checkpoint的恢复加载入口通过。这里不声称验证了中途断电逐步重放的位级一致性。
- full.ps1语法检查通过，未执行该脚本。global正式入口以trainer stub验证，未启动full；外部test/lock被拒绝，模拟E1失败时local被拒绝。
- 原v2源码、control manifest及本包capacity/smoke源哈希一致，smoke不能进入正式full报告。

## 资源

| 设置 | global allocated/reserved GiB | local allocated/reserved GiB | global训练ms/区间 |
|---|---:|---:|---:|
| checkpoint6 | 19.147 /19.826 | 19.146 /19.832 | 406.24 |
| checkpoint5（选定） | 20.647 /21.326 | 20.646 /21.379 | 396.64 |

两臂使用同一选定设置，保持有效batch16与recipe。真实trainer smoke global峰值20.62 GiB，吻合完整反传bench。24GB卡保留余量，不人为填充显存；具体full峰值仍会在每轮history记录。

独立forward：global49.3189ms/缺失层、local48.9561ms；峰值均.870795GiB。与control使用同一硬件、PyTorch、输入形状、AMP、10次warmup及30次计时；global时间比1.03408、显存比1.01403，前置效率检查通过。正式full完成后会重新测量其best checkpoint效率。

部分FLOPs为448.64264G/三层区间，包含Conv2d/3d、Linear及四锚点稠密SDPA的QK/AV矩阵乘法；不含FFT、softmax、归一化等全部算子。local使用同一稠密SDPA加mask，不能把被屏蔽位置当作已由稀疏kernel省去计算。

初始实现检查纠正了第一个固定训练series的后缀拼写，并修正新效率驱动继承的旧plane-hook计数。两项均在正式能力检查和trainer smoke前完成，未修改样本患者、假设、效果门槛或旧源码。

## 执行

用户当前仅运行 `full.ps1 -Variant global -Seed 3407`。结果目录 `runs/full_global_seed3407_vram20` 尚未建立。80轮上限不因best位于末轮自动延期；E1对control需+.10 dB及全部guards，失败停止。

原fastMRI test24继续是历史development test；本模型没有新的test结果。最终三seed和外部测试都尚未开始，不能将这份执行核验写成SOTA确认。

- [capacity](capacity.json)
- [checkpoint5 benchmark](bench_cp5.json)
- [global效率](efficiency_global.json)
- [local效率](efficiency_local.json)
- [最终验证JSON](final_verification.json)
