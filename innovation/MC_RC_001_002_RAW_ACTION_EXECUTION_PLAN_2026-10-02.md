# 001/002既定开发患者：raw动作执行前合同

本方案在首次读取这两名MC-RC患者MR pixel_array前保存。raw分支是在看到004/005/006开发结果后选出；本次为额外开发复核，不是未见方法确认。原三人pipeline主门槛失败继续保留，不将本次raw结果改写成原主成功。

继承 [保存的准备](experiments/mc_rc_three_development_action_oracle/next_development_followup_preparation.json)：每人最早头+label-grid合格时间点，不换序列/尺度。VS-MC-RC-001 UID末尾10875952303942319530925289292568369177，256×256×30、spacing0.527344/0.527344/0.7000mm、名义厚度1.4mm；VS-MC-RC-002 UID末尾76141570754740903352816737277274474217，512×512×36、spacing0.507812/0.507810/0.8000mm、名义厚度0.8mm。它们不是VS-SEG-001/002。

## 来源、观测与动作

原ZIP/标签/hash和首批独立proof必须吻合。使用首批追加全IPP拟合affine和对应整数label变换，不使用中位步长affine；原失败/事后修正不覆盖。解码前逐对象读取头检查Patient/Study/Series/SOP、MONOCHROME2、单帧、bit/transfer syntax、rescale；不把未知codec或身份默认为通过。失败保持两人固定分母，不换时间点。标签只按已证整数轴置换/翻转，无插值注册。

phase0 stride4完整观测、观测min/max、256resize/clip/已有HAT权重（SHA256 2fae831ab933cf260972260ebec4349f3895106ac7b4d1af3ba368f407498eae）固定；raw PCHIP→HAT为本次开发主动作，pipeline PCHIP→HAT仅诊断。主tile32、α=clip(m/d,0,1)，对照α0,.25,.5,.75,1、slice/volume oracle；完整内部缺层分母21+24=45，观测层逐位保留、尾端复制末观测。支持域是相邻观测1%阈值并集，病灶为标签∩支持域；空/非法支持明确失败。

复用已冻结三人脚本的decode/analyse，仅在当前进程指定首批header目录、BASES顺序和新case的修正summary/grid；原三人代码文件不改。本次run_contract保存旧源码/新执行器/计划/来源/证明/权重hash和修正case由哪些原字段构造。HAT只CPU、禁止CUDA初始化、单线程/自身低优先级、RAM8GB/磁盘15GB底线；不训练、不动用户训练、根环境/.gitignore或锁定IXI test。

## 开发门槛与独立复核

每患者tile32支持域目标等权NMSE相对raw/HAT较佳端点改善≥0.1dB，且病灶目标等权和像素加权两个端点各不高于raw/HAT该端点较小值。任一两名新开发复核未过则不启动raw收益头；五人汇总不算确认CI，不让层/tile数增加样本数。不因pipeline或常数结果更好改本次主动作。

独立脚本以原三人独立算法为冻结来源，另存派生版本，仅适配输出/首批header路径、两人数量和raw主方向；保留Hermite解析、向量化投影/全部层误差和直接网络首/中/末共六前向。保存精确源码替换provenance，不能称原三人全部HAT已再生成。原MR独立重解码、NIfTI方向工具核label变换、源码/权重/全部HAT输出hash、全部45目标/tiles和六前向逐位复核。只有采样前向，不以此支持全部模型输出独立确认。

即使两人通过，也仅得到五开发患者的target-assisted空间；之后仍需部署可见收益/误差头等对照、完整预算、任务表现和未见确认。本合同不做分割/Dice或收益头训练。真实PSF和厚层观测未认证，模拟抽层不等于临床厚层恢复。原45+1 session83910继续原合同，不读动态效果。
