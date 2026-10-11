# 完整能力结果后的全28series描述

四last2992已8042cc真实完整exit0、288edd审计、7e4c67完整比較成功；开发均值高、已见验证低，下一步先描述两组是否有明显采集/病灶构成差异。仅读固定病例metadata及既有四臂完整计数，不加载MRI/GT/model数组、不训练、不改阈值、不据结果筛患者或制定验证集专用增强。

固定全部11开发患者19series与4已见验证患者9series；读取native_shape、affine三轴spacing与绝对determinant体素体积，既有full域GT_foreground count换算mm³与全FOV前景比例，核四臂同病例GT计数一致。逐series保留，series→patient→全患者均值，范围和各患者值均报告。非配对队列，不做显著性或采集/病灶单因素因果。GT体积只用于分析/训练监督，不得进入部署收益特征。

CPU1/60秒/输出<30kB，新stage总<=2MB、live输出预算及8GB储备不降。8确认12series/lockedIXI关闭；这是已见队列描述，不是独立确认。
