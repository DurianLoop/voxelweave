# 实验主表模型权重归档

整理日期：2026-09-20。

唯一范围依据：`D:/MRI/docx/experiment/experiment_master_table.md` 当前版本。包内保存该文件快照，本次不修改主表、不重训、不改动任何原始权重。

## 1. 包含什么

共覆盖主表及其附表中的 **108 项学习模型结果、458 份 best checkpoint**，原始权重合计约 **7.21 GiB**。主表中另外 14 项数据集/尺度组合下的 Linear、Cubic 结果是非学习插值，没有模型权重。

| 分区 | 学习模型结果项数 | 权重文件数 | 口径 |
|---|---:|---:|---|
| 三数据集 x4 主表 | 33 | 110 | IXI 11、fastMRI 11、NingXia 11×8 折 |
| fastMRI x2/x6 | 22 | 22 | 两个倍率各 11 个学习模型，test n=24 |
| NingXia x2/x6 | 22 | 176 | 两个倍率各 11 个学习模型，每个模型 8 折 |
| NingXia 60 轮敏感性 | 16 | 128 | 每个配置 8 折，独立于标准预算结果 |
| NingXia Res-SRDiff x2 90 轮 | 1 | 8 | 诊断配置，不替换标准预算 |
| fastMRI 60 轮敏感性 | 3 | 3 | SwinIR x2、ACVTT x6、Res-SRDiff x2 |
| PAST-Net fastMRI x4 开发轨迹 | 11 | 11 | G079、G081 至 G090，不冒充三数据集验证 |
| 合计 | 108 | 458 | 目前未发现缺失权重 |

按数据集计：IXI 11 份、fastMRI 47 份（含 PAST-Net）、NingXia 400 份。

学习方法包括 ACVTT、Res-SRDiff、ArSSR、CycleINR、ResUNet residual、Pix2Pix-GAN 2.5D、SwinIR 2.5D、SAINT、I3Net、HAT 2.5D、SMamba-UNet 2.5D，以及表内 PAST-Net 开发版本。

**此包是“当前主表结果对应权重集”，不是全硬盘所有训练存档。** 不包含表中未列出的 IXI x2/x6、smoke/mini、其他自研模型、每轮中间存档和 final checkpoint。没有为了省空间裁剪或转换 best checkpoint；其中已有的生成器、判别器、模型配置和其他状态原样保留。已有完整模型的 warm-start 上游权重，若未列入当前主表，不额外收录。

## 2. 如何查找

优先查看 [CHECKPOINT_CATALOG_ZH.md](CHECKPOINT_CATALOG_ZH.md)，按数据集、倍率、方法、训练 profile 查找。需要定位每一折和校验值时，查看 [checkpoint_index.csv](checkpoint_index.csv)。CSV 使用 UTF-8 BOM，方便 Excel 打开。

```text
README_ZH.md                    本说明
CHECKPOINT_CATALOG_ZH.md         按主表结果分组的中文目录
checkpoint_index.csv            458 份权重逐项索引、来源、SHA256
checkpoint_metadata.json        CPU 安全加载检查、checkpoint 内部元数据
table_index.json                主表 122 个数据集/倍率结果项及对应权重
checkpoint_plan.json            逐结果、逐折关联与缺失检查
inventory.json                  主表与原始五指标来源的匹配记录
file_manifest.csv               包内文件大小与 SHA256，不包含该清单自身
project/
  docx/experiment/experiment_master_table.md
  baseline/.../runs/.../checkpoints/*best*.pth
  pre/ixi_diffusion/runs/.../checkpoints/*best*.pth
  design/fastmri_brain_pastnet_2p5d/runs/.../checkpoints/*best*.pth
  ...相关指标、配置、训练历史、代码及已有审计证据
```

`project/` 下保留当前工作区的相对路径。相同方法的不同倍率、预算、fold 分别保留，不能互换。NingXia 的汇总值对应 8 个独立折模型，不存在一份代表八折的“总模型”。

## 3. 对应关系如何核对

1. 直接解析当前主表的 HTML 主表和 Markdown 附表，保留原分区，不按测试分数重新选结果。
2. 检查同数据集、同倍率、同方法的 PSNR、SSIM、MAE、MSE、NCC，要求五项均与主表四位小数精度一致。
3. NingXia 先检查 fold_00 至 fold_07 完整，再对八个 fold summary 等权平均；不把 22 个序列当 22 个独立患者。
4. 从已定位运行中取相应方法的 best checkpoint。IXI 的 eval-only 单独关联到原训练目录。
5. 使用 `torch.load(..., map_location="cpu", weights_only=True)` 检查所有权重可读取并包含对应模型状态；不运行训练或推理，不调用 GPU。
6. 打包时按源文件计算 SHA256；写完 ZIP 后逐文件解压读取并再次校验 SHA256，同时检查 ZIP CRC。外部 `validation_report.json` 记录最终结果，ZIP 同目录的 `.sha256` 保存整包校验值。

**证据边界：** 本次校验确认当前文件存在、可安全加载、打包前后字节一致，以及已有指标来源与主表对应；不是用 458 份模型重新推理。历史运行普遍没有把评估时 checkpoint 的 SHA256 写入结果，因此不能把本次新生成的 SHA256 说成历史评估时已经绑定的证据，也不能保证换版本环境后逐位复现。

## 4. 必须留意的历史情况

### IXI n=115 的复用权重

ArSSR、CycleINR、ResUNet residual、SwinIR、SAINT 的 n=115 结果是 eval-only，不是重新训练。前 3 类通用目录中的 ArSSR、CycleINR、SwinIR 使用各自 `runs/full` best；ResUNet、SAINT 使用 `pre/ixi_diffusion/runs/resunet_full_t2`、`saint_full_t2` 的 best。索引分别保留 `training_run` 与 `evaluation_run`。

I3Net 对应 `full_test115_stable`；其他方法以逐项索引中实际匹配到的配置为准。IXI GAN 的 best epoch=0 是已有弱基线记录，仍原样保存，不因效果弱而遗漏。

### fastMRI SAINT x2/x6 的共享输出目录

`baseline/fastmri_brain_saint/runs/full_x2` 和 `full_x6` 同时存有 SAINT、ResUNet 的权重。当前 `summary_metrics.csv` 和部分运行信息被 ResUNet 的运行覆盖，不能把它们直接当作 SAINT 的配置或训练日志。

SAINT 的五指标来自之前已完成的恢复审计：对保留的 48 份 SAINT 预测按原定义复算，与主表一致。本包附上 `project/design/paper/PLAN15_BASELINE_INTEGRATION/outputs/saint_recovered_summary.csv`、`saint_recovered_per_case.csv`、`saint_recovery_manifest.json` 和审计报告。SAINT 权重仍是对应目录中的 `saint_epoch_best.pth`，不是 `resunet_epoch_best.pth`。不声称被覆盖的原 SAINT 运行日志已完整找回。

### 主表预算和方法身份

- fastMRI HAT x4 主表采用 `full_extend60`，不是旧 `full`；其 manifest 记录 warm-start 与总预算。附表其他 extend60/90 不因此都具有相同的续训方式。
- `_root_results_202607` 是历史根目录实验迁移后的保存目录。本包沿用当前真实位置；旧 manifest 中的 `D:/MRI/...` 绝对路径可能已过期，查找时以索引为准。
- 60/90 轮敏感性和标准预算独立保存，不自动替换主排名。本包也不是等算力、公平性或收敛性的重新认证。
- 方法名称沿用主表，但本地任务适配不能自动宣称为官方论文的逐项严格复现。尤其 SMamba 的既有审计指出它使用 dependency-light directional selective-scan surrogate，而非原版 SMamba-UNet 完整实现。HAT 也是本地 2.5D 适配。
- 包内 HAT/SMamba 2026-09-16 审计对更严格的另一套协议提出限制；这些限制不会因本次归档而消失。请阅读 `project/handoff_hat_smamba_evidence_2026-09-16/AUDIT_REPORT.md`。
- 原主表末段关于 ACVTT x6 “60 轮低于标准预算”的文字与数值相反：PSNR 实为 19.8309 → 20.0269。本次仅保存快照，不擅自改动原主表；既有 Plan15 报告也记载了这一纠正。

## 5. 加载与环境

常见 checkpoint 含 `model_state_dict`；GAN 包含 `generator_state_dict` 和 `discriminator_state_dict`。完整键名、epoch、倍率及可提取配置见 `checkpoint_metadata.json`。不要统一把整个 payload 当作 state_dict，也不要仅凭当前 settings 默认值构造模型：倍率、通道数、深度、I3Net 窗口等参数必须与该权重一致。

只读检查示例：

```python
from pathlib import Path
import torch

checkpoint = Path("project/baseline/fastmri_brain_hat_2p5d/runs/full_extend60/checkpoints/hat_epoch_best.pth")
payload = torch.load(checkpoint, map_location="cpu", weights_only=True)
print(payload.keys())
print(payload.get("epoch"), payload.get("stride"))
```

运行模型应优先使用项目对应 `train.py` 中的加载器/Interpolator，并明确指定本包的 checkpoint 路径。源代码快照包含 baseline、pre、相关 PAST-Net 模块及 I3Net/ACVTT/Res-SRDiff 外部依赖代码，帮助追溯实现；**这是打包时的代码版本，不是对全部历史代码版本的恢复，也不是一键可运行的完整环境镜像。** 第三方依赖仍需按 `requirements.txt`、`environment.yml` 及对应源码说明安装。

本包不是完整断点续训备份；不保证所有 checkpoint 都含 optimizer/scheduler/RNG 状态。不应直接运行 `run_all` 来“检查权重”，以免触发训练或覆盖已有结果。

## 6. 数据和使用范围

不收录 MRI 原图、NIfTI 预测、可视化图片或数据集。少量运行配置、逐例指标和审计文件包含已有病例/序列标识与本机路径，本包用于内部交接；若要公开发布，应先审查数据使用协议、匿名化要求和第三方源码许可证。

源权重和原结果目录全部保留，未移动、删除或改写。外部校验报告的 `status=PASS` 表示归档完整性检查通过，不代表模型结果获得新的科学有效性认证。
