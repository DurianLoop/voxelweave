# 顺序、roundtrip与评估器暴露：后续区分方案

状态：45新post CPU task对照已启动；下列额外模型/新来源实验prepared_not_executed。当前GPU用于用户训练，不运行新训练、不改变其进程；没有假定可用的新确认患者或新任务模型。

**最近的可执行对照。** [当前CPU合同](VS_SEG_POST_RESIZE_TASK_CPU_PLAN_2026-10-03.md)固定原45CISS，测post_resize_pchip，并对照已经完成的raw/pipeline输出。若post任务接近pipeline而两者远离raw，优先研究空间roundtrip；若post与pipeline任务明显不同，保留顺序敏感性，不能把图像均值的0.84%直接映射为Dice贡献。主要full原JSON读数和全部18敏感性同时报告，不挑有显著性的标签/边界域。

**仍需区分的空间因素。** 在同一observed-only归一化、同原生网格、相同anchors/tail下，后续可以固定比较：原网格插值；down/up roundtrip；只改变anti_aliasing；只改变固定中间网格；只改变内部resize clip。每次只能回答自己实际改变的处理因素，不能把roundtrip统称“裁剪损伤”。当前两个解析核的显式clip都0，并不使skimage整个resize成为理想线性算子。不能根据本45数据反复挑最优网格后继续称其test。

**评估器暴露的控制。** 在[既有交叉输入方案](FROZEN_TASK_EVALUATOR_FOLLOWUP_PREPARATION_2026-10-03.md)的native/raw/HAT/mixed任务模型矩阵中，后续将post和pipeline均作为固定evaluation输入加入。容量、训练patient名单、epoch/step曝光、augmentation和阈值一致；同一任务模型必须评价全部输入，不能每输入挑最适模型。如果任务差缩小，只支持暴露的重要性，不证明图像解剖无损。新增训练只有在GPU空闲和新的实际训练来源资格核验后才执行；当前不发布虚构可运行train命令。

**确认角色。** 45CISS、MC-RC旧8开发人和过去已查看效应的公共队列均不能再作为未来新方法完全未见确认。独立程序复核是数值/流程校验，不是独立科学验证。需固定另一来源的MRI患者ID、序列/原生来源、标签网格、patient/group split和任务模型资格；确定名单并冻结合同后才读取新结果。不能从locked IXI test取代缺失的独立来源。

**仅观测输入的风险候选。** PCHIP顺序差C=U(P(D(anchors)))−U(D(P(anchors)))由观测层可计算，可作为预处理敏感性候选特征，当前没有显示其能预测有害修正。评价应以真实动作收益/损害为目标；含单纯绝对误差、raw−pipeline可观测差、强固定alpha、随机同预算及原网格旁路对照，避免换坐标构造“新收益头”。局部病灶guard不得由部署时不可得的target标签驱动；需要真实可得的任务表示，旧native/QDA/岭失败不抹去。

**补读。** 神经母细胞瘤T2预处理研究DOI `10.1148/ryai.230208`尚缺正文；仅从合法公开作者版本或用户已有全文核读。PCHIP窄检索只有CEST频谱与无关压力条目，order查询被first/fractional-order噪声污染，不能作为充分查新。继续查医学image-resampling、signal-processing和slice interpolation的直接算法/流程先例。
