# 精确风险与动作收益：合成CPU检验协议

本协议在运行前另立，不读MRI数据、权重、validation/confirmation，不训练，不初始化CUDA。检查已知风险/决策条件是否足够，不主张新定理或患者效果。

固定4个可观察group，各100个合成二分类样本。baseline/action错误交集四格顺序为(两者正确,仅action错,仅baseline错,两者错)：A=(0,10,5,85)，B=(30,10,50,10)，C=(60,0,30,10)，D=(90,0,10,0)。baseline预测均0，GT按baseline错误指示构造，action预测GT xor action错误；由此固定baseline条件risk=(.90,.60,.40,.10)，action risk=(.95,.20,.10,0)，gain=(-.05,.40,.30,.10)。没有从结果挑表。

同预算只允许对一个group的100样本调用action。比较最高baseline风险、真实两路径risk差/已知cost-sensitive、每个group等概率随机、全部调用和从不调用；后两项标不同调用预算。校准检查使用每group精确经验error与事前risk表，一一一致；以Fraction独立四格计算复核，baseline/action校准差为0不等于任意选择有正收益。以gain最大和cost最小的所有24排列选择规则核查两者等价。

补充离散阈值t使高baseline-risk组接受action：调用支持嵌套但系统error对coverage可非单调，依次列(0,100,200,300,400)调用的全样本error，不把这些损失当CRC嵌套预测集合loss。必须至少有一个增加调用使error增加，且不改变数据救结果。

CRC算术检查B=1，n=(4,8,11,19,59,99)，alpha=(.05,.1,.3)。保存修正式(n*empirical+B)/(n+1)及zero-empirical情况下的1/(n+1)，精确Fraction计算。n=19仅显示错误把series当独立样本会改变校准修正，11是开发患者数量，4已见validation已用于设计、8确认不是本轮可用校准集。以上n均不放行真实calibration。若论文中的前提/公式有不同，以原文记录偏差，不能把算术推广为真实保证。

输出<=2MB，单线程CPU、below-normal、8GB磁盘/RAM余量、60秒内。NumPy用于实际样本枚举，独立Fraction用于四格统计；无统计bootstrap。软件/精确反例结果归档，并在读完原文后单独写解释。

