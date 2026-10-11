# 训练内已知 profile 小试：留出观测选核失败

**结果：当前固定规则未通过可辨识性诊断。** [推理前方案](KNOWN_PROFILE_HOLDOUT_PILOT_PLAN_2026-10-01.md)只使用 IXI seed3407 的前三名 **train** T2 患者 IXI013/015/017，未访问 val/test 图像、GPU 或运行中的训练。每人的原生体积缩到 32x32 面内，在 z 轴合成 `sigma=0/1.5` 两种已知高斯模糊，分别每 4/6 个原生层采样；在每种条件下从真实模拟观测锚点留出约三分之一，比较假设 `sigma=0/1.5/3` 的同一二阶平滑线性逆解。选择只依据留出观测 MSE，最后用全部已采观测重拟合并在**非锚点原生层**测真实误差。

| 冻结诊断 | 结果 |
|---|---:|
| 患者 / 完成条件 / 候选记录 / 失败 | 3 / 12 / 36 / 0 |
| 留出观测选到设定真核 | 5/12 |
| 其中真实 `sigma=1.5` 的选中率 | **0/6** |
| 相对固定 `sigma=0`，缺层 MSE 改善 / 持平 / 恶化 | **0 / 10 / 2** |
| 真实核相对固定核确能降低缺层 MSE 的条件 | 4/6 个真实 `sigma=1.5` 条件 |

最明显的反例是 IXI017、stride 4：真实 `sigma=0` 时，留出规则选 `sigma=3`，全观测重拟合后的目标 MSE 从固定核约 `0.000493` 增至 `0.005934`；真实 `sigma=1.5` 时同样选 `3`，从 `0.000452` 增至 `0.001860`，而设定真核约 `0.000321`。另四个真实模糊条件中设定核优于固定核，但留出观测规则都选了 `0`，没有兑现 oracle 空间。留出 MSE 和最终目标 MSE的训练观测数不同，不能把两者的绝对值相减；这里比较的是**候选排序是否对齐**。

[逐条件](experiments/known_profile_holdout_pilot/per_condition.csv)、[逐候选](experiments/known_profile_holdout_pilot/per_candidate.csv)、[运行摘要](experiments/known_profile_holdout_pilot/summary.json)保存全部结果。[CPU 实现](experiments/known_profile_holdout_pilot.py)记录方案、脚本、split 和三个源图像的 SHA-256；[独立只读复核](experiments/verify_known_profile_holdout_pilot.py)对 train-only 身份、12 条件/36 候选、所有最小分数选择和汇总返回 `PASS`。额外直接检查高斯前向矩阵对随机 120x8 信号与 `gaussian_filter1d` 的最大差为 `4.44e-16`。

这否定的是**本次 32x32、三患者、两个模糊宽度、两个间距、固定 `lambda=0.03` 和特定留出设计**的 profile 选择规则，不证明一般 profile 不可辨识，也不能外推到真实 RF slice response。由于高斯退化叠加在原生已采切片上，目标仍是该来源的原生响应；没有真实薄层 GT。小样本来自训练集，不能给置信区间或投稿结论。对这三个病例继续调候选核/正则/留出模式会把它们变成开发集；若重启，需要另写新方案并用未碰的病例，同时比较同观测预算的固定核、已知核及独立估核方法。当前不投入新模型训练。
