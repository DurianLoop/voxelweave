# 本轮结果

MIRTO原文43页文字已读、13个物理页视觉核读（另放大表4一次）；52行公开表的CPU差分/分解审计通过，完成CRC小样本条件算术、4096组Jaccard精确穷举和计时分母核算。MIRTO作者默认branch网页及README实读成功，当前展示占位说明；API tree403限流保留。没有复现作者源码或本项目MRI效果。

- 同nominal预算不等同实际FP：UCCD−cDDPM Dice从validation的+0.020变成同实际FP下−0.001，0.021差异由threshold transfer解释。
- UCCD后处理Dice增益92.435%来自阈值放宽，病灶sensitivity0.674→0.629；加入强calibration-only、fixedτ、完整患者漏检/FP与全成本控制。
- 4/8患者不足以使此CRC修正式在α.1可行；即使未来8独立患者0伤害，一侧95%伤害率上界也为31.234%。这只是条件算术，本轮未打开确认集。
- Jaccard Eq9为所有有限集合成立的不等式，不能认证配准。K32 bootstrap/Holm打印统一p_H<.005的问题已定位；源码未核，不判其实际算法错。
- 本助手曾把表4的CI下界0.503误读为均值；放大原PDF确认0.519，已撤回“表间矛盾”。PowerShell inline Python引号丢失导致一次SyntaxError，另存脚本后渲染成功，失败均保留。

主要创新候选仍需MRI验证：充分适配之后的合法病灶动作余量，及相对同信息强控制的action-value—完整成本增益。泛阈值/配准评价和latent aggregation已有先例。详见 [原文笔记](PRIMARY_READING.md)、[后续控制](PATIENT_TASK_CONTROLS.md)、[CPU结果](cpu_audit_attempt01/receipt.json)。

最新实际poll bd10f3：raw7425、invocation累计新27225、累计wall62966.393889699946秒，session99542仍live，无terminal exit。GPU a226a6 free1394MiB，未启动新作业；RAM99,076,521,984 bytes、disk8,118,083,584 bytes储备通过，根.gitignore/environment.yml原SHA不变。未动原终端或其他PID，无新增MRI/标签/权重数组、神经/GPUforward、head/action标签；确认集/locked IXI保持关闭。goal active，经验证可发表MRI claim尚未达成。
