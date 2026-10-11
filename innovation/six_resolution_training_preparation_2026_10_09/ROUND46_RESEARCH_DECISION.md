# 本轮科研判断：已验证的实现进展与仍未成立的创新

原项目PAST-Net G086已有四锚点、phase/validity/difference/curvature条件、soft fusion、多尺度latent、空间/FFT专家和learned gate。next_sota_handoff.md还已提physical-mm conditioning、correspondence、anchor clamp和risk目标；这些旧计划不能换名当本轮新贡献。历史fastMRI test24多次开发查看，不作独立确认；IXI历史汇总仅项目文档背景，本轮没有打开其像素/GT或评价原训练checkpoint。

本轮继承上一批routing/RUGS的330提取块22表及21作者源码631行，不重复计新主文。实际复核了已读DG-TTA的35–47块和原XML引用[15]/[37]，并新按DOI核GIN与SSC两条EuropePMC核心元数据/摘要。两个新条目没有EuropePMC开放XML正文，没有取得或读原PDF/作者实现：新主文阅读计数为0。GIN元数据指向2023卷42/1095–1106而DG-TTA引用写2022，保留在线/卷期口径差，不推断无效。SSC摘要是3D US/MRI配准，不是当前稀疏CISS病灶分割证据。

尚待证伪的窄问题：强普通训练及真实SR/TTA动作建立后，合法采集信息或observed响应是否能提高患者病灶动作净收益选择。在同信息同容量action-risk差/QC/error/defer、metadata-only、去额外采集特征、最强static/always/none及费用匹配random之上验证。g=L(a0)-L(a)本身与两action-risk之差等价，不能靠改head名字宣称创新；不能删除任务query/geometry制造不公平去采集对照。

研究顺序仍为普通task泛化→实际动作余量与完整费用→患者cold-init cross-fitting→冻定端点/模型/动作/预算→独立确认。19998 parent看过全11开发GT，只作开发能力诊断，严格LOPO必须cold-init；4已见验证不改名新确认，8未见确认12series和lockedIXI继续关闭。所有失败/负收益/fallback/defer保留，联合动作实际全FOV重跑，不相加单动作收益。

当前实质新增：全19series的228GPU更新资格及审核通过；保持精确舍入的局部依赖插值已复现228完整GPU输入SHA，并有失败大体积12patch原始/support逐位比较，49.05s→4.82s。它是减少后续实验成本的实现优化，没有证明临床收益或方法首创；仍缺全35904新实现资格。原六臂点估计25.208h属于旧完整grid实现，不能事后改写原结果；新candidate-only估计另记，未当完整训练/全部评估上界。

全38FOV原attempt在第3停止：最大概率差5.334615707397461e-6>3e-6，二值0差。两布局完整FOV诊断得到相同GPU SHA，channels_last未修复且更慢；不降低概率门槛、不把2/3prefix当38成功。InstanceNorm执行设备诊断另计，完整结果依据actual terminal更新。本轮没有完成正式六臂训练，没有独立确认可发表claim，goal active。

最新入口v3接104,156,359bytes完整family预算，preflight actual0b6fcd exit0/ready=false：尚缺35904实际终态/审核、完整FOV资格及disk准入，磁盘缺约49.2MB。旧冻结checkpoint的透明压缩只回收359472bytes；只读新文本候选17个合计3.53MB，也不足当前缺口，本轮没有扩大压缩或删除范围。未触原训练或其他PID。
