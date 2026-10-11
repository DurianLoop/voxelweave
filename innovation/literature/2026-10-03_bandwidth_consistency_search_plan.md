# 面内带宽与层间一致性：针对当前 MRI 项目的补充查新

本轮继续已有研究目标。GPU 被占用，不使用 GPU、不修改或停止用户终端训练、不读取 locked IXI test；所有新增内容放在 innovation。新建/委派代理不在本轮操作范围。

现有证据：45 已见 CISS 的解析顺序对照已完成；post_resize_pchip 的完整 CPU 任务队列仍在运行（session 20644），未读取动态子集 Dice。仅观测层 order_rms 风险候选的独立复核已启动（session 35552），不得提前把 producer 结论当独立确认。

要区分的问题是：缺层经面内 down/up，而观测 anchors 保持原样，是否产生沿 z 周期性的带宽差异，并影响冻结的 2.5D 分割器。此时序模式是候选解释，不是已验证结果；对 anchors 做相同处理只能作为解释性干预，会改变观测层，不能称为满足 observed-preserving 合同的新 SR 方法。

预先固定五类公开索引查询：

1. MRI、slice interpolation 与 blur/aliasing。
2. anisotropic MRI、segmentation 与 resolution/partial volume。
3. medical imaging、resampling 与 pipeline/order/interpolation。
4. MRI、slice super-resolution 与 segmentation/boundary。
5. MRI、slice inconsistency 与 blur/sharpness/bandwidth。

每类最多返回 12 条 core 记录，发布日期截断 2026-10-03；保存 exact query、URL、原始返回、SHA、失败和实际读取范围。返回题名不等于全文阅读；重复题名/DOI 不重复算论文。没有检出直接相同方法不证明首创。

正文优先选有明确对照、可合法公开访问且未在本项目已读的文章。优先核读方法、采集/重建分辨率、任务网络、数据独立性、局限和结果反例；原作者指标单独标记，不能当项目复现。读后写碰撞矩阵和具体后续准备，再决定是否值得新 CPU 前向实验。当前不预写成功 claim，也不根据动态新 Dice 挑参数/患者/标签。
