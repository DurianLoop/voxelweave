# 007/009/010七系列来源与标签联合资格结果

本批已完成固定7系列、527原DICOM头、全部7官方标签的检查及独立复核。6系列/3开发患者通过原生头与整数label-grid资格；007 MPR保留拒绝。没有新MR数组解码、模型推理、Dice或独立患者确认。

[原合同](MC_RC_007_010_SOURCE_AND_LABEL_EXECUTION_PLAN_2026-10-02.md)、[头索引](literature/source_cache/mc_rc_007_010_native_headers_2026-10-02/attempt_01.json)、[标签结果](experiments/mc_rc_007_010_native_label_gate/attempt_01.json)、[独立原头/标签复核](experiments/mc_rc_007_010_native_label_gate/independent_raw_geometry_grid_verification.json)。

| 患者/系列 | 标签前景体素 | grid角点误差mm | 联合资格 |
| --- | ---: | ---: | --- |
| 007 / _T2_MPR cor | 3613 | 0.002183 | 拒绝：MPR |
| 007 / _T2_FIESTA-C | 1077 | 0.002049 | 通过 |
| 009 / _T2_FIESTA-C | 136965 | 0.001385 | 通过 |
| 009 / _T2_(TRIGEMINAL) t2_ci3d_tra_iso | 314183 | 0.000741 | 通过 |
| 010 / _T2_3D FIESTA Hi Res | 206411 | 0.004037 | 通过 |
| 010 / _T2_T2_3D_DRIVE AX | 913 | 0.001641 | 通过 |
| 010 / _T2_FIESTA-C | 2655 | 0.000553 | 通过 |

七条实际MR ZIP传输共134,734,262 bytes，API FileSize的261,941,288 bytes不是实际传输。新标签提取ZIP payload 2,308,969 bytes，名义数组总615,471,104 bytes，全部先核预算再用≤32MB slab读取。各标签finite、binary及原生整数grid均通过；MPR拒绝来自原生采集证据，标签grid正确不会消除该拒绝。

独立复核实际重新读全部527头，以全矩阵lstsq重建IPP affine、固定4-plane slab核7标签，反解signed整数grid/角点/extent、核官方CSV/完整artifact联结和ZIP成员hash。errors=[]。这是独立来源实现复核，不是新的科学确认队列。

截至此阶段三批24系列中15合格、9拒绝/pending，001/002/004/005/006/007/009/010共8位开发患者全部合格时间点纳入[覆盖诊断](MC_RC_LABEL_ANCHOR_VISIBILITY_RESULT_2026-10-03.md)。不把多时点当独立人数，不能按覆盖/性能删系列；下一新MR读取和表征实验见[准备](MC_RC_NEW_VISIBLE_REPRESENTATION_PREPARATION_2026-10-03.md)。
