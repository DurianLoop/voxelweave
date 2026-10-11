# 六分支GPU图诊断结果与边界

[attempt03终态](attempt03/receipt.json)实际9897da exit0，session42442结束；[独立审核](terminal_audit_attempt01/receipt.json)实际09b462 exit0。开发VS-MC-RC-009、固定step2，两输入×三模式共12完整64×128×128patch；6次GPU forward、6次backward，全模块有限非零梯度，母GT/geometry配对，source与parent参数前后SHA一致，optimizer更新0、权重保存0。

所有分支peak reserved=2,334,130,176bytes，未超过原2.5GB限制。主程序elapsed48.774秒（不包含Python启动/模块import）；其中12patch候选+独立oracle累计39.029秒，6forward累计2.432秒，backward含重算累计.875秒，完整逐项费用在receipt/审核保存。此单病例不认证普遍速度或医学收益；6个crop loss只作finite graph诊断。未进行GPU/CPU完整FOV概率一致性资格。

[独立CPU synthetic资格](checkpointed_cpu_qualification_attempt01/receipt.json)2×1×16×24×32上原图与non-reentrant checkpointed图的全部输出、loss及全部parameter gradients逐位相同。该fixture不等同所有MRI上的独立gradient oracle。

失败都保留：[v1](attempt01/receipt.json)原CPU导入使CUDA_VISIBLE_DEVICES=-1，在CUDA初始化前停止，医学数组0；[v2](attempt02/receipt.json)恢复可见设备后，第一个完整batch forward触及本进程10%显存cap而OOM，没有完成forward/backward/update。v3只对本模型ConvBlock重计算，原source与两次失败不修改；完整batch/loss/FP32/参数命名保持。

下一步需完整AdamW状态/更新、训练terminal capture、完整FOV推理和独立数值/费用资格。当前graph已接近cap，不可凭空称optimizer必定可装下；也不能将checkpointed配置成功当成原未checkpointed runner成功。六臂整轮仍须完整35904先通过及磁盘准入。11GT parent仅能力诊断，严格LOPO cold-init；确认患者与lockedIXI均未打开。没有发表claim。
