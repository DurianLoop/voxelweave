# 本批 CPU 探索预设协议

本批只读公开论文、合成分布及已有数值 receipt；不读取 MRI/GT、确认集或 lockedIXI，不新增 GPU 和医学训练。所有输出另立 attempt01、不覆盖。资源沿 resource_guard_v1.py，CPU1/below-normal，wall180秒、输出≤100KB。

1. 用标准正熵 H=-Σp log p，对6个动作、所有3个可选动作集合、独立二值图像标签，精确枚举分布。策略均匀随机选择当前可选动作、完全不看图像。比较 I(A;(M,X))、I(A;M)、I(A;X|M)。独立以KL求和核对：预期前两者log2，后者0，容差1e-12。正控制在固定集合内由X选两个动作，预期conditional MI为log2；负控制固定集合均匀策略为0。这个反例只说明一般指标不能独立证实图像信息依赖，不复现或指控任何论文实际曲线，不作新颖性/医学 claim。

2. 根据实际原文表格，独立 Decimal 算术核对 OpenMASC full 对随机同架构、equi、去DCR及去co-train 的增量；Greedy 对NA Oracle及gamma.9的四配置差值、附录粗略wall×GPU训练天数；few-shot K4/8/16 combined增量、K+8标签槽位（是否重复/患者唯一性待代码核验）。不能从均值和标准差恢复配对检验，不重算p值，不把去组件差分当可加贡献比例。

3. 辅助提取 greedy Algorithm1 listing lines（blocks parser遗漏），保留原文压缩HTML绑定，实际读完后另立provenance；参考列表、图像像素和作者代码仍未读。原HTML中 entropy alttext缺负号的情况只作版本文字注意，本探索按标准数学定义，不猜测作者实现。
