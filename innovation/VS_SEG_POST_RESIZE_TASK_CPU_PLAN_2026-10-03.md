# PCHIP处理顺序的冻结分割对照：45已见CISS

写于全45解析实验与独立复核完成之后，尚未计算新post_resize_pchip分割结果。这是结果后机制诊断，原45患者已见，科学独立确认患者0；不复活失败的原HAT负向主张。

新证据：显式clip没有实际改像素；线性顺序最大归一化差<1e-6；PCHIP全45超过阈值、最大像素差约观测范围1%–2%。支持域平均order NMSE效应约整体pipeline−raw的0.84%，双病灶平均order效应CI跨0。因此图像均值不足以判定分割敏感性，新增一项直接任务控制有区分力。

唯一新输入为固定post_resize_pchip，完全沿用既有解析实验：原网格PCHIP，observed-only归一化，缩256、同显式clip、恢复原网格；原真实anchors与不可插值tail沿用。其原始数组SHA必须与45解析输出一致；不调alpha/网格/核/clip，不看任务效果选患者。对每人只做一次作者冻结UNet CPU forward，不重跑HAT、SwinIR或旧七条件。

同一官方checkpoint、原始模型/过程局部MONAI兼容层、RAS方向、NormalizeIntensity、sliding-window(384,384,64)、gaussian、argmax及两标签。CPU单线程、仅自己below-normal、15GB磁盘和8GB可用内存门槛；CUDA_VISIBLE_DEVICES=-1且官方loader禁止CUDA初始化。不操作GPU、用户终端训练、locked IXI test、根环境/.gitignore。

保存每人的bool prediction_ras与物理affine、SHA、完整重建SHA、任务混淆计数、full/observed-anchor-slab/排除参考1mm边界域Dice、完整ASSD/MASD/HD95、逐患者post−pipeline/post−raw及旧pipeline−raw。新增预测不得用新标注/新阈值。全部45固定分母，TSE248不并入；失败完整保留，不用后续成功替换。

主要机制读数是原JSON full Dice post−pipeline，RT同域为预设敏感性；所有2标签×3域×3比较共18个描述性端点完整报告。full/slab固定45患者等权；1mm域若原参考core为空则Dice undefined，按三条件共同非空患者配对，保留全部undefined名单和45原分母，不填零或换参考。共享bootstrap seed20261101、5000draw，区间未familywise校正；没有预写发表成功阈值，不能根据显著端点择优宣布确认。记录正/负/零患者及逐患者绝对变化。pipeline−raw是既有对照，仍属于次要诊断。

先验证新预测的bool/shape/RAS/源与输入SHA，再独立ROI confusion、完整网格物理边界距离、逐患者差值、math.fsum bootstrap和手写分位。解析重建的全部像素由前一独立proof覆盖，本任务再次生成并逐位hash；不安排45次额外相同network forward。共享native解码、网格、skimage、冻结checkpoint/MONAI和RNG，不声称软件栈/模型/科学样本独立。

若post与pipeline差异小，而二者对raw的任务下降相近，只支持“单次固定冻结评估器中，processing-roundtrip是主要候选因素、PCHIP顺序难解释全部差异”，不能单独归因抗混叠、缩网格、内部resize clip或真实解剖损伤。若新post改变任务结果，需完整报告患者反例，再做预先固定另一任务模型/输入训练矩阵/独立来源。任何结果均不能自动成为宽方法创新。

执行：`D:\conda\envs\MRI\python.exe -X utf8 -B innovation\experiments\vs_seg_post_resize_task_cpu.py`。一次45 CPU推断按旧单人约65秒，估计约50分钟；耗时估计不作为完成或终止证据，必须实际poll。
