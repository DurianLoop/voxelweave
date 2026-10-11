# 第6217字段的确定性诊断，原门槛不改

前一turn有实质进展：两篇新主文、原表CPU核验及6441冻结链。当前第一轮实际poll74234得到093916 exit1且无session_id；旧full pipeline成功6216/35904，下一失败case3/raw_pchip/step1868/patch0/throughplane。原source/config/journal/receipt保留，真实terminal已写旧stage的ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json。旧success audit要求exit0，不能冒用。原training29823/035a88仍live1210/2992，不能干预或提前挑分支评分。

失败primitive.enabled=false，pre/shared-post误差均0、binary差0；isolated/full-chain3.814697265625e-6超过固定3e-6。只诊断同一个完整1048576 voxel字段，不删患者/轴/体素，不以ULP/相对误差放宽既定absolute门槛。原max_errors只有success6216的最大值，失败error以failed_field为准。

从冻结case3合法raw-PCHIP观测重建物理cache，对QPATH原input SHA；用已固定failed_field geometry/primitive重建patch，因此无需新增GT读取。核原全FOVresolution两实现一致、gamma和bias分阶段差异、float32/float64统计与恢复运算的影响。小范围数学variant仅探索，不当已过完整资格或患者医学效果。

若有高精度修复，只创建新版本module与新protocol/output，不改原augmentation.py、independent_intensity.py、旧qualify脚本或正在运行训练绑定。先单failed-field+已有合成/真实stress覆盖，再另冻结完整35904 MRI重放才可能训练普通增强；新合格字段不能替代原失败。任何影像变化先记录幅度与来源，不修改现存cache/labels。

CPU1/interop1/低优先级，wall180秒，本diagnostic stage<=2MB、receipt<=100KB、单MRIcache及临时float64数组，不保存影像/新权重。磁盘/RAM各8,000,000,000bytes、原医学评价3MB预留保持。没有神经forward/backward/new updates，确认8人/12series、已见验证及lockedIXI不读取。所有新增innovation，不查询/操作其他PID。
