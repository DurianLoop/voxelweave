# 最终投稿补丁复现

当前主文源文件及PDF：`revised_manuscript/main.tex`、`main.pdf`；补充材料：`supplement.tex`、`supplement.pdf`。本目录是独立补丁，原始材料在 `original_snapshot/`；约93.6 GB的预测/输入/目标等数组原址保全，由 `ARRAY_FREEZE_MANIFEST.json` 逐文件绑定。不要删除或改名其源文件。

## 本地完整复现

在 `D:\MRI` 执行：

```powershell
D:/conda/envs/MRI/python.exe -B design/paper/FINAL_SUBMISSION_PREPARATION/reproduce_main.py --complete
```

只使用CPU，不调用网络模型、不训练、不加入评分公式。脚本依次完成：

1. `scripts/reproduce_arrays.py`：重读322个历史control、966个历史finite-response及695个phase文件；历史CSV只提供已冻结的行键与数值断言目标。
2. `scripts/reproduce_new.py`：重读695个phase、834个acquired-response、24个proposition文件与各自目标/掩膜，独立重建三项主要实验的观察值和bootstrap。
3. `scripts/reproduce_main.py`：从新重建观察表生成历史控制、影响和架构统计，断言旧显示值。部分历史非神经补充结果按原协议和旧表保留，不冒称本轮把所有111项baseline重新训练。
4. `scripts/reproduce_sensitivity.py`：再次独立读取cross-architecture预测/目标/原NIfTI，以另一像素能量公式重算三种支持；独立重建几何资格；输出到 `outputs/independent_sensitivity/` 并断言本轮正式CSV。bootstrap聚合复用固定分析合同，不宣称完全独立的统计软件实现。
5. `scripts/paper_assets.py`：原数组派生观察表 → 主图1/2/3/4、完整Proposition scatter、旧ranking/prevalence补充图、表1/2、主报告卡与54条详细卡。图1始终读同一已冻结实例。
6. `scripts/assert_submission.py`：断言主文数值、图表输入、报告卡NA、稳定性、几何反例、摘要边界与补充的内部项目措辞；生成各项PASS/FAIL。敏感性完整LaTeX表由 `scripts/sensitivity_tables.py` 从正式CSV生成，正式CSV已与独立复算逐列比较。

最终日志为 `outputs/reproduction_run.json` 和 `logs/reproduce_*.log`，各次运行写本目录。`common.py` 特别区分旧输入根 `P` 与新输出根 `PATCH/OUT`，不能把旧目录当成新输出目标。原版旧复现启动器不在本补丁中调用。

## 统计合同与支持区域

本轮协议在敏感性计算前固定。三个支持区域、residue类、最近距离及严格四锚资格均只依据既有定义或索引几何，不能依照效应选取。所有模型对共享检查bootstrap抽样；新敏感性每个cohort/端点/支持区域内校正20对，不声称对整轮所有端点总体校正。家族行使用描述性percentile interval，字段名`simultaneous_low/high`沿用统一CSV结构，其`ci_family`明确标明family percentile，不能误读为模型对同时区间。

`mirror_residue1_minus_residue3` 行中的shared_O/disjoint_O是各条件的residue差，delta_O是两个干预效应的residue差；不是绝对O，不能与support表的shared_O混读。严格四锚fastMRI行标记NA和原因，不填零。详细geometry registry保留全部695目标及实际资格。

## LaTeX与视觉检查

```powershell
D:/conda/envs/MRI/python.exe -B design/paper/FINAL_SUBMISSION_PREPARATION/scripts/build.py
D:/conda/envs/MRI/python.exe -B design/paper/FINAL_SUBMISSION_PREPARATION/scripts/render.py
```

需要既有本机MiKTeX（pdflatex/bibtex）和Poppler（pdfinfo/pdftotext/pdftoppm）。受控环境中这些本机命令需要正常工具审批；上次因使用额度导致的审批失败不是编译错误，已保留中断说明，未通过替代shell绕过。`build_logs/build_audit.json`记录实际页数、编译状态和警告。页面渲染进入独立轮次目录，审阅记录在 `VISUAL_REVIEW.md`。

PDF生成器可能写入创建时间，重复编译二进制hash不必相等；源数组hash、数值断言和可见输出必须一致。源文件环境及最终hash记录于 `outputs/environment.json`、`DELIVERY_MANIFEST.json`。

## 原始证据定位

主数组：`../FINAL_SCIENTIFIC_STRENGTHENING/outputs/{phase_arrays,acquired_responses,proposition_arrays,legacy_control_arrays,legacy_influence_arrays}`；目标/输入在该目录的 `targets/`、`inputs/`。

acquired union既有定义：`../PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/PROTOCOL.md`。反射类分析先例：`../ARCHIVE/PLANS/PLAN11_CLAIM_STRENGTHENING/scripts/p11_matched_geometry_identity.py`。旧数值合同有float32先做差，新cross合同float64先做差，二者不可随意统一。原始same-model清洁控制mask由phase0预测定义，新cross原mask由目标定义，不能混称acquired-only。

旧项目的源文件目录、原始病例ID、访问路径和完整机器清单留在本地追溯材料。公开审稿包仅包含可达LaTeX、图表和必要说明；不包括原MRI数组、原始DICOM或本地临床身份目录。该包不是可自由再分发的数据集，也不能认证尚缺的人类数据许可。


## 原补充材料移出的详细证据路径

`latex
\subsection{Reproducibility and Evidence Map}
The frozen sources are:
\begin{itemize}
\item clean intervention and stable wrong: \path{CVPR/archive/CVPR_UPGRADE/outputs/clean_max_overlap*} and \path{stable_wrong_prevalence.json};
\item analytical ladder/influence: \path{compact_four_anchor_overlap_ladder*} and \path{shared_influence*};
\item neural influence and chain: \path{plan6_neural_shared_influence_confirm3*} and \path{plan6_mechanism_chain*};
\item Anchor-CV/consequence: \path{plan6_anchor_cv_explanation*} and \path{plan6_ixi_x2_consequence*};
\item Plan-7 stability and negative gates: \path{ARCHIVE/PLANS/PLAN07/PLAN7_ACCEPTANCE_OPTIMIZATION/outputs/p7_cvpr_*};
\item exploratory recovered-model-bank breadth audit: \path{ARCHIVE/PLANS/PLAN10_ACCEPTANCE_ITERATION/outputs/p10_*};
\item fixed-rule retrospective same-model densification audit: \path{ARCHIVE/PLANS/PLAN11_CLAIM_STRENGTHENING/outputs/p11_same_model_benefit_*};
\item frozen IXI five-architecture replication and identity swap: \path{ARCHIVE/PLANS/PLAN11_CLAIM_STRENGTHENING/outputs/p11_ixi_clean_*_full.*} and \path{p11_identity_swap_*_full.*};
\item full selection rationale: \path{CVPR/archive/CVPR_RECOVERED/PAPER/EVIDENCE_SELECTION_AUDIT.md}.
\end{itemize}



`
