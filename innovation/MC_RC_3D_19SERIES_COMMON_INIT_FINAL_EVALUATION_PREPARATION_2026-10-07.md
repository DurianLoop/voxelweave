# 最后19,998权重的评价与独立重放准备

这是尚未执行的后续准备。只有两臂正式预算39,996全部完成、训练实际exit0、history及同GT/增强核验通过、两个最后checkpoint同时冻结后才能执行。当前只有前99步在运行；没有开发/验证任务效果，也没有最终checkpoint。

角色仍11开发/19series、四已见验证020/022/024/025共9series；评价两臂native信息上限和observed-only PCHIP各28series，共56完整FOV。八确认与locked IXI test不读。采用事前定义全部shape/affine、PATCH64×128×128、半窗stride、Gaussian正权重、概率裁padding并trilinear回原native、阈值.5，无GT ROI/TTA/connected-component筛选。只在推断后加载GT做端点。

每个series记录输入构造hash、模型SHA、全部tile/覆盖、概率hash及完整二值预测。预测保存为little bitorder packbits+shape，不保存native/physical图像或GT缓存；准备时先用既有28series shape metadata计算56完整预测packbits字节上界。独立核验unpackbits完整分母/shape和所有tp/fp/fn/tn、非空、undefined、full/anchors/missing/tail。full=anchors+missing+tail逐项核对，anchors为z%4=0，missing为最后anchor之前非anchor，tail为最后anchor之后。

主端点先患者内series均值、再患者均值，任何参与series/患者指标undefined则整体undefined，另记定义数量。原能力gate .70 full Dice/.65 missing Dice/.70 full recall/.50 full absRVE；四患者full/missing均正、9series full TP>0，两臂都报告。完整开发/四验证不是科学确认，也不根据这次分数延长步数、选择中间checkpoint或调阈值。几何标签roundtrip011已知失败保留。

独立核验应先重新生产同最后模型的全部56概率及hash，再用独立functional网络+独立Gaussian/coverage/NumPy native插值重放；保存全量最大概率差<=3e-6、固定.5二值差异0及float64结果，失败仍保留，不以float64通过覆盖float32失败。该设计约两次完整前向，成本在执行前另冻结；此前FOV metadata核验不是这个核验。源数据/标签已认证，但最后权重的跨坐标数值必须实测，不能依据单001推断其他28series。

主评价与独立神经重放建议各CPU4/1、below-normal、无CUDA，分别3600s上限；每阶段保存<=250MB、RAM/磁盘各8GB余量。19series旧模型两臂完整FOV共约754s，验证9series、最后模型、重复前向、几何核验成本未测，不以建议上限保证成功。正式可执行入口在最终训练结束前仍需准备并解析验证；此文件不是已存在最终评价脚本的声明。

能力全部通过之后才推进完整公平矩阵及病灶修正余量。收益策略必须与已有defer/双路径成本头、直接任务、风险/误差和预算随机对照；如果强适配后没有可修正余量，则停止此候选的正向claim。当前科学确认0、claim0，goal active。
