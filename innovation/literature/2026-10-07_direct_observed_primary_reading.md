# 稀疏观测原文核读：对本项目创新边界的新增约束

本轮核读两份作者 arXiv 原文的方法、主要结果及相关分析，不是作者代码/实验复现。共成功PDF30页；实际完整选读21页：Uhrig等p1-8，Eldesokey等p1-13。额外render并实际查看4页：Uhrig p6（跨稀疏度矩阵）、Eldesokey p4（式9/10）、p7（四种fusion结构）、p13（confidence/error相关）。未读Uhrig p9-16及Eldesokey p14，不把下载/提取称为完整阅读。

## 1. Uhrig et al., Sparsity Invariant CNNs

- 身份：Jonas Uhrig、Nick Schneider、Lukas Schneider、Uwe Franke、Thomas Brox、Andreas Geiger；3DV2017，DOI [10.1109/3dv.2017.00012](https://doi.org/10.1109/3dv.2017.00012)。本轮实际PDF为 [arXiv1708.06500v2](https://arxiv.org/abs/1708.06500v2)，页首30 Aug2017，16物理页。
- p3式2：卷积只累加observed值，再除以validity总量+epsilon；分母不是learned filter加权和。p3式3：max pooling传播binary mask。p4式4：有mask的skip融合；其“dense情形回到标准sum”的文字与印刷分母公式需结合实现解释，本轮未复现作者代码，不能直接作为我们skip层定义。
- p6 Fig4：三种对照是普通CNN、CNN+concatenated mask、SparseConvNet，同一五层kernel11/7/5/3/3、16channel结构，改变train/test随机dropout稀疏度。作者在Synthia报告SparseConvNet跨稀疏度稳定，CNN+mask仍显著失效。这是特定2D场景/配置结果，不是所有普通CNN必然失败定理。
- p7 Table3：synthetic-to-KITTI transfer的SparseConvNet MAE约.722-.734m，对照较差。p7 Table4：KITTI的depth-only模型有ConvNet、ConvNet+mask和SparseConvNet，并有RGB-guided方法；不能把RGB方法的额外信息抹掉。
- **直接影响创新边界**：p8 §5.3和Table5已经从稀疏depth直接做semantic labeling，VGG-depth/VGG-depth+mask/VGG-sparse的15类mean IoU为6.4/4.9/31.1%。因此“直接从稀疏观测做任务”“加mask做分割”“重建不是必须中间步骤”均非独立首创。
- p8 §5.2.1的不同输入density来自随机dropout。MRI本项目是固定整层stride4缺失，经0.5mm trilinear映射；不等同于独立像素随机缺失，不移植稀疏度不变性结论。普通dense U-Net与本轮direct基线都需要实测充分适配。

## 2. Eldesokey, Felsberg, Khan, Confidence Propagation through CNNs for Guided Sparse Depth Regression

- 身份：Abdelrahman Eldesokey、Michael Felsberg、Fahad Shahbaz Khan；TPAMI DOI [10.1109/TPAMI.2019.2929170](https://doi.org/10.1109/TPAMI.2019.2929170)。实际PDF为 [arXiv1811.01791v2](https://arxiv.org/abs/1811.01791v2)，页首5 Aug2019，14物理页；页眉LaTeX模板年份2015不是论文发表年份。
- p3式3-5将confidence与applicability分开，normalized convolution基于1993年Knutsson/Westin，并非本论文或本项目新概念。
- p4式9：`sum(z*c*Gamma(w))/(sum(c*Gamma(w))+eps)+bias`；非负Gamma可用SoftPlus。式10传播`(sum(c*Gamma(w))+eps)/sum(Gamma(w))`。同一个核同时用于信号加权和confidence归一化，区别于Uhrig mask-count分母。
- p5式13额外鼓励output confidence，系数随epoch下降；p5 Fig4多尺度confidence maxpool并按indices挑feature、nearest upsample融合。p7 Fig7已经比较early/late fusion及multi-stream/encoder-decoder。我们的两通道普通U-Net既不实现这些normalized layers，也不应冒称复现NConv-CNN。
- p8方法比较：分开训练并冻结unguided estimator再接guided网络；p11-12 Table6说明end-to-end版本未必更好。训练配方变化会影响结论，不能仅匹配参数量就宣称所有方法公平。
- p9 Table3：KITTI test的guided MS-Net[LF]-L1 MAE207.77mm，L2 RMSE829.98mm；unguided NConv-CNN MAE360.28mm/RMSE1268.22mm。guided有RGB额外信息。p10 Table4：NYU200 samples的EncDec RMSE.171m，500 samples .123m；UNet+CSPN .117m，不能写所有指标/所有条件都最佳。
- p12 Table7作者报告unguided480params/0.01s、guided约356k/0.02s；KITTI运行时间取benchmark server，硬件/操作不同，不能作为我们MRI系统节省的计量。作者也明确指出downsample/slicing/upsampling令时间不随参数数目线性变化。
- **影响我们的confidence/repair收益命题**：p12 §7.8、p13式16不是概率校准；分析absolute prediction error和negative log confidence，在两者histogram equalization后算Pearson。简单由input mask高斯传播的baseline，在NYU平均相关.1、KITTI -.25；learned output confidence报告.3和.4，后两值原文次序未在此强行绑定数据集。这证明作者已有confidence/error相关研究，也提醒“观测更密=>误差更低”在有错误输入时未必成立。
- p13关于未知分布相关上界低的泛化陈述没有在本轮得到定理支持；普通Pearson总上界仍1。不把本文经验相关当校准概率、部署保证或可修正性证明。高risk、低confidence和行动的净task benefit是不同标签。

## 与已有MRI工作结合后的决定

| 想法 | 原文已有内容 | 本项目接续方式 |
|---|---|---|
| sparse observation+mask直接分割 | Uhrig2017 §5.3有semantic任务 | 必须加入公平基线；不占有概念首创 |
| confidence-aware convolution/continuous传播 | Eldesokey式9/10及1993normalized convolution | 若普通direct基线弱，可作为已知增强对照，需另立容量/初始化/资源配方 |
| 在局部低confidence处做SR | confidence/error相关已有，旧项目也有risk/defer prior art | 比较同feature/capacity的error-risk与**实测增量收益**，看收益预测是否有额外价值 |
| fraction availability就是真实信心 | 当前mask只经已知插值核、没有误差监督/校准 | 名称保持availability；不解释成slice profile/临床confidence |
| mask+zero填充保证对观测强度平移不变 | 当前资格仅验证线性映射/增强合同 | `s*numerator+t*availability`用于数值正确性；不作为新机制或MRI效益 |
| 普通直接task基线输给SR即发表 | 当前未训练；已知更强mask-normalized方法还未适配 | 首先验证充分任务能力与合理强基线；失败不得利用弱baseline制造提升 |

下一步先等现有19series两臂完成及原gates。通过后进行同observed两通道dense-PCHIP/direct-task充分适配，保留旧one-channel及新padding增强配方因素；再公平接入原SR。若有task修正余量，再构建真实GT-free候选及联合效益label/全成本对照；若无余量，记录受控负结果。8保留确认继续关闭。

## 原文获取与阅读证据

题名索引 `source_cache/direct_observed_primary_2026-10-07/identity_attempt01.json`，PDF成功保存在同目录。第一次fetch脚本实际exit1：PDF已下载，但pdfinfo的Windows本地化诊断按UTF8解码失败，保留全部文件和失败JSON；第二次使用现有Poppler并以bytes接收diagnostics、明确UTF8输出正文，实际exit0（chunk644ac8）。四页render实际exit0（f7940c），随后四次view_image均成功。SHA与页级工具出处由该目录reading_provenance.json保存。
