# 两臂最后checkpoint的固定诊断面板

在512更新两臂最终效果尚未打开时预先定义。目的仅定位拟合/推断能力限制，不改正在运行的训练，不选择checkpoint、阈值或最佳诊断变体。

前置条件：`mc_rc_3d_cpu_fixed_fit_2026_10_07/attempt_01.json`确已完整结束，两臂均512更新，完整FOV效果和最后checkpoint保留；先完成既定独立重放核验。本面板只使用同一个开发系列001、同固定采样起点与前景/背景两个crop、seed20261007、同最后checkpoint。验证和八确认不打开。

对两输入各运行4种预定crop变体：原训练增强；只保留flip；只保留intensity scale/shift；无增强。标签随flip一致变换，crop起点完全相同。逐位重建原训练batch SHA。所有变体报告主/半/quarter head的GT数量/占比、BCE、当前批量soft-Dice、两个样本独立hard-Dice、GT前景/背景概率、阈值0.5预测计数。不把去增强后的训练crop表现当完整FOV表现或新方法增益。

对每head的logit单独计算BCE和Dice梯度。当前loss的闭式梯度为：`dCE/dz=(p-y)/N`；`dDice/dz=(A-2*y*B)/B^2 * p*(1-p)`，其中`A=2*sum(p*y)+1`、`B=sum(p)+sum(y)+1`，N为整个batch体素数。与同logit上autograd逐值比较（atol1e-9、rtol1e-5）。记录前景/背景L1梯度总量、主导方向及两项L2 norm比；这是对实际训练配方梯度的局部描述，不是参数梯度或因果证明。

所有4变体固定报告，不挑最优。不执行任何参数更新、不存新的MR/标签/概率体积，新增结果<=5MB；单线程、自身below-normal，RAM/磁盘仍各保留8GB，不初始化CUDA。若资源条件不满足保留deferred结果，不操作用户训练。
