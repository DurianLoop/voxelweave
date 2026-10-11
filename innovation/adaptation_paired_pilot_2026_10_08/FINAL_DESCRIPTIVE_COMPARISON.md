# 固定99步配对续训：完整评价

原父模型与四个新最后state一起报告；所有数字为已见4患者/9series的患者先均值。

| 输入 | 条件 | full Dice | missing Dice | recall | absRVE | 六门槛通过 | 零TP series | 空预测 series |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| native_reference | parent | 0.506632 | 0.507568 | 0.462613 | 0.474591 | 3/6 | 0 | 0 |
| native_reference | basic | 0.432088 | 0.434118 | 0.389185 | 0.571816 | 1/6 | 1 | 1 |
| native_reference | strong | 0.507813 | 0.508967 | 0.507842 | 0.601841 | 2/6 | 0 | 0 |
| raw_pchip | parent | 0.445159 | 0.445335 | 0.372408 | 0.571475 | 1/6 | 1 | 1 |
| raw_pchip | basic | 0.523190 | 0.522249 | 0.462381 | 0.451181 | 2/6 | 1 | 0 |
| raw_pchip | strong | 0.526725 | 0.524898 | 0.528917 | 0.487844 | 3/6 | 0 | 0 |

四个新分支共36生产+36functional完整FOV，严格数值/坐标/二值/计数/患者聚合均完成；不是第三次跨进程重跑。

strong-minus-basic与strong-minus-parent逐患者差异见JSON。训练配方只有99步续训；重置optimizer对两个匹配分支相同，父模型未作该次更新。强度增强优于本次basic不等于优于原父模型或达到医学能力。

没有新独立确认、显著性或充分适配结论；8确认患者与lockedIXI未打开，科研goal仍active。
