# 新增强原型的真实开发输入资格，执行前冻结

前置：8fb81e synthetic形状/物理坐标/32点oracle全部通过，49f6f4 checker/wide补核通过；旧source与新模块不改。此新协议允许有限加载原11开发患者/19series已认证MRI及人工标签，用于准备可执行训练入口；不是模型医学效果验证。此前纯文献/CPUtoy协议继续保留其自身无数组范围。

每series依旧读取原native_reference与合法observed-PCHIP两输入，以及同v2 physical label；逐位array SHA匹配原QPATH资格cache。母batch与旧sample_batch/batch_rng(19998+i)、两输入母GT/geometry/foreground pivot匹配。固定强制enabled的两个stress参数（三轴15,-11,8/scale.85；-12,9,-7/scale1.15），两输入完全相同；这是入口stress，不冒充当前训练真实随机augmentation或预算。

各batch先图像roundtrip再原intensity primitives(i)；labels保持母GT逐位一致且forced-FG仍为1，不做二值warp。检查float32、finite、shape、完整GT/geometry/pivots/theta/强度配对、不修改母input。依旧同observed stats/真实spacing。记录image change、resampling calls与耗时，保留每series包括困难病灶。无网络state/forward、训练更新或新医学Dice，不根据图像变化判实际检测改善。

只CPU1/interop1/below-normal，wall<=600秒，磁盘/RAM各8GB储备，整个新stage<=5MB；一次一个series/一个input，不保存MRI/GT/概率体积或新cache，只小JSONreceipt。持续resource guard，失败保留并停止，无retry/删除旧输出。所有病例限定development_cases断言的11/19；不加载4验证或8未见确认与lockedIXI，不执行作者代码，不初始化CUDA。

原训练session29823保持，不迁移/重启/改源。未来是否训练新增强须另立全matched配方/预算/完整评价合同，本资格通过不等于能力门槛、增强收益或发表claim。
