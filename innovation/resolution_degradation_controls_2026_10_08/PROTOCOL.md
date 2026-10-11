# 普通分辨率降质对照的资格（执行前）

上一轮为progress：5984几何与独立2992母采样审计完成，18前景支持不足反例及whole-patch gate使5患者0可执行增强，实际改变下一步。前轮完整归档98871c exit0、累计6324，旧hash保持。原四臂29823此次535e82仍含session_id，不能从空输出称停止；GPU9f2d68仍1394MiB空闲，原新GPU阶段8192MiB储备不改。用户GPU授权有效，不干预/枚举/重启/迁移其他PID。

本阶段只准备文献普通分辨率增强控制，不缩小发表目标或把软件资格叫医学claim。11开发患者/19series；4已见验证不用于选这里的规则；8未见确认/12series和lockedIXI关闭。先metadata/synthetic，成功后真实开发MRI资格；不读模型、没有forward/backward或新分割效果。

## 新算子定义和来源域

从已经资格并hash固定的physical cache取**完整unpadded resampled image区域**，不能把这个区域称每体素真实采集。active分支先线性降采样到coarse网格，再取原位置的线性恢复值；各轴的第一个和最后一个体素中心固定，align_corners=True，真实coarse spacing是`(N-1)/(M-1)*原spacing`。不同于旧align_corners=False/rotation算子，重新资格，不复用其通过结论。

沿原5984记录primitive.enabled，不根据GT/预测/效果筛增强。设u=(原scale-.85)/.30，requested factor=1.1+.4*u；该映射执行前固定，与文献普通resolution degradation的范围相近，但不冒充忠实复制VINN/TorchIO配置。候选axes为throughplane=[z]、inplane=[r,c]、allaxes=[z,r,c]，全部比较，不能只留下容易通过的一轴。受影响轴M=min(N,max(2,floor((N-1)/factor+.5)+1))，N=1则M=1；其余轴M=N。记录实际整数尺寸修正和realized spacing，不能用requested factor替代。

恢复只对母patch原有unpadded域内的位置采样，其余位置逐位保留原母baseline，包括原padding的基本intensity scale/shift。不存在源坐标不会被采样、反射、复制或用值假装有效组织；label API不接GT。基本强度顺序固定：有效区域的cache降质值先float32，再原scale/shift；完整后续gamma/bias/noise尚待资格，当前不训练。原未改变区域、inactive分支、母label和完整患者/监督分母保持。

新的支持语义是**保持母输入的unpadded-domain validity，新增降质不引入缺失源采样**，不是整个target全1。所有有效采样stencil来自实际cache域内；原padding仍validity0且输入值按母baseline保留。用双通道MRI+全1 true-domain支持进行生产数值检查，独立SciPy重算，确认恢复支持mask与独立母域mask一致。此域相对标准不会倒写旧绝对gate或18反例为通过，也不证明InstanceNorm输出安全、信息无损或医学效益。真实padding对模型仍有影响。

## 资格与证据要求

生产Torch float64 interpolate+grid_sample，独立SciPy affine_transform+map_coordinates；强度<=3e-6、坐标<=3e-12、支持二值0差。所有target数值检查包含原padding未变，单例轴和边界/flip fixtures。完整5984 metadata几何逐项检查三候选的实际尺寸、整数有理stencil支持、原validity体素数和11患者/19series全部事件覆盖；仅读已审计journal/metadata，不新读GT或MRI。metadata通过不等于5984真实MRI全部重算。

之后先原19series两输入各两母patch×三候选=228真实stress fields，独立全target数值重算、缓存/母crop SHA、原母GT不变（使用已认证GT SHA或必要开发label重放），统计实际CPU时间和数组体积。结果若未通过，失败原样保存；不放宽门槛、不从验证/GT选择规则。所有5984开发schedule的真实MRI/intensity管线和完整训练/推理费用仍需后续资格，未完成就不启动新训练。原四臂医学评价依赖与六gate/last/全患者分母不变。

CPU1/低优先级；metadata+synthetic墙钟900秒，真实stress阶段1800秒；阶段保存5,000,000bytes，磁盘/RAM各8,000,000,000bytes储备。新增只本目录及必要innovation追加记录，不改根.gitignore/environment或旧冻结源，不安装依赖、不委派。不输出或上传用户患者数据到外站。
