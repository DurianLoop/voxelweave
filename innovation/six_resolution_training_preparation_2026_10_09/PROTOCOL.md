# 两输入 × 三分辨率增强的六臂训练准备

这是开发能力诊断。native_reference/raw_pchip 各沿 throughplane/inplane/allaxes；每臂2992更新，合计17952，11开发患者各272曝光、19series全部保留。各输入从对应19998 parent开始；parent含全部开发GT，严禁作为严格LOPO外折warm-start。三种增强不称为临床SR部署动作。

使用原2992 schedule、5984 geometry journal、完整母GT、原采样/flip/basic intensity、certified_resolution及float64-stat intensity。每step逐项核对患者、series、两patch geometry和母GT SHA；没有GT筛选增强、没有改label、没有减少FOV/曝光/分支。每臂reset AdamW lr1e-4/decay1e-4/betas(.9,.999)/eps1e-8，foreach=False/fused=False；CheckpointedTaskUNet3D原参数名/算子，FP32/TF32off/deterministic。训练无验证评分或中间checkpoint选择；不支持自动resume。记录全步骤journal，只有last2992权重。

`run_six_resolution_training.py --preflight` 只读已结束JSON、父文件哈希和小schedule，不读MRI/GT/model数组，不初始化CUDA。报告可能complete但ready=false。`--train` 会重新检查全部门槛；门槛未齐则在读医学数组前拒绝启动。

启动条件：完整35904实际exit0且独立v2审核通过；六首步AdamW实际exit0且终态审核；完整GPU→CPU/独立functional的38个原parent完整FOV概率<=3e-6、坐标<=3e-12、二值零差，以及完整滑窗/重采样、磁盘原子保存和费用组件已实际资格。训练费用测量须覆盖19开发series的实际batch（不等于预先完整训练17952步），整轮wall是基于这些实测的预测。后者未来单独写 `FULL_GPU_DEPLOYMENT_QUALIFICATION.json`，须绑定真实terminal与审核，不接受仅估计或单病例首步资格。该文件目前未生成，当前入口未就绪。

整轮预算沿既有完整family61,356,359bytes（六权重、atomic temp、journals、metadata、evaluation、cost/audit），不压缩科学scope。此前额外allowance16.8MB与GPU graph1MB不减少，本批论文/诊断stage另2MB：合计至少80,156,359bytes高于8GB磁盘reserve。准备目录文件包含在family metadata内。GPU起始free8192MiB；进程cap10%、peak2.5GB/runtime free4GB；RAM8GB/CPU1/interop1/below-normal。预算资格必须有正的训练wall估计及上限，估计涵盖实际分辨率计算、GPU step、保存和推理；不得拿一病例首步时间外推整个医学family。

医学原六gate仍为患者先均值fullDice>=.70/missingDice>=.65/recall>=.70/absRVE<=.50、各患者full/missingDice正且无series零TP。四已见验证不作新确认。八未见确认患者12series与lockedIXI关闭。

准备完成仅指代码、固定参数、门槛和预检可审查；未执行完整六臂训练、未完成114完整FOV评价、未认证收益或可发表claim。后续修复生成新版本，已执行/冻结源不修改。
