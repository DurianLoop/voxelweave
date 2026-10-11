# 3D GPU 实际拟合预检（独立新阶段）

目的：测量新候选真实batch2/64×128×128的显存、梯度、速度和可拟合性，不能用CPU小shape梯度或增大参数量代替。必须先全28native/source proof和修正后的全28双输入grid proof complete。原19开发/9验证未训练，八确认仍关闭。本pilot只读第一个冻结开发系列 VS-MC-RC-001 / 1.3.6.1.4.1.14519.5.2.1.10875952303942319530925289292568369177 的实际训练和评分。

两臂native_reference/raw_pchip，都是相同observed统计、同native监督/物理标签、同架构、同初始seed20261007权重、同两个固定patch和相同augmentation primitive。固定batch第一patch前景中心、第二均匀体素中心（clamp到合法起点，对边界有额外采样质量），三轴flip/强度值记录。不是全数据训练，更不是随机stream或泛化评价。两臂各512更新、AdamW lr .001→.0001 cosine、weight_decay .0001、deep-supervision BCE+Dice、最后checkpoint、阈值.5。没有基于结果停训/选最优checkpoint。

自身GPU启动free>=8,000,000,000字节（比准备协议的4GB最低更严格），allocator<=10%、peak reserved<=2.5GB，实际运行free>=4GB。使用float32、TF32关、cudnn benchmark关/deterministic开；不声称所有CUDA梯度逐位可复现。每16更新检查资源。前32更新测量全1024更新投影，最大3600秒，超限停止并保留已完成更新。阶段checkpoint/预测/记录总保存<=250MB；原失败四因素预算没有被修改。

如果只读GPU totals观测不满足8GB，记录 resource_deferred/zero updates/CUDA uninitialized，exit3；不占GPU等空闲、不查询或控制用户PID。后续GPU空闲时同冻结协议允许新attempt目录，禁止覆盖上一attempt或改变其状态。

拟合检查：固定foreground patch Dice>=.90；单个训练系列完整FOV Dice>=.90、recall>=.90、absRVE<=.25、TP>0；两臂全都检查，失败保留。用native标签评分所有full/observed/missing/tail，空GT/空预测/undefined留存；这些训练内门槛不是原四验证能力门槛，不减少原分母。即便pilot通过也不能作为发表证据；正式19系列充分训练、原四验证全部gate和公平6×5/直接任务对照仍必需。

运行命令：D:\conda\envs\MRI\python.exe -X utf8 -B D:\MRI\innovation\experiments\run_mc_rc_3d_gpu_fit_pilot_2026_10_07.py --attempt 01。
