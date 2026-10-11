# 新无增强20k权重：完整开发与验证评价协议

本协议在训练4831仍live、没有本模型验证前向时写定。只加载新的最后20000 checkpoint，先须独立20000draw/40000完整patch source映射/metadata/weight SHA核验通过；不按loss选中间权重，不修改训练源绑定。

固定顺序：已有11开发患者19series，raw PCHIP/observed_shared完整FOV诊断；随后四验证020/022/025/024共9series，每series raw PCHIP→raw linear，共18验证输入。总37完整条件，不按开发诊断结果省略验证或后见选患者。八确认仍关闭，四验证此前已使用，不能称新独立确认。

沿用训练physical .5mm、同5通道物理上下文/global-local架构、16tile或完整实际网格、覆盖均值融合、bilinear native概率映射后阈值.5。全native grid、全部z，no GT crop/no postprocessing；评价标签仅在该完整预测产生后加载。开发与验证标签轴/SHA、observed包与重建/统计/physical SHA完整保存。

full/missing/anchors/tail逐域报告TP/FP/FN、GT/pred、Dice/precision/recall、signed/absRVE、empty/undefined；边界使用完整affine RAS欧氏距离，pooled双向6邻接surface ASSD/HD95，保留非正交轴残差，不能套正交EDT近似。保持端点/域与原评价一致。每患者先均值series，再患者等权均值，None时不偷偷略去并报defined数。

能力门槛原样：四验证raw PCHIP full Dice≥.70、missing Dice≥.65、full recall≥.70、full absRVE≤.50；四人full/missing Dice均正，9series无TP0。完整37预测独立bincount/label/affine surface和首中末3plane重放，共111plane；重放是同架构实现核验，不是第二独立训练网络。

CPU单线程、自身below-normal、磁盘≥15GB/内存≥8GB；完整第一个开发输入只作运行时投影，预计总前向≤3600秒为资源守卫，不按分数早停。新评价目录<100MB，exist_ok=False保留attempt，不并行新训练或新评价；失败留存后另立resume协议。GPU、用户终端训练、locked IXI test与根环境不操作。

实际运行、指标、分支调用和失败必须从最终JSON与工具exit取得。不将37/111计划写成完成，不将能力gate通过解释为新重建claim。native/6×5公平矩阵、直接任务/随机分辨率与observable缺层修正、八患者确认仍是后续工作。
