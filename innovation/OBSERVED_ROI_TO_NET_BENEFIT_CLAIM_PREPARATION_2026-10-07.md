# 真实输入与成本核验之后：候选 claim 和后续准备

当前证据支持一个工程资格：既有16开发系列的冻结预测ROI可从observed-only MRI构造局部输入探针，原3D窗口重算名单可精确重放。它没有支持可发表的MRI任务效益claim。定位失败在旧QDA/LDA中已知，新增成本和真实值核验不能把它消除。

| 候选内容 | 新意判断 | 当前缺口 | 下一次可判定的实验 |
|---|---|---|---|
| 缓存、按区域重算、task+cost gate、参考刷新 | SACT/DynConv/SBNet/Skip-Conv/DeltaCNN/SIGE/MotionDeltaCNN已有先例 | 实际任务/全成本证据不足 | 作为执行和选择控制，不单独申报首次 |
| 充分适配后，用observed信息预测修正净任务收益，按原batch/window union及探索费用挑联合缺层动作 | 保留主研究候选，尚不能确认首次或效果 | 强基线能力、合法可覆盖ROI、剩余收益与确认均未完成 | 原训练最后模型及全部gates → 固定动作/费用 → 配对收益 → 强选择对照 |
| 低输入误差/高风险处值得修复 | 现有error/confidence/defer已研究；risk不等于可行动收益 | 尚未比较相同feature/capacity的risk头与收益头 | 若有余量，开发内整患者cross-fitting，同预算比较完整患者端点 |
| 动态IN下保持输出的局部执行 | 完整受影响patch重算已有工程先例；SIGE参考IN是近似 | 只有旧001网络资格，无当前最终模型全19资格 | 最终模型/真实合法动作下full vs cached，概率/threshold/全FOV核对 |
| 小ROI面积即可省真实耗时 | 本轮并不支持：非空appearance两例完全无batch省算，其他方法覆盖仍失败 | 实际latency、缓存冷启动、ROI/生成/transfer/后处理全成本 | 固定硬件负载及重复方案，单动作/多动作分别报告 |

接续次序保持原科学合同。先poll原session99542；真实training exit0、两臂各19998最后checkpoint冻结、真实退出receipt齐备后，运行原[evaluation入口](experiments/evaluate_mc_rc_3d_19series_common_init_final_2026_10_07.py)，完成原56FOV和4已见验证患者全部6能力gates，再跑[独立strict](experiments/verify_mc_rc_3d_19series_common_init_final_2026_10_07.py)。不读中间MRI效益，不迁移/重启用户训练，不用float解释器覆盖旧direct理想坐标absolute gate失败。

基线必须覆盖充分适配dense/PCHIP、direct-observation+availability及原合法SR；普通direct不足时，可按既有Uhrig/Eldesokey先例另准备normalized-conv对照，不能利用弱对照制造收益。新GPU工作仍先通过8GB余量及原资源合同；当前只剩1.4GB，已有CPU训练继续。

ROI由部署时可见observed或冻结任务预测产生。可以用当前64输入探针的读权限/anchors/tail/格点/SHA/逐窗口检查代码作准备，但当前ROI不通过旧覆盖门槛，不能直接接controller声称可用。不要通过GT选择扩大半径、删失败患者或替换主方法。若设计新ROI，先冻结开发内方法及代价，再完整评分；确认集合继续关闭。

真实动作需要单独冻结，包括生成器/checkpoint、observed统计、anchor/tail保护、halo、输入映射、候选个数。每个替代动作都从固定PCHIP原输入定义；若连续累计编辑，实际差分必须按当时状态重算，收益也重新评价。连续视频的历史buffer不能在候选间无标记复用。当前插值探针不代替训练过的SR，也不表明linear优于PCHIP。

费用账本至少记录observed_load、生成/ROI、cache_init、候选探索、特征/gate、transfer、infer、postprocess，shared费用患者一次、全部series累加。候选上限及同总预算预先冻结；本轮全图CPU准备58.778秒等记录不能拿来推测GPU省时。

若充分适配后确有剩余收益，用开发内按整患者cross-fitting构造候选的**配对完整任务增益**；GT仅产生训练端点，不进入ROI/features。联合Dice非线性、成本按window/batch union，不加总单动作Dice或面积。比较无修正、最佳固定合法动作、cost/defer、普通risk/误差、成本匹配random、union-aware greedy及已有LTT/Pareto控制；所有探索支出入账。

最终规则冻结后才打开8确认患者/12series。4已见验证不得更名新确认；locked IXI关闭，旧MIRA/MSValid84确认保留。fresh calibration只约束正式风险保证，没有它可研究经验MRI收益，但不宣称高概率证书。

待填claim模板：在明确thin3D phase0/x4抽层范围、相同合法观测和实测总成本下，冻结策略相对充分适配的最强同预算对照改善完整患者病灶端点，并在8确认复现。当前效应大小/确认结果/置信区间均未填。没有余量或确认失败时记录负结果并调整下一轮任务范围，goal保持active。
