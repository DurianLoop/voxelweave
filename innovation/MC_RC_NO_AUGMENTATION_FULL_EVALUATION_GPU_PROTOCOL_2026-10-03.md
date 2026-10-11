# 用户允许GPU后的新完整能力评价入口

用户本次明确指示“可以用gpu”。只读nvidia-smi实际返回RTX 5090 D v2、24455MiB total/0MiB used/24035MiB free/0% utilization，MRI环境torch2.11.0+cu128。该观测是当时状态，不据此操纵任何其他训练。当前自身CPU训练继续完成其冻结20000合同，不迁移、不重复。

这份新协议在该checkpoint完整评价尚未开始时写定。原CPU评价脚本/协议保留为已准备但不启动的历史方案，不修改其绑定；新GPU脚本在单独目录运行。需要先取得4831真实exit、complete=true/errors=[]，并通过原CPU训练20000draw/40000patch/最后checkpoint核验。

患者/series/输入/归一化/监督/阈值/最后权重/聚合/gate均沿用原CPU评价合同：19开发raw PCHIP，然后四验证9series各raw PCHIP→raw linear，共37完整FOV条件。每条件标签在完整预测后加载；首中末111plane独立几何重放与完整计数/full-affine距离。四验证已用，科学确认0；八确认不开效果。

仅网络global/local卷积转GPU。physical context、resize、context_tiles的grid_sample、覆盖融合、float64 native概率映射仍调用原冻结CPU实现；GPU adapter在分支边界传输CPU/GPUtensor，不替换空间坐标算法。torch float32，autocast/AMP关闭、TF32关闭、cuDNN benchmark关闭、deterministic=True。CPU/GPU不同kernel可能产生舍入差；不宣称与未执行的CPU37预测完全相同。

运行前使用无患者/无标签的固定synthetic tensor，对相同初始化global/local网络核CPU/GPUlogit误差≤5e-4、sigmoid误差≤5e-5，并重复GPU结果逐值相同。这是运行库预检，不是训练checkpoint的跨设备准确率复现。正式111plane核验用相同GPU权重与独立NumPy坐标，网络结构相同，绝非第二独立训练网络。

资源：单GPU0、自身allocator最多设备总显存10%（约2.4GiB）；启动时free≥8GB、循环检查free≥4GB，自身peak_reserved≤2.5GB；CPU单线程/below-normal、磁盘≥15GB/内存≥8GB。不枚举或操作用户终端进程；资源不足则保留失败，下一attempt用独立resume协议。GPU运行不与另一新模型训练/评价并行。初次完整输入的总37条件运行时投影≤3600秒，只作资源门槛，不按效果早停。

能力gate仍full Dice≥.70、missing≥.65、recall≥.70、absRVE≤.50、四人full/missing均正、9series无TP0。能力通过不等于创新确认；之后才原生控制、公平矩阵与具体可观测修正。新增仅innovation；根环境/.gitignore/locked IXI test不操作。
