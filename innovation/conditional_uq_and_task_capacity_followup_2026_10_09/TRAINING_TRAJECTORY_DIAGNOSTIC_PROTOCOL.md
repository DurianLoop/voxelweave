# 全部11968训练记录的描述性轨迹诊断

只读取已经真实完整终态并冻结的四个last2992增强分支及其gzip训练记录，不加载模型/MRI/GT数组。先核ACTUAL_TRAINING_EXIT与原receipt、四个日志SHA、完整1..2992步。所有四臂全部保留，校验每步patient/uid/mother标签/母输入/geometry与增强primitive配对；检查全11患者与全部19series曝光。不能据这次分析修改checkpoint、阈值、原医学门槛或称独立确认。

在读取轨迹统计之前固定：前544与末544步，以及连续11块（每块272步），报告mean/median/min/max/p10/p90/非finite；按patient先均值的完整2992步与首/末窗口记录全分母。配对spatial-minus-intensity逐步差、patient均值与正/负/零计数仅用于检查优化难度与暴露覆盖，不做显著性或因果结论。空间增强改变输入和监督分布，即便母crop配对，增强训练loss的大小也不是未增强完整FOV Dice的可比代理。

只有新开发76FOV真终态后，才能将其能力与四已见验证完整結果做描述性对照。parent/子模型均见开发GT，没有LOPO/新患者确认。CPU1/below-normal，60秒/输出100kB以内；磁盘8GB另预留2MB全强度/3MB原医学/2.8MB开发/2MB本阶段。8确认与lockedIXI关闭，不安装、不委派、不控制其他PID。
