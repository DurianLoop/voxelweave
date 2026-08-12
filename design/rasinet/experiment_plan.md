# ICASSP 可靠性实验清单

预先指定的主方法固定为：全体非目标成员组成 committee、median target-to-committee disagreement、原始逆归一化强度、1% target-derived mask、仅评价 x4 真正生成的切片、2,000 次病例 bootstrap、随机种子 20260715。不得依据 fastMRI-brain 或 NingXia 的已观察结果重新选择方法。

状态约定：`[x]` 表示已经实现并经真实运行或测试验证；`[ ]` 表示当前数据条件下尚未完成的后续工作。注册 full 和 2,000 次 bootstrap 已结束。

## P0：投稿前必须完成

- [x] 统一 score variants：median、mean、maximum、trimmed mean、distance to committee mean、distance to committee median、shared standard deviation。
- [x] 从体素图重新计算所有合法 committee 子集及 committee size；不使用预聚合病例分数近似删除成员。
- [x] 实现 raw、p1--p99、robust median/IQR 和 min--max 强度归一化敏感性。
- [x] 实现 0.5%、1%、2%、5% target mask、committee union/intersection/median、input-derived mask，以及严格隔离在 evaluation 阶段的 `ground_truth_offline` upper bound。
- [x] 检查病例集合、重复 ID、缺失文件、shape、affine、orientation、finite value 和 generated-slice pattern。
- [x] 实现 foreground/all-pixel Fisher-z correlation、median/IQR、Spearman、Kendall、raw/oracle/random AURC、nAURC、RRR25/50/75、retained MAE、top-decile AUROC/AUPRC 和 paired bootstrap CI。
- [x] 完成 post-hoc 成本表。30 例 stored-output audit 均值 1.184 s、p95 2.872 s，观测 CPU RSS 峰值 0.89 GiB；linear/cubic CPU 插值也在每队列固定 10 例上完成。
- [x] 自动生成 results registry、LaTeX 表格、结果宏和 figure source data。
- [x] 完成 161 个 examination、504 个汇总组、33,672 行结果和全部 2,000 次 bootstrap 的注册运行；最终验证器通过。
- [x] 使用官方 ICASSP `spconf`/`IEEEbib` 创建独立 regular 和 extended 稿件，不覆盖原稿。
- [x] regular 最终版为 4 页技术内容 + 第 5 页合规/参考文献；extended 为 8 页技术内容 + 第 9 页合规/参考文献。

## P1：强烈建议完成

- [x] 实现 mean/median pairwise disagreement，并为每个 committee 子集记录不使用 ground truth 的 output-diversity proxy。
- [x] 实现 gradient-domain 与 Laplacian-domain target-to-committee disagreement。
- [x] 实现从 x4 observed anchor slices 生成的 input-derived mask。
- [x] 完成 20 个固定 IXI examination、4 个 target、5 个强度的 target-specific/shared additive-patch stress test，并以 examination 为 bootstrap cluster 同时报告 target MAE、committee MAE 和 disagreement。
- [x] 完成 fastMRI-brain 24 个 SwinIR examination 的 TTA variance 统一重评；只作单模型局部对比，不跨模型平均。
- [x] 生成 fastMRI-brain SwinIR TTA 与 committee 主方法的 paired difference CI；nAURC 差为 -0.038 [95% CI -0.119, 0.001]。
- [ ] 只有发现完整、合法、病例匹配的预测集时才评价 x2/x8。目前发现的 x2 推理属于另一条正在运行的模型实验，不能提前纳入本文。

## P2：有资源再完成

- [ ] 增加 T1、FLAIR 或其他器官。当前没有接入完整 committee 输出，论文保持 T2 brain MRI 限定。
- [ ] reader study。需要新的伦理、阅片者和统计设计。
- [ ] downstream clinical task。当前 MAE 不得解释为诊断损害。
- [ ] learned error predictor。当前已有文献对比，但没有重新训练所需标签与预注册开发集。

## 结果治理

- [x] IXI、fastMRI-brain、NingXia 均已观察；新增 variant 只能作为 retrospective sensitivity，不能包装成未观察测试集调参。
- [x] 所有固定 dataset--target profile 都必须进入主结果，不删除低表现组合。
- [x] scoring 和 mask API 不接收 ground truth；oracle 仅存在于 evaluation 代码。
- [x] mask variant 改变 MAE 支持域，因此不与默认 mask 做错误的 paired endpoint difference。
- [x] 失败、被中止和被替代的运行写入 `revision_report.md`；未解决证据写入 `unresolved_todos.md`。
- [x] `build_results_registry.py` 和 `validate_icassp_outputs.py` 已通过：10 个主 profile、504 个汇总组、33,672 行病例结果、161 个 manifest、5,631 条唯一 registry 记录。
