# 单012覆盖×增强2×2固定预算能力实验

先完成draw生产与独立核验，再执行本协议。四条件legacy_aug/legacy_none/coverage_aug/coverage_none；每臂相同初981,602参数GlobalLocalUNet、seed20261004、BCE+两patch整体Dice+.5global、AdamW wd=.0001、cosine .001→.0001/分母3999、4000updates及最后checkpoint，原native完整FOV/全部72z/.5、无GT裁剪/后处理。取消增强指整个几何+强度bundle，不单独解释旋转/强度。

全部4000原legacy增强样本SHA精确等于上一轮BCE+Dice，并需独立验证16000四臂输入SHA和16000完整patch源像素映射。只有这些证据完成才复用legacy_aug已执行训练/最后checkpoint/预测/指标；新updates0、新生产forward0，不将复用臂称独立复制。按固定顺序legacy_none→coverage_aug→coverage_none分别从头4000步，不看中间结果换顺序/预算/病例。若draw核验不通过，停止本协议，另立四臂从头协议，不默默更改。

原.5 foreground-voxel/.5all-z外生draw相同；几何配对保持同一原空间支撑。覆盖在每z的完整physical网格16tile维护游标并循环，增强开关映射对应矩形；72z至少19次、最多96次更新，所有z都遍历了16tile。覆盖改变前景/背景曝光（平均两patch前景mass约1877→684），这属于采样处理，不能拿同预算误称相同foreground exposure；两开关成对等空间支撑、不同浮点归约顺序可有极小mass差。

每新臂前10真实updates估时，仅平均≤2秒资源可行守卫；不依loss早停。逐update生成例子SHA必须等于冻结draw文件该臂记录。每100updates记录局部/全局/总loss/lr/资源；非有限loss/梯度停止保留attempt。每臂都完整评估和保留，不能仅报告最好条件。

预写012完整病例fit gate沿用full Dice≥.90、supported missing Dice≥.90、recall≥.90、absRVE≤.10。full/missing/anchors/tail、precision/recall、FP/FN、signed/absRVE及完整affine ASSD/HD95、empty/undefined全部报告。对四臂独立label/bincount/物理距离和首/中/末共12完整plane重放；旧legacy指标在本因子对照中仍复核，重复重放不是新模型复制。

分析四臂数值和覆盖主差、增强主差及差中之差；只有单训练病例/单seed，无患者显著性/泛化结论。配方/预算固定后看结果，不能把max臂当唯一成功证据。任务能力即使通过仍需11开发/四验证/native与强基线，之后才能验证重建残差；八确认继续关闭。

新增只innovation/experiments/mc_rc_coverage_augmentation_factorial_cpu，exist_ok=False、<100MB；单线程CPU/自身below-normal、磁盘≥15GB/内存≥8GB，三新重训练按序不并行，GPU/用户终端训练/locked IXI test不操作。实际session轮询，不重启live或已完成attempt。科学确认0，goal active。
