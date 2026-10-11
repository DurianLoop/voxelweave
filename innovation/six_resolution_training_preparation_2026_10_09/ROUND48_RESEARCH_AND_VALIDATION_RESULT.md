# 本轮研究结论与真实验证状态

新读原文1篇：Heinrich等MICCAI2013 SSC，DOI10.1007/978-3-642-40811-3_24。publisher原PDF8页文本和8页render全读/检查，4图/3编号公式/完整参考列表。没有读作者源码、没有复现完整registration。笔记在 SSC_PAPER_AND_CONTROL_PREPARATION.md；独立阅读范围在 ssc_reading_provenance_attempt01/receipt.json。不要把旧轮GIN等重复记作本轮新增论文。

SSC 与本项目相关的已有知识：中心排除的六邻域12对patch，自相似结构表示；5bit一元编码只支持六级，每点60bit；Hamming恰等于量化后平均SAD。原13对MRI–US的TRE2.12±1.29mm是registration证据，不能当CISS病灶Dice；对SeSaMI跨论文比较存在US-tracking信息差。独立NumPy/Torch CPU人工公式4种完整场、affine/contrast inversion、中心异常探针、1432种量化距离比较均通过。中心异常+1000在SSC该点不变，而中心包含6NH control差0.37706；这是人工性质证据，也提示异常/病灶盲点，不能断言真实病灶损害或收益。SSC要列强对照和失败检测的候选特征，不命名新方法。

完整同输入算子诊断已真实结束6897→adf1df exit0，独立audit8f300d exit0：96batch/192唯一tile/4704主字段+288辅助字段，52个字段每设备各重复2次，每设备9984实际**算子**evaluations。CPU原96batch概率SHA/完整FOV SHA及坐标gate复现；没有新GPU整FOV。首Conv差0、首IN3.0518e-5、第二Conv全范围最大1.14440918e-4，全局最差局部算子decoders.0.layers.0为2.36511230e-4，relu/pool同输入差0，独立sigmoid最大1.19209e-7。实际inputs逐位传输，设备内重复全一致。局部差异不相加成传播误差，不把local gate当full38资格；native fullFOV仍原失败3.3346e-6。

三视图人工完整图：CPU16³ packed/顺序两步通过；v1缺moment记录、v2另冻结补齐，4次人工updates/版本。GPU原patch packed6 OOM，保留三图的plain sequential2也OOM，更新0。CPU save_on_cpu完整图可完成；two-pass attached VJP两分支虽loss/prob差0、grad7.45e-9/moment9.31e-10，但参数差3.09944153e-6超过原3e-6，实际cb5674 exit1，保留负结果。未记录最差位置两侧梯度，不未经核实断言近零梯度因果。

新增卸载透明性：v1在继承CPU模块把CUDA_VISIBLE_DEVICES设为-1后初始化前检查失败，实际d1efef exit1、updates0，完整文件和失败receipt保持。新v2只在本进程显式恢复已授权device0，真实86184→50953e exit0：builtin save_on_cpu和独立saved_tensors_hooks各两步，全3个head概率、loss、54参数的所有梯度/更新及162 optimizer字段每步全部逐位同。240保存张量，224实际恢复内容/hash/shape/dtype/device全同；16未用保存项保留记录。GPU峰2279604224bytes约2.28GB；显式hooks保存CPU payload峰2810692952bytes约2.81GB。builtin host payload未计量，字段0不能解释为无host内存。全部12 whole-model forwards、168 block调用含checkpoint recompute，4人工GPU更新；本轮未加载MRI/GT/parent做GIN训练，不增加医学患者。内置两步完整图约1.40/1.12秒，审计hooks约4.85/5.07秒，总elapsed15.50秒含准备/捕获/hash/费用；这是人工case时间，不外推真实19series。独立record audit8cf8d5 exit0，没有再运行模型。

准备真实19series/11患者两输入两步资格协议和metadata manifest，完整76 GPU更新/228 GPU forward及同数CPU reference仅为未来数量，当前actual0。独立CPU可微reference与全费用runner仍需实现；不能用GPU hooks内容透明性冒充CPU算术参考。IPA完整3D权重场、医学训练、严格LOPO和新确认仍未执行。

创新判断保持窄、可证伪：建立强普通task和真实SR/TTA/联合动作余量之后，合法采集信息与observed动作响应是否对患者动作净收益选择有额外经验价值。若响应只是输入与固定算法的确定性函数，它不提供新增测量信息；潜在价值是有限数据下的特征/泛化，不宣称增加原始信息或保证辨别hallucination。必须超过同信息action-risk差、SSC-only/QC/defer、metadata-only、strong-static/random，计全部probe/selection/train/evaluation成本，cold-init患者交叉拟合，避免未观察参考特征泄漏。不能把PAST-Net旧physical-mm/anchor/risk、3D随机卷积、self-similarity或内存工程改名作新贡献。

六医学gate不降低；19998 parent见过全部开发GT仅作开发诊断，严格LOPO必须cold-init。4已见验证9series不作新确认，8未见确认12series与lockedIXI关闭。full35904仍session44317 live，不重启、不归档其live输出，实际终态后再audit。full38/atomic/成本资格仍未齐；六臂完整104156359bytes预算未降低，正式训练未启动。磁盘/RAM8GB、GPU cap与CPU1/below-normal保持，原终端/其他PID不枚举不修改。当前没有独立确认可发表claim，目标active。
