# 两通道坐标舍入诊断：保留旧严格数值门槛

主资格真实exit0，chunk3e7ef8，43.48189519997686秒。24draw检查/6次fullPATCH合成更新/两臂8tile FOV完整。物理FOV概率与独立functional实现最大误差0，两臂native阈值差异0；dense native误差2.0265579223632812e-6，direct3.2186508178710938e-6。它们通过**事前冻结atol3e-6+rtol1e-5的combined allclose**，但direct不满足旧absolute<=3e-6判据。本补充不把新的相对误差检查冒称旧strict gate成功。

问题待核：差异是否来自torchfloat32回native与理想float64 pixel-center坐标舍入，而非网络/tile/轴次序错误。诊断仍全合成，不访问MRI数据、live权重、GT、validation或confirmation；当前原56FOV脚本及旧strict gate不改。

重新用上一主资格相同固定合成输入/旧synthetic_after1权重/两通道生产FOV，要求native SHA与保存合成npy以及physical SHA与主JSON完全相同。将两个cropped physical probability体积保存为合成数组（不称MRI），便于坐标核验重放。

独立NumPy构造两条**预先同时规定**的坐标解释器，不根据结果挑门槛：A理想float64 `(j+.5)*input_size/output_size-.5` 与8角float64累加；Bfloat32 scale、float32乘/减得到坐标、8角float32权重累加。分别报告和生产float32的最大绝对误差/阈值差异。A应该准确复现上一主资格独立坐标概率；B只有absolute<=3e-6且threshold差异0才记为“float32-coordinate解释器合格”。同physical概率另用torchfloat64映射，与A的未cast float64数组比较，要求absolute<=3e-12、threshold差异0。若任何数值不通过，保存失败，不改原代码/门槛。

保存字段要并列保留original_ideal_coordinate_absolute_gate，float32_coordinate_replay_gate，float64_coordinate_only_gate。前者direct当前预期仍false；后二者通过不能覆盖它。新两通道未来正式评价若需区分坐标实现，须另立事前协议并说明为何比较的舍入精度对应；当前一通道原56FOV不因本合成诊断变更。

CPU4/interop1、float32神经模型（仅坐标核验float64），自身below-normal、600秒、8GB RAM/磁盘余量、新增保存≤25MB、CUDA不初始化。无新训练。只解释数值来源，不评价MRI恢复/病灶效益。
