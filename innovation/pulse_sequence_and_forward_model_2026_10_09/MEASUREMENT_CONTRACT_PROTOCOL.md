# 点抽层与层厚测量：预定非医疗机制核验

只验证观测合同，既有训练/输入保持不变。当前 `experiments/mc_rc_3d_baseline_2026_10_07.py` 的 `range(0,native_shape[2],4)` 是既有体素的点抽层，不能据此把 anchor 保持延伸为任意 scanner 测量保持。box 层厚是假设，不是患者或扫描仪校准。

先给精确反例：1mm 分段常数体素，box 测量 center0/thickness4；仅 z1=1，则测量 y=1/4。把 y 只写到 z0，点等式成立，但 box 重测为1/16，残差3/16。用 Fraction 独立区间积分核验全部权重。

完整预定扫：61 个 latent cells，中心整数 -30..30；spacing2/3/4/6，每个整数 phase0..spacing-1；thickness1/2/3/4/5/6；测量中心位于 -24..24。12 个固定 latent：九个 z=-4..4 单体素 impulse、五体素 plateau、三角轮廓、交替轮廓。共90几何×12=1080案例，零信号/正负结果全部保留，不按效果筛选。float overlap 与独立 Fraction 区间积分比较<=2e-14，点插值与独立有理数线性插值比较<=2e-14。点保持须逐位零差；box residual 是结果，不能作为失败删除。

从点插值出发的标准最小范数测量投影 `x+A.T solve(A A.T,y-Ax)` 只作合同控制，独立 fsum 重测 residual<=2e-14，不宣称新算法、非负或解剖合理。记录中心改变量、范围越界和求解费用；测量一致也不能证明病灶保持或重建真值准确。

另对连续球体 axial 面积 `pi max(r²-(z-offset)²,0)` 做 slice 积分资格：radius1/2/3/5，offset0/0.25/0.5/0.75，spacing2/3/4/6，thickness1..6，中心-12..12，共384几何/球体组；解析原函数与 SciPy quad 独立积分全部对照，abs error<=2e-12。它与 voxelized latent 是两个不同实验，不能混数。

CPU 单线程、当前进程 below-normal、wall60s，输出<=600KB，本目录总量<=3MB；磁盘/RAM各8,000,000,000 bytes另保留原医学3MB及完整数值2MB。不安装依赖、不初始化CUDA、不触及其他PID，不读医学影像/GT/checkpoints。8确认患者/12series和lockedIXI关闭。所有失败原样保存，研究goal继续active。
