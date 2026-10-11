# 覆盖×增强2×2：真实输入draw及坐标合同（训练前）

当前只做采样/坐标准备，网络前向0、训练0。输入仅已核开发患者012唯一系列/observed-only PCHIP/shared，支持代码、输入/label轴、上轮4000步BCE+Dice及其4000draw独立重放记录全部SHA绑定。不是新重建方法或患者确认。

固定seed20261004/4000updates。按原training_example逐项消耗RNG（包含one-patient/one-series integers(1)），记录z、两flip、rot90、scale/offset、原增强坐标patch位置；完整重建原gv/x/y/gt/location/sample并对全部4000项精确匹配旧draw SHA。原病例物理平面360×360，z分布沿用.5 foreground-voxel/.5 all-z，不改变loss/监督/augmentation分布。

2×2条件：原采样或逐z循环完整FOV tile覆盖，原增强bundle或none。原采样none采用原增强patch矩形经D4整数仿射的逆映射到未增强平面；因此同一draw实际监督空间支撑对应，不是跳过随机调用后重新抽patch。完整覆盖在未增强physical平面按row-major 16tile/stride96维护每z独立游标，每step连续两tile，再映射到增强坐标；none用原坐标。该选择细化旧准备中增强坐标游标，使覆盖两臂严格共用原空间支撑。

增强矩阵先行/列flip后np.rot90；矩形四角取整数像素中心坐标，变换或逆变换后min/max，确保128方patch完整、无out-of-FOV裁剪。独立reference使用编号的完整平面经D4变换，然后检查每个patch全部16384像素来源与局部变换一致；覆盖原生空间像素计数、每z/每tile曝光与foreground mass完整登记。取消增强是同时取消几何和强度bundle，不能把效果归于单一旋转或强度因素。

draw文件保存4000行和digest；校验先原随机primitive/旧4000SHA，再全部patch源坐标/目标与真实原输入。若精确旧baseline合同不能满足，新2×2必须四臂从头；若全部满足，允许旧baseline作为相同既定初始化/预算的已执行臂，另外三臂各4000新训练。原baseline不是新复制，不重复计update/call。

训练必须另立执行protocol并先完成本准备的独立核验，不据中间效果调整预算/病例/阈值。原19开发/4验证/8确认角色不变；这里仅012，不读验证/确认效果。CPU单线程below-normal、15GB/8GB底线、GPU/用户进程/locked IXI test不操作，所有新增只innovation/exist_ok=False。
