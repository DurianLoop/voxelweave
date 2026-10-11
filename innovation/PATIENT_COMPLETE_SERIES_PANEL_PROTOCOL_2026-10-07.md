# 完整series到患者策略面板：事前协议

策略必须覆盖冻结expected_series中的全部(patient, UID, policy)组合；缺失、重复、额外UID、非full-FOV或label进入推理都拒绝，不删除失败series。风险先患者内series等权，再各患者等权；实际总cost则将该患者所有series费用求和，另加一次患者共享费用，不能将多series成本平均掉。

输入每完整series的full_dice、full_recall、full_absRVE和9项实测cost components：observed_load、warmup_cache、sr、candidate_exploration、feature、gate、transfer、inference、postprocess。每(patient,policy)另须显式一行共享cost（相同9字段，可为明确0），不可默认漏项为0。scalar与旗标只有数据声明，真实效益/来源仍须最终评价、独立receipt和metric/provenance冻结；本适配器不凭旗标证明实际full-FOV执行。

固定risk：1-患者mean Dice、max(0,患者mean Dice_base-患者mean Dice_policy)、1{该差值>事前epsilon}、1-患者mean recall、1{患者mean absRVE>事前tau}。连续loss以Fraction先完整计算，再向上舍入30位Decimal供数值执行器；binary事件先用精确Fraction判断。absRVE自身只作原始诊断，不截断后冒称控制原均值。free total_cost为整患者费用之和。

固定合成资格2患者/3series/2完整策略：A2个series、B1个；BASE Dice为(.9,.7,.2)，MID为(.8,.7,.4)，epsilon=.04、RVE tau=.5。应得MID患者Dice(.75,.4)、平均.575；若错误按series平均会得.633333...。BASE patient mean .5，按series则.6。MID正部患者下降(.05,0)，harm(1,0)；非代价等权之和的区别另核。不读取MRI/GT，不把这些ID当真实患者。

强对照运行须配合同一候选/患者全覆盖、相同成本统计以及独立opt/testing角色校验。真实完整MRI输出尚未取得，本轮仅合成资格与独立重算；不颁发MRI风险保证，也不替代原train/56FOV/6能力gates。
