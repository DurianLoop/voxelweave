# 用户提供的接续摘要（原文保存）

目标仍 **active**：继续研究验证，直到形成可发表且独立确认的 claim。此次 compaction 不代表暂停。上一轮和本轮都有实际进展，但尚未达到目标。

### 约束

- 新增内容仅写 `D:\MRI\innovation`。
- Python：`D:\conda\envs\MRI\python.exe -X utf8 -B`。
- 不用 GPU，不枚举/操作用户终端训练，不读 locked IXI test，不改根环境或 `.gitignore`，不创建/委派代理。
- CPU 单线程、自身 below-normal，磁盘≥15 GB、可用内存≥8 GB。
- 不重启 live 或已完成任务；失败保留，新 attempt 修复。
- 11开发/19系列、4验证/9系列、8确认/12系列固定。八确认患者禁止提前开效果。
- 以下路径均相对 `D:\MRI\innovation`。

### 先轮询正在运行的训练

**session `25480`**：

`experiments/run_mc_rc_coverage_augmentation_factorial_cpu.py`

输出：

`experiments/mc_rc_coverage_augmentation_factorial_cpu/attempt_01.json`

最后实际 poll 确认 live，已到 `legacy_none` **800/4000** updates。之后做了文献获取和阅读，**尚未再次实际 poll**；不要依据时间重启，也不要宣称全部完成。

四条件：

1. `legacy_aug`：精确核验后复用上一轮已完成的 BCE+Dice 基线，零新训练/生产前向。
2. `legacy_none`
3. `coverage_aug`
4. `coverage_none`

后三臂按上述顺序，各随机初始化、4000步，合计 **12,000 新 updates**。同初始化、原外生 z/增强 primitive、loss、optimizer、预算、最后 checkpoint、完整原生 FOV/.5。不能改正在运行的源码或协议，否则 SHA 绑定失效。

协议：

`MC_RC_COVERAGE_AUGMENTATION_FACTORIAL_CPU_PROTOCOL_2026-10-03.md`

### 本轮已完成的采样证据

生产 **session83243 exit0**：

`experiments/prepare_mc_rc_coverage_augmentation_draw_cpu.py`

独立核验 **session68189 exit0**：

`experiments/verify_mc_rc_coverage_augmentation_draw_cpu.py`

输出目录：

`experiments/mc_rc_coverage_augmentation_draw_cpu/`

- 4000旧基线样本 SHA 全部精确匹配，因此允许复用旧臂。
- 四臂 **16,000 输入 SHA** 和 **16,000 完整 patch 源像素映射**核验通过。
- 所有72个 z 均覆盖；每 z 更新数19–96。
- physical 360×360，完整 tile 起点 `[0,96,192,232]`，共16。
- 增强关闭时逆映射原 patch 支撑；覆盖两臂使用原空间逐 z tile 游标，再映射增强坐标。独立 reference 用编号全平面验证全部16384个 patch 像素。
- 平均两 patch 前景 mass：原采样约1877，覆盖约684。覆盖改变了前景曝光，必须报告，不能称相同 foreground exposure。
- 网络前向0、训练0、GPU0。

实现：

`experiments/mc_rc_coverage_augmentation_draw_cpu_support.py`

准备协议：

`MC_RC_COVERAGE_AUGMENTATION_DRAW_CPU_PROTOCOL_2026-10-03.md`

### 已完成的上一轮结果，勿重跑

入口：

`SESSION_HANDOFF_DEVELOPMENT_AND_LOSS_2026-10-03.md`

- 冻结20k模型：11开发人19系列 full Dice `.1279470815`；8系列 TP=0，只有2空预测。19指标/57完整 plane 已核。
- 单012同4000预算：BCE+Dice `.8653119162`；Unified `.8237855036`，两臂完整病例 fit gate 失败。后者 recall 增加，但 FP、体积、边界恶化。
- 固定012 z38、16tile各125曝光、1000步无增强：plane Dice `.9841104995`、recall `.9693126023`、面积误差 `.0300736498`，最小 plane gate 通过并独立重放。不能代替完整患者或泛化能力。
- 上轮真实新训练9000步、合成20步；64完整 plane 重放。
- 原 session70121 affine 评分失败保留，未知最终 forward 数，勿编造总数。
- 上轮131文件 stage、全局2156 evidence/2611链接四检查通过；**不覆盖本轮新文件**。
- 上轮全部自有进程已结束；当前 README 顶部描述的是上一轮，尚未更新本轮 live 状态。

### 本轮新文献：获取完成，阅读尚未完成

目录：

`literature/source_cache/coverage_augmentation_fulltexts_2026-10-03/`

两个新原始 JATS：

- `brain_weighting`：**Loss Weightings for Improving Imbalanced Brain Structure Segmentation Using Fully Convolutional Networks**，2021，PMC8393549，DOI `10.3390/healthcare9080938`，98块。
- `lesion_augmentation`：**New lesion segmentation for multiple sclerosis brain images with imaging and lesion-aware augmentation**，2022，PMC9633994，DOI `10.3389/fnins.2022.1007453`，107块。

**实际已显示读完：**

- brain weighting：块 **0–48**。
- lesion augmentation：块 **0–53**。

下一次读：

- brain weighting **49–97**。
- lesion augmentation **54–106**。

205块已获取，只有103块已实际读取；**不能写两篇全文已读完**。尚无阅读报告或 reading provenance。

检索/选择/获取脚本及笔记为：

`literature/*coverage_augmentation_followup*2026_10_03.py`

`literature/2026-10-03_coverage_augmentation_followup_*.md`

已知要点：2021论文比较类频率/focal/距离权重，并从九种 LR×epoch组合选择模型，非本项目固定预算复现。2022论文用双时点 FLAIR、nnU-Net、33%前景采样、五fold集成，已有轴向模糊与 lesion-aware CarveMix；不能把这些宽概念称创新。

### 明确下一步

1. **首先 poll `25480`，继续同一句柄**，保留三新臂全部结果。
2. 读完上述剩余正文，写实质笔记及精确阅读/SHA provenance。
3. 实现因子实验独立 verifier：四臂标签轴/计数/完整 affine surface、checkpoint、全部 draw SHA、首中末共12完整 plane 重放。此 verifier **尚未编写**。
4. 全部核验后报告四臂、覆盖/增强主差与差中之差；单训练患者/单seed，不作患者显著性或泛化 claim。fit gate仍是 full/missing Dice≥.90、recall≥.90、absRVE≤.10。
5. 根据完整结果准备整个开发/四验证能力训练，之后才做 native、6×5公平矩阵、直接任务/随机分辨率、可观测缺层修正及八确认/第二任务网络。
6. 保存本轮公开对话与本 compaction 请求，更新 README/queue、新 handoff、stage/global归档。本轮这些归档工作 **尚未完成**。

保留的创新问题仍是：任务充分适配、统计与预算公平后，是否存在能从 observed 信息识别并优于强 PCHIP/直接任务修复的缺层病灶残差。当前科学确认0，不能 complete 或 blocked。
