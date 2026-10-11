# 独立坐标计算修复，门槛不变

第一版verify_full_geometry_support.py真正7011eb exit1：前两patch全部体素核验通过，第三patch坐标3e-12断言失败。原脚本和full_support_attempt01 receipt保留，不标为38patch成功。

原因待定量核：以physical(e_i)−physical(0)取仿射线性部分会先求带pivot偏移的大坐标再相减，单位基向量差的浮点误差被127体素跨度放大。V2改为直接旋转physical基向量，origin=pivot−A×pivot；数学变换、sampling语义、fullFOV、二值阈值1−1e-9、概率3e-6、坐标3e-12与零二值差均不改。

准备器固定原源SHA，仅替换该函数、输出attempt02和增加绑定来源，生成一个实际可审阅的新脚本；不得覆盖原失败。记录旧/新oracle全38patch的误差诊断后执行V2。即便V2通过也仅是支持mask资格，无新增患者医学效果。
