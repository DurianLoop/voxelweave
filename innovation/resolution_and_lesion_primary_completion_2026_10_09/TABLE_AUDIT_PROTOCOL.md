# 原表与权重公式的 CPU 核验

两篇新主文已分段实际输出，VINN 128–137 的合并工具截断部分另读；不把来源获取或目录预览计阅读。新核验仅用已核正文、原 HTML 和抽取表，不载入 MRI/GT/model。先绑定 SHA，再由原 HTML 重新提取表单元格并对照已保存抽取，随后使用 Fraction 和 Decimal 两种独立十进制算术比较。

病灶集成论文：4任务28个显示验证端点，逐端点计算 Ensemble−最高单模型，以及 Post-processing−Ensemble；不将 MET global validation 与 lesion-wise testing相减。记录缺省表格cell和完整分母，不从显示mean推患者显著性。4组显示权重和与正文 W_i=(sum_{j!=i} F_j)/(sum_j F_j) 比较；n=2..6、F取1..4的全部5456组合核公式权重和=n−1。将其归一化后才得到sum1，不能猜作者代码具体修复或其实验有误。

VINN：使用已读Table6–8，比较外部缩放、attention、HiRes Loss的四端点增量；按DSC越高/ASD越低标方向。显示均值差不是统计等效性，也不是本项目病灶效应。Table6 bi-linear ASD=.293与Table7/8 .303同时保留，不自行改源。

CPU1/低优先级、wall180秒、新audit目录<=50KB、本stage<=1.2MB、磁盘/RAM8GB及live journal/医学评价未来空间不变。新增患者效果和训练更新0，未见确认与lockedIXI关闭，claim未确认。
