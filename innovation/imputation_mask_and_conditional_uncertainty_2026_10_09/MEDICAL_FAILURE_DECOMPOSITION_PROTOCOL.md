# 全36FOV医学失败的精确诊断

原医学评价真实6ede46整体exit0，原capture0fbd7c/summary a165da已取得；36production+36functional数值通过而四分支均未过原六医学门槛。现在只分析已保存整数counts/metrics，不重跑forward、不加载患者图像/GT/checkpoints，不改变阈值/门槛、丢series或选checkpoint。

完整36series×full/anchors/missing/tail重算TP/FP/FN/TN与volume，使用Fraction独立Dice/precision/recall/signed与absolute RVE。以患者内series先均值，再四患者均值重核全部原聚合（abs tolerance3e-12），保留zero denominator语义。逐series counts须full=anchors+missing+tail。

对每输入同预算spatial-minus-intensity逐患者比较full/missing Dice、recall、FP/FN、tailFP占全FP及体积比例，正负/零全部保留。增加描述性leave-one-patient-out均值，只作已见4patient敏感性分析，不挑leaveout、不做训练/检验/校准认证。native平均改善是否被单个患者驱动、raw下降是否伴漏检或过体积，是本次要澄清的问题。

CPU1/below-normal、wall60s、输出<=100KB，本目录2MB，磁盘/RAM8GB另留原full2MB/评价3MB。来源先核actual终态、capture和全部receipt SHA，确认集关闭，无新医学效应或发表claim。诊断不证明augmentation因果机制，只决定下一普通task基线的检查顺序。
