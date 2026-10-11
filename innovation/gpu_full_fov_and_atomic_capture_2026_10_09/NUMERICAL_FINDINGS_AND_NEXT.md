# 完整FOV数值资格失败与后续定位

原38FOV runner actual e47835/session74453 exit1：前两FOV最大差1.9669533e-6/2.5033951e-6，第三5.3346157e-6>3e-6；三个二值均零差。没有后35个FOV、没有第二raw parent atomic文件，不能称38资格完成。已写native parent atomic文件只是旧模型复制，不是训练结果。

原contiguous概率与独立CPU完整参考SHA在两个新诊断均重现。layout v2实际4e77ea/session25418 exit0表示两布局诊断运行完成：channels_last与contiguous概率SHA逐位相同、同5.3346157e-6失败；GPU完整流水线5.31s对6.38s，后者更慢。原layout v1实际89ca59/session79699 exit1在CPU replay之后因继承CPU模块把CUDA_VISIBLE_DEVICES=-1而失败，未有GPUforward；修复为imports之后恢复0，旧源/失败保留。

CPU规范化诊断actual e388fa/session15492 exit0也是运行完成而非资格通过：contiguous5.3397s/差5.3346157e-6；cpu_instance_norm49.2413s/差6.6161156e-6，均二值零差。CPU参考完整FOV178.5274s重现原SHA。它既慢又不满足概率gate，停止此部署方案。不从这一干预负结果断言InstanceNorm无贡献或所有差异仅来自卷积。

下一具体定位：固定该失败series及parent，按原全FOV192tile枚举全部tile，无GT；CPU独立functional各层与GPU相同层输出逐tile对照，统计每层max absolute/relative error、参数/张量范围及下游logit/sigmoid，保留tile identity/最差位置。在同一CPU与GPU设备各自重复一次检查determinism；再对导致误差放大的层设计单一算术/后端干预。不得仅找一个通过的tile或降低3e-6，禁止按病灶GT选位置。需要先冻结新的layerwise协议/源码/预算，不能回改已执行诊断。只有新完整38真正exit0及独立审核才全FOV资格。

当前没有FULL_GPU_DEPLOYMENT_QUALIFICATION_V3.json，正式训练ready=false。原完整35904 session44317仍live，保留原source/执行/等待真实terminal与独立v2audit，不能用新456field选择性资格代替。全部新增只写innovation；原模型/终端训练、验证/确认/lockedIXI及其他PID未操作，gate/资源/患者分母不变。
