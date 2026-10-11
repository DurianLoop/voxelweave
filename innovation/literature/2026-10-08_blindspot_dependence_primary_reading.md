# Noise2Void／Noise2Same：已核原文与MRI动作收益候选的边界

新增核读两篇原文，目的为审查观测留出特征的信息依赖与理论适用范围。不是2026年前MRI方法的系统查新，也没有复现作者训练。论文取得、提取、阅读、视觉核读分别登记；这两篇不证明当前MRI病灶收益。

| 原文 | 身份／实际版本 | 实际文字核读 | 实际视觉核读 | 未核读范围 |
|---|---|---|---|---|
| Noise2Void – Learning Denoising from Single Noisy Images | Alexander Krull、Tim-Oliver Buchholz、Florian Jug；arXiv 1811.10980v2，2019-04-05，9页 | physical 1–8 | physical 5、8 | 主PDF第9页、单独supplementary |
| Noise2Same: Optimizing A Self-Supervised Bound for Image Denoising | Yaochen Xie、Zhengyang Wang、Shuiwang Ji；NeurIPS 2020官方Paper，11页 | physical 1–11；其中正文1–9、参考文献10–11 | physical 2、5、7 | 单独Supplemental的证明A/B、数据／训练细节C–E及F；AuthorFeedback未取未读 |

相关原文共取得20页，实际文字19页、视觉5页。错误ID所得28页铁电晶体管PDF仅核首页身份并排除，不能计第三篇相关论文或28页阅读。正文提到的Supplemental不在11页主PDF里；不能声称证明或附录已核。主PDF引用[18]“Leveraging self-supervised denoising for image segmentation”仅识别为后续查新线索，未取得／未读，不计新增论文。

来源：[Noise2Void公开作者稿](https://arxiv.org/abs/1811.10980)、[Noise2Same官方摘要](https://proceedings.neurips.cc/paper_files/paper/2020/hash/ea6b2efbdd4255a9f1b3bbc6399b58f4-Abstract.html)、[官方主PDF](https://proceedings.neurips.cc/paper_files/paper/2020/file/ea6b2efbdd4255a9f1b3bbc6399b58f4-Paper.pdf)。本地原PDF、逐页文字及渲染路径和SHA见[新增阅读provenance](blindspot_dependence_reading_provenance_2026-10-08.json)。

## Noise2Void：只预测上下文能解释的信号

第2–5页的核心依赖：信号有空间统计依赖，噪声在给定信号后pixelwise独立，且均值为零。屏蔽中心值、只在blind spots计loss，阻止网络直接学identity；上下文可预测的信号可以保留，独立噪声不能由邻居预测。作者明确区分denoising与更一般的blur恢复；不能直接推广为MRI缺层重建证书。

第5页Figure 3及implementation实际核读：64×64 patches，stratified抽样64个masked pixels，以邻居值替换，loss只计算masked点；U-Net加batch normalization。训练时mask不自动保证取消mask后的整个网络仍严格J-invariant，这一点需与Noise2Same分析一起理解。

结果不能照摘要概括为一概优于经典算法：BSD68 Gaussian σ=25，N2V PSNR 27.71，BM3D 28.59，traditional supervised 29.06。模拟显微镜含Poisson／Gaussian；真实显微镜没有clean GT，不能把视觉例子算作定量任务验证。第7–8页的高频／孤立亮点损失和Figure 6 structured noise保留／显现，是对稀有病灶的警示：低误差或平滑视觉不代表稀有结构被保留；噪声空间相关也可成为网络可预测的错误结构。

## Noise2Same：去掉网络严格盲点限制，并未去掉定理噪声条件

第2页Definition 1给出J-invariance；Eq(1)到Eq(2)消去与noise的交叉项需满足条件。第3–4页Eq(5)比较full与masked输出，发现mask训练后的f在full输入推理时通常并不严格J-invariant；mask加network组成的g与取消mask的f是不同函数。这个已知诊断不能作为本项目新方法首创，反事实单点扰动通过也不证明所有输入上的理论性质。

第5页Theorem 1已文字及视觉核对：输入normalized，噪声**zero-mean且各维i.i.d.**，J为uniformly sampled subset。Eq(6)对任意f用reconstruction error及full／masked输出差异的平方均值平方根构造监督风险加噪声项的上界。它取消了f严格J-invariant的要求，不能解释成任意相关／有偏MRI magnitude噪声都获保证。论文“不需要已知noise model”的口头表述不取消定理的zero-mean／i.i.d.条件。

第6页Eq(7)：完整输入上的reconstruction项，加masked维度的invariance项；默认λinv=2。计算需要full和masked两次网络输出，因此“所有像素都参与loss”不等于免费。Theorem 2针对zero-mean additive Gaussian、i.i.d.的分析把noise σ带入系数；随σ调整invariance权重是已知机制。本文没有核单独Supplemental的证明，也没有验证本项目归一化后满足这些条件。

第7–9页实验：ImageNet、HànZì、Planaria 3D microscopy、BSD68，均不是MRI。Table 3中Noise2Same在BSD68为27.95，比N2V 27.71高，但低于Noise2Self-Donut 28.20及BM3D 28.59；Donut在ImageNet却发生collapse（8.62）。因此“consistently outperforms”的摘要不能替代逐数据集比较。Planaria三noise level的Noise2Same为29.48／26.93／22.41，supervised为31.57／30.15／28.13，仍有监督差距。Figure 3的成本单位为50 minibatch steps，batch分别128／64／32，按GPU内存调整；不是本项目完整部署墙时预算。第9页broader impact把分割列为可能下游用途，没有病灶分割收益实验。

## 对当前项目的决定

本次[19系列观测留出结果](../OBSERVED_HOLDOUT_FEATURE_RESULT_2026-10-08.md)已实现先mask再统计／投影／预测。该依赖资格可支持普通经验特征的合法性；它既不证明MRI噪声条件，也不把heldout MSE变成clean-image risk或病灶任务risk。原部署用全部合法observed做统计是合法输入流程，不能因heldout诊断另需mask而把旧部署说成泄漏。

保留的候选是：在同raw观测和完整实测成本下，部署可见的观测特征加任务状态能否预测**动作后的配对病灶净收益**，而非只预测误差／不确定性。需比较同特征同容量误差头／风险头、固定合法动作、成本或defer、预算随机、union-aware greedy；加入共同投影dense-PCHIP因素控制，避免把预处理顺序效应当新恢复先验。

18/19系列的PCHIP heldout MSE较差只是已保留诊断，不能训练一个“选linear”的规则便宣称MRI收益。收益必须来自充分适配后同一患者的真实任务端点，成本必须包含特征计算、定位、动作生成、探索、transfer、推理、组合／后处理；多series按患者合并。若强基线后没有可修正余量，应记录负结果。行动依赖见[下一阶段准备](../OBSERVED_FEATURE_TO_ACTION_UTILITY_PREPARATION_2026-10-08.md)。

## 获取与工具失败链

原arXiv 2010.12062身份错误，PDF和28页提取保留；OpenAlex title lookup实际4cd0eb exit1、HTTP429，未重试同路线；官方NeurIPS index及abstract找到正确Paper。原8MB cap获取attempt01失败，单PDF上限先改10MB／stage25MB；正确PDF9591234 bytes取得成功，attempt02后在pdfinfo退出断言失败。MiKTeX实际打印11页却exit -1073740791，因AppData日志写入受阻；MIKTEX_LOG_DIR试验未修复，不再重复／不升级写AppData。

portable reader v1 urllib PyPI metadata TLS EOF（fb1b24 exit1）；v2 Schannel默认沙箱SEC_E_NO_CREDENTIALS（4f7373 exit1）；另存v3经自动审批允许的公开GET成功（62ac3c exit0），官方PyPI wheel SHA匹配，pypdf6.19.0／pypdfium2 5.14.0仅解包到innovation/tools，MRI环境与根文件不改。没有关闭TLS证书验证，没有自动审批拒绝；没有pip、用户进程控制或新代理。

独立读取器提取与渲染daf7df exit0；pypdf报告两个wrong-pointing-object warning但成功打开11页，原PDF未改。actual view_image核读5页；receipt里的text_read／visually_reviewed=false保持原始生成状态，新增provenance单独记录随后发生的核读，不回填旧receipt。stage完整归档50MB，医学资格作业20MB／1200s合同不变。
