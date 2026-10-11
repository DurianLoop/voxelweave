# 小波主干 IXI-T2 x4：用户指定的跨域探索（2026-09-28）

用户明确要求当前最好候选在IXI评估，并选择小波主干（兼顾质量）。这覆盖之前“未过fastMRI门槛不开放外部实验”的研究顺序限制，但不更改任何旧gate结论。本次是独立预登记的IXI探索；fastMRI小波+0.01755dB未达+.10的事实保留，不伪造三seed晋级锁。

## 固定候选与初始化

只运行PAST wavelet3：64通道/10块MA3，四锚点，三级Haar共享核、640个gate参数，多尺度latent、linear coarse+bounded residual和dual-domain保留。用户选择了质量指标均改善的版本，而不是PSNR最高但部分质量退化的方向增强版。不在IXI比较多个候选挑赢家。

初始化固定为fastMRI `full_wavelet3_seed3407_vram20/best.pth`，SHA256 `6f9002aa41c90ecfab3038dddd65c1a43cd494affb417af14bed82fcdd642728`。在IXI train上微调，非零样本迁移、非随机初始化实验。

## 数据和预算

原IXI seed3407患者划分：404train、58validation、115test，彼此不重叠。只用T2，x4 through-plane。训练和验证都使用实际模拟采集网格z=0,4,...，不引入其它grid offset；每轮在所有train区间中无放回抽4000区间，由seed和epoch唯一确定，每轮重抽。验证使用58名患者全部完整区间，按患者等权PSNR选best，不按test选型。

所有输入只由观测层min/max归一化；target使用同一变换，不clamp。256²模型/评分；4个真实锚点，不足槽重复真实端点并保留valid。训练volume的全部目标只是用于监督，模型forward不读取target。float32预处理缓存按源文件SHA命名并校验缓存SHA，约16GB覆盖train+val，用于避免每个随机样本重复解压/resize；最多4个mmap常驻索引。缓存不是额外训练样本。

固定80epochs/min30/patience15，AdamW lr2e−5（所有参数同lr），wd2e−5，betas(.9,.99)，warmup5+cosine至.05，EMA .999，原完整loss，effective batch16、microbatch2、checkpoint5/10。已有小波参数均已训练，因此不再冻结旧主干/单独提高gate LR。每轮250次尝试更新，最大20,000；这是预定的IXI微调预算，不是与I3Net相同累计训练成本。

使用已经验证的AMP溢出处理：仅GradScaler确认Inf/NaN时跳过该次Adam更新并降低scale，EMA也只在成功更新后前进。原严格有限梯度裁剪保留；所有跳过记录。所有代码、manifest、初始化与协议哈希进入manifest。

## 测试与比较

训练完成后先锁定best SHA和当前代码/配方，再通过独立test入口一次评估115名test患者。入口拒绝smoke和未完成训练。只选择一个模型，不依test修改架构、LR或再挑epoch。用户本次授权探索test，不冒充以前未触碰过的新独立IXI测试集。

I3Net使用现有IXI官方完整模型的 `baseline/ixi_i3net/runs/full_test115_stable/checkpoints/i3net_epoch_best.pth`，保持完整滑窗4→13重建与重叠融合、FP32，不缩成代理。对双方统一使用observed-only归一化、256²、只评分缺失层、双方输出均clamp到[0,1]（I3Net在每个窗口内先clamp再融合，保留其历史推理定义）、逐slice再逐patient聚合的8项指标，并做10,000次患者配对bootstrap、胜率、困难组与效率报告。

这与旧主表31.3058dB的native-volume流程不同，因此必须重新测双方；不得拿新分数直接减31.3058。I3Net历史训练使用dense-volume normalization，PAST还继承fastMRI预训练，目标函数/历史预算也不同，报告必须保留这些限制。统一本次推理/评分不抹去训练合同差异。

PAST−I3Net的均值PSNR>0且配对CI下界>0，才称本次单seed实验的PSNR优势；质量守卫方向不退且>=60%患者胜出才视为有希望的综合结果。不是“超过I3Net就等于全球SOTA”。最终确认仍需三seeds、匹配训练合同与适用的近期强基线；不能重复利用此次test来调参。

文献身份：I3Net为TMI 2024，官方代码 https://github.com/eeeric-code/I3Net 。2025年仍有新的MRI层间插值工作（如Zero-X21，https://www.sciencedirect.com/science/article/pii/S0167865525002296），是否属于同任务/数据合同需进一步核验，不能仅凭论文自称SOTA直接混入当前表。

## Validation smoke 发现并修正的比较错误
2026-09-28 首次评估 smoke 在 validation 病例 IXI002 上发现：旧 IXI I3Net 的训练损失与推理都包含 clamp(0,1)。新入口如果取消该步骤，未裁剪输出会产生严重异常误差，不能据此宣称 PAST 优势。原始诊断保留在 results/smoke_evaluation，明确废弃为正式比较结果。修正版保留 I3Net 逐窗口 clamp 后融合，同时对 PAST 输出执行同范围 clamp；target 不裁剪。这是恢复既有基线语义，并非根据 test 选择后处理。训练/选型仍保持 v2 原始未裁剪 validation PSNR，不在多种后处理间择优。修正版 smoke 位于 results/smoke_evaluation_final；未打开任何 test 像素。
