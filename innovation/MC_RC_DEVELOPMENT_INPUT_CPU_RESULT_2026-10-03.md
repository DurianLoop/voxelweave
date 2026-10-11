# 19真实开发输入与当前角色分母修正

上一轮角色生成器误用旧15条label visibility清单，漏掉已通过最新独立geometry/grid证据的002另一FIESTA时点（UID 1.3.6.1.4.1.14519.5.2.1.213711595575218613093188251544325434833）。本轮按最新 [开发case准备](experiments/mc_rc_current_development_input_preparation/attempt_01.json) 与 [当前全159角色CSV](experiments/mc_rc_current_development_input_preparation/all159_current_patient_roles.csv)追加修正，患者分配不变；旧39/18数值作为历史错误保留，当前为40/19。

| 固定角色 | 患者 | 候选系列 | 当前合格系列 |
| --- | ---: | ---: | ---: |
| 开发/训练 | 11 | 26 | 19 |
| 验证候选 | 4 | 9 | 9 |
| 确认保留候选 | 8 | 16 | 12 |
| 已分配合计 | 23 | 51 | 40 |

科学split仍未启用；同人所有时点同角色，58共享VS-SEG整人排除。此次仅打开开发患者的observed MR像素与监督标签，不打开验证/确认患者，不算方法效果或确认。

生产 [attempt01](experiments/mc_rc_development_training_input_cpu/attempt_01.json)已实际exit0：19系列/11人，observed-only包累计116,973,848字节，支持raw linear/raw四邻PCHIP×observed_shared/full_own统计。只解码phase0 stride4真实observed层；重建/统计没有label/native参数，监督标签单独读取。原生全FOV、同RAS整数轴变换、anchors逐字节保留、tail复制末anchor且与supported missing分列。旧16observed和raw PCHIP输入与旧保存hash一致。改变容器中隐藏层为非有限值不影响稀疏输出。

接续后原session1480已实际exit0，[独立复核](experiments/mc_rc_development_training_input_cpu/independent_all19_observed_inputs_and_label_axes_attempt_01.json)完整核354observed DICOM planes、76输入条件、19label轴映射，complete=true/errors=[]。复核从原ZIP再次只读observed层，用独立Hermite/harmonic slope实现重算PCHIP和手工统计/label轴变换；实际比较调用了生产reconstruct接口，不能描述为完全不引用生产代码。raw linear最大差0，PCHIP最大差0.0009765625（raw强度单位，float32舍入，预写容差通过）；并非所有独立插值逐字节相同。

上述生产/输入复核本身torch未导入、网络前向0、GPU0、科学确认0。随后单独启动的任务训练pilot有真实新前向，其结果另记，不能继续把整个本轮称“新前向0”。输入流水线通过不等于模型能力通过。

当前稀疏训练实现已具备真实case、来源SHA、分离监督、统计合同和原生支持域。下一科学步骤是从头训练任务能力和同预算矩阵，而不是再重复资格/归档计数；本轮 [CPU能力pilot协议](MC_RC_SPARSE_TASK_TRAINING_CPU_PILOT_PLAN_2026-10-03.md)落实这一部分，未替代完整native能力、6×5矩阵或最终确认。
