# 新读三篇、作者实现与下一科研判断

本批新增主文3篇，实际核读341提取块（DG-TTA79、UAF-AIMM178、PEIL84）及11表（DG-TTA4、UAF-AIMM7）。块含标题、摘要、正文、图注和声明，不等于341个独立实验。保留所有截断工具返回；相应遗漏用更短范围补读。图像像素、独立补充材料未读，作者模型未运行。PEIL公式在XML中是GIF，抽取文本没有其符号；已检查原XML确认这个限制，不能声称两式已完整阅读。来源均核DOI/PMCID及保存SHA。

## DG-TTA：强泛化先行，自适应收益必须单独证明

[DG-TTA](https://doi.org/10.3390/s25175603)，2025。主要是CT→MRI的腹部/心脏/脊柱器官任务，不是CISS病灶或SR动作收益。原文36–38将GIN随机浅卷积增强与12通道SSC自相似descriptor结合；39–47单病例两空间增强分支回到原坐标并mask掉反变换新边界，d=2 consistency Dice；12步、每步积累16patch、3fold ensemble，AdamW 1e-5/decay .01。最佳消融65仅A分支反传；不能把正文双分支表达自动实现为两边同时梯度。

Table1普通nnU-Net跨域Dice32.0，GIN76.3、SSC76.1、GIN+SSC78.6。GIN适应后77.4，但HD95由27.9变37.1；GIN+SSC适应后78.2（−.4），HD9517.9→17.2。Table3 TS→AMOS的GIN81.2→81.4，HD95 11.8→14.2；TS→SPINE的GIN73.2→72.8，HD95 11.7→9.7。单指标改善不能认证整体病灶安全或动作净收益。Table1 gain多以32.0共同reference计算，不能将NNUNET BN适应后的“+36.8”误作该模型自身4.8→68.8（实际+64.0）的差。

58/72报告15.3h训练、V100上每fold1.7min、3fold5.2min/scan。费用须包括重置/所有patch与反传、descriptor准备和ensemble完整推理。74明确无GT的可靠停止准则仍未解决且更多适应可能降分。47的12步不是已认证任何病人都值得执行的决策规则。初始强增强消去动作余量是合法负结果。

主文27对TS/SPINE标签约定作prediction邻域mask裁剪；不是原医学GT原样无处理的全部task。TableA1列BTCV原始50病例，而17的实际实验为30标注病例20/10；各自分母要区分。表格范围不自动等同实际test病例清单。原文对应器官标签，未报告本项目要求的病灶FN/FP/检出门槛。

## UAF-AIMM：不确定性特征补偿与轻量自适应已有直接先例

[UAF-AIMM](https://doi.org/10.3389/fnins.2026.1828237)，2026。BraTS T1/T2/FLAIR→pseudo-T1ce feature、三尺度1×1×1 mapper、T1ce teacher supervision、MC K=10、方差门控、normalization-affine-only entropy自适应已成组合先例。92–96独立冻结T1ce teacher、mapper20epoch后冻结；100–106还写aux distillation/variance损失，实际哪些可训练参数收到该项梯度需作者代码核实，不能自动认定有效或错误。

Table5 Avg Dice83.35→86.87(mapper)→88.73(+UAA)→89.20(+SITA)，最后自适应增量.47；不能把83.35→89.20全部归自适应或方差。训练期真实T1ce监督有额外信息/生成费用，是适配对照时必须对齐的条件。本项目单轴缺层，不等同缺一种MRI对比序列。

保留主文内部待核差异：115说baseline一般full-modality训练后missing-channel处理，120说所有方法同三种可用输入训练/评价；118用96³patch，122用128³；132 SegResNet HD95写12.45，表2/5为15.20；Table7为89.20→86.40/87.90，164–165正文写90.30→87.50/89.00；171说T1+FLAIR dual missing但表6实际列T1+T1ce与T1ce+FLAIR。不得自行择最好数字或补齐“官方split”。7:3验证集用于多个模型/超参数比较，不能升级为本项目未见确认患者。

式9 A=sigmoid(−(alpha·variance+beta))的alpha/beta仅说learnable，已读原文未给alpha>0约束。新CPU诊断确认负alpha会随方差上升增大gate；不推断作者实际学到负值。Table3/4提供MC/SITA运行时间，但未逐项拆teacher、mapper准备、每window MC、adapt forward/backward与最终推理，不能据此把本项目全费用设为0。173承认entropy可能使小病灶退化到背景，175把selective triggering列为未来方向；仅提出按不确定性触发自适应并非足够新claim。

## PEIL：重建最优参数不保证物理参数真值，也不是病灶动作收益

[PEIL](https://doi.org/10.1093/nsr/nwag508)，2026。估计显式solver conditioning，固定可微inverse solver，用signal recovery监督而非参数标签，已经有“参数按下游效用而非truth选择”的直接先例。主要无线CFO/CSI实验；MRI是fastMRI knee多coil、4×/8×，0.51M estimator，固定15-iteration CG，另外输出image-domain reference和regularization weight及辅助multi-coil consistency/double-well；不是只有coil sensitivity一项或不需重建target监督。

9/41强调solver相关的局部非辨识集合与物理真值不一致；固定插值近似让协调偏差改善无线SER。Oracle-ref LS只是真参数送入同一近似插值流程，另有analytic Oracle Bound；超前者不是超信息论oracle。33–37 MRI比Deep J-Sense、U-Net、TV-SENSE好，但VarNet PSNR/NMSE更好。完整指标TableS1、成本S3、方法S1–S6在未读补充材料，不能据主文填数或认证速度。

新复数toy验证S'=a exp(i phi)S、x'=x/(a exp(i phi))保持观测，误差约4.97e-16而参数改变。这只是gauge反例，不复现作者CG/正则，也不能直接类推CISS的PSF可辨识性。对本项目的实质要求是：不要以采集参数估计更准/数据一致性更好代实际paired病灶净收益。

## 两个作者repo的核查范围

Phys_Seg固定commit `7adc65d7b228b3a5702acfa9e6d0494d6b4c2dee`。完整读README27行、network_architecture156行、utils123行及predict_case的定向片段。源码确认两FC层的physics encoding送入第一pool之后和penultimate decoder之前；MPRAGE4项、SPGR6项转换在predict_case51–68。SPGR源码用TR/TE指数与FA正弦，不能把主文的exp(−TI)字面表达当实际执行。README引用早期2020/2021稿、tree主要为推理；本次没有取得2023期刊的stratification loss训练代码，因此主文式1/2的负号仍不能依该repo定案。完整data_loading和全部predict_case未读，不计为全文源码阅读。utils有下载/删除参数路径，未执行。

AMDU固定commit `25225a808b6a363c48be705df0c6a06996bf035e`。完整读models184行，KL variant8行；periodic与base trainer只核相关片段。models119–125是正KL(uniform||prediction)，不是字面负KL；base823 classifier feature detach，859–871 confusion不detach且encoder optimizer更新。296–393的optimizer作用于对应encoder stages。新CPU按独立短公式复核梯度方向与隔离，不执行作者repo。当前下载到的periodic variant是warm-up后固定batch轮换，不是已核完论文adaptive accuracy/patience训练；不能把它直接命名为AMDU精确复现。CPU分支存在 `.backwards()`拼写，完整CPU trainer不可直接假定可用；本项目强对照应另建明确adaptation版本或取得论文实际配置/commit后再资格。

## 保留的窄假设与下一实验

最优先仍是强普通增强后的真实paired动作收益，不提出“metadata+UQ+融合+自适应”的宽组合创新。strongest static/always-none/always-action、费用匹配random、同信息同容量QC/error-risk/defer、action-conditioned risk差、去采集与metadata-only都必须同场比较。学gain head本身不能规避与risk差的已知等价；联合动作必须完整重跑FOV，不能相加局部收益。

新增应备普通对照：GIN-only、SSC-only、GIN+SSC及固定步consistency/entropy TTA。先训练期对照与合法observed-input descriptor数值/边界准备；12-channel SSC改变容量与费用，必须raw复制/同容量feature控制。任何GT ROI/native missing pixels不得进入部署feature。TTA必须每患者从同一冻结init重置，全部series按patient同fold，不能沿上一病例的adapted weights继续；全11GT parent不能用于严格LOPO外折。

只在11开发患者内折设augmentation、UQ、gain/cost、action集、阈值与停止规则。4已见验证患者可诊断但不是新独立确认。8未见确认患者12series/lockedIXI继续关闭，先冻结端点/比较family/全费用再一次确认；原六医学门槛不降，发表claim尚未确认。新CPU成功为4项，首次KeyError失败保留且不计成功。
