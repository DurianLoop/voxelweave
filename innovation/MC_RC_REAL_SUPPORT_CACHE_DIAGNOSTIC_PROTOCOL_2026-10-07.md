# 19开发系列的真实标签支持与缓存成本：事前协议

本协议先于新的标签值读取、统计和结果查看。只纳入已冻结开发准备中的全部19系列/11患者（001/002/004/005/006/007/009/010/011/012/013），不按体积、位置或计算节省挑病例。已有15系列的phase0/1/2/3标签接触审计保留；本实验不重复主张病灶可见性。4位已见验证、8位未见确认和locked IXI保持关闭；原session99542继续，绝不重启训练或读取中间MRI效果。

只读开发官方二值标签和既有几何metadata。使用冻结read_supervised_label的逐4层slab、整数signed-axis变换、原文件SHA及前景数。新MR像素、MRI缓存、模型checkpoint、前向和GPU调用均为0。只降低自身优先级，CPU4/interop1、不初始化CUDA；既有RAM8GB/磁盘8GB储备，新增输出小于5MB，执行最多900秒。失败如实保存，重试必须新attempt/source。

固定phase0/x4、最后观测之前的非观测层。只定义两个**GT oracle诊断支持**：缺层真实前景；同前景在原生row/column方向Chebyshev半径2体素膨胀的边界包络（不沿z膨胀）。不是部署ROI、不是最优任务修改支持，也不是任何有效修正的下界；错误阳性、远处结构和IN耦合都可能要求别的支持。

支持经过原physical_mr的0.5mm中心网格、trilinear/align_corners=False与零padding，取正值。不能用nearest标签映射代替MR修改支持映射。正支持是假设在这些位置施加同号非零修改时的几何依赖；不读取或证明真实MRI差分，混合符号相消和float舍入可能改变实际非零差分。固定原PATCH=(64,128,128)、50%重叠、原tile排序及每2tile的完整batch；触及tile就重算其原batch，不重排或缩batch。

对每种支持报告整个缺层联合支持，以及每个非空缺层的单层支持。非空层全列，不择最大/最有利层。记录原生/physical支持体素、受影响tile/batch的ID、重算tile、完整N与重算k、条件forward节省1-k/N、5个相同支持替代动作含缓存初始化的调用比(N+5k)/(5N)、严格节省所需最少动作数floor(N/(N-k))+1（k=N时null）。5仅为固定说明情景，不是已经测量的5个模型动作。

单层支持联合必须等于整支持的受影响tile/batch集合；额外报告所有非空层分开求值的sum(k_z)与一次联合求值的k_union，说明重叠依赖而非增益相加。全部汇总患者内series等权、患者间等权；计算total另求全部series的调用总数，不用体素/时间点冒充独立患者。不做显著性测试。

独立核验从原NIfTI按transpose/flip重新读标签，避开生产坐标scatter；使用有理数pixel-center上下邻居的Boolean OR构造resampling正支持，避开torch插值；独立重建lattice/tile/batch、每个plane的原生依赖集合，核所有计数、ID、hash、比值与患者汇总。独立性限于实现与重放，不宣称独立标注/临床确认。

决策：若真实联合支持几乎总使全部batch失效，降级“整个病灶一次修正靠缓存降成本”，保留更细单层/小区域待评；若有条件节省空间，也只有在原两臂训练真实exit0及56FOV/6gates/strict通过后，才测真实MRI差分、等价和总延迟。必须计observed读取、初始化/存储、SR生成、探索、特征、门控、传输、推断、聚合及postprocess；forward数量不等于延迟。SIGE/DeltaCNN已读先例排除缓存首创。本诊断不产生Dice收益、风险保证或可发表新claim。
