# 已冻结真实配对任务结果的标签适配资格

目的：把尚缺的完整患者动作label接口推进到实际保存的MRI结果；不重新做神经推断，不制造收益标签，不绕过当前正式训练能力门槛。全部新文件仅本目录、exclusive-create，旧源码/结果/SHA不改。原session99542继续、不重启/迁移，不操作其他进程。

固定资格来源为2026-10-03 intensity-only同一20000 checkpoint的旧full-task结果及已通过的independent_all37_metrics_and111_planes_attempt_01.json。只将其中已见validation4患者/9series、PCHIP与linear共18完整FOV结果配成9对；原模型capability_gate_passed=false保留。开发19series只有PCHIP，不能伪造第二路径；八确认和lockedIXI不读。JSON文档本身也含原开发metadata/分数，读取来源时明确此范围，不冒称只读物理上隔离的18行。

真实Q：原full Dice，基准raw_pchip，候选raw_linear，ΔQ=Qlinear−Qpchip。分数从已认证TP/FP/FN精确Fraction重算；患者内series等权、患者间等权。非正、零、失败/undefined全部保留；不把多个series当独立患者。同步核同patient/UID、全部source/label/统计/coverage、唯一checkpoint与旧独立计数，不能只按行位置连接。动作在此为整患者输入分支更换，不偷换成局部修正或joint作用。

只用standard library读取JSON/Python源文本；audit白名单拒绝MRI/GT/预测npz/checkpoint数组。CPU1/BLAS1/CUDA不可见、below-normal，单作业<=120s，磁盘8,000,000,000bytes储备、输出<=5MB。所有实测完整动作成本缺失保持null；旧inference_elapsed_seconds只登记原infer_native interval，不填作9个完整费用相位。真实路径score资格可通过但fitting/cost/risk/claim readiness仍false。

新generic adapter须拒绝缺series、重复key、错source/label/checkpoint、非完整coverage/GT入推断、scalar/count不一致、source统计不一致及以已见验证角色启动学习。检查使用真实metadata副本注入错误，明确不是新MRI失败或收益。独立verifier从旧source计数用不同端点公式及患者分组重放，不导入生产adapter。

不新计论文，本轮目标是实质可执行的label join资格。新正式模型及强三臂的开发action labels仍等原两臂真实final退出/冻结→56FOV/全部6gates/strict→同信息同容量强适配/合法动作及全成本。旧弱模型数据仅用于标签接口资格和原结果描述，不训练收益头、不选择新winner、不主张可发表。
