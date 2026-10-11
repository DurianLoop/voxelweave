# 可观测顺序差是否能预测处理动作风险：固定45开发诊断

本计划写于新post分割队列18/45运行时；不读取动态子集新Dice。只使用已完成且已见的45CISS解析输入与旧raw/pipeline task输出。没有新确认患者、没有模型训练、没有新神经forward；结果为post-result development，不能当独立确认或发表claim。

候选主信号：PCHIP pipeline/post顺序差在observed-only support上的患者内缺层等权RMS；预设max全图差为次要候选。两者仅由观测层的解析输出构造，不使用缺层真实像素、病灶标签或native分割预测作为输入。

固定三个简单强比较：raw−pipeline PCHIP可观测输出差RMS；observed anchors的面内down/up roundtrip差RMS；raw PCHIP−raw linear输出差RMS。前/后差的各支持域只由观测邻层阈值决定；anchor差support仅用该anchor。统一observed min/max、原网格、同resize/AA和显式clip。真实缺层与标签只能在独立评分阶段使用，不影响特征、排名、平局或预算。

固定动作：对45人中15人采用pipeline PCHIP，其余保留raw PCHIP。每个可观测信号选最低15名；按事先冻结的原名单顺序解平局，不调方向/阈值/预算。不把此batch排名规则当已成立的部署方法。

任务效用为旧pipeline−raw full Dice，两标签完整保存；图像效用为旧support target-equal NMSE pipeline−raw。保留逐患者原始值，不读取新post task结果。oracle按两标签Dice效用较小者从高到低选15人，仅为不可部署的可行性上界。

主候选开发门槛：所选15人的每位full Dice两标签均≥raw−0.01；两标签所选任务均值都严格优于三个固定简单比较（1e-12浮点裕度）；且均严格超过5000次随机同预算无放回选择的97.5分位。主候选全部条件满足才可进入后续准备。max候选同表完整报告，不用它替换失败的主候选。随机seed20261102；这里不是familywise显著性检验，门槛通过也不宣布科学确认。

同时报告五特征与实际两标签动作效用的Spearman描述相关，预期低feature对应高utility，故相关应负；不对正相关改排名方向。全45固定分母。若不足15人满足双标签−.01 guard，则本预算下连oracle也无法满足逐人guard，直接保留此可行性反证。

全45新可观测差值重新从anchors生成，180旧解析输出必须匹配已认证SHA；逐层support/count/dot-product、anchor roundtrip及三个新RMS由另一公式/归一化表达式独立复核。候选order RMS/max另核对已完成解析记录。排名、guard、随机同预算分位用math.fsum及手写分位复核；不重复旧task网络。

CPU单线程、自己低优先级、15GB磁盘与8GB内存gate。不操作GPU、终端训练、locked IXI test、根环境/.gitignore。失败首记录保存，不根据结果换名单或配置。
