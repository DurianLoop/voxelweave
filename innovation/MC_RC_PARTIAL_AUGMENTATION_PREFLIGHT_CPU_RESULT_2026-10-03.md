# 两个未训练增强因素臂：实际输入预检通过

[零前向预检](experiments/mc_rc_partial_augmentation_development_cpu_preflight/attempt_01.json)的session72028已实际exit0，complete=true/errors=[]。11开发患者19系列，每系列32 draw，共608旧结束RNG/旧增强example/旧无增强example/冻结primitive完全一致；仅几何与仅强度的1216真实输入SHA和1216标签/监督身份检查通过；1216完整128×128源像素patch映射通过。网络前向0、训练0、验证/确认效果0。

新接口为[partial support](experiments/mc_rc_partial_augmentation_cpu_support.py)，[协议](MC_RC_PARTIAL_AUGMENTATION_PREFLIGHT_CPU_PROTOCOL_2026-10-03.md)在无增强20k仍live且效果未取得时冻结。primitive/context生成与torch插值库共用；旧sampler、独立tensor assembly和编号整平面像素支撑分别核验，不声称完全独立算法。

仅几何复用旧增强空间和patch坐标、去掉scale/shift；仅强度复用原空间逆映射patch、保留scale/shift。它们不增加coverage或改变被采到的源像素。不把关闭整个bundle的效果归给某个因素，也不把预检通过当模型效果。

两个新训练尚未运行；若无增强能力不足，需先固定单独训练/完整评价合同，且当前训练/核验/评价实际结束后才启动。若当前能力通过，优先原生控制与公平矩阵。增强拆分属于任务能力开发，不是MRI重建新方法。
