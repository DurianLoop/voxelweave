# 已执行数值细节与独立核验范围

实际执行器在binary Fraction CDF转换80位Decimal时向上舍入，Bonferroni的delta/N门槛向下舍入；continuous HB才额外上加1e-60。原协议概述的“上加1e-60”不是binary分支规则。数值输入有限十进制<=30有效位、非零数绝对十进制阶<=30；alpha/delta在(0,1)。这些限制均已执行，已执行源码及protocol snapshot保留，不静默修改其绑定。

独立verifier只读合成面板和source_snapshot，不import执行器：Fraction重算binary CDF；120位Decimal用entropy展开式重算HB（生产用log-ratio式），核80位输出保守余量/误差<=1e-58；独立按弱/强支配及max-p-value构造次序与认证集。invalid输入拒绝记录只核内部一致性，不声称独立再次执行其异常分支。实际理论适用条件还需独立患者/i.i.d./全pipeline冻结，fixture不证明MRI保证。
