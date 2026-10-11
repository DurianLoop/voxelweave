# 最后共同初始化模型的完整评价执行绑定

此协议具体实现上一准备文件，在最终模型和任务效果打开前冻结。训练session99542仍live，不能现在执行MRI评价；可运行仅合成/metadata的预检和readiness检查。八确认及locked IXI test关闭。

前置条件：训练invocation01+02实际共39,996更新；各最后19,998权重同时冻结，source-bound模型/config/流/历史匹配；完整训练实际exit0 receipt，名称`SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_2026-10-07.json`，含training_result_file、training_result_sha256、training_observed_tool_exit=0、formal_training_updates=39996。最后权重SHA、AdamW全部参数step19998/有限moments与19998行流/配对GT/augmentation由评价加载前核验；没有这些材料就deferred，不初始化CUDA、不读MRI/GT。

主入口计划 `experiments/evaluate_mc_rc_3d_19series_common_init_final_2026_10_07.py`，无update。两臂native/PCHIP各完整开发19+已见验证9共56series，身份和输入geometry来自既有认证metadata，native为信息上限参照，PCHIP只读observed包。推断不读GT，不用GT ROI；结束推断后读native GT，计full/anchors/missing/tail完整TP/FP/FN/TN、Dice/precision/recall/signedRVE/absRVE、所有空和undefined。二值预测以little-bitorder packbits和原shape保存，概率只存hash；全56原始packedbytes115,491,840，不含NPZ元数据。

病例内先series均值、再患者均值；任何参与指标undefined则该均值undefined，同时保存定义数量。两臂分别四验证gates：fullDice>=.70、missingDice>=.65、fullrecall>=.70、fullabsRVE<=.50、四患者full/missing正、9series fullTP>0。阈值.5/无TTA/无component过滤/完整grid/半窗Gaussian始终固定。能力失败也可以完成技术评价，不因分数低返回“未运行”或改样本。保存每患者/series全结果，后续论文没有独立确认效果前不能正向claim。

独立入口计划 `experiments/verify_mc_rc_3d_19series_common_init_final_2026_10_07.py`：只在主评价实际exit0、complete、56完整结果与预测SHA匹配后执行。逐series重新生产同最后模型全部概率，概率SHA与所有packed预测完全一致；再独立functional网络、独立Gaussian/coverage/NumPy坐标重放，float32概率最大差<=3e-6/0阈值差异；同physical概率的float64 torch坐标与独立NumPy坐标最大差<=3e-12/0阈值差异另记。float64只是坐标核验，不是float64神经训练或改变生产精度；不能覆盖float32失败。全56都报告strict pass/failure；一例数值不通过不删除该病例或剩余病例。

全部56预测full计数与四域分区由独立集合/逻辑实现核验，patient-first均值用独立Fraction/整数比值复算，不复制主聚合浮点结果。主评价和重放分别CPU4/1、below-normal、无CUDA、墙钟3600s，两个步骤作为同一后处理阶段累计保存250MB（每次都检查全目录），RAM/磁盘各8GB余量。guard逐series并进入推断循环；每阶段所有源码/协议/模型/输入源SHA绑定。新来源/配置变化另立版本，旧失败保留。

主评价完整技术执行exit0不代表能力全部通过；独立重放完成但strict gate失败时结果complete=true同时返回exit1，并保存numerical_failures，不能宣称核验成功。计算/来源/资源异常则complete=false并保存traceback。执行资格预检包括完整28shape/tile/packed分母、无最终模型时确实deferred、有限体积合成FOV/阈值/空值/不等series患者聚合检查；不读真实MRI/GT、不计任务能力。

[上一准备](MC_RC_3D_19SERIES_COMMON_INIT_FINAL_EVALUATION_PREPARATION_2026-10-07.md) · [正式训练](MC_RC_3D_19SERIES_COMMON_INIT_CPU_PROTOCOL_2026-10-07.md) · [独立99资格](MC_RC_3D_19SERIES_COMMON_INIT_SEGMENT99_RESULT_2026-10-07.md)。
