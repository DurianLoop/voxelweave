# ROUND52：原尺寸两步通过，进入完整开发series资格

目标仍是可发表且独立确认的医学claim。当前获得的是完成原完整数据处理流程、解决新数值分支的原尺寸显存限制、并验证两步人工GPU/CPU关系；还未获得强task医学效果或患者动作净收益，因此goal保持active。

## 已经完成且有实际终态的进展

原session44317真实结束：actual6d016a exit0/no session，35904 fields、5984 case-kind steps、38 MRI输入与19母GT处理完，elapsed30733.331589900074s。max intensity/support误差0、coordinate1.1368683772161603e-13。其输出原tool包含截断提示，最后真实terminal和完整diskreceipt/journal均保留；不能把截断日志算完整文字阅读。独立audit5c05c5 exit0核全部35904唯一field、11patient/19series/114series-mode/66patient-mode分母、原geometry/metadata和实际journal；审核本身未重跑医学数组。原live目录已是terminal，本轮可以冻结其静态内容，不能重启44317。

新模型首路显存定位7b66f1 exit1保留：最后decoder的norm输入FP64(2,16,64,128,128)，进入时allocated1804156416/reserved1923088384；旧归一化多个256MiB临时tensor导致OOM。只读modulehooks，没有修改旧模型、没有backward/update。

新compact-double-norm使用一个FP64前向buffer、独立CPU保存、按batch/channel解析VJP，eps、affine、biasedvariance、54FP32parameter/AdamWstate及loss不变。CPU数学v1 71b301 exit1：float64常量输入小步FD因消减误差未过1e-8，保留。v2采用独立60位Decimal目标与扰动，case/direction/步长/门槛不改，2c6617 exit0；8项random/constant/nearconstant/sparse×FP32/FP64affine的output/dx/dgamma/dbeta全部过3e-6，12个方向最小h=1e-5的FD误差最大5.130095402990579e-12。该custom autograd只支持一阶VJP，不认证二阶导。

原16³人工三view两步：CPU50666c exit0（4更新）、GPU9ca76e exit0（GPU2/CPU2）；逐位CPU saved hooks29afa8 exit0（GPU2/CPU2、pack224/unpack206）；释放消耗后skip引用版1681e4 exit0（GPU2/CPU2）；每block拆两段checkpoint版337cc7 exit0（GPU2/CPU2）。全部54param/162state、所有概率及binary检查保留，parameter最大1.4901161193847656e-8、binary0。

原patch(2,1,64,128,128)完整三view成本df60e2 exit0：3路forward、一次GPU更新、elapsed17.4654023s，peak_reserved2392850432bytes，逐位CPU保存pack112/unpack103，CPU逻辑保存peak4230974136bytes。该一次成本成功随后并未自动认证两步：独立fullpatch v1 389141 exit1在step0 backward OOM，GPU/CPU更新0；释放skip引用/临时GPUinput v2 6bf525 exit1，step0已过3e-6/binary0、GPU/CPU各1更新，step1 GPUbackward OOM，未执行step1 CPU更新。两失败保留，不调预算或算法门槛。

最后v3每个conv/norm/activation段分别checkpoint、消费后释放skip、临时GPUinput，数学和参数初始化相同；GPU对独立CPU functional/nativeCPU pooling/显式FP64 norm，原fullpatch完整三view两步cfcae8 exit0：GPU2/CPU2更新，step1loss差2.692455147723649e-10、概率2.660146258826046e-8、gradient4.656612873077393e-10、parameter **3.725290298461914e-9**、optimizer1.1641532182693481e-10、binary0。peak_reserved **2304770048bytes**、结束free21670920192bytes，elapsed388.23346360004507s。保持strictdeterministic/TF32off、allocator<=2.4GB、peak<=2.5GB。

独立audit587024 exit0重新核Decimal记录、全部小图/fullpatch54/162误差聚合、旧失败gate、全部保存journal ID/pack/unpack/hash/逐位恢复记录和完整35904terminal/audit。tensor原payload没有落盘，不能把journal算成离线重放原tensor；模型没有被该auditor重跑。记录完整已终态人工运行CPU更新15/GPU12（包含失败v2的各1更新），正在运行的医学资格另计，不把其prefix混入通过的人工总数。

## 仍在运行的真实资格

新qualify_compact19_real_graph_v1.py实际fe231e启动，session44838；最近6f0b06仍有session_id，case0/native_reference/CPU/step0三view前向完成。这是真实开发qualification，不是正式2992训练，也不评分医学效果。完整合同38个case×kind，两持续更新，预计GPU76/CPU76、228/228whole-modelforward、152 BytesIO model+optimizer恢复。必须实际完成全部19series、GT/mother/geometry/hash、54NumPyAdam和162state、binary0与真实全成本才认证；已完成prefix不能当完整资格。

新数值分支FP64graph/FP32parameter/optimizerstate，不能当旧FP32production或六臂已ready。真实runner在原FOV20MB未花余量里分配out<=1.8MB，其他stagecaps和原六臂104156359bytes预算不改。live输出排除本轮归档，静态source/protocol保留；不重启真实live作业。

## 论文/创新工作与下一步

本轮没有新增全文论文计数。查到nnU-Net Revisited在旧2026-10-07记录已读，避免重复计新文。补读Greedy current commit的ZF生成、真实列选择、policy input、quality scoring与trajectory更新，静态AST7daf63 exit0：选定policy和下一重建函数body没有GT字段，GT均值/std出现于评分；external callback/model/helper传递未全审，不能声称整个作者pipeline非干扰已证。未导入执行作者代码，也未认证发表时commit。

后续合法动作的部署信息合同已写OBSERVED_ACTION_INFORMATION_CONTRACT_ROUND52.md：selector/candidate只用observed像素/索引/合法采集元信息/历史/费用，隐藏GT和未测参考像素只进监督/评分；固定observed、扰动隐藏truth后action/probability应逐位不变的真实检查仍pending。delta与两risk-head同容量同信息，metadata/mask-history/availability-stratified shuffle与same-budget强static/random/QCdefer是必要控制，不把收益重参数化、条件MI、联合RL或3D预训练当新方法。

待19series真实资格终态+独立audit后，继续新分支完整FOV/磁盘atomic capture/真实费用/完整训练预算；获得通过六医学gate的强task和合法action oracle正余量后才检验患者选择收益。4已见验证9series不能独立新确认；8未见确认12series及lockedIXI保持关闭。原终端训练及其它PID未枚举或修改。

证据：[独立本轮核查](../six_resolution_training_preparation_2026_10_09/independent_round52_audit_attempt01/receipt.json)、[完整35904审核](../full_certified_schedule_2026_10_09/full_real_terminal_audit_attempt01/receipt.json)、[原尺寸两步结果](../adaptive_acquisition_primary_followup_2026_10_09/compact_norm_fullpatch_independent_attempt03/receipt.json)、[真实19series协议](COMPACT19_REAL_QUALIFICATION_PROTOCOL_V1.md)。
