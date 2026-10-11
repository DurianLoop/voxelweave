# 固定2992更新四分支的最终评价入口

本文件在 training session 29823 仍 live 时准备。准备通过不等于训练结束或医学成功。先保存实际工具 terminal 返回，再执行 capture_training_terminal.py；未取得 exit0 和四个 last2992 时 evaluate_matched.py 不允许加载验证像素。

评价只取原已见4验证患者/9series，每分支全部9个完整FOV，共36生产+36独立 functional 实现；同进程两实现，不宣称跨进程重执行或独立科学确认。输入、物理重采样、滑窗、V4 native映射、threshold=.5 和无损二值存储沿用前已验证合同；不采用验证GT定位、TTA、连通域清理、阈值搜索或中间checkpoint选择。19开发series不在本阶段评分，8未见确认患者/12series及locked IXI继续关闭。

先检查实际exit、receipt/config、四state与全部11968条gzip训练journal的来源/步序/配对。每分支必须2992步，11患者各272曝光；同输入强度与空间分支的母GT/base input/crop/flip/增强primitive完全匹配，跨输入母GT与空间后GT匹配。同输入起始state一致，跨输入不同的起始state必须照实保留。

完整FOV概率绝对误差<=3e-6、float64坐标映射误差<=3e-12、所有二值差异0；独立整数计数、Fraction患者先均值和完整full/anchors/missing/tail分区核验。神经forward FP32，坐标float64。任何数值失败都保留并停止解释医学差异。

医学原六门槛不降：患者先均值fullDice>=.70、missingDice>=.65、fullrecall>=.70、fullabsRVE<=.50；四患者full/missingDice均正；无series零TP。主增强效应为同输入spatial-minus-intensity，2992步预算匹配。原parent及旧99步pilot仅描述，不把额外续训当空间增强贡献。

评价CPU4/interop1/below-normal，不初始化CUDA；wall<=3600秒、同新目录总量<=45MB，磁盘/RAM各8GB储备。旧36FOV完整评价实测437332bytes，仅作为大小预测；本次开始前要求当前训练文件+3MB评价预算仍<=45MB且磁盘储备足够，运行继续guard。评价不写训练receipt或journal、不保存新checkpoint、不支持自动删历史腾空间。

训练/评价的实际终止文件分别单独冻结。若所有分支未过医学门槛，继续补强普通任务基线，不进入未见确认或收益头claim。若通过，也仅为在已见小样本上的能力资格，必须补齐强raw/直接任务/error-cost-defer/随机/静态匹配控制与全部费用，再冻结确认方案。
