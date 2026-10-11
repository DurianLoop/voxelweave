# 原始 nnU-Net 与 Revisited：基线资格对创新判断的影响

本次实际核读原始公开 HTML 的全部提取文字：nnunet_original blocks 0–80（81 块）、nnunet_revisited 0–75（76 块），包含正文、公式文字、主表/附录表文字及参考文献，共157提取块。部分 IEEE control 字符是格式残留，不能算157独立科学段落。全文来源为 arXiv 的原文表示；原论文图像像素、独立补充文件及作者代码没有核读，不声称完成作者实验复现。获取日志中的 reading=false 保持历史原样，另存阅读登记。

## nnU-Net: Self-adapting Framework for U-Net-Based Medical Image Segmentation

[arXiv:1809.10486](https://arxiv.org/abs/1809.10486)，2018；本次读的是该题名的 arXiv 文本，不将其等同于2021 Nature Methods最终文或 nnU-Net v2的完整配方。

块6–7直接提出：未充分配置的 U-Net 留有很大提升空间，预处理/训练/推断甚至比新模块更影响表现；作者在这篇省略 residual/dense/attention 等额外结构。块12：两次conv、InstanceNorm、LeakyReLU .01；块21–25按图像形状、patch、显存自动调整网络。3D基础例为128³、batch2、base30channels；各任务不同，不能拿单一数字当统一配置。

块16、19、32指出，fullres patch 视野不足可能难以识别器官，作者因此使用 lowres-to-fullres cascade。我们新增64×128×128的 .5mm网格只有约32×64×64mm物理patch，优于旧±2mm上下文却仍未证明覆盖足够解剖信息；小原生slab还含zero padding。不能因为换成3D就宣布强任务能力。

块31 MR用三阶样条、GT nearest，统一到数据集 median spacing；块34 MRI逐体积z-score。块37–43为训练集5fold、Dice+CE、Adam3e-4、每epoch250batches和loss趋势触发的降学习率/停训；不是本项目旧20k固定最后权重。块45–50包括rotation/scale/elastic/gamma/mirror和超过1/3样本前景强制。本项目的有限增强/半前景batch只能称标准候选，不是忠实复现自动配置nnU-Net。

块52–57：半patch overlap、中央权重较高、mirroring TTA、5fold模型ensemble、部分任务依据训练GT连通性做largest-component后处理、由CV选择两模型组合。额外推断和模型选择预算须计入；本项目单模型/无TTA/无筛组件，不能直接对比作者分数。块61的表2包含高低类别及测试分布差，块63承认部分配方选择未逐一消融。网页纯文本不保留bold语义，本记录不猜表格哪行被作者选中。

对应项目：完整native MR不是PCHIP变量；输入原生/观测统计、物理上下文、标签重采样、前景采样和全FOV覆盖需要先有实施证据。将这些修复当新技术贡献已经被本文直接排除。

## nnU-Net Revisited: A Call for Rigorous Validation in 3D Medical Image Segmentation

[arXiv:2404.09556v1](https://arxiv.org/abs/2404.09556)，2024，按v1文本解读。

块11 P1/R1：不能将新模块与residual encoder、额外训练数据、pretraining、大显存/长训练、20fold ensemble捆绑后，只与小baseline比较。P2/R2：标准化且充分配置的baseline比只分配“同样人工调参预算”更可靠。块13 P3/R3、P4/R4：数据集数量、统计稳定性、类别选择和小测试集决定结论范围；5fold有帮助，但在同数据开发和验证仍可能隐性过拟合。

块17–19：六数据集、共享5fold split、主Dice/次NSD。所有实验在单A10040GB同最大显存预算，但实际显存和时间各方法不同；不能解释成每个方法执行相同总预算。除A3DS SwinUNETR默认预训练例外外训练from scratch；作者透明保留这一例外，不能写成全方法完全无pretraining。该研究不开发新方法，未分开发/测试数据集池；这不授权本项目已多次使用的四验证充当独立确认。

块23表1：original nnU-Net约7.7GB/9h、ResEncM9.1GB/12h、L22.7GB/35h、XL36.6GB/66h；MedNeXtk5约18GB/233h。这些是在其六任务/设备的报告，不是本机RTX5090任务耗时预测，也不是GPU占用时越过资源守卫的理由。

块24比较No-Mamba Base与U-Mamba Bot/Enc，提示去掉mamba后优势可由residual U-Net解释。作者也发现CNN配置在本benchmark总体强，但不能扩展成“所有未来Transformer/Mamba在所有MRI都更差”。块74表5显示spacing就能解释部分MedNeXt差异：ACDC ResEncL91.69→isotropic92.64，MedNeXt92.65；BTCV83.35→84.01，MedNeXt84.70。这直接要求我们的SR/任务矩阵固定物理重采样和统计合同。

块19、72用inter-method/intra-method SD比值讨论数据集区分能力，该度量本身依赖所比较的方法/数据和配置。当前MC-RC 11开发/4已见验证/8保留确认，不能根据本文断言队列已足以量出小增益或泛化到所有临床病灶。

## 对剩余 claim 的决定

这两篇进一步排除“仅扩大3D网络/改变loss/加前景采样/换物理spacing/改滑窗即创新”，也排除“仅弱冻结任务网负差说明SR破坏病灶”。真实native输入和标准3D候选是基础设施与能力对照。

精确剩余问题仍是：充分任务适配后，同observed信息/统计/监督/容量/总预算下，能否修正可观测缺层病灶残余并优于强raw PCHIP及直接任务适配。若公平对照后无稳定残余，不能坚持正结论。该问题目前仍未验证其正答案。

新增准备：独立完整MR loader及全28源像素/label坐标核验完成；3D候选物理grid、前景与全FOV资格核验正在运行；实际GPU更新和能力结果尚无。GPU首次观测仅1394MiB空闲，因此没有启动自己的GPU训练。八确认关闭、科学确认数0。

原文与SHA见 [获取记录](source_cache/strong_task_baseline_2026-10-07/retrieval_attempt02.json)、[提取记录](source_cache/strong_task_baseline_2026-10-07/extraction_attempt01.json)；阅读登记另外保存，失败代理获取也保留。
