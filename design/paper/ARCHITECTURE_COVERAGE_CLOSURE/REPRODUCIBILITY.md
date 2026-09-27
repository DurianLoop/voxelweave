# 复现与文件入口

工作目录 D:/MRI，Python D:/conda/envs/MRI/python.exe，使用 -B 防止在受保护代码路径写缓存。

已冻结协议 PROTOCOL.md；旧原数组清单绑定 FINAL_SUBMISSION_PREPARATION/ARRAY_FREEZE_MANIFEST.json。SOURCE_MANIFEST.json 绑定来源与原稿快照；model_registry.json 是22个使用权重，不是所有候选checkpoint的总计。

CPU重新计算：依次运行 scripts/analyze_core.py、scripts/analyze_expanded.py、scripts/eligibility.py、scripts/revise_paper.py、scripts/reproduce_closure.py、scripts/build.py、scripts/write_reports.py。analyze_core 读取原观察表，reproduce_closure 从原始响应独立验证它；analyze_expanded 直接读新相位NPZ。

GPU推理（已有输出无需再跑）：core_acquired.py；通过IXI稳定性后 saint_covariance.py。expanded_phase.py 为首版冻结wrapper路径，ArSSR首病例精度检查失败记录保留。validate_phase_v2.py 验证坐标/RNG等价，全部通过才允许 expanded_phase_v2.py。该脚本复用已完整保存并有metadata的输出。不要再次运行setup.py覆盖当前冻结记录。

模型来源、native指标路径、确切信息合同在 MODEL_EVIDENCE_ELIGIBILITY.csv/.md。新响应、协方差和相位数组与所有哈希在最终输出清单（实际数量以清单为准）。临床原数组不放入LaTeX交付ZIP，不对外发布。

LaTeX源码在 revised_manuscript；原稿在 original_snapshot/manuscript；经最终检查后仅更新 CVPR/CVPR_ARCH_GENERALIZED/PAPER 的相关文件。TMI与旧交付包未修改。数据伦理/使用授权仍由作者提供真实资料。
