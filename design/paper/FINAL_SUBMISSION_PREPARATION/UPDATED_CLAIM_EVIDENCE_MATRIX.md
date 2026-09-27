# 最终投稿主张—证据矩阵

旧主要证据 A、本轮事后敏感性 B、编辑重表达 C 分开记录。下表 pp 均指百分比点；所有检查/患者均保持完整配对。完整模型对矩阵不由家族摘要替代。

| 论文主张 | 类别/原始来源 | 估计量与统计单位 | 稿件落点 | 结果与允许措辞 | 仍不能说 |
|---|---|---|---|---|---|
| 共享输入下存在aligned-error blindness | A；既有定性 `main_median_real_arrays.npz` | 固定示例，像素O；不是患病率 | 主图1；补充随机示例 | A误差73.8，shared D22.8/O2.0%；disjoint D69.3/O19.8% | 一个例子证明普遍比例或临床损伤 |
| 原同模型现象可用统一local estimand表达 | C；`outputs/array_reproduced/clean_max_overlap*` 与 `overlap_covariance*`，数值从322个legacy数组重建 | 同一paired键；每检查每模型目标均值、模型等权；NingXia先series后患者；点值/CI均对应独立单位 | 主图2、表1 | ΔO fastMRI16.74 [15.73,17.74]；IXI28.63 [28.19,29.07]；NingXia15.03 [13.73,16.35]pp；pointwise cluster CI | 改写为新的事前确认检验；与原pooled-plane相关混用 |
| 跨架构共享证据仍掩盖部分误差 | A；695个`phase_arrays`和139个`targets/*_cross.npz` | 5目标先均值，再24/115检查均值；每端点/队列20对同时CI | 主图4、摘要、表3 | fastMRI6.236–16.022pp，IXI13.113–28.531pp；两队列各20/20正同时CI | 20个独立重复；架构总体或纯identity因果效应 |
| 结果不依赖所测试的target-1% support | B；相同A0/B0/B2、目标、原NIfTI acquired anchors | target1%、既有acquired union、全共同有限像素；5000joint examination bootstrap；每支持/队列20对同时CI | 主文5.3敏感性段；补充support全矩阵；`CROSS_ARCH_SUPPORT_SENSITIVITY.csv` | acquired: 6.165–15.878/13.009–28.420pp；full:6.153–15.870/12.995–28.356pp；均20/20。模型对效应排序最差rho .997，最大移一名 | 所有掩膜普遍不敏感；无需目标就能计算O；敏感性跨端点全部多重校正 |
| residue平衡后局部方向保留 | B；固定目标与实际phase几何注册 | residue1/3分别目标均值，检查内各50%平衡，再检查均值；20对同时CI | 主文5.3；补充geometry全矩阵；`CROSS_ARCH_GEOMETRY_SENSITIVITY.csv` | 平衡6.293–15.655/13.055–28.550pp，均20/20正同时CI；每residue单独也20/20 | 所有有符号几何或解剖差异被消除 |
| 几何残余是实质边界 | B；同上 | mirror=ΔO(res1)−ΔO(res3)，每对同时区间 | 主文、摘要、结论、补充 | fastMRI8/20、IXI6/20显著；fastMRI家族镜像差−.937 [−1.555,−.339]pp；严格四锚双residue fastMRI NA | 无orientation effect；非显著等于等价；虚构fastMRI边界锚 |
| 并非由某一模型单独支撑 | B；同一全部模型对检查矩阵 | 每次去除涉及一个架构的所有pair，余12；joint examination bootstrap percentile描述CI | 主文5.3；补充家族表；`CROSS_ARCH_FAMILY_ROBUSTNESS.csv` | 五种排除后均值9.237–11.639pp/20.107–25.040pp，区间均正；中位数亦保留 | 独立模型对重采样或任意新架构保证 |
| acquired-only influence超出count | A；834个`acquired_responses`、单独retrospective targets | 非self全部8contexts，3目标；检查bootstrap；每队列/端点2模型同时CI | 主图3a、表2/3 | beyond-count IXI .098/.093、fastMRI .103/.093；均正CI | 五个模型均已验证；跨架构报告卡借用同模型probe结果 |
| exactly-one-anchor association | A；同上 | rank residualization：span/asymmetry/examination；同样2模型同时CI | 主图3b、表2/3 | IXI .270/.265；fastMRI .474/.365；稳定性最低.880、既有门槛.85 | old六stratumaggregate gate通过；否认NingXia历史null/mixed或新架构失败 |
| 条件局部covariance趋势被神经网络试验支持 | A；24个`proposition_arrays` | 12 IXI检查×2模型×4幅度；同边缘分布coupled/Cartesian independent；固定epsilon0=.0025 | 主图3c、补充完整scatter | 8/8 mean ΔED²同时区间负；median relative error1.9–10.6%；worst126.4% | 同幅度covariance恒等式闭合是独立理论验证；uniform Jacobian guarantee；存在opposing实证分支 |
| 排名与局部几何不同 | A；跨架构原数组、明确fixed-A MAE端点 | 检查均值Spearman差；20对同时CI | 主文5.3、表3、完整补充 | IXI16/20正；fastMRI0/20且1负点。condition-specific paired MAE另列IXI20/20 | 用更有利paired端点替代fixed-A；通用临床排序或校准 |
| MIRA输出分开的证据字段 | C；新独立重算明细54行+主表7行 | 缺失测量为NA；covariance不借用local ΔO；不合成scalar | 主表3、`MIRA_MAIN_REPORT_CARD.csv`、`mira_report_cards.csv` | 设计/队列/local/ranking/influence/fixed/stability/contract/eligibility都可审阅 | “NA=0”；单张报告卡给出个体正确概率 |
| 基线及负结果保留 | A；原受保护完整补充与历史CSV | 各自既定估计量，不跨协议池化 | 补充完整模型库、budget、历史rank/prevalence、scoring、外部MRA | 13模型、111配置、20budget，旧计数反例、膝关节混合、SAINT区间跨零、I3Net/CycleINR不稳、guard无明确收益、Res-SRDiff恶化、外部vessel负结果 | 只展示有利实验；称新reconstruction模型；宣称部署superiority |
| 回顾性与伦理范围 | A事实审计/C措辞 | hash只能证内容与本轮次序；本地ID只能证本地分组 | 主方法/局限；补充1.4；数据审计 | 长期cohort reuse、历史selection未计入CI、精确fastMRI release与NingXia许可待作者资料 | preregistered study、untouched cohort、已获伦理批准或已全面脱敏 |

复现分层：本轮71项原数组列一致性 +24项新增敏感性一致性；87项历史显示值与148项本轮稿件断言。原数组复读与最后完整执行状态以 `REPRODUCTION_CHECK.md` 和 `outputs/reproduction_run.json` 为准，不以计划替代完成事实。旧CSV只提供冻结键/选择以及数值断言目标。敏感性独立重建像素公式与几何，统计汇总复用固定bootstrap合同；这不冒称完全独立的软件实现。
