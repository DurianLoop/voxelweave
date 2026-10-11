# 原网格与256网格插值顺序：固定完整45开发诊断

这是完整45CISS结果核读后的结果后探索，不是原主要确认，也不复活已失败的HAT−pipelinePCHIP负向claim。新问题是：raw/pipeline解析对照的差异，是否包含实际裁剪和PCHIP与面内重采样的顺序效应。只用既有45主名单，全部内部缺层、两原参考，TSE248不并入；这45人已见，不声称新方法独立确认。

两插值核各三个固定条件：原raw_linear/raw_pchip；原pipeline_linear/pipeline_pchip；新post_resize_linear/post_resize_pchip。新post先构造原生float32 raw预测，使用同一observed-only min/max、1e-8分母、同一skimage resize默认order/clip及anti_aliasing将预测下采样至256，再显式clip[0,1]，再回到原网格并逆归一化。anchors和末端tail逐位沿用原raw。它只使用重建和真实观测构造，完整native只用于评价。post分支额外float32量化写清楚，不声称理想实数交换性。

四个已有解析体积每患者必须重新生成并与旧reconstructed_array_sha256逐位hash一致，原全部图像端点先重算并核旧记录。所有45均纳入，source/proof/合同链固定，失败保留、不换病例。新三个条件的所有层支持域、originalJSON病灶、RT病灶SSE/像素/null与两种患者加权都保存。原图像NMSE仍用旧运行时的float32差后float64归一化定义；方法间order差异另用float64差，区别明确。

每核记录pipeline和post相对raw的差、pipeline相对post的差，精确描述性分解pipeline−raw=(post−raw)+(pipeline−post)。三域两权重两核三比较共36端点，全部保存45等权患者/5,000draw/seed20261031的描述性95%区间，无familywise成功claim。保留逐患者与逐层效应，不能把恒等式当因果中介分析或新理论。

同时统计显式clip改动的像素/层及越界幅度（before与post各两核），方法间输出差异的支持域/病灶RMSE和最大绝对差/observed-range。线性解释门槛预写为全部患者最大归一化order差≤1e-6；PCHIP另报告超过此门槛的人数，不强制寻找阳性。若clip未激活，则不能把这些解析对照差异归因显式clip；若PCHIP order差很小，也不据此安排昂贵任务推断。skimage内部clip与抗混叠正核另保留，显式clip0不意味着所有处理操作都线性。

独立复核随后用已有独立Hermite PCHIP/显式linear、逐层ROI切片dot-product及math.fsum汇总、另一方式构造post、标量患者bootstrap/手写linear分位检查。共享原生解码/网格、resize与原RNG，不宣称全软件栈独立。原模型权重未调用，不做新的神经/任务推断，不用GPU，不碰用户终端训练、locked IXI test、根环境。CPU一线程、仅自己below-normal、≥15GB磁盘及≥8GB可用内存。

执行：`D:\conda\envs\MRI\python.exe -B innovation\experiments\vs_seg_resampling_order_cpu.py`。只有全45及独立proof完成后才核读汇总。后续若要讨论任务机制，须另写有区分力的新任务对照/另一来源确认；图像差异不能代替Dice或解剖/临床因果结论。
