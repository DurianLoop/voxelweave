# 逐方法使用情况：不能把列名当作验证完成

以下“原生重建比较”对每个模型都包括 IXI／fastMRI／NingXia ×4，以及 fastMRI／NingXia ×2/×6，共七个已完成队列／倍率。所有模型都进入当前两稿正文的三队列 ×4 表、补充材料的五指标表，以及本轮全部 13 方法的病例难度分析。

| 方法 | 当前原生比较 | 既有两脑队列物理干预 | 本轮纳入的额外训练预算 |
|---|---|---|---|
| Linear | 七个队列／倍率齐全 | 非五神经架构；另有解析干预 | 无学习预算 |
| Cubic | 七个队列／倍率齐全 | 非五神经架构；另有解析干预 | 无学习预算 |
| ACVTT | 七个队列／倍率齐全 | 尚无对应完整干预 | fastMRI ×6：60 |
| Res-SRDiff | 七个队列／倍率齐全 | 尚无对应完整干预 | NingXia ×2：60/90；×6：60；fastMRI ×2：60 |
| ArSSR | 七个队列／倍率齐全 | 尚无对应完整干预 | NingXia ×4/×6：60 |
| CycleINR-style | 七个队列／倍率齐全 | 已有五架构之一；有限响应稳定性门失败仍保留 | NingXia ×2/×6：60 |
| ResUNet | 七个队列／倍率齐全 | 尚无对应完整干预 | NingXia ×4/×6：60 |
| Pix2Pix-GAN | 七个队列／倍率齐全 | 尚无对应完整干预 | 原表未列额外预算 |
| SwinIR | 七个队列／倍率齐全 | 已有；包含历史三队列分析 | NingXia ×2/×4/×6：60；fastMRI ×2：60 |
| SAINT-style | 七个队列／倍率齐全；补回两项覆盖丢失指标 | 已有五架构之一 | NingXia ×2/×4：60 |
| I3Net | 七个队列／倍率齐全 | 已有五架构之一；有限响应稳定性门失败仍保留 | 原表无独立列出的额外预算；IXI 主表采用 stable 运行 |
| HAT | 七个队列／倍率齐全 | 已有；包含历史三队列分析 | NingXia ×2：60；fastMRI ×4 的 extend60 已是原主表配置 |
| SMamba-UNet | 七个队列／倍率齐全 | 尚无对应完整干预 | NingXia ×2/×4：60 |

历史 fastMRI／NingXia 受益审计覆盖这 13 方法；candidate-bank 目标行覆盖其中 11 神经方法。模型库候选成员只有六神经方法加 Linear/Cubic，目标数与候选成员数不应混为一谈。该来源解释以 [Plan 14 更正](../PLAN14_SCIENTIFIC_STRENGTHENING/SOURCE_CORRECTIONS_ZH.md) 为准。

原表中的 PAST-Net G079–G090 开发轨迹没有被删除或否认价值，但这些版本反复使用 fastMRI 开发评价，缺少同一冻结版本的三队列结果。本轮未把它们塞进统一 baseline 表，也未把 ECSI／ACSI／RASI 的其他协议结果强行改名为本表结果。旧稿中的 ACSI 等附加背景记录继续保留在历史支撑表；本轮 13 方法表严格对应用户指定的主表。

实际来源见 [111 行配置](outputs/baseline_all_verified.csv)，机制范围和科学风险见 [完整报告](FINAL_REPORT_ZH.md)。
