# 固定特征的主输出层能力诊断：新探索协议

依据已核验的001系列两臂512更新结果提出本实验：主head背景平均概率约0.13、soft Dice约0.011，但quarter head soft Dice约0.94。本协议在本项新参数更新和结果打开前冻结；这是结果驱动的开发诊断，不是预注册的独立科学确认。

精确问题：在保持最后checkpoint骨干与原训练增强batch完全固定时，主head只改变偏置或全部17个线性参数，能否拟合同一批的foreground hard-Dice及概率？若成立，只说明最后特征已有某种可利用分离能力。完整训练FOV若仍失败，需训练采样/context覆盖。不能把此诊断称MRI恢复创新、第二独立任务网络或四验证门槛通过。

固定输入：仅VS-MC-RC-001开发系列，native_reference与raw_pchip最后512权重、原两个crop、同输入/标签/primitive SHA；骨干及另外两个head完全冻结。按native bias-only、native full-head、PCHIP bias-only、PCHIP full-head顺序训练。每个分支从相应原最后权重重新开始，不串接分支。

每支固定1024次CPU AdamW更新，lr0.01，不调整学习率或延长；bias-only只更新1个参数，weight_decay0；full-head更新16个权重+1个偏置，weight_decay0.0001。仍使用原fine-head BCE+Dice及权重4/7，另两head贡献是冻结常数；不采用新标签、权重/采样、阈值或最优checkpoint选择。这里的lr/输出层隔离是已知优化诊断，不能将变化归因仅于参数数目。

将最后decoder特征展为逐体素16维矩阵，证明矩阵linear与原Conv3d概率最大误差<=3e-6、0.5预测0差异；首步闭式输出层梯度与autograd核对。全部分支最后参数冻结后才计算patch及完整FOV；保存1024条每步历史/最终checkpoint/全部四域。主head损失另用float64 NumPy logaddexp和soft Dice核对<=3e-6；最终checkpoint使用独立functional网络及NumPy native重采样计算所有FOV，推断不依赖GT。原两个失败checkpoint及所有门槛保持不变。

固定训练拟合gate：foreground crop Dice>=0.9、完整训练FOV Dice>=0.9、recall>=0.9、absRVE<=0.25、TP>0。所有空/undefined保留。新诊断成功也不得打开验证或八确认；原四验证gate及患者内均值后患者均值不变。

单线程、自身below-normal，不初始化CUDA，不枚举/操作其他PID；RAM和磁盘各保留8GB。新输出<=100MB，不存MR/GT/特征cache。整次墙钟上限3600秒；首32步投影四分支更新耗时超过3600秒时停止保留失败，不扩大预算。每64更新检查资源、记录有限loss/梯度。时间/资源失败保留原记录，修复另写版本。

论文解释仍受限制：梯度核验仅证明当前目标/实现一致，不能解释全部非凸训练动态；InstanceNorm与AdaIN等已有先例。部署候选参考统计必须由可见PCHIP生成。所有修改位于innovation。

前置证据：[512结果](MC_RC_3D_CPU_FIXED_FIT_RESULT_2026-10-07.md)、[阶段归档](SESSION_ARCHIVE_VERIFICATION_CPU_FIT_FOLLOWUP_2026-10-07.json)、[失败解释](MC_RC_3D_CPU_FIT_INTERPRETATION_2026-10-07.md)。
