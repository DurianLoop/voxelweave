# 7639 冻结链后的继续入口

ROUND49 archive actual2c9528 exit0/no session；新增101、累计7639，原7538所有文件SHA/bytes保持。APPEND_ROUND49_INDEX.json SHA6a76ef3d2e183e1df4cb757c0124ab9bfd593ffb332171bb9350e4059c945aa2，bytes30226；proof SHA007ebf7f54c088e63785af70f436eb23ed7a7eec6be540134f4527b85c83bfaf，bytes1335。独立post-check actual93c40d exit0/no session，新文件全rehash及manifest链通过。归档终态、post-check、此handoff及最终答复为后归档静态文件，下轮增量绑定，不编辑index/proof/已执行代码。

唯一live44317，最新actualf3a77f仍带session_id且无新增stdout；最后可见进度actual9ac933为12720/35904、elapsed13813.16355s，强度/support全0、coordinate1.1368683772161603e-13。其原runtime guard为RAM/disk8GB、wall64800、CPU1/CUDA未init、family2MB/journal1.5MB，原启动另预留15.8MB。未修改/重启。继续真实poll，只有exit0/no session才保存ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json及44317并跑audit_full_real_terminal_v2.py；live/full_real_pipeline_attempt01排除归档，prefix不当完成。

本轮末其余作业全部终态，不poll42978/12870/31564/82611/24948。CPU人工reference actuala37390 exit0；真实v1冻结JSON预算失败7ea18e exit1、MRI/GT/update0；v2 compact完整scope后42978→7f7ed3 exit1，首病例GPU/CPU各2更新、6forward、84blockcall，实际仅step0跨设备比较失败：prob3.48687e-6/grad1.84253e-5/param1.992689e-4/5binary。原216 NumPy更新检查总计跨两设备四步，不是每设备各216；用户传入摘要的歧义以journal及audit为准。独立CPU损失归因12870→81f534 exit0、CPU2诊断更新，maxloss-formula-grad5.681e-8，最差坐标符号一致且独立分支原model/optimizerSHA复现。独立real/loss audit0e113a exit0。

Conv局部归因31564→2f6ab5 exit0（结果stdout在f32d2f、终态stdout空）：CPU/GPU各3wholeforward/1backward、各12局部VJP、optimizer0。每设备整层gradient逐位复现原全图；原flat1658符号跟传入cotangent来源，而不跟卷积backend或input来源。其他weight坐标backend最大约9.96e-6仍超gate，不声称局部卷积全部通过。

IN局部归因82611→3bac68 exit0：各3wholeforward/1backward、各12IN VJP、optimizer0。原6个view/device的dx全部逐位复现；原最差coordinate[3,13,1,0,2]在所有input/upstream组合CPU IN给+3.92e-6/GPU IN给−2.13e-6，float64解析IN也是负。共享input/上游时元素级dx差max2.81375e-11，view0该weight坐标归约差约6.05e-6。这只隔离一个病例一个坐标的IN数值敏感性，不解释所有54参数、CPU具体底层kernel或临床效益。

纯NumPy finite difference24948→1386af exit1：新增CPU3forward/1backward、GPU0、optimizer0。h=[1e-3,1e-4,1e-5]全部负且收敛，误差2.92754e-8/2.92691e-10/1.65283e-12；固定所有h误差<=1e-8 gate最大h失败，原样保留、不降低gate、不改h、不重新命名通过。独立record audit685a01 exit0验证全部组合/6bitwise/终态/失败；没有重跑病例。

下一实质步骤：建立另版本高精度归约独立CPU norm参考，验证人工导数/真实最差层/全部54参数和162state/两步/完整19series两输入。不能为模拟GPU舍入而修改参考、忽略其他conv差、放宽既有数值gate或把局部归因当GPUfull38资格。完整GPUfull38和GIN19仍false，正式六臂训练未启动。协议在GIN_REAL_NUMERIC_ATTRIBUTION_AND_NEXT_PROTOCOL_ROUND49.md。FD严格预设失败同时记录小步长收敛，不回改旧receipt。

GIN accepted PDF全文12页和12render已读，reading provenance014586 exit0，下载fa9325 exit0。新增独立论文0、同论文accepted-primary-version1，7表8图6公式1算法73references，source DOI10.1109/TMI.2022.3224067；官方Imperial Accepted version，不是publisher typeset final。原PDF4498435bytes/SHA c9b7dc075caceb7bc53743dbd7a138e774637fd1e18697c575ca972f11be8c56，citation UI405保留、明确public REST content正常匿名GET成功。窗口版本差early[-275,125]/accepted[-125,275]，MRI不使用CT窗。accepted增加alpha插值/原图比例消融、IPA scalar比较、源域与95/85% prediction overlap ERM/mean/DG选择及作者2D计算费用。故一致度路由、GIN/IPA/3D都不称新贡献；候选仍须强task+实际动作余量之上的合法采集信息/真实动作响应患者净收益与同信息risk差/QC/defer/SSC/metadata/static/random/agreement强对照。

只新增innovation、不安装/委派/删除历史/枚举或修改他人PID。CPU1/interop1/below-normal，RAM/disk8GB；GPUallocator min(10%,2.4GB/total)、启动8192MiB、peak2.5GB/runtimefree4GB、FP32/TF32off/deterministic。归因GPU峰2116026368bytes。prep7MB/FOV20MB/other22.8MB保持，加paper6MB；guard使用free−22.8MB−各cap尚余字节，不重复扣当前占用，不缩预算。末freshfree8040976384，prep5872402/FOV7286773/paper5676210（后归档文件还会少量增加）；六臂总104156359预算不变、正式训练未ready。

11开发19series完整，19998 parent见全部开发GT仅开发诊断，strictLOPO cold-init；4已见验证9series不作新确认，8未见确认12series和lockedIXI关闭。六医学gate不变。70可用实际buffers/可见用户请求/上一模型摘要/进度/真实错误和源材料均保存，隐藏推理和不可恢复聊天不补造。没有独立确认可发表claim，goal保持active，未markcomplete/blocked。
