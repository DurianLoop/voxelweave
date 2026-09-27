# 本轮复现与保护检查

状态：PASS；UTC 2026-09-14T07:38:57.489324+00:00。

- 417 acquired-response hashes, physical identities, masks, scales and all 13344 independent embedded-vector measurements：PASS；{"max_influence_error": 3.3306690738754696e-16, "max_metric_error": 2.842170943040401e-14}
- All 192 new covariance observations: independent distance-matrix and fixed-odd-response reconstruction：PASS；{"max_observed_error": 6.439222488552332e-10, "max_prediction_error": 2.842170943040401e-14}
- Original two-model inference unchanged; ineligible core values remain NA; .90 SAINT gate unchanged：PASS；{}
- All 22 bound checkpoint hashes unchanged：PASS；{}
- Historical numerical table-row retention, with independently checked acquired table reformatting：PASS；{"reformatted_rows": 0}

逐像素/物理锚嵌入重建独立于原influence查找实现；固定上下文使用完整两两距离矩阵重算。聚类bootstrap沿用冻结统计代码，并用显式重复检查重采样核对前3个draw。不是声称统计软件实现完全独立。
原HAT/SwinIR数值保留其旧完整原数组复现记录，本轮再断言原数值和家族不变；不冒称重训或重新计算全部111个训练配置。
扩展相位的数值表来自新NPZ与原目标/实际acquired mask。完整输出一致性与随机状态核验保存在outputs/phase_v2_validation.json；ArSSR最初失败记录未删除。

编译：[{"document": "cvpr", "success": true, "pages": 9, "issues": [], "bytes": 534671}, {"document": "supplement", "success": true, "pages": 36, "issues": [], "bytes": 1012755}]