# 冻结分割器的可见区域诊断：15系列CPU执行合同

前置证据：全部15系列的理想观测mask并集+2mm传播通过预写几何门槛，独立原标签/物理disk/全部759缺层及9策略复核errors=[]。它只证明采用真值观测区域的几何可行性；本合同在任何新的预测区域推理/评价前冻结，不训练门控或改变旧政策。

## 模型与身份来源

复用已认证官方UNet2d5_Att_Hard_T2_final.zip（Zenodo6323472，SHA256 76d4c427188bbbe2f40e2ba5a5d5f3c12525e67f413eba842980b43302d83777；best checkpoint SHA256 9105ad78fed0561bb04a82e660eed6083c3d182fc43642bc332f68a272ede0a7）。固定Git33410a2d44e3f57b4df1c3ed005e6d40c0824aa6、MONAI0.4已认证wheel/逐文件stage、CPU兼容层及tuple推理等价proof；不运行作者硬编码CUDA入口，不安装新环境。checkpoint日志与Git的176train/20validation/46test角色已认证。

15系列/8人固定上一诊断全部开发名单。实际重新核它们均属于当前官方ID规则下candidate_nonoverlap_patients，排除全部58共享VS-SEG患者；不能只凭SeriesUID无交集说独立。旧八行legacy UID crosswalk仍失败，不升级为全crosswalk认证。这是开发用冻结模型，独立科学确认患者仍0。

## MR像素与模型输入

每系列只解码已认证MR ZIP中ordered plane indices=0,4,...的真实观测DICOM pixel_array，逐对象核patient/study/series/SOP/Rows/Columns、MONOCHROME2及finite slope/intercept。其余MR对象只复用已经独立认证的头，不解码隐藏plane。15源固定、单worker逐系列，无网络下载或自动重试，不能因小病灶/失败删系列。

纯函数由真实anchors生成native float32 raw-PCHIP display：所有内部3余数，首尾不具四观测上下文时用线性，其他用四个真实anchors的局部PCHIP；保留observed planes，末尾unsupported tail复制末观测。没有resize、clipping、隐层真值或人工label输入。标准化仅对这个observed-derived display作作者NormalizeIntensity；完整display包含生成plane，但全部由稀疏真实观测决定。

固定native affine转RAS，不作label crop、resample、人工ROI或task fine-tuning。复用经认证Gaussian滑窗384×384×64、batch1、冻结segmenter第一输出logits、argmax。将预测反转回native grid，**先保存native预测及输入hash，再读真实label评分**。此路径不以label选择crop、scale、model或阈值。当前不是新的重建方法对比，只检验冻结预测区域能否提供保护所需信息。

## 冻结区域与评价

唯一主要ROI：只取冻结native预测在真实observed planes上的mask，两侧并集并按2mm plane内膨胀，沿用上一诊断完整phase0内部759缺层与tile32规则。次要ROI为冻结模型每个dense plane的预测mask+2mm（完全由稀疏display派生），不能用其较有利结果替代主失败。同时报告未膨胀的predicted-bracket-union与主要ROI的环移/像素与tile同预算随机对照，使用上一合同seed协议；全部区域成本计入空病灶目标。

真实label只在prediction保存后用于评价完整缺层foreground/boundary/tile覆盖、precision/几何Dice/面积。另报告冻结任务预测对官方标签的native全volume与observed/missing planes的Dice/recall/precision，仅为冻结检测器能力诊断；不声称SR vs native improvement、独立临床安全或病灶检出率。

主要ROI沿用同一几何门槛：每个15系列foreground≥.99、boundary≥.99、tile foreground≥.995、ROI面积≤5%plane、tile面积≤10%plane。所有15处理完后才做患者内时间点等权汇总及all-series gate，不以动态成功子集推断效果。未达门槛保留失败，停止这个固定checkpoint/primary-region配置；不能调2mm、阈值、crop或改选次要dense ROI救方向。将来新模型或表征需不同合同及真正未用于设计的患者确认。

## 资源、产物与验证

隐藏CUDA、CPU单线程/interop1、deny_cuda初始化、模型eval+inference_mode，自身低优先级、可用RAM≥8GB、磁盘≥15GB。只写innovation，不动用户训练或原session83910。native float32显示单≤250MB，anchor arrays单≤80MB；推理激活沿用已经CPU认证的384×384×64窗口预算，最多一个本脚本model worker。病例资源门槛不足即保留错误并结束，不能反复重启。

保存run_contract逐输入hash、模型/环境来源、MR decode scope/SOP/anchor array hash、raw-PCHIP display hash、native prediction压缩文件及hash、每目标ROI计数与主要mask packbits、失败、全系列/患者汇总。成功目录exist_ok=False；脚本中病例失败完整记录，无自动retry，不静默换源。计划15个新task前向，不运行HAT/SwinIR、不训练神经网络。

后续独立验证需要逐原DICOM重读真实anchors，独立Hermite公式复算raw-PCHIP输入、检查observe/tail和预测回转/label信息依赖；对全部ROI用独立physical-disk实现与原标签重新评分。要宣称模型结果可靠还需独立重跑冻结CPU前向/逐位预测确认，不能只核JSON。本次先执行来源与固定诊断，任务/模型独立验证及未见患者确认状态据实际proof报告，不能提前标完成。
