# 四个last2992模型的原开发集完整FOV能力诊断

原四臂训练95b0a1完成/df9ebf审计，原36FOV评价6ede46完成/0fbd7c审计/a165da汇总。全部严格数值通过，四臂均未过原医学门槛；native spatial均值改善只1/4patient为正、recall4/4下降，raw spatial均值下降。发表收益头或确认集仍不放行。

本阶段只用原11开发患者/19series，四个固定last2992；全部76production+76independent functional完整FOV，同g.source_image/物理重采样/滑窗/production mapping V4/阈值0.5/packbits无损存储。无GT定位、阈值选择、TTA、postprocessing或checkpoint选择。四模型全部跑完，不挑较好模型。加载原GT仅用于development评分；原4validation图像/GT不加载，本阶段只读取已完成指标作描述性比较。8未见确认12series及lockedIXI关闭。

先核真实训练与完整医学terminal、来源、四last2992/11968journal审计，再建立frozen_config，之后才加载development影像/GT/checkpoints。全部概率3e-6、float64坐标3e-12、二值零差、独立计数与患者先均值必须通过。能力描述仍参考fullDice0.70/missingDice0.65/recall0.70/absRVE0.50，不降低原医学门槛；开发集见过训练GT，不能宣称未见泛化、LOPO或确认。

判断的是“同模型在其训练患者上是否也弱”，以及原开发与已见验证的描述性差异；样本与采集条件不同，不能直接把组均值差当causal augmentation或病灶动作收益。原19998parent已对19development完整评分，可读其冻结结果作描述，不重跑或挑state。

CPU4/interop1/当前进程below-normal，不初始化CUDA。GPU授权保留但free1394MiB<8192，不迁移现有训练/强度任务、不枚举或控制其他PID。磁盘/RAM8,000,000,000 bytes，本目录总<=3MB，预先留2.8MB输出并保留full2MB和原医学3MB；wall5400s（原56FOV2193.9s只作预算预测）。不装依赖、不委派、不删历史。每个FOV后资源/时间guard，失败保存并停，不放宽阈值。

真正成功terminal后保存ACTUAL_DEVELOPMENT_EVALUATION_TERMINAL_TOOL.json并记录实际session；独立来源/全部76FOV/全11患者完整审计后才能冻结输出。运行中receipt/npz不作为归档固定来源。完成此诊断也不等于发表claim，科研goal保持active。
