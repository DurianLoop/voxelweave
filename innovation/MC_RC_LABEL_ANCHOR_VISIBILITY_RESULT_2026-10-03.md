# 四倍抽层标签覆盖：完全隐藏成分不能解释主条件失败

事前固定全部15合格系列、8开发患者、phase0主条件，另全部4phase与6/26连接规则。主phase0在两种规则下均无完全避开观测层的缺层标签成分。四个phase下每个系列的最大标签成分都接触观测层。此前001/005门控失败不能据此归因于完全隐藏病灶。

[合同](MC_RC_LABEL_ANCHOR_VISIBILITY_PLAN_2026-10-03.md)、[逐系列/成分结果](experiments/mc_rc_label_anchor_visibility/attempt_01.json)、[输入hash合同](experiments/mc_rc_label_anchor_visibility/run_contract.json)、[独立label/slab/坐标复核](experiments/mc_rc_label_anchor_visibility/independent_label_phase_verification.json)。

| 患者/系列 | 26连接成分 | 主相位观测前景占有效范围 | 主相位隐藏成分 |
| --- | ---: | ---: | ---: |
| 001 / _T2_I.A.C.     * T2 TSE | 1 | 23.34% | 0 |
| 001 / _T2_I.A.C.     * T2 TSE | 1 | 26.00% | 0 |
| 002 / _T2_Ax 3D FIESTA | 1 | 24.41% | 0 |
| 004 / _T2_t2_spc_tra_iso | 1 | 25.55% | 0 |
| 005 / _T2_3D FIESTA HIGH RESOLUTION | 1 | 25.33% | 0 |
| 005 / _T2_Ax 3D FIESTA | 1 | 24.69% | 0 |
| 006 / _T2_FIESTA-C | 1 | 25.20% | 0 |
| 006 / _T2_t2_spc_rst_tra_p2_iso | 1 | 23.57% | 0 |
| 006 / _T2_t2_spc_tra_iso_384 | 1 | 23.23% | 0 |
| 007 / _T2_FIESTA-C | 1 | 31.94% | 0 |
| 009 / _T2_FIESTA-C | 1 | 25.03% | 0 |
| 009 / _T2_(TRIGEMINAL) t2_ci3d_tra_iso | 1 | 24.92% | 0 |
| 010 / _T2_3D FIESTA Hi Res | 1 | 25.07% | 0 |
| 010 / _T2_FIESTA-C | 2 | 27.08% | 0 |
| 010 / _T2_T2_3D_DRIVE AX | 1 | 22.23% | 0 |

预写相位敏感性：26连接在phase1/2/3各有1个隐藏成分，均来自010 FIESTA-C的同一个48体素成分（约2.967mm³），位于native z=32单plane，并触及column视野边界。不能未经标签语义检查把它称独立临床病灶或漏诊，也不能删除后另报成功。6连接在phase1/2/3各有2个，主要成分仍全部接触观测。主相位结论保持。

独立验证errors=[]，从全部原标签slab显式映射并检查787,030前景坐标、所有native plane counts、15×4×2的phase/成分计数、bbox及6对26分割细化关系。连通生成本身仍来自SciPy，未独立重写算法。全部标签来源属于开发，独立患者科学确认仍0。

观测前景比例只是体素几何比例，不是实际MRI病灶可视性或检测概率；采集厚度/profile不由spacing确定。该反证不否定其他疾病的薄层检出收益，也不保证边界可由稀疏输入恢复。下一步先测理想观测区域传播，再考虑稀疏MR导出的预测区域/边界特征，保留强对照与未见确认。
