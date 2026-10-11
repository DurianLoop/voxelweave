# 下一项 CPU 诊断的具体准备（尚未执行）

当前固定 20,000 步模型在四验证人上 mean full/missing Dice=.127522/.135304，三系列全漏检，门槛失败。完整输入、坐标、计数、距离和54plane重放通过；这些只排除了相应实现不一致，未确定优化、数据量或跨来源差异哪一项是原因。

下一步先用这个冻结最终模型检查开发训练集可拟合性，预算与阈值不改。为避免继续只看训练前景 patch 的偏置表现，优先完整推断全部 11 开发人/19系列的训练匹配 raw PCHIP/observed_shared，完整 FOV 与全部原生 z。只读已认证的19 observed-only包，不读 native隐藏MR。报告原生 full/missing/anchors/tail、物理表面、漏检和signed/absolute体积；所有19系列保留，先患者内再患者等权。

输入/API已具备：mc_rc_global_local_task_cpu_support.py 的 load_authenticated_observed、sparse_image、physical_shape、resize_image、infer_native；监督标签仍用 developer-only read_supervised_label。指标函数在新纯CPU模块，避免导入旧 Torch support。冻结 checkpoint/支持源码/训练身份与本轮诊断split的SHA必须相同；输出新目录/新协议，不覆盖当前验证结果。每个开发输入至少首/中/末3plane独立重放，计数/距离用同批独立算法；共享architecture仍不能算第二独立模型。该完整开发 evaluator 的新入口尚需编写，不能把本文件当已执行。

解释事前写清：训练内也很低→仍不能说明重建无效，优先单病例同架构拟合与同预算loss/采样对照；训练内充分拟合而验证低→检查预先已知来源/spacing/FOV分布及训练样本覆盖，不据验证换人或调确认阈值。global loss 接近1与监督稀少仅是诊断线索，不当作已确定的失败原因。

后续单病例/优化对照需单独事前协议。已有012/013仍为开发；不能用四验证病例作训练再宣布验证。loss候选须先核作者实现中的类别顺序、FP/FN权重及γ定义，以相同初权重、同patient/series draw、augmentation和更新预算对照BCE+Dice，不混淆更多训练与方法改进。native能力控制也需独立完整MR loader与自己的证明，尚未执行。

CPU单线程、自身below-normal，磁盘15GB/可用内存8GB底线，先单输入估时再固定完整推断预算；不操作GPU或用户训练，八确认保留仍关闭。该诊断无新训练update，不计科学确认，也不构成新方法claim。
