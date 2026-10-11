# 19开发系列充分3D训练的资源与视野准备

仅从已认证输入JSON的geometry/shape/count推算，不读取新MRI或GT、不前向、不训练，不打开验证或确认效果，不安装nnU-Net。当前环境没有nnunetv2/dynamic_network_architectures，现有候选不能宣称官方自动规划器复现。

逐19开发series记录实测物理grid的unpadding shape、实际spacing、padded shape、whole-grid padding比例、64×128×128 patch毫米视野、该series每方向最多真实观测毫米跨度。缓存方案计算float32 image+float32 label单臂、两臂共享label，以及二值label按uint8缓存的准确字节数（不将其写到磁盘，不假定torch训练显存等于这些数）。体素乘法由Python任意精度整数完成，byte/GiB单位分开。

三个完整训练更新数20k/50k/250k是资源情景，不是已冻结强能力预算。借当前单系列固定batch CPU每臂实测512更新耗时给理想纯更新下界，不当随机多病例I/O/采样/整FOV评价的实际时间。GPU时间/峰值仍未测；原GPU资格protocol不放宽。根据结束后的拟合与后续真实GPU资格，另立正式19series协议，不能据纸面情景启动未知时长训练。

患者角色继续11开发/19series、4已见验证/9series、8保留确认/12series。原四验证门槛、病例内先均值后患者均值、所有9series TP>0/四患者full和missing均正、空/undefined保留。强baseline资格之后才开展6×5、同observed直接任务和resolution-randomization；最后冻结后才八确认和第二独立训练网络。
