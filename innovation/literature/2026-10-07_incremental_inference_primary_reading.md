# 增量推断三篇原文的阅读与项目判断

新增核读3篇原文的方法、主要实验和限制段落，新增摘要0。共取得42物理页的原始PDF和逐物理页文本；没有声称读完全部参考文献、补充示例或复现作者实验。实际完整文本阅读范围：DeltaCNN页1–8；SIGE页1–11和15–16，另核页12限制段落与页13–14相关引用；DeepCache页1–8。关键页DeltaCNN4、SIGE4、DeepCache5已渲染并实际视觉核看。合并输出曾截断，相关方法页单独重读；以另存阅读provenance为准。

| 原文与取得版本 | 核读证据 | 对本项目的直接影响 |
|---|---|---|
| Parger等，DeltaCNN，CVPR2022，10页，CVF accepted version | 页3–5 Eq1及Eq3–6、mask膨胀、截断阈值；页6–8精度/速度/存储/固定相机限制 | 稀疏修改、缓存及实际GPU跳过计算已知；FLOPs节省不等于真实延迟节省 |
| Li等，Efficient Spatially Sparse Inference for Conditional GANs and Diffusion Models（SIGE），arXiv:2211.02048v4，2023-09-13，21页 | 页4复用IN/GN统计的近似假设；页5–7 attention与实现范围；页7/9/11主要表格；页12限制；页15–16融合和编辑区域评价 | “固定参考统计量+局部更新”已有明确先例；其输出保持是近似性质，不能当完整原模型逐位等价 |
| Ma等，DeepCache，CVPR2024，11页，CVF accepted version | 页4 Eq4–6、页5 Eq7、页6–8表1–6及限制 | 高层feature跨扩散步缓存、uniform/non-uniform刷新已有先例；需要与减少采样步数作同吞吐对照 |

SIGE本文首页是IEEE TPAMI模板，年卷期占位；此处只确认实际下载作者稿v4日期，未核定正式期刊发表日期或DOI。它不是另计一篇2022会议稿。DeepCache的arXiv候选响应超过固定32MB上限，没有保存或阅读该PDF；首acquisition真实exit1和错误保留，换CVF取得6,232,623-byte会议原文后真实exit0，不将两次取得当两篇。

## DeltaCNN：局部性与数值保持不可混同

作者利用卷积线性 c(x+δx)=c(x)+c(δx)，但非线性层需要保留旧输入，计算 f(x+δx)−f(x)，不能直接对δx做普通激活。截断值另缓存并累计，避免小改动被永久丢弃。更新mask随卷积膨胀，GPU采用tile级skip/dense/very sparse分支；内存操作和控制流是实际瓶颈。

主要实验使用训练集子集调逐层ε，允许总loss增量3%，不是无条件无误差。其BatchNorm推断可与卷积融合；原文没有证明本项目逐patch当前输入统计的InstanceNorm3d能保持有限层内更新范围。不能把摘要“applicable to all CNNs”替代这项适用性核验。

表1 HRNet / RTX3090 / batch1：cuDNN 10.1FPS，作者dense 26.9FPS，sparse 30.5FPS。因此相对cuDNN的约3倍包含kernel/backend差异，单纯稀疏化对自身dense约1.13倍。batch32时sparse433FPS和作者dense97.6FPS是另一条件。项目后续必须同backend、同batch形状/顺序/precision比较，不能把最大7倍借用到MRI。

存储开销随batch线性增加；相机移动使输入近乎dense，稀疏收益减小。MRI中强全局SR动作、重新归一化或整幅缺层变化同样可能消除复用机会，需要实际输入差分，而不是按“动作名为local”预设局部。

## SIGE：与参考归一化候选的直接碰撞

第4页“Pre-computing normalization parameters”明确区分固定推断BatchNorm与动态IN/GN。对于后两者，它假设原图和编辑图feature相近，直接复用原图统计，替换为Scale+Shift。第7页实现说明：扩散模型复用所有GN统计；GauGAN复用较高分辨率IN统计。它同时利用逐层gather/scatter、kernel fusion、query剪枝，复用全局context。

这对项目之前的reference-statistics-forward是明确先例：现有实现仍可当机制对照，但“固定参考IN统计”单独首创需撤下。新增的单001缓存试验在受影响原batch内重算完整模型及动态IN，不应用SIGE的近似统计冻结；这只建立一种容易审核的执行资格，不能由此声称新稀疏推断方法。

表1显示DDPM与原模型的PSNR为52.4dB、LPIPS .009，有限PSNR本身已说明不是逐位相同；GauGAN对应26.5dB/.113，mIoU62.1 vs原62.4。页12明确承认未编辑区域正常full inference也会变化、局部冻结可产生seams，并可能漏掉全局光照/反射变化。MRI任务的微小病灶变化必须额外评价，不能用自然图像视觉相似替代病灶端点。

表2是单forward延迟；GPU200 warm-up+200 runs、CPU10 warm-up+10 runs重复5次。扩散还需逐t缓存，额外存储169M/56M/239M等float参数及全部迭代步；可放CPU但仍有转移成本。项目当前单次并发负载下6.36s/3.23s不具备这种benchmark条件，只记录forward削减。

## DeepCache：同吞吐对照与小病灶限制

它在某skip branch缓存上一步的高层up feature，下一步更新浅层down feature并拼接缓存；每N步刷新，非均匀策略在feature变化快的时段增加刷新。Eq5使用旧feature，不是旧值与新值严格相等的证明。

表1LDM-4-G：250DDIM基线FID3.37；N5速度4.12倍/FID3.59；N20速度10.54倍/FID8.23，非均匀N20为7.11。速度与质量存在明确tradeoff。表3同近似吞吐，50-step PLMS+DeepCache对比25-step PLMS：PartiPrompts CLIP29.46 vs29.33，不可只拿50-step慢基线宣称方法收益。表6匹配的是完整模型调用数而非总计算，浅层额外调用也应入账。

该原文未研究本项目MRI、缺层恢复或临床病灶任务。高层cosine相似>0.95不是小病灶任务保持保证。若将来确有可用扩散MRI基线，须固定seed/sampler/anchors并按实际总成本比较完整推断、减少采样步数、固定cache、既有non-uniform cache；真实task指标是必需，且在强任务适配能力通过后才能解释。

## 来源

- [DeltaCNN官方landing](https://openaccess.thecvf.com/content/CVPR2022/html/Parger_DeltaCNN_End-to-End_CNN_Inference_of_Sparse_Frame_Differences_in_Videos_CVPR_2022_paper.html)，[原PDF](source_cache/incremental_inference_primary_2026-10-07/deltacnn.pdf)。
- [SIGE arXiv](https://arxiv.org/abs/2211.02048)，[实际v4 PDF](source_cache/incremental_inference_primary_2026-10-07/sige.pdf)。
- [DeepCache官方landing](https://openaccess.thecvf.com/content/CVPR2024/html/Ma_DeepCache_Accelerating_Diffusion_Models_for_Free_CVPR_2024_paper.html)，[会议原PDF](source_cache/deepcache_cvpr_alternate_2026-10-07/deepcache_cvpr.pdf)。
- [首批取得记录](source_cache/incremental_inference_primary_2026-10-07/acquisition_attempt01.json)，[官方alternate记录](source_cache/deepcache_cvpr_alternate_2026-10-07/acquisition_attempt02.json)，[关键页渲染记录](source_cache/incremental_inference_key_page_renders_2026-10-07/render_attempt01.json)。渲染记录保持当时visually_reviewed=false；实际view_image后的记录另立provenance，不改旧文件。
