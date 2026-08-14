# CVPR 稿件分支说明

| 分支 | 角色 | 建议用途 |
|---|---|---|
| `CVPR_RECOVERED/` | 从早期材料恢复的机制稿 | 历史参考 |
| `CVPR_UPGRADE/PAPER/` | Plan 6 升级稿 | 历史实验整合版本 |
| `CVPR_UPGRADE/PAPER_FINAL/` | Plan 7 风险优化版 | Plan 8/9 前的冻结候选 |
| `CVPR_ARCH_GENERALIZED/PAPER/` | Plan 9 架构族泛化版 | **当前最新科学候选** |

当前入口：

- [Plan 9 CVPR 主文源码](CVPR_ARCH_GENERALIZED/PAPER/main.tex)
- [Plan 9 CVPR 主文 PDF](CVPR_ARCH_GENERALIZED/PAPER/main.pdf)
- [补充材料源码](CVPR_ARCH_GENERALIZED/PAPER/supplement.tex)
- [补充材料 PDF](CVPR_ARCH_GENERALIZED/PAPER/supplement.pdf)
- [最终构建审计](CVPR_ARCH_GENERALIZED/PAPER/FINAL_BUILD_AUDIT.md)
- [最终审稿模拟](CVPR_ARCH_GENERALIZED/PAPER/FINAL_REVIEW_SIMULATION.md)

最新分支把物理测量依赖、局部误差对齐/抵消和架构族证伪作为中心。它明确保留不利结果：新架构中只有 SAINT 通过全部影响稳定性门槛，且其固定计数效应区间跨零。该稿不能写成普适影响度方法，也不能在未处理与 TMI 的科学重合前直接并行投稿。
