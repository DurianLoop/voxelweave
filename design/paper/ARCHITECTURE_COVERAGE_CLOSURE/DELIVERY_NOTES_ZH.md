# 最终交付与验收补记

本轮只完成附件限定的 CVPR 架构覆盖闭环，科学扩展到此停止。

## 论文和完整记录

- [更新主文 PDF](revised_manuscript/main.pdf)：8 页正文，1 页参考文献。
- [更新补充 PDF](revised_manuscript/supplement.pdf)：36 页。
- [详细中文报告](ARCHITECTURE_COVERAGE_CHANGELOG.md)；[主张—证据矩阵](UPDATED_CLAIM_EVIDENCE_MATRIX.md)。
- [13 模型资格审计](MODEL_EVIDENCE_ELIGIBILITY.md)；[五核心影响实验](FIVE_ARCH_ACQUIRED_ONLY_INFLUENCE.md)；[八模型相位敏感性](EXPANDED_PHENOMENON_BREADTH.md)。
- [最终版面核验](VISUAL_REVIEW.md)；[独立复算记录](REPRODUCTION_CHECK.md)。
- 论文源码与图表包：`CVPR_ARCHITECTURE_COVERAGE_REVIEW_PACKAGE.zip`，包含可达 LaTeX、图表、主文和补充 PDF，不包含临床数组及私有源清单。
- 原稿快照：`original_snapshot/manuscript/`。CVPR 入口更新前逐文件对照该快照；更新文件及前后哈希记录于 `outputs/installed_files.json`。最终文件清单为 `DELIVERY_MANIFEST.json`。

## 验收证据

新 SAINT：417 份原始响应文件，13,344 条非自身上下文/幅度观察；另有 12 份协方差文件、192 条观察。八非核心模型：1,112 份相位预测文件，16,680 条逐平面结果、48 行汇总。输入、原始响应与所有结果保留可追踪记录。

独立锚空间向量重算最大影响差为 3.33e-16；独立协方差距离矩阵重算最大观察差为 6.44e-10；另一种共同/差分误差公式复算相位结果，最大逐像素差为 2.22e-16，最大汇总差为 1.67e-16。bootstrap 仍使用冻结实现，并非声称全部统计软件独立重写。

`outputs/final_protection.json` 记录 7,349 项保护检查通过。`outputs/delivery_checks.json` 进一步沿实际 LaTeX 引用图遍历：原 23 个可达源码仍全部可达，新稿为 25 个；除按真实结果扩展的两张报告表外，15 个文件中的 580 行数值表内容保持不变。两张扩展表的 10 条核心模型/队列记录与结果 CSV 核对通过；NA 没有被历史数值填入。

两份最终 PDF 都重新编译并完成视觉检查。验收脚本现在检测重复标签，修复了原新旧影响表共享标签导致的错误引用。主文表格字号放大，完整报告卡放入补充，避免表格单独挤出正文页数。没有压缩正文字号或删除负结果。

## 解释边界补记

13 个模型都有相位接口和输出记录；其中八个新增模型采用同一输出的重复作为共享对照，shared O=0 属于构造事实。因此本轮不能声称新增了八次独立机制验证。Res-SRDiff 的 RNG 抽样索引还依赖相位；相同初始种子不保证同一物理目标获得相同采样噪声，其差异包含这一混杂。正文覆盖表、补充第 5 节及本报告均需结合这些限制理解。

本轮保留 HAT/SwinIR 原有多重比较家族，SAINT 使用结果计算前冻结的独立扩展家族：影响端点各覆盖两队列，协方差覆盖四幅度。它不构成跨原研究与扩展研究的共同家族，也不提供五模型的全局同时覆盖。

五个非核心接口仅记“可用但未运行”，不能作为已通过稳定性或机制验证计数。ArSSR 的双锚适配器尚未完成验证，其代码与内部 CycleINR 有共同谱系；13 个实现名称不代表 13 个结构独立家族。

历史 SAINT 空结果、I3Net/CycleINR 历史稳定性失败、原 126.4% 最坏局部近似误差、fastMRI 排名不确定性、guard 负结果和预算敏感性仍有效。NingXia 与 fastMRI 的真实资料仍标注 NEEDS HUMAN CONFIRMATION。其余投稿风险见完整报告。本地证据无法给出可信的 80% 接收概率。

## 重建顺序

保留现有冻结记录，**不要再次运行 setup.py**。从 `D:/MRI` 使用 `D:/conda/envs/MRI/python.exe -B` 执行相关脚本：数值复算见 `REPRODUCIBILITY.md`；稿件生成 `scripts/revise_paper.py` 会自动调用 `polish_layout.py`，再执行 `build.py`、`render.py`、`delivery_checks.py` 和 `write_reports.py`。完整科学复核另包括 `reproduce_closure.py` 与 `verify_expanded.py`。

`finalize.py --install` 是一次性入口更新操作：它要求更新前文件仍匹配原快照，不能在已更新入口上重复执行。安装完成后的交付核验另使用 `verify_delivery.py`，不会再次修改入口。MiKTeX/Poppler 在本环境需通过正常审批访问已有用户缓存；先前审批额度拒绝已由本次正常重试解除，没有绕过审批。
