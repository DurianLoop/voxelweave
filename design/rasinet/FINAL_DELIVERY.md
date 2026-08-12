# 最终交付清单

1. 候选方法：132 个原子设计、40 个 score–committee 设计、367 条注册记录。
2. Committee 配置：8 类策略；逐目标执行 self-exclusion。
3. Score/pooling：12 个实际原子 score family、3 类部署 mask 和预先限定的 mean/tail pooling 组合；结构全组合因实测成本过高未完成。
4. Development：IXI ×4；fastMRI-brain ×2/×4/×6。
5. Validation：NingXia ×2/×4/×6，22 个 examination，八折 OOF。
6. Target：I3Net、HAT、SwinIR；原因是三者同时覆盖 IXI 与全部多倍率 profile。
7. Development high-fidelity peers：I3Net、SAINT、SMamba-UNet、Pix2PixGAN；按开发集冻结，目标出现时删除自身。
8. 排除原因：缺少通用 profile、重复设计、筛选排名不足、或结构域全笛卡尔成本过高；全部保留在 registry。
9. Baseline validation：mean/worst nAURC 0.070/0.125，rho 0.901，RRR50 21.8%。
10. Universal validation：0.116/0.207，0.839，19.9%；未迁移。
11. Low-cost validation：0.080/0.166，0.893，21.2%；未证明优于 baseline。
12. Scale-aware：未在观察 NingXia 前冻结，未事后加入 finalist。
13. NingXia ×2/×4/×6 逐 target 结果见 `outputs/optimization/finalist_validation_results.csv`。
14. Universal 相对 baseline：开发 mean nAURC 改善 0.048，验证恶化 0.045；worst-profile 验证恶化 0.082。
15. RRR50：universal 验证较 baseline 低 1.9 个百分点。
16. Matched-target advantage：验证范围 −0.008 至 0.014，未显示稳定 attribution。
17. 成本：low-cost committee size proxy 为 3，其他 finalist 为 4；post-hoc 旧实测 1.18 s/病例，在线模型成本未统一测量。
18. Cross-scale consistency：138 个比较均因 depth/generated-support shape mismatch 不可直接计算。
19. 验证失败 finalist：universal 与 shared-difficulty；未替换或重调。
20. 标题：*Target-to-Committee Disagreement for MRI Slice Review: Selection, Transfer, and Failure Boundaries*。
21. 三项贡献：target-excluded ranking/failure boundary；registered selection protocol；冻结多倍率 transfer failure evidence。
22. 模拟 ICASSP 综合评分：3.8/5，borderline–weak accept。
23. 三大风险：基础 score 简单；NingXia 小且非完全外部；无 reader/downstream 与统一在线成本。
24. 复现：`D:\conda\envs\MRI\python.exe -u -B -m rasinet.run_candidate_optimization --stage development`，随后运行 `--stage validation`。
25. 编译：在 `paper_updated` 执行 `pdflatex ...; bibtex ...; pdflatex ...; pdflatex ...`。
26. ZIP：`paper_updated/paper_icassp_regular_optimized_overleaf.zip` 与 `paper_updated/rasinet_optimization_full_delivery.zip`。

