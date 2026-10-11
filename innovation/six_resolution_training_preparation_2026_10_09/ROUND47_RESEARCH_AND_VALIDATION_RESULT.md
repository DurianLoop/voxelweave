# 本轮结果：一个新公开稿，强对照算子已验证，两个GPU修复均否定

实际新增阅读1篇GIN公开早期稿，104正文提取块、Algorithm1、4张独立实验表；7份固定作者文件1489不同源码行静态读完。最终期刊全文、图像像素、外部supplement未读，不将旧DG-TTA/routing/RUGS重复计本轮新文。阅读范围/固定来源/版本区别见GIN_READING_AND_PROJECT_DECISION.md和gin_reading_provenance_attempt01/receipt.json。

已实现独立的3D GIN参数采样/显式重放、Frobenius scaling、IPA互补混合算子和mean-target KL方向/reduction。CPU24 synthetic案例全部通过独立NumPy公式、重放、有限性、shape、输入不变、zero、epsilon scaling；最大公式差2.562999725341797e-6；互补混合差3.5762786865234375e-7。当前Torch2.11.0+cu128中attached/detached loss一样，梯度最大差5.574304601205834e-4；attached梯度NumPy有限差分误差6.703150946633929e-12。CUDA未初始化，医学数组/GT/模型/训练0。准备不冒称完整GIN/3D IPA复现或临床收益。

全192tile逐层CPU/GPU定位与独立metadata审核完成。原CPU/GPU完整FOV SHA重现，首Conv完全同；首IN差3.0518e-5、tile概率差2.1040e-5，完整原概率仍5.3346e-6不合格。两个预先固定全FP32 IN算术候选，各重复两次完整FOV，概率差5.7220e-6/5.3644e-6，均失败且约7.9–8.0s慢于native5.30s；两候选停止。本轮GPU诊断768+960=1728实际tile forwards，但唯一开发患者仍1、series仍1，不能把重复次数增加医学分母。

不能以随机卷积/3D移植/空间混合命名创新；原PAST-Net G086及旧计划已有physical-mm/anchor/risk等，不改名重算新贡献。保留待证伪的窄假设：强普通task与真实动作余量建立后，合法采集信息/observed响应是否提高明确SR/TTA/联合动作的患者净收益选择；必须超过同信息action-risk差、QC/defer、metadata-only、strongstatic、random并计全费用。可尝试项和缺项在GIN_PENDING_EXPERIMENTS_AND_BUDGET.md；新的same-input operator诊断协议已准备，尚未执行。

fresh六臂预检仍ready=false，完整预算104156359bytes保留，当时磁盘缺51444935bytes；缺35904终态/audit、full38/atomic/费用资格。35904原session44317仍live，不重启、不用prefix代完成、不冻结其live attempt；后续真实exit0/no session_id才能保存终态并运行audit_full_real_terminal_v2.py。

11开发患者19series保留；parent看过全部开发GT，只用于开发能力诊断，严格LOPO必须cold-init；4已见验证9series不作新确认；8未见确认12series及lockedIXI关闭。医学六gate和数值gate不减。仅写innovation，不安装/委派/删除历史或动原训练/其他PID。可见请求/完整传入摘要/消息/可用实际tool buffers均保存，所有真实失败保留。目标active，尚无独立确认可发表claim。
