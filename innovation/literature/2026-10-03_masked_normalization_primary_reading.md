# 已知区域统计、掩膜卷积与归一化等变：三篇原始PDF核读

这批实际取得3份公开原始PDF及逐页文本。阅读覆盖范围各不相同；不能把下载、提取或题名命中计作完整阅读，也没有复现作者实验。对应[阅读登记](source_cache/masked_normalization_primary_2026-10-03/reading_provenance.json)绑定原始PDF、文本、实际已读页和三页视觉检查。首下载后的缺依赖错误及第二次链接解析错误均保留，第三次使用既有Poppler成功，不安装依赖或改根环境。

## Region Normalization for Image Inpainting

AAAI2020，DOI [10.1609/aaai.v34i07.6967](https://doi.org/10.1609/aaai.v34i07.6967)。[原始PDF](source_cache/masked_normalization_primary_2026-10-03/region_normalization.pdf)，[逐页文本](source_cache/masked_normalization_primary_2026-10-03/region_normalization_pages.json)。已读8页正文及参考文献范围，重点PDF页2–7；页3公式与Figure 2实际视觉核看。

页3 Eq.8–12把每个channel按区域mask分组，用每区域自己的mean/std归一化，再合并；Eq.1–4的动机例子假设hole区域全部为255。不能把这个特殊分布假设当作任意MRI解剖区域的定理。RN-B在早期按原始已知/未知mask分开处理，RN-L在后层根据特征估计区域并学习空间affine调制。它在特征层分区域归一化，不等同于本项目只从anchors取一次全局输入统计，但直接占位“未知区域改变全空间统计、用掩膜排除其影响”的宽思路。

原文页5–7实际比较Places2/CelebA、固定和不规则hole、RN-B/RN-L位置以及None/IN/BN/RN。Places2全验证集36,500张，Table 3 baseline IN的PSNR24.37、RN25.10，SSIM .806→.823；这些是作者自然图像inpainting结果，不是MRI或独立任务分割表现。后层错误使用原始mask会降低结果，RN-L放到encoder也不如作者组合；不能把所有层同一种mask统计默认成有效。

**对项目的决策：** anchor-only mean/std可以作为阻断生成内容反馈的控制，不能单独当方法创新。需要在同统计规则训练的任务网络中、相同observations与训练曝光预算下比较，且保留raw强基线。本项目的小幅统计互换结果不能借自然图像结果升级成MRI收益。

## Image Inpainting for Irregular Holes Using Partial Convolutions

ECCV2018，DOI [10.1007/978-3-030-01252-6_6](https://doi.org/10.1007/978-3-030-01252-6_6)。[原始PDF](source_cache/masked_normalization_primary_2026-10-03/partial_convolution.pdf)，[逐页文本](source_cache/masked_normalization_primary_2026-10-03/partial_convolution_pages.json)。实际重点读PDF页3、5–9、12–14；没有把16页全部记作核读。页5 Eq.1–2实际视觉核看；没有另读supplement或复现实验。

页5的partial convolution是对`X*M`卷积，并乘窗口像素数/有效像素数；有有效输入才加bias，无有效输入输出0。下一层mask只要窗口至少一个有效输入就更新为1。页5还明确引用sparsity-invariant CNN与Shepard convolution等前例，所以“只卷积可见体素”“mask逐层传播”本身也不能宽称新意。

页6–7区分原输出与composited output：后者把已知像素从输入拷回，同时用于perceptual/style等loss。页9明确讨论hole污染BatchNorm mean/variance，先训练，再在fine-tuning时冻结encoder BN、保留decoder BN。不是首次发现未知区域统计污染，也不是严格的全网络masked BatchNorm。ImageNet/Places2/CelebA-HQ及不规则2Dhole不能替代本项目规则缺层的真实MRI任务确认。作者页13披露稀疏结构与大hole仍会失败。

**对项目的决策：** observed-preserving compositing是必要合同和强对照，不能单凭“拷回anchors”宣称创新。输入归一化、网络内部BN与最终图像值保持要分别记录；冻结官方checkpoint的BN不消除输入全volume统计反馈。部分卷积如后续使用，应与已有实现及同容量模型直接比较。

## Normalization-Equivariant Neural Networks with Application to Image Denoising

NeurIPS2023，DOI [10.52202/075280-0249](https://doi.org/10.52202/075280-0249)。[原始PDF](source_cache/masked_normalization_primary_2026-10-03/normalization_equivariance.pdf)，[逐页文本](source_cache/masked_normalization_primary_2026-10-03/normalization_equivariance_pages.json)。实际读PDF页1–10及附录页21；其他附录和另附材料未完整核读。页3 Lemma 2与denoiser定义实际视觉核看；页21 Table 6按文本核读，未声称视觉核图。

对正比例λ和共同offset μ，要求`f(λx+μ)=λf(x)+μ`。页5–7用无bias、卷积权重总和1的affine卷积，以及每两channel排序替代逐元素ReLU；组合、concatenation、affine residual可保性质。padding须由已有特征填充，普通zero padding对shift不能自动成立。仅移除bias不够；原文还明确指出attention模块通常破坏scale-equivariance。不能把这个性质直接归给现有HAT/SwinIR/官方BatchNorm任务网络。

作者比较ordinary、scale-equiv、normalization-equiv DRUNet/FDnCNN，重点是噪声水平外推。页8–9 Table 2的接近PSNR是去噪实验条件下结果，不保证分类/分割保持表现。页21 Table 6已经明确：分类向量等变经过argmax变为标签不变；且VGG8b norm-equiv在MNIST/Kuzushiji-MNIST/Fashion-MNIST的误差均高于ordinary，例如Fashion-MNIST4.53%→6.57%。因此“等变logits导出强度不变标签”和简单分类应用均不是本项目新推导或现成收益。

**对项目的决策：** 可以把affine输入变化列为审计对象；不得将归一化等变架构改名成新MRI方法。若以后比较该类网络，必须重新训练、核对padding/残差/BN/attention全链条件，并报告同域损失。仅解释已有checkpoint输入变化不构成架构贡献。

## 本轮留下的研究空间

三篇共同说明归一化/掩膜控制有成熟前例，但未替本项目完成“相同采集observations、重建图像改变、任务输入统计改变、任务训练曝光改变”的受控区分。这个窄问题可以继续做；当前仅是研究问题。三人互换统计的小幅异质响应，以及全45原post−raw损失，均不支持已有新方法成功。下一步先完成[全45输入统计审计](../FULL45_NORMALIZATION_DRIFT_CPU_PLAN_2026-10-03.md)，再按[既有训练矩阵](../POST_TASK_AND_PHASE_NEXT_VALIDATION_PREPARATION_2026-10-03.md)准备来源资格与预算对照，不挽救已失败的anchors带宽干预。
