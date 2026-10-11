# Learn then Test 校准排序 CPU 解析审计：事前协议

仅合成 binary loss；不读取 MRI，不修改真实模型/策略。固定 n=8、alpha=3/10、delta=1/10，两个相互独立策略的真实错误率均 q=31/100。每个策略的校准错误总数 K~Binomial(8,q)，检验 p=P(Binomial(8,alpha)<=K)。以 Fraction 枚举 9x9 联合计数的概率，不作 Monte Carlo 或搜索更有利参数。

比较先验固定顺序（第一不拒绝即停止）、按相同 calibration 错误数排序后冒用固定顺序、Bonferroni 两策略。前者 family-wise false rejection 应 <=delta；后者只要任何零错误即错误认证，预期超过 delta；Bonferroni 零错误的 p 仍大于 .05，故此例无认证。

另记录原来 4 个已见 validation 患者即使假设独立 fresh、零错误，p=.7^4 仍不能通过单策略 delta=.1；实际这 4 人已用于开发，并不具备 fresh calibration 资格。此项是已知多重检验方法的适用性反例，不是 MRI 发现、风险控制新理论或已确认 claim。
