# 三人 anchors-only × 归一化任务预检：完整结果

固定 VS-SEG-202/203/204，各四条件，12 次新增 CPU 前向。producer session55424、最终输入/标量 verifier11226 均实际 exit0。12 个保存预测的指标复核、12 个完整网络输入 SHA 重放、6 个 fixed 缺层身份与全部 36 个配对端点均通过。没有使用 GPU；科学独立确认患者为 0。

这是开发机制诊断。四条件都改变 observed anchors，违反原 observed-preserving SR 合同，因此其结果不能当作可部署 SR 方法改进。fixed 使用相应 raw/post 基线的全体积均值和标准差；缺层及 tail 网络输入逐位不变。own 使用干预自己的统计量，会同时改变缺层的归一化输入。

| 预先固定比较 | JSON full 平均 ΔDice | RTSTRUCT full 平均 ΔDice |
| --- | ---: | ---: |
| raw_anchor_own-raw | +0.00923680 | +0.00899792 |
| raw_anchor_fixed-raw | +0.00958135 | +0.00944103 |
| post_anchor_own-post | -0.00813223 | -0.00816166 |
| post_anchor_fixed-post | -0.00505496 | -0.00507443 |
| raw_anchor_own-raw_anchor_fixed | -0.00034455 | -0.00044311 |
| post_anchor_own-post_anchor_fixed | -0.00307727 | -0.00308723 |

| 患者 | JSON full post_fixed−post | RTSTRUCT full post_fixed−post |
| --- | ---: | ---: |
| VS-SEG-202 | -0.00149780 | -0.00344332 |
| VS-SEG-203 | -0.02975063 | -0.03012942 |
| VS-SEG-204 | +0.01608354 | +0.01834945 |

主要关注的 JSON full post_fixed−post 均值为 −.00505496，三人分别 −.00149780、−.02975063、+.01608354。RTSTRUCT full 均值为 −.00507443。当前结果不支持“同时处理 anchors、平衡带宽就能恢复 post 分割表现”的固定解释；停止这一恢复主张，不盲目扩展到全 45 人。

raw_fixed−raw 的 full 平均为正（JSON +.00958135、RT +.00944103），但 202 仍变差；不能改用 raw 条件挽救原 post 恢复解释。post 的 own−fixed 平均为负（JSON −.00307727），只能描述这个实现下归一化选择的条件效应，不能说全体积归一化解释了全部损失。

保留域反例：JSON 去 1mm reference 边界的 post_fixed−post 为 +.02011658，RT 为 +.01731318，与 full 的负均值不同。去边界域同时排除带内的 FP/FN，不是独立“病灶核心恢复”证据。该三人 full/slab Dice 相同，不能当作重复的独立成功。n=3，不进行 bootstrap 显著性声明，不挑患者、标签、域或条件。

| 比较 | 标签 | 域 | n | 平均 ΔDice | 正/负/零 |
| --- | --- | --- | ---: | ---: | --- |
| raw_anchor_own-raw | original_json | full | 3 | +0.00923680 | 2/1/0 |
| raw_anchor_fixed-raw | original_json | full | 3 | +0.00958135 | 2/1/0 |
| post_anchor_own-post | original_json | full | 3 | -0.00813223 | 1/2/0 |
| post_anchor_fixed-post | original_json | full | 3 | -0.00505496 | 1/2/0 |
| raw_anchor_own-raw_anchor_fixed | original_json | full | 3 | -0.00034455 | 2/1/0 |
| post_anchor_own-post_anchor_fixed | original_json | full | 3 | -0.00307727 | 0/3/0 |
| raw_anchor_own-raw | original_json | observed_anchor_slab | 3 | +0.00923680 | 2/1/0 |
| raw_anchor_fixed-raw | original_json | observed_anchor_slab | 3 | +0.00958135 | 2/1/0 |
| post_anchor_own-post | original_json | observed_anchor_slab | 3 | -0.00813223 | 1/2/0 |
| post_anchor_fixed-post | original_json | observed_anchor_slab | 3 | -0.00505496 | 1/2/0 |
| raw_anchor_own-raw_anchor_fixed | original_json | observed_anchor_slab | 3 | -0.00034455 | 2/1/0 |
| post_anchor_own-post_anchor_fixed | original_json | observed_anchor_slab | 3 | -0.00307727 | 0/3/0 |
| raw_anchor_own-raw | original_json | exclude_reference_boundary_1mm | 3 | +0.02024232 | 2/1/0 |
| raw_anchor_fixed-raw | original_json | exclude_reference_boundary_1mm | 3 | +0.02055475 | 2/1/0 |
| post_anchor_own-post | original_json | exclude_reference_boundary_1mm | 3 | +0.01818890 | 2/1/0 |
| post_anchor_fixed-post | original_json | exclude_reference_boundary_1mm | 3 | +0.02011658 | 2/1/0 |
| raw_anchor_own-raw_anchor_fixed | original_json | exclude_reference_boundary_1mm | 3 | -0.00031243 | 2/1/0 |
| post_anchor_own-post_anchor_fixed | original_json | exclude_reference_boundary_1mm | 3 | -0.00192768 | 1/2/0 |
| raw_anchor_own-raw | rtstruct | full | 3 | +0.00899792 | 2/1/0 |
| raw_anchor_fixed-raw | rtstruct | full | 3 | +0.00944103 | 2/1/0 |
| post_anchor_own-post | rtstruct | full | 3 | -0.00816166 | 1/2/0 |
| post_anchor_fixed-post | rtstruct | full | 3 | -0.00507443 | 1/2/0 |
| raw_anchor_own-raw_anchor_fixed | rtstruct | full | 3 | -0.00044311 | 2/1/0 |
| post_anchor_own-post_anchor_fixed | rtstruct | full | 3 | -0.00308723 | 0/3/0 |
| raw_anchor_own-raw | rtstruct | observed_anchor_slab | 3 | +0.00899792 | 2/1/0 |
| raw_anchor_fixed-raw | rtstruct | observed_anchor_slab | 3 | +0.00944103 | 2/1/0 |
| post_anchor_own-post | rtstruct | observed_anchor_slab | 3 | -0.00816166 | 1/2/0 |
| post_anchor_fixed-post | rtstruct | observed_anchor_slab | 3 | -0.00507443 | 1/2/0 |
| raw_anchor_own-raw_anchor_fixed | rtstruct | observed_anchor_slab | 3 | -0.00044311 | 2/1/0 |
| post_anchor_own-post_anchor_fixed | rtstruct | observed_anchor_slab | 3 | -0.00308723 | 0/3/0 |
| raw_anchor_own-raw | rtstruct | exclude_reference_boundary_1mm | 3 | +0.01748700 | 2/1/0 |
| raw_anchor_fixed-raw | rtstruct | exclude_reference_boundary_1mm | 3 | +0.01771038 | 2/1/0 |
| post_anchor_own-post | rtstruct | exclude_reference_boundary_1mm | 3 | +0.01532960 | 2/1/0 |
| post_anchor_fixed-post | rtstruct | exclude_reference_boundary_1mm | 3 | +0.01731318 | 2/1/0 |
| raw_anchor_own-raw_anchor_fixed | rtstruct | exclude_reference_boundary_1mm | 3 | -0.00022338 | 2/1/0 |
| post_anchor_own-post_anchor_fixed | rtstruct | exclude_reference_boundary_1mm | 3 | -0.00198358 | 1/2/0 |

fixed 条件保持缺层网络输入相同，但改变邻层上下文；3D 网络及滑窗仍可使缺层输出变化。该事实只在实际 checkpoint/预处理/阈值下成立，不证明局部解剖损伤、临床危害或恢复机制。输入重放共享 decoder/PCHIP/resize/NumPy；不是独立来源、独立任务模型或完整第二软件栈复现。

后续先检查任务评估器暴露与完整操作链，保持 raw 原网格强对照；将来训练使用跨输入 × 跨任务网络矩阵，且需要真正未用于选择的确认患者。不得重启已结束队列，也不得把当前失败用新名字覆盖。

证据：[事前方案](ANCHOR_BANDWIDTH_TASK_CPU_PILOT_PLAN_2026-10-03.md)、[全部36端点](experiments/anchor_bandwidth_task_cpu_pilot/all36_descriptive_task_endpoints.csv)、[108逐人配对值](experiments/anchor_bandwidth_task_cpu_pilot/all108_patient_differences.csv)、[72条件/标签/域指标](experiments/anchor_bandwidth_task_cpu_pilot/all72_condition_label_domain_metrics.csv)、[最终独立输入与标量复核](experiments/anchor_bandwidth_task_cpu_pilot/independent_inputs_and_all36_estimates.json)。
