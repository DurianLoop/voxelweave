# 保留原网格细节的固定残差相加：开发对照

本计划在45CISS正式结果及112次要统计已核读后写出，属于结果后开发探索，不改变原主比较。HAT相对pipelinePCHIP的主Dice上升必须保留；rawPCHIP平均Dice较高只作为强基线敏感性，不提升为新的预注册主claim。

固定候选 `transfer = raw_PCHIP + (HAT - pipeline_PCHIP)`，alpha=1，原生float32输出，不新增clip。真实anchors及外推tail沿用已有输出。仅使用已缓存重建图及observed-only构造的两解析基底，完整native MR/label只用于核对与评价。残差相加/detail addback是普通对照，不作为新模块、新理论或可部署风险保证。

固定全量开发材料：既有MC-RC001/002/004/005/006的五个首时点HAT缓存，以及已见作者training病例VS-SEG001的原七条件缓存。它们都已用于研究，独立确认0；不使用新45队列再拟合、挑alpha或逐患者选公式。全部六项均报告，不因首失败跳过其余。MC-RC只评价既有全部240缺层；VS-SEG001既有全部57缺层。两任务来源不能自动合并成独立患者确认。

候选先过逐项图像门槛：完整支持域target-equal NMSE相对rawPCHIP与HAT中较好者至少0.1dB提升，同时lesion的target-equal与pixel-weighted NMSE均≤rawPCHIP（数值容差1e-12）。所有六项必须通过才能进入新的任务推断/确认准备；若任一失败，停止这个固定alpha=1对照，不后调clipping/alpha/ROI救结果。该严格开发门槛不是统计或临床安全认证。

原raw/pipeline/HAT端点先从缓存/原MR重新评分并核对旧证据；保存candidate数组SHA、全部层SSE/分母和逐项门槛。独立复核用单层逐ROI切片、另一种`HAT + (raw - pipeline)`表达及math.fsum汇总，候选float32量化需使用同一定义逐位比对。共享已有native解码/坐标与解析构造，独立性范围明示；无新神经推断、GPU、locked IXI test或环境修改。

执行：`D:\conda\envs\MRI\python.exe -B innovation\experiments\residual_addback_cpu.py`。全部候选均由可得重建生成，没有真值系数选择；若图像门槛通过，任务Dice仍待单独冻结和执行，不能把图像指标替代任务成功。
