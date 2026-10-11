# 从头全视野/局部任务基线（训练前协议 v1）

前一轮是实质进展：19稀疏输入独立证明、四篇正文及两个失败CPU训练已完成。任务能力未证明；单012训练内Dice .555不足以验证重建方法。本轮继续推进真正可用的任务评价器，而不是将归档成功当科学确认。

预写新开发基线：标准coarse-to-fine全FOV与局部U-Net，不宣称新架构。随机初始化训练全部固定11开发患者19合格系列，包含已作开发检查的012/013；无预训练权重。4验证患者020/022/025/024（9系列）只用于最终能力验证，8确认保留患者禁止加载。当前先不启用最终科学split；所有同人时点同角色。训练患者均匀、患者内系列均匀，20,000updates，固定seed20261004，无早停，无中途验证/择checkpoint/阈值调整。

输入仅phase0/stride4真实observed MR经四邻raw PCHIP和observed_shared统计生成，不提供native隐藏MR。完整FOV在平面方向依实际spacing重采样到约.5mm，目标大小round(原大小×spacing/.5)，不使用label crop；图像bilinear，监督mask area平均（仅训练监督），不把这称真实组织占比gold standard。z输出仍原生层；5通道在当前z物理±2/±1/0mm处由同稀疏重建volume线性取样，边缘clamp。最终预测概率映回原生RCZ网格再.5阈值，所有指标在原生GT上计算。任务输入重采样不声称保留原强度anchors；原重建接口仍保留anchors。

全FOV分支：5×256×256输入，双3×3 Conv+GroupNorm(4)+ReLU，通道8/16/32/64/128、4 max-pool，bilinear上采样/skip；末层8通道特征与1logit。局部分支：5真实稀疏上下文通道+全FOV8特征+1logit，用align_corners=False grid_sample从全视野feature对应区域采样；通道16/32/64/128、3 max-pool和bilinear/skip，1logit输出。无真值提示/最大成分后处理，局部预测是最后输出，不硬门控至粗mask。

每update：选择1患者/1系列，z以.5概率从训练原生GT前景体素均匀取一个的z、否则所有z均匀。该z完整5通道视野和训练soft label一起作独立左右/上下flip及90度整数旋转；强度乘U(.9,1.1)加U(-.1,.1)。然后2个128×128局部patch：一个以该z监督前景像素为中心随机±32平移（该z无前景则均匀），一个中心在全FOV均匀。GT只决定训练采样/损失，不进入推断。

局部loss=BCEWithLogits均值+soft Dice（两patch整体smooth1），全FOV辅助loss为同公式，总loss=local+.5global。AdamW lr=.001/weight_decay=.0001、cosine衰减到.0001，20,000步；不梯度裁断，非有限梯度停止保留失败attempt。每100步记loss/lr/资源/patient采样，最后checkpoint保存初/终权重SHA、所有训练身份、代码/协议/数据SHA；GPU初始化禁止。

推断每个z先完整FOV一次，再以128patch、stride96覆盖全FOV，最后tile贴边、等权概率平均；影像尺寸小于128则只按影像边界padding。无标签crop、无人工侧别或确认/验证GT提示，不修改阈值。评价9验证系列的raw PCHIP和raw linear两固定条件，主为训练匹配PCHIP。raw linear不是已训练匹配对照，不能拿小差距宣布重建效能。

验证前先准备9真实observed-only包、raw两插值/统计/RAS/label轴的生产及独立重读证明；新allowlist仅11开发+4验证，明确拒绝8确认及其他患者。验证影像与标签可做输入资格证明，但在最后weights冻结之前不运行任务效果。独立指标采用source label signed permutation、逐slice编码counts、cKDTree物理surface；最后checkpoint对每验证条件至少3完整z-plane重放（不是独立模型训练）。

预写能力门槛：以系列指标先在同患者均值，再4患者均值；主PCHIP mean full Dice≥.70、mean supported missing Dice≥.65、mean full recall≥.70、mean full abs relative volume error≤.50，且4/4患者full/missing Dice>0、无系列完全漏检。full/missing/anchors/tail、precision/recall、物理ASSD/HD95及空/undefined全部报告；不删小病灶/不按结果挑系列。通过只允许进一步native能力/公平6×5矩阵，不等于新方法成功或发表claim。native参考能力本轮不虚报，正式矩阵仍需实现独立完整输入控制。

先10步仅合成张量/梯度估时，若单步>2秒或GPU初始化则停止，不改预算强行推进。正式训练自身CPU单线程below-normal，每100步磁盘≥15GB/内存≥8GB，cache仅RAM，新增训练/预测文件<100MB，观测包<500MB。本进程不枚举/中断用户训练、不使用GPU。长任务按实际session持续poll，不因观察超时重启；可在等待中读论文和实现验证输入，但不并行运行第二个重训练任务。

若门槛失败，此固定基线不作重建评价器，下一开发需另写协议，验证已看过后仍只是验证，不转确认。若通过，冻结同容量/预算并行比较native/raw/mixed曝光和统计条件；将直接任务/随机分辨率作为既有方法强对照，最后新可观测修正须8保留患者确认和独立任务网络一致证据。科学确认当前0，goal active。
