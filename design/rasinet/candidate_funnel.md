# 候选筛选漏斗

## 数据治理

- 开发集：IXI ×4，以及 fastMRI-brain ×2/×4/×6。
- 独立冻结验证集：NingXia ×2/×4/×6，22 个八折 OOF examination。
- 目标模型：I3Net、HAT、SwinIR。它们同时存在于 IXI 和全部多倍率 profile，目标始终从自身 committee 排除。
- 宁夏验证开始前冻结文件：`outputs/optimization/frozen_finalists.yaml`。

## Stage A：原子设计

- 实际评价 132 个 score/mask/pooling 候选，共 74,052 条逐病例记录。
- 覆盖 median、mean、trimmed mean、maximum、分位数、committee center distance、标准化差异、relative difference 和 shared spread。
- 覆盖 target 1% mask、committee union 与 input-derived mask，以及 mean/tail pooling 的预先限定组合。
- 结构域全笛卡尔积在真实 smoke 后被判定成本过高，保留已有 factor-4 结果并记录为 `excessive_cost`，未伪装成已完成。
- 预设 baseline 在原子筛选中排名第 5；最优原子候选为 median + committee union + mean pooling。

## Stage B：委员会设计

- 5 个提升的 score 定义与 8 类 committee 策略组成 40 个候选，共 22,440 条逐病例记录。
- 策略包括 frozen primary、full universal、neural-only、analytical-only、family-balanced、analytical-anchor、low-cost 和 development-only high-fidelity。
- high-fidelity 成员仅依据开发集冻结为 I3Net、SAINT、SMamba-UNet、Pix2PixGAN；评价某目标时继续执行 self-exclusion。

## Stage C：冻结 finalist

使用 2,000 次固定种子的病例 bootstrap，冻结：

1. 预设 baseline：median + target 1% mask + frozen primary committee。
2. universal：median + committee-union mask + development high-fidelity committee。
3. low-cost：mean + committee-union mask + analytical-anchor committee。
4. decomposition：high-fidelity committee 的 shared/target 分解；开发集选择 alpha=1，说明开发结果更偏向 shared examination difficulty。

## 冻结验证结论

- 预设 baseline：mean/worst nAURC = 0.070/0.125，mean Spearman = 0.901，RRR50 = 21.8%。
- universal：0.116/0.207，0.839，19.9%；开发集优势未迁移。
- low-cost：0.080/0.166，0.893，21.2%；成本较低但未证明优于 baseline。
- decomposition：0.111/0.195，0.848，20.4%；shared-difficulty 方案同样未迁移。
- 冻结 baseline 因独立验证最稳而保留为最终推荐方案；没有用验证集替换或再调 finalist。

