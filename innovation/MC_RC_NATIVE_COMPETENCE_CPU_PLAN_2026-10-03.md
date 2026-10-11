# 16 系列冻结模型 native 能力对照：新的 CPU 合同

本合同在读取新的完整 native MR 像素及新分割评分前冻结。目的为区分「冻结模型在当前来源本来就不能定位」与「稀疏输入进一步损害定位」；两者也可能同时发生。不是新 SR 方法的优势试验，不是临床安全认证。

名单固定由 mc_rc_source_denominator_correction/attempt_01.json 提供的 16 合格系列/8 开发患者，24 来源中其他8个拒绝/pending保留。旧15主实验保持原合同；遗漏002第二时点属于同一开发患者，补做相同 phase0/raw-PCHIP 冻结预测和理想观测区域传播，单独报告并追加到16系列描述性结果。不能把新时间点当独立确认、不能调已有2mm半径救失败。

固定模型、RAS方向、NormalizeIntensity、Gaussian 384×384×64 滑窗、CPU single-thread/interop1、argmax、官方checkpoint和认证tuple inferer与旧 sparse 实验相同。旧15 affine/spacing沿用其原合同；遗漏系列用独立几何修正后的 fitted affine/integer-grid。没有label crop、空间resample、checkpoint挑选、threshold变化或task微调。Native参考读取全部真实 MR planes；它的隐藏plane像素只作为指定完整采集参考，不输入 sparse 预测或后续门控。

仅在旧15预测独立 raw-anchor/Hermite/全模型 replay proof 成功（errors=[]且绑定当前结果SHA256）后执行。单worker顺序处理16系列。每系列先只解码anchors并核旧input hash；遗漏系列先由anchors构造display/保存预测，再读真值与 native。随后全部native像素解码，核identity/SOP/shape/finite/同观测数组，再跑一次native前向。Native预测保存完成后才读官方label评分。旧15 sparse预测复用经完整重放认证的文件，不重复推断。每系列不超过250MB float32 native，单个label slab≤32MB；磁盘≥15GB/可用内存≥8GB，低优先级、禁CUDA，无自动retry或静默换源。

固定描述性主端点：全16来源、每位患者内系列等权的完整缺层 Dice(native)−Dice(sparse raw-PCHIP)，再8患者等权。并列完整体积/真实anchors任务Dice、recall、precision，逐系列zero-TP/empty-prediction；「missing」严格是phase0两真实anchors之间的内部759旧目标与遗漏新增目标，unsupported tail只在full统计。没有把 native自动分割当无误真值，所有Dice对官方人工label。

固定ROI比较为native预测在observed planes并集+2mm vs sparse同一规则，均报告foreground/boundary/tile recall、ROI/tile面积和原门槛。Native ROI是能力对照，需要完整MR，不能称可部署仅观测策略。遗漏系列另做真值anchor并集+2mm的理想输入诊断。只解释固定配置的适用性：native也失败时不能把sparse失败全归为抽层；native成功/sparse失败也不自动证明哪个采集参数导致差异。

产物：逐源contract/hash/解码范围、native/sparse预测、全部指标和完整患者汇总、异常记录；成功目录不可覆盖。必须再从原ZIP和label独立重建 native 输入、全部16 CPU前向重放、显式native坐标映射、disk ROI计数及患者平均后才能把新native结果标为已复核。当前另有原VS-SEG session83910继续；队列等待不重启/终止该进程。确认患者仍0，发表claim未达成。
