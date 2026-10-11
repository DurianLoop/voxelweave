# 理想观测区域传播：固定15系列的开发诊断合同

本合同在任何新ROI覆盖、边界覆盖或区域预算统计前保存。上一轮主phase0无完全隐藏成分只是几何反证，不保证病灶轮廓可以从真实观测区域传播。本轮检验一个更具体的必要条件：若真实观测plane的标签都能被理想识别，简单传播的区域能否在有限面积下覆盖内部缺层病灶及其边界？这是采用真值观测mask的开发诊断，不能称部署能力、新理论或模型优越性。

## 全部来源与信息边界

固定上一轮`mc_rc_label_anchor_visibility/run_contract.json`的15合格系列、8开发患者及9个拒绝/pending记录，不再筛选。逐项核原合同/结果/独立proof及component artifact hash。使用已认证native component前景作为二值标签（原slab的787,030前景坐标已独立核），独立复核再从原NIfTI解码。15时间点不是15独立人，三批所有时点继续归开发；未见确认0。

只读标签，不解码新MR、不运行HAT/分割网络。每个策略输入只含phase0真实observed masks、原生row/column物理间距和plane位置；隐藏层标签只供事后评分。观测mask是真值上限信息，不是已取得的检测器输出。物理间距取此前authenticated DICOM affine/proof；它不是PSF或真实厚层profile。x4、phase0、评分只含首至末观测plane之间所有三个余数，不评末端外推。

## 冻结策略与预算对照

对每个缺层z，左右真实观测为L=4floor(z/4)、R=L+4；最近策略在距离相同的余数2取左。冻结八种诊断：

1. nearest：最近observed mask。
2. bracket_union：左右mask并集。
3. union_1mm：并集在plane内按1mm Euclidean距离膨胀。
4. union_2mm：并集在plane内按2mm膨胀，**唯一主要策略**。
5. union_4mm：并集在plane内按4mm膨胀，敏感性，不用于替代主策略失败。
6. shifted_union_2mm：主要mask按row/column各floor(size/2)作环移，像素面积完全相同，检验定位信息。
7. random_pixels_matched_union_2mm：每目标在完整plane均匀无放回抽与主ROI同数的像素；只作为像素面积对照，不说它tile预算相同。
8. full_plane：完整plane，覆盖正对照、面积成本100%，不能作为有用策略。

再独立提供`random_tiles_matched_union_2mm`的tile对照：native row/column原点开始32×32不重叠tiles（边缘保留实际尺寸），按tile实际面积分组，在每面积组均匀无放回抽与主策略相同数量的tiles。因此总tile数和实际像素面积都完全匹配。主ROI到tile的规则为tile与ROI有任意交集就选择；随机pixel的tile区域通常不保持预算，单独报不用于tile优越性结论。

所有随机用PCG64；每目标seed为SHA256(`20261003|SeriesUID|z|pixels`或`...|tiles`)首16hex转integer。没有按结果改seed、多次抽样后挑最好或扩大预算。SeriesUID只标确定性随机复现，不作为学习特征。

## 评分与事前判别门槛

记录每目标及每系列的缺层真值体素recall、ROI precision、Dice、ROI/plane面积、ROI面积对真值foreground的倍率、32tile覆盖recall和区域面积。几何Dice只比较传播真值mask与原真值，不是新图像模型的分割Dice。另以完整native真值的6邻接边界（image外为background），只在内部缺层上计边界覆盖；边界truth仅用于评分。零分母为null，不按lesion-positive targets替换完整目标分母。所有目标的ROI成本都算，包括该目标没有真值病灶的情况。

统计先系列累计计数，再患者内全部时间点等权汇总；同时列全部15系列、全部8患者，不作独立样本CI或显著性推断。零/失败/主策略反证不删。主诊断仅当**每个15系列**同时满足：缺层前景覆盖≥.99、缺层边界覆盖≥.99、32tile前景覆盖≥.995、完整内部缺层平均ROI面积≤5%plane、tile面积≤10%plane，才认为固定2mm理想区域留下进一步预测表征实验的几何可行性。尺度和门槛是本次事后开发诊断的预写设计，非临床接受标准；不据结果换4mm、改连通规则或门槛。随机/环移的同预算结果完整报告，差值不升级为可见模型能力。

任何主门槛失败，停止这一固定union2mm传播路线的正向准备；更多学习表征需提出不同且可失败的合同，不能以较有利敏感性结果救主假设。如果通过，下一步仍必须实际检查仅稀疏MR派生的冻结预测区域，确认模型来源/患者重合排除和CPU预算；理想mask成功不免除预测错误、旧动作收益失败、任务端点或未见患者验证。

## 实施与独立核验

一个CPU数组worker，隐藏CUDA/单线程/自身低优先级，可用RAM8GB/磁盘15GB。单series允许≤512MB临时数组，slab≤32MB；输出保存所有目标计数、主要ROI和同预算随机pixel/tile的packbits、策略及输入hash、失败、患者汇总。目录exist_ok=False，不盲目重跑覆盖。

主要实现用EDT计算2D Euclidean距离。独立复核从原NIfTI以4-plane slab重建native二值标签，按原整数grid坐标核foreground，边界用显式6个轴向邻居构造，主要/1mm/4mm膨胀用物理integer-offset disk及tight bounding box内binary dilation。重新评分全部目标/策略/随机预算及患者汇总，比较packbits与原始实际像素；不能只核JSON布尔值。随机使用同规定PCG64复现，不能称独立RNG算法。新结果不改原VS-SEG队列或旧30特征失败政策。
