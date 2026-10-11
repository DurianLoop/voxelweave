# 新候选完整开发队列数值资格（执行前冻结）

沿用原始 frozen metadata 的两母 patch、stress primitive 和强度 primitive，不重新选择病例或位置。11 开发患者、19 series、native_reference/raw_pchip 两输入、throughplane/inplane/allaxes 三模式，共 228 个完整 64×128×128 target。MRI cache 必须与既有 QPATH SHA 一致；不读取 GT 数组、模型或未见确认集。

另外重新执行原 40 个完整强度 synthetic fields，以及原 270 个分辨率 synthetic fields（包含完整百万体素 target、singleton、padding、flip、constant/ramp/texture）；补原首次失败的三模式与 v2 已知失败模式，共 542 个 field。另补 direct oracle 的九个 tiny/dynamic-range 精确点，不把原 144 tiny 当完整资格。

candidate 使用已绑定 certified_resolution.py；独立 direct oracle 使用已绑定 direct_interval_reference.py/exact_tensor_reference.py。不得编辑这些文件。完整 field 插值图像要求逐位一致，support binary 零差，inactive/padding 与原 baseline 逐位一致。强度生产 v2 与原独立强度 oracle 保持 3e-6；坐标 rational stencil 与独立 Fraction/原浮点坐标的误差保持 3e-12。保存 fallback 数量、完整耗时、资源及失败字段，不以 float64 或更宽阈值掩盖失败。

每一个 active 分辨率 field 的 raw 结果另按每轴四个均匀有效坐标的预设笛卡尔积（最多 64 点）核 Fraction 精确值、两实现区间包围；这只是额外精确探针，完整体素比较仍执行。所有原 40 强度 synthetic fields 本来没有分辨率步骤，按同一原定义重跑。

CPU 1、interop 1、below-normal；CUDA 不初始化，wall 1800 秒。本目录累计 <=2MB，磁盘和 RAM 各保留十进制 8GB，另保留本目录 2MB、原医学 3MB、开发 2.8MB。只写 innovation，不安装、不委派、不枚举或修改其他 PID。中途失败原样保存，新 attempt/新脚本修复，不能覆盖已绑定源码。

这不等于从头 35904 完整 schedule 资格；全部通过并记录实际工具 exit0、独立终态审核之后才准备下一资格。当前 new_production_selected=false、training_ready=false，科研 goal active，发表 claim 未证实。全 11GT parent 禁止作严格 LOPO 外折初始化。
