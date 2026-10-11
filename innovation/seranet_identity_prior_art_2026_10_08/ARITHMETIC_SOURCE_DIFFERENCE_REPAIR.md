# 保留实际算术失败，改为显式记录来源差异

audit_recurrent_arithmetic.py 实际工具5467d3 exit1，失败在 SERANet Table1/2 所有均值四位小数容差假设。原脚本和已创建的空 recurrent_audit_attempt01 留存不改。

复核 SERANet Table1 第6页 final_lce / 20%：三个打印数 .8083/.8762/.8415 等权平均 .8420，打印 Aver=.8423，相差 .0003，大于打印小数舍入容差。可能存在其他聚合定义或原始精度原因，正文没有核实，不修原表、不推断原因。其余均值在新版本中逐项保存并检查。

另存 v2，完整算术可以成功执行，但明确 all_printed_means_consistent=false，差异单独保留；不能把 v2 exit0 说成论文算术完全正确。其它后续算术保持原定范围。
