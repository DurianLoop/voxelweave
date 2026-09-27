# Claim → evidence matrix

“A”表示在现有合格数据上的局部重复性，不表示预注册成功；B 为条件性证据；C 为探索性／未支持。本文层级与用户此前接管的提交资料 A 类无关。

| 主要主张与级别 | 实验／直接证据 | 数据 | 独立单位 | 统计／理论检查 | 当前稿件位置 |
|---|---|---|---|---|---|
| A：已测试共享测量条件下，局部误差可观测性下降 | Plan 9/11 正式 per-plane；Plan 13 `architecture_sensitivity.csv` | fastMRI 24、IXI 115；五架构 | examination；模型不充当患者重复 | 10,000 joint bootstrap；队列内五模型同时区间；四种均值／中位数口径 | 主 Fig.4、§5.3；补充历史全表 |
| A：旧 HAT/SwinIR clean sharing 隐藏约 97–99.8% paired-error energy | `clean_max_overlap*_per_plane.csv`、原 summary | fastMRI 24、IXI 115、NingXia 22 序列/8 患者 | examination／patient cluster | 旧 pooled-plane 点相关及簇 CI；与 case-level ranking 明确区分 | 主 Fig.2、Table 1 |
| A（条件数学）：共享协方差 κ>0 在固定偏差／边缘协方差下增加期望误差内积并降低期望分歧能量 | Proposition 1、E01、完整推导 | 固定目标的局部加性模型 | 数学命题；非医学样本 | trace 展开；12 情形×100,000 Monte Carlo；包含负敏感性反例 | 主 §3.3、补充 §2 |
| B：稳定情况下影响量含超出 overlap count 的信息 | 原 Plan 6 fixed-one；新 E06 去除 self-pair | 两模型×三队列 | examination／NingXia patient | E06 5,000 簇 bootstrap，六分层同时区间；固定计数用历史 pointwise 簇区间 | 主 Fig.3、Table 2；补充原 self-inclusive 表保留 |
| B：局部影响仅对部分架构和设置稳定 | Plan 7 perturbation/plane checks；Plan 9 stability | HAT/SwinIR；SAINT；I3Net/CycleINR | 设置内 examination/configuration；不把设置数当患者数 | .90 稳定性门限；保留 I3Net/CycleINR 未通过、跨平面失败 | 主 §3.4、§5.2；补充 stability 全表 |
| B：分离测量有时改善 case-level 排序 | Plan 13 within-case median ranking | fastMRI/IXI 五模型 | examination | 10,000 bootstrap 五模型同时区间：fastMRI0/5、IXI3/5 | 主 Fig.4、§5.3 |
| B：实际二成员解析 ensemble variance 在 IXI 共享／不相交对照中有差异 | E03B `practical_proxy_summary.csv` | IXI115；fastMRI24因几何不合格排除 | examination；先 residue 等权再病例等权 | 5,000 bootstrap，各端点两方向同时区间；fixed reference 与 paired error 分列 | 主 §5.3；补充 Table 2 |
| 描述图示：同一目标可出现小分歧、大共同误差 | E03A actual arrays；预先保存中位／随机选择 | 两例 fastMRI SwinIR | 仅图示，不增加统计样本 | 共同显示尺度、无人工 ROI、CPU/GPU 数值差公开 | 主 Fig.1；补充 Fig.2 |
| C：新 guard 有稳定的 target-free 优越性——不支持 | E02；`score_evaluation.csv`、`score_paired_deltas.csv` | development12、internal eval12、既用 IXI115；两对四架构 | examination | 仅一个公式；dev CDF/阈值；5,000 paired bootstrap；IXI12对比 simultaneous全跨零，fastMRI AP/AUC未定义 | 主 §5.4；补充 Table 1、完整 CSV |
| C：真正未见队列上的可行动优越性——未证明 | 资源资格与历史使用审计 | 所有现有适用队列已有分析使用 | patient/examination | 无合格未触及外部 cohort；不重新命名旧 test | 主限制、`research_audit.md` |
| C：Anchor-CV 独有价值／前瞻采集收益——未证明 | Plans7、11、13、14 完整失败与受益诊断 | fastMRI、IXI、NingXia；MRA解析扩展 | examination／patient | 原始和条件相关；量纲交叉；保留退化 Res-SRDiff | 补充 §§17–21；主限制 |
| 背景：13 方法、111 配置覆盖完整 | Plan15 原生 baseline 全量来源；全部预算对照 | 三队列；多倍率和20训练预算 | examination／patient-fold estimand | 原生整平面汇总，不混同 QA mask；20预算 simultaneous | 补充 Table3、Tables18–25及末页预算图；主限制引用 |
| C：非 MRI 或全部 uncertainty 方法普遍成立——未支持 | E05 未启动自然图像实证 | 无 | 无 | 理论数值检查不冒充域外实验；TTA/解析ensemble不涵盖全部Bayesian方法 | 主引言、§5.3、限制 |

输入路径、SHA-256、完整设置和异常记录由 `research_ledger.json` 索引。本表不将代数共享定义的相关性作为独立因果证据，也不把改换主线解释为早已预设的主要终点。
