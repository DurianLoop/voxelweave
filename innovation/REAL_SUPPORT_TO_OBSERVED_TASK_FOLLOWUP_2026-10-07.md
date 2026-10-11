# 从开发几何空间到可发表MRI claim的实验准备

本轮真实标签几何诊断给出继续准备的理由，而没有替代能力/效益验证。候选仍是：在当前明确的thin3D phase0/x4抽层任务中，部署仅用observed输入，选择能够改善完整患者病灶任务的修正，在相同真实总成本下超过充分适配基线和强选择控制。不能扩成真实厚层采集、首次局部计算、首次不确定性路由或首次缓存。

1. 接续同session99542，真实exit0且两臂各19998/共39996最后checkpoint冻结后，才写实际训练退出receipt。沿原[evaluation入口](experiments/evaluate_mc_rc_3d_19series_common_init_final_2026_10_07.py)完成56FOV、4位已见验证全部6能力gates、[独立strict](experiments/verify_mc_rc_3d_19series_common_init_final_2026_10_07.py)和真实退出receipt。旧direct理想坐标absolute gate失败保留；float解释器不能覆盖。正式CPU训练不迁移设备、不读中间效益。GPU授权仍有效，但新GPU实验先满足既定8GB余量。
2. 在充分适配dense/direct/SR及原合同完成后，单独冻结实际资源/等价协议。先用固定observed-derived ROI或冻结任务预测做输入修改；GT只评分，不能输入定位/成本路由。标签oracle只保留机制参照，不训练部署时看不到的feature。不要以本轮标签诊断新发现全部病灶可见；旧15系列审计已覆盖该问题。
3. 对真实MRI修改，先固定observed归一化统计、geometry/model/device/precision、tile排序及原batch组合，再取实际physical input差分。逐位不变窗口复用资格与完整候选推断比较：概率差、阈值差、完整FOV、anchors/missing/tail与费用；不能只核ROI输出。重估全图归一化、换checkpoint或修改batch形状会使缓存失效。候选生成本身若全图计算，必须计入。
4. 测完整费用：observed_load、warmup_cache、sr、candidate_exploration、feature、gate、transfer、inference、postprocess；shared费用每患者一次、所有series费用求和。先做资源资格，再少量预热和固定重复；按同硬件、backend、batch、precision及负载条件比较，包括无修正、只一个动作、多动作，记录峰值显存/缓存字节和时间。forward计数用于解释，不换算成速度。训练阶段总开销另列，不与部署预算混淆。
5. 收益监督使用开发患者的配对完整任务增益；只在开发内按整患者cross-fitting，全部纵向series随患者走。Dice是分式，多个动作的增益不能相加；窗口覆盖亦按union。模型输入必须来自真实observed、冻结预测和合法生成候选，预测目标/GT不得入特征。不先建复杂收益头：确认充分适配后的剩余收益，零/负剩余则保存负结果并转任务/退化范围。
6. 在相同完整预算下比较无修正、最佳固定合法动作、成本最少/defer、普通风险/误差头、随机且成本匹配、union-aware greedy以及此前已实现的LTT/Pareto选择控制。空间门控可用既有思想作控制；不要把未复现的DynConv/SBNet作者整网视为已经跑过的MRIbaseline，也不要求一次全部新增架构训练才能报告窄经验结论。区别可预测任务增益与仅ROI稀疏/误差排序解释；任何controller候选探索成本一并计入。
7. 规则和完整策略冻结后，才打开8确认患者/12series做一次规定确认；第二任务模型及其他退化/profile需要另行预注册验证。4已见验证不是未见确认。fresh calibration仅是正式高概率风险保证的条件，不增加成经验MRI效益论文的硬门槛；没有独立calibration就明确不声称正式保证。旧MIRA/MSValid84确认不抹除，locked IXI保持关闭。

可能支持的窄claim模板（尚未成立）：在[任务/范围]、[合法输入]、[冻结policy]和[全部实测预算]下，[患者端点]较[充分适配且同预算最强对照]提高[效应及患者不确定性]，在8确认复现，并由机制消融排除Dice分式/区域覆盖/弱baseline。仅“找到局部空间”“正确实现cost库”“与旧方法差异”不填入该模板。本轮不填写虚构效应或置信区间。

本轮geometry决定：18/19系列有条件window复用空间，故保留局部执行研究；5动作含初始化只有17/19严格有forward计数节省，故必须报告不同动作数的完整预算。001第二系列无窗口复用不能被平均值掩盖。SACT/DynConv/SBNet原文把门控/分块/预算放回已知对照层，创新判断继续依赖实际MRI剩余任务收益。
