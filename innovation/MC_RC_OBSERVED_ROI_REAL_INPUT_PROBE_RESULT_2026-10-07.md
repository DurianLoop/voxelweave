# 冻结观测 ROI 的真实 MRI 输入探针：结果

完成16开发系列/8患者、4冻结方法、64个候选。只从既有observed-only包生成PCHIP与linear：每个候选在原预测ROI内部缺层直接赋值linear，区域外保留PCHIP，同observed统计归一化，再用原physical_mr映射。没有完整native MR、GT或checkpoint读取、模型/GPU forward或训练更新。

生产真实exit0，115.4394秒；独立v2真实exit0，121.5063秒。两次成功各加载16观测包和64冻结预测数组；独立失败v1另加载1观测包、0预测数组。因此本轮真实探针**共33次观测MRI数组加载**，不是32或0。各次权限审计未发生禁止路径访问。

| 冻结ROI方法 | native真实changed体素合计 | physical真实changed体素合计 | 实际k/几何k | 无实际改变系列 | 非零改变系列 | 原ROI gates通过 |
|---|---:|---:|---:|---:|---:|---:|
| joint_QDA 主 | 947872 | 846949 | 209/209 | 1 | 15 | 0/16 |
| appearance_QDA | 2089515 | 1753124 | 43/43 | 14 | 2 | 0/16 |
| coordinates_QDA | 0 | 0 | 0/0 | 16 | 0 | 0/16 |
| joint_LDA | 200770 | 183775 | 156/156 | 0 | 16 | 0/16 |

总原始tile数1039，每方法完整forward521；独立重建64候选并核4156个逐tile输入相等比较。实际changed mask与逐tile `np.array_equal`完全一致；全体64候选实际触及batch数与几何估计相等，anchors/tail逐位不变，actual physical差分全部在既有几何支持内。真实体素计数在不同格点中，不能直接比较为同物理体积比例。这里只是这一个固定输入探针的发现，不证明任意SR动作、其他归一化或模型配置都有同样成本。

joint_QDA患者等权条件forward节省仍55.1371%（包含1例无编辑），而旧来源前景覆盖仍5.3781%、boundary6.0097%。成功核对输入支持未改变定位覆盖。appearance两例非零改变都触及全部batch；coordinates全空不能当100%有效提速；joint_LDA虽有实际输入变化但旧前景覆盖0。不能把这些候选称病灶修复或正收益。

本轮完整输入准备16系列合计56.0311秒；4×16候选准备记录合计58.7780秒，包含全图映射、mask生成、逐tile核对、压缩与哈希，分方法为16.4353/14.0263/13.3432/14.9732秒。它们是并发负载下CPU执行记录，**不是部署benchmark**。生产当前仍全图生成linear/PCHIP并对每候选全图重采样；局部生成、网络cache初始费用、controller探索、数据转移、最终推断和后处理还未实测，不由forward减少换算速度。

独立实现使用显式disk dilation、`np.where`候选构造、自写重建/窗口/Fraction费用；共享既定SciPy PCHIP及torch trilinear算子和同来源。因此是实现重放/成本核验，不是独立库算子验证或临床独立确认。

独立v1真实exit1，0.1508秒，读第1观测包后误引用旧QDA series行不存在的`observed_array_sha256`，traceback保留。新v2从该观测包的权威input-preparation行取得数组SHA，未放宽检查或改输入；全部16包通过。原v1源码/失败JSON及v2源码/成功JSON均保留。

证据：[事前协议](MC_RC_OBSERVED_ROI_REAL_INPUT_PROBE_PROTOCOL_2026-10-07.md)、[生产](experiments/mc_rc_observed_roi_real_input_probe_2026_10_07/attempt01.json)、[独立失败v1](experiments/mc_rc_observed_roi_real_input_probe_2026_10_07/independent_real_input_replay_attempt01.json)、[独立成功v2](experiments/mc_rc_observed_roi_real_input_probe_2026_10_07/independent_real_input_replay_attempt02.json)。64个压缩bool差分包和全部绑定SHA在同结果目录，未保存新增完整MRI浮点数组。
