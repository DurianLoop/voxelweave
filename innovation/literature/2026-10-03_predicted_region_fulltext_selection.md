# 新增正文选择

本轮四条预写 Europe PMC 查询实际返回 41 条记录（12+12+5+12）。已有 PRETTIER、spinal-SR、crossMoDA 正文不重复算新增。选择三篇未在本地正文核读的直接相关公开文章：

- SynthSeg，2023，10.1016/j.media.2023.102789，PMC10154424：分辨率/对比度域随机化，检查冻结区域预测的可迁移先例。
- Automatic segmentation of spinal cord lesions in MS，2025，10.1162/imag.a.45，PMC12319988：各向异性 T2 病灶与多中心来源、整患者划分及失败边界。
- Reconstruction from multi-planar MRI with foundation models for uterine fibroid analysis，2026，10.1038/s41746-026-02780-6，PMC13385847：基础分割模型、真实多平面与一致性/连通约束已有机制。

逐篇 EFetch 单次取得 JATS，12MB cap、timeout30s，认证 DOI 和 article body 后保存原文/段落。取得与实际核读分别记录。没有临床/模型训练复现，不能据标题称项目方法新颖。图注和表格文本核读；图像视觉审阅若未执行需明确。
