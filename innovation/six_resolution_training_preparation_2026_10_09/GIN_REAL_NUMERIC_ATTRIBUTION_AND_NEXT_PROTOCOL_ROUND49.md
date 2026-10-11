# 首个真实病例 GIN 数值失败、归因及下一步

开发VS-MC-RC-001一个series、native_reference两个真实scheduled batch，三个GIN视图和原母GT，全模型cold-init。GPU/独立CPU参考各两次AdamW实际更新、各6whole-model forward、各84block调用含checkpoint；各设备的独立float64 NumPy AdamW检查及内存capture/reload全部通过。完整19series×2input资格在比较step0失败后停止，step1虽实际更新但未完成跨设备判定；不能报告两个step全部资格，也不是医疗效益训练。

step0概率误差3.4868717e-6、gradient1.8425286e-5、parameter1.9926892e-4和5二值分歧超既定gate；loss1.19209e-7/moments1.84216e-6各自小于gate不能替代整体通过。最差 decoders.2.layers.3.weight flat1658、coordinate[3,13,1,0,2]，CPUgradient+3.7831851e-6、GPUgradient−2.1291125e-6，首步AdamW解析gap与实际参数gap误差3.6e-11。此训练状态只作诊断，不推进正式训练。

同一CPU logits两种loss公式的grad差最多5.6811e-8，两种CPU loss各执行一个诊断更新；最差坐标仅2.5539e-9差且符号相同。独立loss分支模型与optimizer SHA逐位复现原CPU step0。该公式差不足以解释原最差坐标符号翻转；不概括为所有算子已正确。

局部隔离先在最差Conv3d捕获CPU/GPU真实input及完整反向cotangent，每个2×2×2组合三视图，共CPU12/GPU12局部conv VJP，两设备各3whole forward/1backward、optimizer0。原全层weight gradient每设备均逐位复现；同input/cotangent换卷积backend在该坐标不变号，换cotangent变号。卷积backend仍在其他坐标有约9.96e-6最大差，不能称整个卷积通过3e-6gate。

再隔离之后的decoders.2.layers.4 InstanceNorm，同input/source-output-cotangent/backend的8组合，总CPU12/GPU12 IN VJP、每设备3whole forward/1backward、optimizer0；6个原设备/视图局部dx全部逐位复现完整图。跨两个input来源、两个上游来源，CPU IN均给该卷积坐标约+3.9197～3.9223e-6，而GPU IN均约−2.1286～−2.1310e-6；纯float64 NumPy解析IN导数也均负。view0只换IN backend，元素级dx最大差约2.81e-11，但交叉相关归约后的该weight坐标差约6.05e-6。表明在这个真实输入、坐标及线性化路径中，IN反向浮点数值差足以改变首步AdamW方向；不能从这一点定位底层具体CUDA/CPU kernel、全部54参数、所有病人或断言CPU/GPU整体医学优劣。

额外用纯NumPy float64中心差分检查局部 `sum(dn * normalize(z+h*direction))`；只新增CPU3whole forward/1backward、optimizer0。三个事前冻结h=[1e-3,1e-4,1e-5]的总导数分别−2.1010809e-6、−2.1300636e-6、−2.1303546e-6，解析值−2.1303563e-6；误差2.92754e-8、2.92691e-10、1.65283e-12，均为负并随h减小收敛。**预设全部h误差<=1e-8的gate因最大h失败，实际exit1保留；没有修改h/阈值或标为通过。** 这不是完整非线性模型loss的有限差分，更不构成发表claim。

这些新增归因合计GPU6whole forward/2backward/24局部VJP，CPU9whole forward/3backward/24局部VJP，无新增optimizer更新。另原真实资格两设备各2更新、loss归因CPU2更新、人工CPU参考4更新分别保留原scope，不把block重算或局部VJP计成whole-model训练。

下一步预注册准备：原CPU FP32参考和原GPU结果全部冻结。单独建立高精度归约的独立norm参考版本，在人工可微例、真实首病例和全54参数/162state上检查其误差方向；用解析和明确Taylor误差预算的导数检查支持参考资格，不能为了与GPU相同而仿制其舍入或强迫GPU模拟已有CPU误差。必须在全图、全部深监督head、两步AdamW、19series两input、全费用和完整FOV再次检查，不能由局部1坐标替代。若任一gate失败原样保存，不启动六臂正式训练。

论文方面，accepted稿补出了基于预测一致度选择ERM/DG的先例和更完整的GIN/IPA消融；详细版本比对见 [录用稿阅读与创新边界](../gin_accepted_primary_followup_2026_10_09/ACCEPTED_VERSION_READING_AND_INNOVATION_BOUNDARY.md)。GIN/IPA、3D迁移、一致度路由、norm精度和GPU内存工程都不改称方法贡献。研究候选仍是强task与实际动作余量之上的合法采集信息/真实动作响应患者净收益，需同信息risk差/QC/defer/SSC/metadata/static/random和agreement selector；strict LOPO必须cold-init，确认12series及lockedIXI关闭。六医学gate不变，没有独立确认可发表claim，goal保持active。
