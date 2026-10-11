# 独立参考实现的费用优化候选（非科研创新）

当前 v1 direct oracle 逐项展开 fine-grid tensor-product，allaxes 最多64项，完整35904资格费用可能很高。新候选仍用 exact_tensor_reference 的独立合并有理数权重，只按轴累加（每轴最多4项），按输出/输入长度比确定轴顺序以降低中间数组；区间向外舍入，歧义点仍用独立 Fraction + bit binary search。数学算子不变；不调用 certified candidate 的权重、区间或舍入 fallback。不改已绑定 v1 文件，不降低门槛。

先重新跑原144 tiny fixture，与 candidate、v1 direct、exact tensor逐位核；每有效点核新上下界包含 Fraction。补9个tiny/dynamic-range点及原 v2 失败 geometry 的throughplane/inplane/allaxes三个完整百万体素场，与 v1和candidate逐位比较、gamma v2/原独立强度reference保持3e-6；每场预设64个有效坐标核 Fraction。费用记录包括新旧所有计算。

这一预试通过不代完整11患者19series/542资格，更不代35904。全部队列尚需另冻结并运行，之后费用准入才选完整harness。本阶段不选新生产、不训练、不初始化CUDA，不读取GT/model/未见确认数据。CPU1/below-normal，wall900秒，本阶段2MB，磁盘/RAM8GB，另本阶段2MB、原数值阶段2MB、文献2MB、回收2MB、医学3MB、开发2.8MB；只innovation。
