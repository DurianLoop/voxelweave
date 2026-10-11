# 全开发序列的两步优化器/组件费用资格

上一轮为实质progress：六真实GPU首步、独立公式/终态审核以及六臂入口完成，7291冻结链。唯一长时间live44317本轮工具再次确认仍live；此新阶段与它独立，不冒充完整35904终态或正式训练。

覆盖全部11开发患者19series、两输入×三模式，共114个reset分支。每分支原对应19998 parent开始，连续两次AdamW更新，计划228updates/456完整64×128×128patch。每series选择原2992 schedule中第一个两patch primitive均enabled的step，再取该series下一次原schedule曝光；selection只读既有journal/metadata，不读GT/预测效果。此选择用于最少19series组件/状态资格，不代表2992训练轨迹或患者级效应实验。

母GT、crop/flip、primitive及强度顺序沿原source；两inputs所有label/geometry逐项匹配原5984 frozen journal。候选certified_resolution逐patch与独立collapsed reference核全target逐位相同、support/domain二值零差、padding逐位不变；原强度/坐标gate保持。完整35904仍单独待终态。

CheckpointedTaskUNet3D；FP32/TF32off/deterministic；AdamW lr1e-4/decay1e-4/betas(.9,.999)/eps1e-8/foreach=False/fused=False。用真实GPU梯度，独立NumPy float64延续首/次步m/v、bias correction及weight decay，核全部54参数tensor，绝对gate3e-6。该检查条件在实际梯度上，不声称独立神经梯度oracle。每步BytesIO保存model+optimizer并重载，全部tensor逐位比较；不保存磁盘训练权重、不声明恢复完整训练资格。

费用分开记录病例加载/采样/分辨率候选/独立reference/强度/transfer/forward/loss/backward/AdamW/同步/数值比较/内存capture/日志。此组件实测覆盖19series，不能称测完全部17952正式更新或全FOV；后续wall只按coverage实测与完整schedule numeric耗时做有注明不确定性的forecast。

GPU起始free8192MiB/本进程10%cap/peak reserved<=2.5GB/runtime free4GB，CPU1/interop1/below-normal，RAM/disk各reserve8GB。新stage2MB、其他既有allowance18.8MB不降低、wall7200秒；journal gzip cap1.4MB。查询仅GPU汇总，不枚举/修改其他PID、不动原终端训练，不安装、不委派、不删历史。只新增innovation文件，旧冻结/执行源不改。

全部开发病例source/parent SHA前后核验。4已见验证不新增读像素或GT；8未见确认12series/lockedIXI关闭。114分支/228步必须全部有真实terminal再独立审核；前缀/局部成功不认证全scope。parent含11GT只可开发能力诊断，严格LOPO cold-init。原六医学gate不降，无发表claim。
