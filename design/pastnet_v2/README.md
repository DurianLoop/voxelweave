# PAST-Net v2：物理几何条件下的多尺度特征对应

更新：2026-09-10。独立包：`D:\MRI\design\pastnet_v2`。旧 Design1 代码、checkpoint、split 和实验记录均未修改。

**最新 full 判定（2026-09-09）**：control=25.562011 dB；geometry=25.564138 dB，增益仅+.002126，配对95% CI跨零、13/23胜，未晋级。原geometry→correspondence累加链停止，勿继续本页旧累加命令。下一次是另行登记的 [correspondence-only独立实验](../pastnet_v2_independent/PROTOCOL_ZH.md)，去掉geometry FiLM和毫米先验，只与control比较空间特征对应。原始 [geometry gate](results/gate_geometry.json) 保持 `promoted=false`。

**2026-09-10续报**：correspondence-only也已完成，25.564482 dB，相对control仅+.002471，95% CI[+.001158,+.003992]，18/23胜；因未过+.10 dB门槛而停止。两条结构假设均未晋级，目前没有需补3seeds或可进入外部测试的候选。已完成两模型的validation急性模块关闭诊断，详见 [独立分支结果与停止结论](../pastnet_v2_independent/README.md)。此更新取代上一段“下一次”的待运行状态。

**已完成：证据复核、23 个干净 validation series 的误差/信息探针、三域几何审计、新模型与单变量开关、真实数据 smoke、control/geometry/correspondence-only full、配对判定及失败诊断。当前无晋级候选，未开展最终 3-seed full 或 IXI/NingXia 正式复评。** 不能用 smoke 代替正式结果，也没有 SOTA 或 26 dB 承诺。

## 阅读入口

1. [审计与信息上限分析](docs/01_证据与信息审计.md)：实测数值、泄漏和不可辨识性边界。
2. [模型与预注册协议](docs/02_设计与实验协议.md)：有效信息、唯一主变量、晋级/停止标准。
3. [分开的运行指令](docs/03_运行指令.md)：smoke、每阶段 full、最终 3 seeds、IXI、NingXia。

## 核心变化

原始 DICOM 恢复的毫米位置和方向进入零初始化的 feature FiLM；query 从线性 coarse 提取，在每个真实锚点的 1/4、1/2 尺度局部邻域建立对应，再进入成熟 MA3 宽主干。它改变了**空间信息被融合的位置**，而不是在已完成图像上再加 Flow。

G086 的 326 个状态张量全部迁移，六个开关配置的初始化输出最大差均为 **0.0**。保留四锚点 rich condition、64ch/10-block MA3、已有多尺度 latent、双域 residual、bounded coarse skip，以及 AdamW/warmup-cosine/EMA。没有新增输出端 3D、三 offset attention、INR 或 unrolled refiner。

频率分解解码、soft-CVaR、较长上下文是三个后续独立变量，不默认合并成“最优模型”。第一候选核心是 `correspondence`；只有 `geometry` 先晋级才能启动其正式验证。

## 已测结果的含义

| 项目 | 实测 |
|---|---:|
| 原始 G086 development-test PSNR | 24.446977 dB，复核原始 CSV |
| 旧 validation 患者交叉 | 1 名，已隔离其 validation series |
| v2 可用 validation | 23 series / 23 patients |
| 已核验 DICOM 几何 | train/val 134/135 series；1 个未知 |
| 新输入规范下冻结 G086 validation PSNR | 25.515590 dB |
| control / correspondence 参数 | 992,179 / 1,011,988 |
| control / correspondence AMP 单层延迟 | 48.09 / 50.80 ms |
| 全开关 256×256 AMP 反向峰值 | 10.00 GiB |

新规范使用**观测稀疏层 min/max**，以 256×256 missing slices、range=1、病例等权计算。25.515590 与旧 24.446977 的数据、归一化、聚合口径不同，不能相减作为收益。

## 文件索引

| 文件 | 用途 |
|---|---|
| `model.py`、`vendor/` | 新模型、带 SHA256 来源记录的 G086 本地快照；训练无需导入旧模型包 |
| `prepare.py`、`data.py` | 几何核验、patient split、仅观测层归一化、真稀疏输入 |
| `losses.py` | 共同损失骨架、平滑 CVaR、几何一致的反向对称 |
| `run.py` | 独立 train/val/test；manifest、EMA、完整恢复、外部测试锁 |
| `report.py` | 一/三 seed 严格配对、晋级门槛、候选锁定 |
| `external_report.py` | IXI 115 病例、NingXia 8 个患者 fold 的三 seed 配对汇总 |
| `audit.py`、`domain_audit.py`、`evidence.py` | 可复现的诊断、几何和历史证据审计 |
| `smoke.py`、`efficiency.py`、`figures.py` | 语义/梯度检查、同口径效率、固定病例误差图 |
| `manifests/fastmri/fold_00.json` | 新 split 映射与 geometry sidecar；不改旧数据 |
| `results/` | 原始逐 slice/series/patient CSV、审计 JSON、图像 |
| `commands/` | 分阶段正式运行脚本；不自动串起未晋级实验 |

最终代码版本的真实训练/恢复 smoke 位于 `runs/smoke_release_seed3407/`，交付检查记录为 [release_checks.json](results/release_checks.json)。四项语义测试全部通过；旧源码及 G086 checkpoint 的哈希在完成时再次核验一致。

**24 GB 显存更新（同日）**：上述记录保留为初始版本。当前 control 的真实训练 smoke 为 `runs/smoke_control_vram20_checked_seed3407/`；micro-batch=2、累积8次、前5个主干块 checkpointing，峰值 allocated/reserved=19.62/20.31 GiB。固定输入下的完整训练计算吞吐比原 batch=1 配置提高约55%（不包含数据读取）；五项语义测试通过，包括不同 micro-batch 和部分 checkpointing 的梯度一致性。正式 run 使用 `_vram20` 后缀，详见 [显存实测](docs/04_24GB显存与吞吐.md)。

本次并未启动耗时的正式训练。执行 full 前先看运行指令；如果某阶段不晋级，就记录负结果并停止该累加链，不能绕过门槛继续叠模块。
