# 真实开发上下文入口与作者实现接续（运行前）

上一goal轮为progress：两篇作者原文核读、38patch支持/19label重叠及InstanceNorm合成反例改变了下一步决策，归档已实际1698d0 exit0，累计6224。当前f503f6仍含session29823、第二native_reference_spatial2090/2992；第一intensity已完成2992，另外两支未观察完成。原四臂配方/device=cpu保持，不干预/枚举其他PID；GPU授权有效，新阶段仍沿已冻8192MiB起跑储备。

本轮先弥补真实halo MRI入口尚未资格的缺口。仅11开发患者19series，使用已认证native_reference和合法observed-only raw-PCHIP两输入；独立完整source/hash及physical cache/hash必须与此前资格匹配。38独特几何、两输入76个fields，64×128×128 target，原stress primitives和pivot/start/flips不改；不是独立76病人/几何。

新API只接值和source-validity，不接GT：source-validity表示**unpadded resampled image domain**，不是raw-PCHIP每格点真实采集过。只从现有physical cache合法坐标取值；未存在源坐标存明确0+validity0，该值是算子填充值，不能称补造真实halo、信息无损或完全支持的增强。缓存内padding按旧基本强度scale/shift重放，但validity仍0。全部source box允许超过域，仅对实有值读取，须传递支持字段并明确mask/identity策略尚未冻结，当前不训练。

生产context extraction使用向量坐标索引，独立extract用合法缓存交集切片+翻转插入；逐位相等。生产双Torch float64 grid_sample与独立物理旋转矩阵/SciPy affine_transform全目标体素重算，比对全部76 MRI fields，强度最大误差≤3e-6（未添加最终gamma/bias/noise），坐标≤3e-12，支持二值差0、固定支持mask SHA匹配前轮unpadded-domain结果。原裁剪baseline与crop-only旧实现须先匹配。GT只复原原mother label，独立image算子不读GT，标签SHA保持；不据GT挑增强或删患者。

记录cache加载、context提取、双插值、support、独立重算时间和中间array体积。CPU1/低优先级、wall900秒、stage5MB、磁盘/RAM各8GB储备，零模型/患者forward/训练更新，不安装依赖、不委派。4已见验证、8未见确认12series和lockedIXI像素均不读。结果是真实入口资格和普通baseline准备，不是患者分割收益、发表claim或完整2992训练分布资格。

作者代码若有合法公开入口，可新只读GET限定版本文件以核查VINN采样或2026ensemble公式/OOF语义；取得来源不等于读完/执行，不下载数据或模型，不用论文接口发送用户影像。本轮不改旧冻结来源或根配置。
