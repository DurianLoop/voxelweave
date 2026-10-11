# 新数值候选完整35904从头资格（执行前）

保留原2992step/5984geometry、两MRI输入、三resolution模式、母GT原位合同，共35904完整64×128×128字段。不能继承旧6216/14673prefix。候选是certified_resolution，独立reference为已完整542资格后的direct_separable_reference；gamma v2与原独立强度reference不改。插值新增逐位零差；强度/概率3e-6、coordinate3e-12、support binary零差、padding baseline逐位不变，医学gate不降。

执行前必须：旧542实际exit0+独立audit；费用优化144同形状tiny/三个固定百万字段actualexit0；费用优化新542实际exit0+独立audit；fresh compute/storage admission。不得把当前session31883“正在运行”作为通过。新数值来源/全cache/geometry/label SHA绑定，全部患者有效字段、fallback、完整费用保留。读取19个开发GT是原合同检查，8确认患者12series及lockedIXI不开。

此候选需要Fraction fallback，CPU成本比旧Torch/SciPy大，旧32400秒wall的失败harness不修改。本新版本执行前另定wall64800秒（18h），fresh forecast使用完整新542的candidate+oracle累计费用作保守每active字段估计、按10710 enabled schedule字段外推，再留25%及1200秒sampling/intensity/IO额外预算；预计超过wall则不启动，先优化。运行过程中费用/墙钟超限则明确失败，不改容差、不删字段。不是为了得到通过结果而事后扩大预算。

CPU1/below-normal、CUDA不初始化、本stage2MB、journal1.5MB、RAM/disk8GB、原医学3MB/开发2.8MB及在用其它stage allowance保留。qualification是一个新的纯CPU医学数组比较；不是GPU训练，也没有发表claim。只有实际整体exit0与独立终态audit后才准备六臂训练/完整推理费用资格及fresh resource admission。
