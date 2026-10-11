# 56完整FOV评价入口：执行准备与合成资格结果

主评价、独立重放和两项预检入口已准备；**没有执行真实MRI评价**。训练99542仍运行，不能用此软件准备宣称任务能力或可发表claim。

主入口 `experiments/evaluate_mc_rc_3d_19series_common_init_final_2026_10_07.py`；独立入口 `experiments/verify_mc_rc_3d_19series_common_init_final_2026_10_07.py`。主入口的`--readiness-only`真实子进程返回3，具体缺少最终退出receipt、完整terminal训练、两臂最后权重；MRI/GT数组读取0、CUDA未初始化、真实评价目录未创建。真实执行必须原训练39,996完成且实际exit0。终态receipt协议和全部历史/Optimizer/最后SHA校验在执行文件中给出，不能手写假的终态receipt提前运行。

## 真正完成的准备

28已有患者/series角色metadata核验，开发19每臂1139tile、已见验证9每臂369tile，两臂共56输入/3016tile，packed二值预测原始115,491,840bytes。4已见验证和8确认角色未变，本轮四验证MRI/GT像素未读，八确认与locked IXI test关闭。

全256合成四位置二值组合的full/anchors/missing/tail计数、空/undefined、完整分母，由两套实现核对；8种非整字节shape的保存/解包SHA一致。患者聚合示例A两series（Dice1/0）、B一series（Dice1），patient-first=.75，而错误series-first=2/3；空预测令precision均值undefined、空tail保留undefined，而且平均Dice合格仍不能掩盖一series TP0。此检查防止分母/聚合错误，不是新的MRI结果。

单真实尺寸64×128×128 patch、padding和非identity回映的合成网络：float32最大概率差1.13249e-6、阈值差异0；float64坐标最大差3.77476e-15、阈值差异0。修复后预检tool chunk996bad实际exit0。

两项事前规定的8tile重叠合成资格session60498/chunk13e1f2实际exit0：identity native的混合预测模型，float32/float64误差0；非identity native的固定背景head模型，float32差1.93715e-7、float64差5.13478e-16；全部阈值差异0，Gaussian覆盖为正且交叠最大coverage>1。没有optimizer更新，不是正式任务网络最终权重的MRI重放。

## 保留的失败与修复

首次预检chunk039f07实际exit1，256计数/packing/聚合/readiness已通过，float64检查失败。诊断a04b39实际exit0证实生产float32已过原3e-6/0门槛，但新写float64 NumPy核验误差5.93603e-8。原因是`physical`仍float32，先乘Python scalar时NumPy保留float32，随后才与float64广播。加一行显式`np.asarray(physical,dtype=np.float64)`后，float64错误降到3.77476e-15。原3e-12和0阈值门槛不改；旧失败源文件`.failed_float64_attempt01`、失败JSON与诊断都保留，源码diff/两个SHA在真实退出receipt。原失败预检源码也未改，新attempt02用独立包装入口和新目录。

## 后续实际执行边界

两臂最后19,998权重同时冻结后，主评价全部56概率hash/预测和端点。独立步骤重新生产全部56概率并核hash，再functional+独立Gaussian/coverage/NumPy完整坐标重放。float32原<=3e-6/0、float64坐标<=3e-12/0均保持，数值失败完整列出且不以float64覆盖float32；不会因一例失败删余下病例。主评价完成与能力全部gate通过分开。两步骤各3600s、合计新阶段保存250MB、CPU4/1、below-normal、RAM/磁盘各8GB余量；每forward guard，没有CUDA。

原能力gates及信息合同保持；科学确认0。实际完整MRI独立重放尚未运行，不用本合成成功推断28真实系列都过。准备入口减少长训练结束后的等待，不能替代训练结束、全FOV效果和真实患者确认。

[执行协议](MC_RC_3D_19SERIES_COMMON_INIT_FINAL_EVALUATION_EXECUTION_PROTOCOL_2026-10-07.md) · [修复与真实退出](SESSION_OBSERVED_EXITS_19SERIES_FINAL_EVAL_PREFLIGHT_2026-10-07.json) · [修复后预检](experiments/mc_rc_3d_19series_final_evaluation_preflight_attempt02_2026_10_07/attempt01.json) · [重叠资格](experiments/mc_rc_final_eval_overlap_synthetic_2026_10_07.json)。
