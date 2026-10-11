# 真实19series三视图资格的可执行协议

继承ROUND48完整19series/11开发患者/两个输入/两步清单，cold-init seed20261009，固定所有case、原schedule几何/母GT和GIN参数seeds，不用GT生成augmentation。shape(2,1,64,128,128)，3 view，qualification lambda0.1，原GPU深监督loss与attached reverseKL(mean||each)、element mean不变。GPU builtin save_on_cpu完整图与新独立CPU可微functional graph各两步AdamW；CPU显式母target nearest-exact索引、binary softplus和xlogy KL人工两步已通过，完整scope待本作业核验。原协议、metadata准备不编辑。

完整预算分母38case×kind，GPU76实际optimizer更新/228whole-model forward，CPU同数；所有checkpoint block调用另外记录，不增加患者。CPU先做两步，GPU再做两步，都是同common init和同每步三个CPU生成view；每步全部head概率/loss/54参数梯度/更新/moments比较3e-6、step逐位同。CPU/GPU各自再用其实际梯度与独立float64 NumPy AdamW检查全参数/moments3e-6，不以共享公式更新替代跨设备检查。母target whole physical resampling额外用独立NumPy voxel-centre索引逐位核对，每patch与冻结几何/母hash核对，两input共享全label SHA。GIN不改变坐标/target，完整view/target content保持。

首次完整branch同时是实际费用观察。冻结wall21600s（6h）的硬上限，不根据某prefix删scope；第一branch若通过，记录其actual费用及对完整38branch的简单预算外推，但外推不当实测全部费用。若任何3e-6/二值/资源gate失败，保存完整prefix和最差位置两侧值/参数名，停止整个资格；失败branch不算完成或完整19资格。不因原scope难而缩小。模型optimizer snapshots只在内存序列化/重放，不持久权重、不改变原终端训练，不作临床效益实验。

最多journal1.2MB/frozen_config0.25MB/receipt0.35MB，合计1.8MB，纳入原prep7MB/FOV20MB/other22.8MB完整余量（实际写入前后guard）。GIN具体参数用little-endian float32 byte payload+base64+shape/hash记录并反解逐位核对，完整记录统计norm，不只保存seed。CPU1/interop1/below-normal，RAM/disk各十进制8GB。GPU只查询aggregate，启动free≥8192MiB、allocator≤min(10%,2.4GB/total)、peak≤2.5GB/runtimefree≥4GB，FP32/TF32off/deterministic；每block/perview和backward后guard，不枚举/修改其他PID。原full35904 job保持，不重启。

费用分开计GT/MRI读取resampling、basic crop、GIN四层conv/统计/校验、模型/优化器准备、每view forward/checkpoint recomputation、attached loss/backward、CPU卸载、同步、梯度/概率捕获、AdamW、独立NumPy、完整state内存保存/恢复/hash、journal，以及总elapsed。GPU卸载和CPU参考的传输/同步/hash都不能隐去。3e-6是资格数值gate，不是医学/临床等效界限。此作业即使通过，full38推理、完整35904、IPA、普通/GIN等同预算强对照、医学六gate、cold-initLOPO和未见独立确认仍单独pending；确认集/lockedIXI保持关闭。
