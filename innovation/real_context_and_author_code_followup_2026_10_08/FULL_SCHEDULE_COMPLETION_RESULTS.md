# 本阶段实际研究结果（完整资格与独立审计均通过）

## 完整增强分布发现的反例

候选image-only往返增强的完整2992步、每步两个patch已真正a4b6f8 exit0完成，5984个几何字段、11开发患者/19series，总计6,274,678,784 target**曝光**体素。1785 active、4199 primitive identity；3398个patch的整个target通过既定`support>=1-1e-9`数值定义。这里未读新的MRI或模型，也不是正在运行四臂的单次spatial结果。

Torch/SciPy全target支持重算最大差9.836575998178887e-14；物理坐标差1.1368683772161603e-13；二值差零，原门槛保持。GT19仅合法训练crop/pivot及支持重叠诊断。完整分布的病灶前景支持不足最终为18/90,636,500曝光体素，约0.0000198595%。它们来自开发患者VS-MC-RC-010的一条series；不是18个独特病灶或独特原始体素，更不是已经发生18次医学损害。

这证伪了从38stress geometry“FG不足0”推断完整schedule同样全支持。未按GT修改候选分布、删patch/患者或放宽threshold。域是unpadded resampled cache，不是每格点真实采集证书；“全支持”使用明确浮点阈值，不能转称精确信息无损或任何网络输出完全不受边界影响。

## 独立审计和普通基线政策

qualification脚本自己的旧receipt保持independent_journal_audit_completed=false，历史原样保留。另进程用原sample_batch重放2992母label/geometry的审计首跑因基础Python缺nibabel在import前退出；改用已有D:/conda/envs/MRI/python.exe，无依赖安装或脚本配方改变。audit session56539真正402242 exit0、202.940秒：全部5984行、2992原sample_batch母label/geometry及11患者每人272步匹配。该进程没有第二次重算全部support mask；全field的Torch/SciPy独立支持资格来自前一qualification。

候选普通基线规则是整个target通过支持门槛才执行RT，否则identity、全部监督及患者分母保留。analysis真正805460 exit0生成全部5984条确定decision，零新GT/MRI；1785 active仅272 eligible（15.2381%），1513 active回到identity；整schedule执行率仅4.54545%。完整全target支持3398中还有3126是primitive identity，不能把3398当作有效增强次数。

更重要的是覆盖偏差：5/11患者（001/004/007/011/013）有效RT为0，9/19series为0；执行的272中227来自forced-FG（83.4559%），45来自random patch。original active的forced-FG是905/1785（50.70%）。所有患者仍544patch/272步，监督分母没删，但接受的增强事件分布显著改变。因此不将该绝对全patch gate当作已充分增强的强baseline，不据GT重采样补齐或放宽门槛，也不启动这一候选的2992训练。

这改变下一实验准备：优先对普通in-plane/resolution degradation等候选做新的域资格和患者覆盖比较，明确原始padding如何保持、是否新增缺失支持；不能把任意valid-mask混合或边缘复制称为真实halo，也不能先挑效果再定接受规则。真实MRI/intensity完整schedule、全部训练/推理费用和能力门槛仍需收齐，见[下一步准备](NEXT_ACTUAL_STAGE_PREPARATION.md)。76个真实stress输入field不是全分布MRI认证。

## 作者证据和保留的创新假设

FastSurfer v2.3.0共11源文件3970行，发布YAML→loader→dataset→Trainer调用链已核：内部SF高斯扰动、native skip/实际整数尺度修正、top_left、batch8累积均有静态依据，非2022精确历史运行资格。2026病灶集成所链unofficial ranker追加162行源码和README；它只做静态CSV指标排名，不补齐OOF/ensemble归一化实现。全阶段实际源码行数4132，新增不同论文正文0，作者代码执行0。

保留的研究问题是：充分任务能力后，合法采集可见性与模型输出能否预测某个实际动作的病灶损害差及全部费用，并胜过静态最佳动作、强QC/error/cost/defer和去采集特征对照。增强、halo或ranker本身不作新claim。严格患者折外task/localization/收益模型必须排除heldout；全11GT的19998parent不能作所谓独立外折warm start。

原四臂仍live，native两臂2992完成、raw intensity最新7ef5e1到440，raw spatial仍待。真正all-last2992后才走原terminal capture→36production+36functional完整FOV→六医学gate与strict数值复核；当前没有新的分割效果，8未见确认/12series和lockedIXI关闭。目标active，尚未有可发表且独立确认的claim。
