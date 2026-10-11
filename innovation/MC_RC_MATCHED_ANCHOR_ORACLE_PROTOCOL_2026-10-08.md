# 当前19系列的匹配理想观测区域诊断

在新标签数组读取前冻结。上一轮15系列标签可见性/理想传播和19系列缺层GT前景/2体素包络都保留，不将其当本轮新发现。新增范围为当前全部19开发series/11患者，相同phase0/stride4、两侧anchor并集+原面内2mm、当前physical grid/原PATCH64x128x128/50%overlap/原batch2，匹配上轮三固定预测方法。

唯一主几何支持 `ideal_observed_anchor_union_2mm_19`：每侧mask来自真实**观测层标签**。先通过原observed_truth仅解码z=0,4,...标签；全部19理想anchor包及SHA保存后，才读取完整GT评分。该标注不是部署可见MRI信息，不能叫可部署定位器、有效修正、MRI任务提升，也不是所有有效修复支持的上下界。没有MRI像素/网络checkpoint/新训练/forward。

固定保持所有19病例、不调2mm/阈值/后处理，原全部foreground>=.99/boundary>=.99/tile32foreground>=.995/ROI<=.05/tile32area<=.10门槛逐项保留。门槛为旧几何诊断，**面积门槛不等价于当前3D实测总成本门槛**，0通过也不能单独证明任何大ROI政策不可能有效；真实成本/任务收益另测。报告全部原端点、N/k、空ROI、全batch失效、与冻结3预测的患者等权覆盖/面积/窗口差值及支持集合关系，不更名主方法。

完整GT评分阶段附带phase0标签成分几何：6/26连接、全部fullGT成分、前景bbox内计算避免背景内存。保留每成分体素数/bbox/观测、内部缺层、tail体素数；统计内部缺层存在但无观测接触的成分。只叫标签接触，不推断MRI可识别信号、临床独立病灶、检测率或厚层acquisition profile。小边界成分不删。主要几何仍全19无条件评分。

费用固定两种场景及m=[1,2,5,10]：A cached N+m*k vs dense m*N（dense不需要另行baseline）；B 两对照都确实需要同baseline，cached N+m*k vs dense N+m*N。不能单边删除初始化，也不能假设当前真实策略已满足B流程。分别报告原患者/series两层等权、完整患者sumN/sumk后ratio且患者等权、全队列pooled。定位/生成/探索/transfer/后处理未计，全部只是条件forward-count诊断，非速度。支持重复假设不外推累计编辑。

仅metadata附加受影响tile数T与ceil(T/2)重打包计数场景，作为原pair仲裁的潜在空间；原k门槛/费用不替换，原窗口/batch顺序等价尚未验证、不是执行器或加速结果。有限精度/归一化/硬预测可能受batch布局影响，任何实际新打包须独立最终模型资格。

独立核验重读observed标签（inverse索引）和完整GT（signed transpose/flip），重建全部anchor、物理disk(binary_dilation而非EDT)、GT boundary(显式6邻域)、原roi metrics、Fraction中心Boolean support、原tile/batch费用/汇总。成分连接仍共享SciPy，显式声明；核各成分体素/观测/missing/tail/bbox与6→26细化关系，不声称独立连接算法/科学确认。比较3旧预测只读冻结结果JSON，不新load模型或MRI。

自身CUDA不可见、CPU1/interop1、BLAS1、below-normal；每生产/核验<=900s、RAM/磁盘>=8GB、当前阶段保存<=20MB，native bool<=256MB、label slab<=32MB、component cropped int32<=1GB。19observed masks压缩包不存MRI/完整GT/概率体积。所有读取列明并审计；仅innovation写，不枚举/控制其他PID，原live99542不重启/迁移。失败保留，新version/attempt修复。4已见验证/8确认/lockedIXI继续不读，旧MIRA/MSValid84证据保持。
