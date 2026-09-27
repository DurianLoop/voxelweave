# Continuous influence 扩展：执行状态

更新时间 UTC：2026-09-15T06:43:51.512699+00:00。新响应目标 2085/2085。每个目标含全部九上下文、四幅度、双锚和四随机场。

| 模型 | 队列 | 已完成/计划目标 | 接口检查 | 统计完成 |
|---|---|---|---|---|
| linear | fastmri | 72/72 | PASS | True |
| linear | ixi | 345/345 | PASS | True |
| acvtt | fastmri | 72/72 | PASS | True |
| acvtt | ixi | 345/345 | PASS (batch1; batch4 record retained) | True |
| resunet | fastmri | 72/72 | PASS (batch1; batch4 record retained) | True |
| resunet | ixi | 345/345 | PASS (batch1; batch4 record retained) | True |
| smamba_unet | fastmri | 72/72 | PASS | True |
| smamba_unet | ixi | 345/345 | PASS | True |
| arssr | fastmri | 72/72 | PASS | True |
| arssr | ixi | 345/345 | PASS | True |

所有模型/队列完成或明确技术失败后，才构建新的八模型同时区间与最终大表。正在计算中的模型不能写成 NA、失败或成功。

原始响应：outputs/responses；运行日志：logs/linear_run.log、logs/neural_run.log；分析日志：logs/analysis.log。

此文件仅记录实验执行进度；论文入口是否安装、PDF 是否重建及视觉检查是否完成，以 DELIVERY_STATUS.json 为准。