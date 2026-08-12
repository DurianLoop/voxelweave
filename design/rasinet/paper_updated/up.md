你现在进入 Goal / Autonomous Execution 模式。

请在当前最新 ICASSP regular/extended 论文和实验代码基础上，完成一次“跨插值倍率泛化 + target-specific 直接验证 + paired statistical comparison”的完整扩展。

目标是将当前模拟 Overall 约 3.8/5 提升至接近或达到 4.0/5。

不要只输出建议。必须：

1. 审计现有 ×2、×4、×6 数据和预测；
2. 修改实验代码；
3. 真实运行实验；
4. 自动生成表格和图；
5. 修改 regular 和 extended LaTeX；
6. 编译并检查最终 PDF；
7. 输出完整 ZIP。

==================================================
一、已有条件与本轮目标
==================================================

当前论文研究：

Target-to-Committee Disagreement for Ground-Truth-Free
Reliability Ranking of MRI Slice Interpolation

当前主实验为 factor ×4，包括：

- IXI T2，n=115；
- fastMRI-brain T2，n=24；
- NingXia T2，n=22，8-fold out-of-fold；
- I3Net、HAT、SwinIR；
- IXI 额外包含 ACSI；
- Linear、Cubic 作为 analytical members；
- target-specific median disagreement；
- case Spearman；
- pixel correlation；
- nAURC；
- RRR；
- mask、normalization、committee、TTA、cost 和 shared-error 分析。

现在工作区还应包含：

- fastMRI-brain T2 的 ×2 和 ×6 训练/预测结果；
- NingXia T2 的 ×2 和 ×6 训练/预测结果；
- 现有 ×4 结果；
- 每个倍率的 ground truth；
- 可能存在的完整 reconstruction fidelity 结果，包括 PSNR、SSIM、MAE、MSE 和 NCC；
- 多种模型的预测输出。

本轮完成三项主要增强：

A. Cross-scale generalization：
在 fastMRI 和 NingXia 上评估 ×2、×4、×6。

B. Matched-target specificity：
证明 target-specific score 更对应被评分目标模型自身的误差，而不只是反映病例总体难度。

C. Paired statistical comparison：
用配对 bootstrap 明确比较核心 score 和 baseline。

==================================================
二、先完成数据和预测审计
==================================================

创建：

cross_scale_audit.md

自动定位并记录每个 dataset × scale 的：

- dataset；
- scale；
- case IDs；
- ground-truth path；
- observed sparse input；
- I3Net prediction；
- HAT prediction；
- SwinIR prediction；
- ACSI prediction，如存在；
- Linear；
- Cubic；
- 其他方法预测，如存在；
- volume shape；
- affine；
- orientation；
- intensity range；
- generated-slice indices；
- training fold；
- test/out-of-fold status。

至少审计：

fastMRI：
- ×2；
- ×4；
- ×6。

NingXia：
- ×2；
- ×4；
- ×6。

IXI：
- 保留 ×4；
- 不虚构不存在的 ×2 或 ×6。

对每个 dataset × scale 输出：

1. 总病例数；
2. 所有方法共有病例数；
3. 缺失病例；
4. 重复病例；
5. shape mismatch；
6. affine mismatch；
7. orientation mismatch；
8. non-finite prediction；
9. intensity range；
10. 是否真正 out of fold；
11. 不同倍率是否使用同一批病例；
12. 不同模型是否使用同一 ground truth。

必须建立：

common_case_manifest.csv

字段至少包括：

dataset, scale, case_id, fold, target_model,
prediction_path, ground_truth_path, input_path,
shape, affine_hash, intensity_min, intensity_max,
is_out_of_fold, is_complete

任何不完整 profile 不得静默进入实验。

==================================================
三、将 Method 从 factor-four 泛化为任意倍率
==================================================

当前论文中不能继续写死：

Zg = {z : z mod 4 != 0}

改为一般插值倍率 r。

设观测锚点索引为：

Z_obs^(r)

生成切片索引为：

Z_gen^(r) = Z \ Z_obs^(r)

如果实际采样规则是等距锚点，可以写：

Z_obs^(r) = {z : z mod r = 0}

Z_gen^(r) = {z : z mod r != 0}

但必须根据真实代码确认边界和起始索引，不得默认所有数据都从 z=0 开始。

定义：

G_r = {i : i_z ∈ Z_gen^(r)}

所有 score、mask、MAE 和 pixel correlation 都只在 G_r 上计算。

将病例 score 改写为：

s_m^(r) =
sum_{i∈G_r} M_m^(r)(i) U_m^(r)(i)
/
sum_{i∈G_r} M_m^(r)(i)

Method 中增加一句：

“The formulation is independent of the interpolation factor; the factor only determines the generated support G_r.”

同时说明：

1. ×2、×4、×6 使用相同的 target-exclusion 原则；
2. ground truth 仍不参与 scoring；
3. 不同倍率的 score 数值尺度可能不同；
4. 因此跨倍率比较使用：
   - Spearman；
   - nAURC；
   - RRR；
   而不是直接比较 raw score；
5. MAE 只能在相同 dataset 和强度表示下比较；
6. 不同倍率必须分别形成 review queue。

更新全部代码，移除任何 hard-coded “4”：

- generated index；
- anchor index；
- mask propagation；
- slice selection；
- stress-test support；
- evaluation；
- plotting；
- configuration。

增加参数：

--scale 2
--scale 4
--scale 6

配置示例：

configs/fastmri_x2.yaml
configs/fastmri_x4.yaml
configs/fastmri_x6.yaml
configs/ningxia_x2.yaml
configs/ningxia_x4.yaml
configs/ningxia_x6.yaml

==================================================
四、冻结跨倍率 primary committee
==================================================

跨倍率实验必须避免 committee composition confounding。

首先计算 fastMRI 和 NingXia 在 ×2、×4、×6 上都存在的模型交集。

优先 primary intersection：

- I3Net；
- HAT；
- SwinIR；
- Linear；
- Cubic。

对目标模型 m，committee 为上述集合中除 m 外的所有成员。

例如 target=I3Net：

C_I3Net =
{HAT, SwinIR, Linear, Cubic}

要求：

1. ×2、×4、×6 使用完全相同的模型身份集合。
2. 不能在某个倍率加入额外模型、另一个倍率不加入，然后直接比较。
3. 如果某个共有模型的预测缺失：
   - 使用所有倍率共有的最大模型交集；
   - 在 audit 中记录；
   - 不得按实验表现选择成员。
4. ACSI 仅保留在 IXI ×4 原主实验中。
5. 其他方法如 ACTVT、Res-SRDiff、ArSSR、CycleINR、ResUNet、Pix2PixGAN、SAINT 等：
   - 只有在每病例预测真实存在；
   - case 对齐；
   - ×2/×4/×6 均存在；
   才能加入独立的 extended committee-diversity 实验。
6. 不要根据 PSNR/SSIM/MAE 表选择 committee。
7. reconstruction fidelity 表只能作为背景描述或 supplementary 结果。

==================================================
五、运行跨倍率 reliability 实验
==================================================

对以下 6 个 dataset-scale profile 运行完整 primary protocol：

fastMRI：
- ×2；
- ×4；
- ×6。

NingXia：
- ×2；
- ×4；
- ×6。

每个 profile 对以下 target 分别评分：

- I3Net；
- HAT；
- SwinIR。

总计至少：

2 datasets × 3 scales × 3 targets = 18 个固定结果。

每个固定结果报告：

1. n cases；
2. mean reconstruction MAE；
3. foreground Pixel rz；
4. Case Spearman ρ；
5. 95% bootstrap CI；
6. Kendall τ；
7. nAURC；
8. 95% bootstrap CI；
9. RRR25；
10. RRR50；
11. RRR75；
12. MAE50；
13. AUROC/AUPRC，secondary；
14. post-hoc score runtime。

使用：

- 2,000 paired case-bootstrap replicates；
- 固定 seed；
- 同一 dataset 的不同 scale 尽量复用相同 case bootstrap identities；
- 如果 scale 之间 case set 完全相同，可以进行 paired cross-scale comparison；
- 如果病例集合不同，只能分别报告，不得声称 paired difference。

输出：

cross_scale_primary_results.csv
cross_scale_bootstrap.csv
cross_scale_summary.tex

==================================================
六、跨倍率主要研究问题
==================================================

不要把正文组织成大量 RQ 标题，但实验应回答以下问题。

1. 随着倍率从 ×2 到 ×6，重建误差是否增加？

报告每个 dataset 和 target 的 foreground MAE。

2. 即使绝对重建难度增加，病例风险排序是否保持？

主要观察：

- Case ρ；
- nAURC；
- RRR50。

3. score 是否在困难倍率 ×6 仍然有用？

重点报告：

- ×6 的 CI；
- ×6 相比随机审核的 RRR；
- 是否仍位于 random 和 oracle 之间。

4. 结果是否跨 fastMRI 和 NingXia 保持？

不要要求数值完全一致。
只判断 ranking utility 是否具有相同方向。

5. 不要因为 ×2、×4、×6 中某一个结果较差而删除。

==================================================
七、生成跨倍率图表
==================================================

生成一个紧凑的 cross-scale figure。

推荐：

Figure X:
Cross-scale reliability on fastMRI and NingXia.

布局：

第一行：
- fastMRI Case Spearman vs scale；
- fastMRI nAURC vs scale；
- fastMRI RRR50 vs scale。

第二行：
- NingXia Case Spearman vs scale；
- NingXia nAURC vs scale；
- NingXia RRR50 vs scale。

或者更紧凑：

Panel A:
Case Spearman by scale，分别画 fastMRI 和 NingXia。

Panel B:
nAURC by scale。

Panel C:
RRR50 by scale。

每个 target 使用不同 marker。
置信区间使用 error bars。
不要使用过多颜色。
保证灰度打印可区分。

另外生成一张 compact table：

Dataset | Scale | Mean MAE | Mean Case ρ | Mean nAURC | Mean RRR50

这里的 mean 是对固定 target 平均。
完整 per-target 结果放 extended paper。

Regular paper 只保留：

- 一个紧凑的 cross-scale 图；
- 或一个六行 compact table。

为了腾出空间：

- 将 qualitative MRI figure 移至 extended；
- 或将详细 sensitivity table 移至 extended；
- 不删除主结果表和 risk–coverage 图。

==================================================
八、使用 reconstruction fidelity 表
==================================================

现有表包含：

- IXI-T2 ×4；
- fastMRI-brain-T2 ×4；
- NingXia-T2 ×4；
- PSNR；
- SSIM；
- MAE；
- MSE；
- NCC；
- 多种 classical 和 neural methods。

完成以下工作：

1. 找到生成该表的原始 CSV，而不是从截图 OCR。
2. 验证所有数值和模型名称。
3. 检查每个方法是否有 per-case prediction。
4. 不使用平均性能选择 primary committee。
5. 在 extended paper 中加入完整 reconstruction fidelity table。
6. 在 regular paper 中最多写一句：

“The committee spans analytical, convolutional, transformer, and interpolation-specific models with substantially different reconstruction fidelity.”

只有真实模型组成支持时保留。

7. 可以分析 reconstruction quality 与 reliability contribution 的关系：

- 模型平均 MAE；
- 作为 committee member 被移除后的 ΔnAURC；
- 成员质量是否等于成员价值；
- 高 fidelity 模型是否总是最有用的 committee member。

该分析只作为 extended exploratory analysis。

8. 不要得出：

“PSNR 越高的模型越适合作为 committee member”

除非统计结果明确支持。

==================================================
九、Matched-target specificity 分析
==================================================

这是本轮用于增强技术贡献的核心实验。

对于同一个 dataset × scale 和 target score s_m，计算它与所有目标模型真实误差的关联。

例如存在 I3Net、HAT、SwinIR：

构造 3×3 correlation matrix：

行：
- score for I3Net；
- score for HAT；
- score for SwinIR。

列：
- true MAE of I3Net；
- true MAE of HAT；
- true MAE of SwinIR。

元素：

R_{m,b} = Spearman(s_m, E_b)

其中：

- 对角线 R_{m,m} 是 matched-target correlation；
- 非对角线是 mismatched-target correlation。

每个 dataset × scale 都计算一个 matrix。

定义：

Matched advantage =
mean_m R_{m,m}
-
mean_{m≠b} R_{m,b}

使用 paired case bootstrap 对 matched advantage 给出：

- point estimate；
- 95% CI。

同时计算：

1. 对角线超过同一行非对角线均值的 target 数量；
2. score 指向病例内最高误差模型的 top-1 accuracy：
   argmax_m s_m
   是否等于
   argmax_m E_m；
3. 每病例跨模型 Kendall/Spearman：
   corr_m(s_m, E_m)
   作为 secondary；
4. target-invariant all-output spread baseline：
   同一个 spread score 无法区分 target identity。

必须明确区分两个 baseline：

A. All-output spread：

V(i) = std_{b∈B} yhat_b(i)

对 target identity 不变。

B. Target-excluded committee spread：

V_m(i) = std_{b∈C_m} yhat_b(i)

会随 target 变化。

Matched-target 对比优先使用 A，因为它真正是 target-invariant baseline。

输出：

matched_target_matrix.csv
matched_target_bootstrap.csv
matched_target_heatmap.pdf

Heatmap：

- 行是 scored target；
- 列是 error target；
- 每格标 Spearman；
- 对角线加框；
- 每个 dataset-scale 可单独画；
- regular paper 只放一个汇总 heatmap 或 matched advantage 表；
- extended 放完整 6 个 matrix。

结果解释规则：

1. 如果对角线普遍高于非对角线：
   可以写 target-specific score preferentially tracks its named target。
2. 如果优势很小：
   必须诚实写 score also captures shared case difficulty。
3. 如果某些 profile 无优势：
   不得隐藏。
4. 不通过选择数据集或倍率制造优势。
5. 该实验结果不能反向用于修改 score。

==================================================
十、Paired statistical comparison
==================================================

使用相同病例 bootstrap indices 比较以下方法。

Primary comparisons：

1. Median target-to-committee vs Mean target-to-committee。
2. Median target-to-committee vs all-output shared spread。
3. Median target-to-committee vs target-excluded committee spread。
4. Full frozen committee vs pre-specified neural-only committee。
5. Full frozen committee vs analytical-only committee。
6. Committee score vs TTA：
   仅在相同 fastMRI SwinIR 病例和对应倍率上比较。

对每个固定 profile 报告：

ΔnAURC = nAURC_methodA - nAURC_methodB

约定：

- ΔnAURC < 0：A 更好；
- ΔnAURC > 0：B 更好。

输出：

- point difference；
- 95% paired bootstrap CI；
- win/loss/tie；
- profile count；
- aggregate fixed-profile mean；
- 不进行数据集加权混淆。

创建一个 forest plot：

纵轴：
- 每个 dataset / scale / target profile；
- 最后一行 aggregate。

横轴：
ΔnAURC。

至少生成：

A. Target-specific median vs all-output spread。
B. Median vs mean。

TTA 单独做局部 comparison，不混入全 profile aggregate。

Multiple comparison：

- exploratory comparisons 使用 Holm correction；
- 或只报告 CI，不宣称正式显著性。

不要因为某方法没有显著获胜而删除。
如果 median 与 mean 无显著差异，结论写成：

“The reliability signal is not specific to the median aggregator; the contribution lies in target conditioning, self-exclusion, and selective-review evaluation.”

==================================================
十一、跨倍率 paired comparison
==================================================

如果 fastMRI 的 ×2、×4、×6 使用完全相同病例，计算：

- Δρ(×4−×2)；
- Δρ(×6−×4)；
- ΔnAURC(×4−×2)；
- ΔnAURC(×6−×4)；
- ΔRRR50。

NingXia 同理。

这些比较主要回答：

- 倍率变难时 ranking 是否显著恶化；
- ×6 是否仍保持实际 review utility。

不要将“差异 CI 包含零”解释为完全等价。
使用：

“no conclusive degradation was observed”

而不是：

“performance is identical”。

==================================================
十二、修改 regular paper
==================================================

保持：

- 4 页技术内容；
- 第 5 页仅 references / 合规允许内容。

推荐 regular 结构：

Page 1：
- Abstract；
- Introduction；
- Method 前半；
- compact pipeline figure。

Page 2：
- generic scale-r Method；
- target-specific score；
- common-mode invariance；
- selective review；
- experimental protocol。

Page 3：
- 原 ×4 主结果表；
- risk–coverage；
- 简化 committee/score 结果。

Page 4：
- cross-scale figure/table；
- matched-target summary；
- paired comparison summary；
- TTA/cost；
- limitations；
- conclusion。

为了容纳新增内容：

1. qualitative three-case MRI figure 移到 extended paper；
2. mask/normalization 完整表移到 extended；
3. regular 只用一句或一行总结 sensitivity；
4. AUROC/AUPRC 只留一句；
5. cost 保留一行；
6. 不删除 bootstrap CI；
7. 不缩小到不可读字体；
8. 不使用违规负间距。

Abstract 增加跨倍率结果，格式类似：

“Cross-scale evaluation on fastMRI-brain and NingXia at factors two, four, and six shows that the review signal [remains stable / degrades at factor six / varies by cohort — 根据真实结果填写].”

不得提前写结论。

Contribution 更新为：

1. Target-specific ground-truth-free reliability ranking。
2. Selective-review protocol and common-mode identifiability boundary。
3. Multi-cohort and multi-scale evaluation with matched-target and paired comparator analyses。

==================================================
十三、修改 extended paper
==================================================

Extended paper 保留完整内容：

- ×4 三数据集主结果；
- ×2/×4/×6 fastMRI；
- ×2/×4/×6 NingXia；
- full reconstruction fidelity table；
- all matched-target matrices；
- full forest plots；
- all committee subsets；
- mask；
- normalization；
- TTA；
- stress test；
- qualitative failures；
- runtime；
- AUROC/AUPRC；
- reproducibility。

增加章节：

5.X Cross-scale generalization

5.X Target-specificity beyond case difficulty

5.X Paired comparator analysis

Discussion 中明确回答：

1. ranking 是否跨倍率稳定；
2. reconstruction difficulty 增大时 score 如何变化；
3. score 有多少是 target-specific；
4. 有多少是 shared case difficulty；
5. median 是否必要；
6. committee 与 TTA 的适用边界。

==================================================
十四、结果治理和防止 test-set selection
==================================================

更新：

results_registry.csv

增加字段：

- scale；
- common_case_set；
- matched_or_mismatched_target；
- comparator；
- paired_bootstrap_id；
- primary_or_sensitivity。

冻结以下 primary specification：

- common model intersection；
- median target-to-committee；
- all non-target members；
- raw common source-intensity representation；
- 1% target-derived mask；
- 2,000 bootstrap；
- seed fixed。

不能根据 ×2、×4、×6 结果重新选择：

- mask；
- normalization；
- committee；
- score aggregator。

所有新结果属于：

- pre-declared cross-scale evaluation；
- 或 retrospective sensitivity。

必须在论文中说明。

==================================================
十五、代码测试
==================================================

增加 unit tests：

1. scale=2 generated indices 正确；
2. scale=4 generated indices 正确；
3. scale=6 generated indices 正确；
4. observed anchors 不进入 score；
5. target self-exclusion；
6. common model intersection；
7. matched-target matrix 对角线索引正确；
8. mismatched error 不会进入 deployment score；
9. paired bootstrap 使用相同病例索引；
10. scale case-set mismatch 会触发明确警告；
11. all-output spread 对 target identity 不变；
12. target-excluded spread 可随 target 变化；
13. no ground truth passed to scoring API。

运行：

pytest -q

保存完整日志。

==================================================
十六、最终交付文件
==================================================

至少交付：

1. paper_icassp_regular_multiscale.tex
2. paper_icassp_regular_multiscale.pdf
3. paper_extended_multiscale.tex
4. paper_extended_multiscale.pdf
5. cross_scale_audit.md
6. common_case_manifest.csv
7. cross_scale_primary_results.csv
8. cross_scale_bootstrap.csv
9. matched_target_matrix.csv
10. matched_target_bootstrap.csv
11. paired_comparisons.csv
12. cross_scale_figure.pdf
13. matched_target_heatmap.pdf
14. paired_comparison_forest.pdf
15. reconstruction_fidelity_table.tex
16. updated results_registry.csv
17. test log
18. revision_report_multiscale.md
19. unresolved_multiscale.md
20. 完整 ZIP。

==================================================
十七、最终验收标准
==================================================

只有满足以下条件才算完成：

1. ×2、×4、×6 的 generated support 定义正确。
2. fastMRI 三倍率病例和预测经过审计。
3. NingXia 三倍率病例和预测经过审计。
4. NingXia 每个预测均为 out-of-fold。
5. 跨倍率使用相同模型交集。
6. 不根据测试 PSNR/SSIM/MAE 选择 committee。
7. 18 个 dataset-scale-target profile 全部报告。
8. 所有主要结果有 bootstrap CI。
9. matched-target matrix 真实计算。
10. matched advantage 有 paired CI。
11. all-output spread 定义明确且 target-invariant。
12. paired comparison 使用相同 bootstrap identities。
13. TTA 只在公平可用的 profile 报告。
14. regular 仍为 4+1 页。
15. 新图在 100% PDF 缩放下可读。
16. 没有 Type 3 字体。
17. 没有 TODO、ethics placeholder 或内部指令。
18. 所有数字可追溯到 CSV。
19. 不隐藏负结果。
20. 不夸大跨倍率泛化。
21. 原始版本不被覆盖。
22. ZIP 包可直接在 Overleaf 编译。

==================================================
十八、最终回复
==================================================

完成后汇报：

1. 各倍率实际可用病例数。
2. 各倍率共同模型集合。
3. ×2、×4、×6 的 Case ρ、nAURC 和 RRR50。
4. ×6 是否仍保持 review utility。
5. matched-target advantage 及 CI。
6. median vs mean 的 paired comparison。
7. target-specific vs all-output spread 的 paired comparison。
8. TTA comparison。
9. 哪些结果发生恶化。
10. 是否存在 scale-dependent failure。
11. regular PDF 页数。
12. extended PDF 页数。
13. 模拟 ICASSP 新评分。
14. 所有文件路径。
15. 一条完整复现命令。
16. 最终 ZIP 路径。

现在开始执行。先做数据审计和 common-intersection 冻结，再修改 Method 和运行实验，不要先根据结果调整 committee。