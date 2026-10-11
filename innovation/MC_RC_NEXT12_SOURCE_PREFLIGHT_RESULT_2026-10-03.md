# 固定12患者、25系列：来源与标签网格结果

25/25官方MR ZIP下载实际exit 0，1,475原始对象，302,254,256传输字节，零自动重试。随后25标签语义/网格检查实际exit 0，独立重读全部1,475头/25标签也exit 0、errors=[]。全部12患者各至少有1个通过序列。

22/25系列通过非像素头资格，21/25通过头+标签网格：015一个DRIVE及031两个DRIVE头阴性；027的T2W_DRIVE_HR Tra头通过，但标签原生网格角点差0.054087070mm，超过原固定0.05mm，拒绝。该差异接近门槛仍不放宽，保留全部原名单与时点。

| 患者 | 序列描述 | 头资格 | 网格角点差mm | 最终源资格 |
| --- | --- | --- | ---: | --- |
| VS-MC-RC-015 | _T2_T2_3D_DRIVE | False | 0.000361853 | 未通过：Missing MR Acquisition Type pending |
| VS-MC-RC-015 | _T2_I.A.C.     * T2 TSE | True | 0.000305690 | 通过 |
| VS-MC-RC-015 | _T2_I.A.C.     * T2 TSE | True | 0.000371512 | 通过 |
| VS-MC-RC-019 | _T2_FIESTA-C | True | 0.001722916 | 通过 |
| VS-MC-RC-019 | _T2_T2_3D_DRIVE AX | True | 0.000804709 | 通过 |
| VS-MC-RC-020 | _T2_t2_spc_tra_iso_0.5 | True | 0.000654520 | 通过 |
| VS-MC-RC-022 | _T2_t2_spc_tra_iso_0.5 | True | 0.000120186 | 通过 |
| VS-MC-RC-022 | _T2_t2_space_tra_iso_ZOOMit | True | 0.001043238 | 通过 |
| VS-MC-RC-022 | _T2_T2_3D_DRIVE AX | True | 0.000285908 | 通过 |
| VS-MC-RC-024 | _T2_t2_spc_rst_tra_p2_iso | True | 0.000102611 | 通过 |
| VS-MC-RC-024 | _T2_t2_spc_tra_iso_0.5 | True | 0.000217945 | 通过 |
| VS-MC-RC-025 | _T2_t2_ci3d_tra | True | 0.000122760 | 通过 |
| VS-MC-RC-025 | _T2_t2_spc_rst_tra_iso_384 | True | 0.002242572 | 通过 |
| VS-MC-RC-025 | _T2_FIESTA-C | True | 0.003500198 | 通过 |
| VS-MC-RC-026 | _T2_FIESTA-C | True | 0.001075681 | 通过 |
| VS-MC-RC-027 | _T2_T2W_DRIVE_HR Tra | True | 0.054087070 | 未通过：label-native grid corner error exceeds fixed 0.05 mm |
| VS-MC-RC-027 | _T2_FIESTA-C | True | 0.000549628 | 通过 |
| VS-MC-RC-028 | _T2_t2 tra 3d-ciss | True | 0.000003145 | 通过 |
| VS-MC-RC-028 | _T2_t2_spc_rst_tra_iso_384 | True | 0.000120830 | 通过 |
| VS-MC-RC-029 | _T2_CISS_3D_AX | True | 0.000129231 | 通过 |
| VS-MC-RC-030 | _T2_t2_spc_tra_iso_0.5 | True | 0.001922565 | 通过 |
| VS-MC-RC-030 | _T2_FIESTA-C | True | 0.000939637 | 通过 |
| VS-MC-RC-031 | _T2_T2_3D_DRIVE | False | 0.000224266 | 未通过：Missing MR Acquisition Type pending |
| VS-MC-RC-031 | _T2_T2_3D_DRIVE | False | 0.000173705 | 未通过：Missing MR Acquisition Type pending |
| VS-MC-RC-031 | _T2_t2_spc_rst_tra_p2_iso | True | 0.000556748 | 通过 |

[25完整CSV](experiments/mc_rc_next12_label_grid/all25_source_qualification.csv)、[标签生产记录](experiments/mc_rc_next12_label_grid/attempt_01.json)、[原始头与下载](literature/source_cache/mc_rc_next12_headers_2026-10-03/attempt_01.json)、[独立重读](experiments/mc_rc_next12_label_grid/independent_all1475_headers_and_25_labels_attempt_01.json)。

标签压缩成员累计6,313,485字节；按32MB分块读取，没有整批驻留。没有解码MR像素，没有导入torch，没有神经网络前向或GPU运行；没有对新患者计算方法效果。

连同上一批011/012/013，固定新增15患者、30系列，24系列源资格通过；患者角色和模型训练身份另审计。资格通过不等于任务能力、方法成功或未见患者科学确认。当前新claim仍0，旧8开发人及旧45队列不升级为确认。
