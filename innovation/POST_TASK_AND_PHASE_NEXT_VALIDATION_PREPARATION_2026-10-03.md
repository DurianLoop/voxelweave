# 完整post结果后：具体后续验证准备

## 2026-10-03完整pilot后的状态更新

[三人pilot](ANCHOR_BANDWIDTH_TASK_CPU_PILOT_RESULT_2026-10-03.md)及12输入/36端点复核均已完成，不再运行。主要post_fixed−post JSONfull−.00505496、RTfull−.00507443；去1mm带正向但full负向，固定带宽恢复解释停止，不盲扩45。新增边界计数与实际missing预测审计均已完成，无新前向。原文下列“正在执行/尚无结果”等保留为写作时点记录。

[新增三篇直接先例](literature/2026-10-03_task_normalization_context_fulltext_reading.md)证明归一化、多输入训练、分割条件生成与独立任务评价不能宽称首创。优先准备[6模型×5输入矩阵](experiments/task_input_contract_matrix_preparation_2026-10-03.json)：三种训练曝光×full-volume/observed-anchor统计，统一容量/患者权重/20,000拟定updates；比较native、raw、pipeline、post、HAT。anchor-only统计从observed MR计算，无reference labels或missing真值。该规格design_prepared_not_executed_not_frozen，真实训练/验证/未见确认名单及全部参数资格完成后才能冻结，当前没有启动GPU。

[创新判断](INNOVATION_DECISION_AFTER_POST_TASK_AND_PHASE_2026-10-03.md)给出强对照和停止候选；旧45及MC-RC8患者只作开发，FeTA SRR体积不是原生薄层确认源。下一项独立工作是更窄先例与来源资格审计，不重复失败blur/排序候选。

## 原准备内容（历史时点保留）

全部GPU训练prepared_not_executed，用户GPU/终端训练不干预。最新正在执行的工作是[固定3人12forward CPU机制pilot](ANCHOR_BANDWIDTH_TASK_CPU_PILOT_PLAN_2026-10-03.md)，不是新方法确认；必须等12条件和独立输入/36端点复核结束再统一分析。

## 最近的CPU控制

完整45中raw/pipeline/post的JSON full Dice .74460/.65476/.65284。post与pipeline差平均−.001918，描述区间[−.004830,−.000159]；两标签/全部域保留，原JSON去1mm边界的顺序差区间跨0，不宣称所有域均显著。顺序不是目前raw/缩放两路径大差距的充分解释。

新pilot固定原缺层数组，对anchors做一致roundtrip，分别使用own和paired baseline fixed normalization。fixed使送入任务网络的缺层不变，但修改anchors仍能经网络上下文影响预测。若fixed条件改善，只支持anchors介入在冻结网络内有影响；仍可能是absolute blur、训练分布、全volume上下文等，不能直接称全部为bandwidth mismatch。若无改善或变差，保留反例，停止用当前干预解释任务损失的恢复主张，不能反调sharpness参数/换人/换标签。

需要全45开发扩展时，必须另冻结全部四条件及预算、报告两标签/全部反例；不能只扩展pilot中最好的条件并称确认。在确有可区分的新问题之前，不重复原已结束的45新post前向或已失败order_rms/残差相加。

## 将来GPU空闲时有区分力的矩阵

复用[已准备的跨输入任务网络方案](FROZEN_TASK_EVALUATOR_FOLLOWUP_PREPARATION_2026-10-03.md)，将raw/pipeline/post和observed-preserving SR全部作为固定evaluation输入。训练输入native/raw/混合曝光，统一capacity、patient名单、steps、augmentation和阈值，不能为每输入挑最佳checkpoint。此矩阵区分冻结评估器暴露与输入变化，不能一概证明解剖无损。

若考虑native特征旁路或latent resampling，必须显式与VINNA/Lazy Resampling直接先例比较。若考虑slice频率loss/contrast约束，dStripe是直接先例；若考虑interleaved自监督、跨帧context或冻结downstream任务，STRESS/SMORE是直接先例。本static CISS没有可用邻时帧，不能补造输入。

尚未实现/训练的新候选是：仅从observed MR获得尺度/纹理信息，在保持anchors和tail不变的条件下生成缺层，并检查对任务输入归一化与邻层统计的影响。需要同容量native-grid、简单raw PCHIP、固定频率修正、taskloss及随机预算等强对照；旧残差相加2/6、order_rms失败不能通过改名覆盖。宽结构已经有先例，是否有窄可发表贡献完全取决于真实效应及充分查新。

## 科学独立确认资格

原45CISS与MC-RC已见8开发患者不可用于以后新方法完全未见确认。已有native冻结评估器在MC-RC16系列明显失败，不能默认它适合新肿瘤来源。先在独立开发来源审任务模型能力，再冻结真正未用于选择的确认患者；确认队列不能按native Dice挑患者。

新来源需实际acquisition header/原生层厚与step、重复/共享患者跨walk、标签同网格及语义、source发布/处理链、patient-group split及frozen任务模型训练角色核验。重建1mm/MNI体素不能冒充原生薄层。现有71候选/159有标签T2只是来源准备，不是合格独立确认名单；锁定IXI test继续不读取。

最终claim必须明确只在什么合同/输入/任务/来源成立，保留未通过的假设、首失败与反例。软件复核、论文数和开发pilot均不完成科学目标。
