# 原表与临床口径核验

读取本批已完整核读的两个原始XML，另用ElementTree直接抽取原始table cells，核对保存提取结果；不从手写报告抄数。用Fraction核VSRAD Table1声明的7项Bonferroni与显示的raw/adjusted p值，并检查9项系数是否与显示精度兼容。所有科学解释保留原数、显示四舍五入区间与是否改变原显著性。

Table2核median ±1.5 IQR的7行边界及64例分母的outlier百分比。输入/输出显示到2位小数时，不把0.01差异直接当统计错误；用每格±0.005的闭区间检查是否可由隐藏小数解释。不将difference of medians当median of paired differences，不由Table1/2符号差异断言配对原始数据错误。median±1.5IQR不能在未假定分布/未给coverage估计的条件下被本项目称为95%患者守卫。

SynthSR三表保留各任务分母，核Table1 segmentation-loss相关变化、scan→subject聚合变化和Table2分辨率变化。相关性变化不是paired病灶损害改善，435扫描不能计435独立患者。总9146扫描、1110sessions/正文另称patients的表述保留，不作身份crosswalk认证。

另算临床流程105s采集+77s生成与232s原采集之差，仅作为已报告两个阶段的串行算术，不包括DICOM/WSL/重定向/VSRAD/失败复核或人时，不宣称全费用节约。总75生成、11剔除、64分析；诊断AUC29AD+8normal=37报告分类样本，不当完整75外部独立确认。

CPU单线程/below-normal；本stage输出<=100KB、wall<=60秒，所有目录总量<=4MB，磁盘/RAM8GB并预留另两live阶段。没有医学数组、模型、forward或训练；goal active。
