# Pilot最后模型的描述比较，等待全部结果

四分支396更新真实完成并通过cp/journal/全部99step配对核对。评价session80828目前正在进行，未观察实际退出，不能冻结滚动receipt。每个完成分支的九series均全FOV，不按病例选最优checkpoint。

原父native已见四验证患者full Dice .50663194、recall .46261318、absRVE .47459105。已完成native/basic：.43208781/.38918502/.57181610，六门槛1/6；native/strong：.50781330/.50784223/.60184102，六门槛2/6。因此strong较basic的Dice差+0.0757255不能直接宣称较原父模型显著改进；相对父模型仅+0.00118136，体积误差更大。basic/strong都重置optimizer并续训99步，parent未作这次更新。全部raw结果须等完成后一起报告，不能挑其中最优臂。

后续描述表固定六个state（native/raw各parent/basic/strong），full和missing的Dice/recall/absRVE、门槛通过数、零TP/空预测series、患者逐对差异全部列出。strong-minus-basic与strong-minus-parent分别计算，同输入内比较。不把四个已见患者或同患者多时间点当新的独立确认；不作显著性/充分适配/正SRclaim，最终source/预测/数学数值核对以实际退出为准。

若需纵向辅助诊断，使用已核对原affine_voxel_volume_mm3与计数计算体积，按已有去标识StudyDate的同患者相邻时间点比较变化。它只属事后数学方向诊断，不是临床增长、复发或治疗判断；不能要求真实不同时间点体积恒定。

完整19998步四分支资源预测已经实测99step journal的无损gzip/zlib双重重读后计算：日志直接外推28,875,496bytes；四final cp实测22,488,836bytes；加25%日志容差、metadata和原子写临时峰值的weights-only预测66,205,415bytes，当前储备外64,598,016bytes，尚不够。带一个/four optimizer resume预测94,348,608/144,996,711bytes亦不足。CPU仅step时间预测135,763.66秒，不含缓存/IO/评价重放。预测不当实际全预算测量，未冻结或启动完整新训练，不删历史或减储备。
