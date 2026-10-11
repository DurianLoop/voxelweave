# 真终态后的完整开发/已见验证比较入口

此准备不解释开发partial结果。compare_complete_development_and_validation.py仅在12652实际整体exit0、原capture_development_terminal.py完整审计成功后运行；当前未执行。先核terminal、来源、原36验证审计、76开发/36验证和全部11/4患者分母、固定四last2992，才生成新complete_comparison_attempt01。未达依赖不建结果目录，不修改live runner/protocol或历史结果。

从每个region的tp/fp/fn/GT/pred以Fraction重算五指标，按series→patient→全患者；任一未定义使该聚合null，保留全分母，与原source聚合1e-12内一致。报告全四臂、每患者与全4region，组间均值差仅描述，不做paired患者比较、因果或显著性声明，不挑checkpoint。开发参考fullDice.70/missingDice.65/recall.70/absRVE.50沿原协议，只用于能力诊断；不替代原六验证门槛。

开发高、验证弱时优先检查泛化/普通增强；开发也弱时先检查训练patch与部署完整FOV一致性、优化和基础能力。loss/exposure统计只能辅助定位，不自动证明原因；无法用数据不同的组均值排除采集/病灶构成差异。无模型/MRI/GT数组加载、前向或训练，CPU1/60秒/输出<=200kB；原确认集保持关闭。
