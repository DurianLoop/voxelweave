# 固定观测 MRI 自适应计算：本轮原文核读

本轮取得并读完两篇实际原文：RD-ViT 2605.03999v1（23文字页、12视觉页）和 HiFi-MambaV2 2511.18534v1（9文字页、7视觉页）。共32文字页、19不同视觉页。阅读原文和公开算术不能证明本项目有可发表的医学收益。两篇均为这里取得的 arXiv 版本，不能据模板页眉推断正式期刊发表。

实际来源、SHA和下载状态见 [下载 receipt](primary_attempt01/receipt.json)，选择来自此前实际索引 [receipt](index_attempt01/receipt.json)，不是凭空拼题名或链接。19张图像已实际逐张查看；提取/渲染 receipt 的初始 `text_read`/`visual_reviewed=false` 保留为执行时状态，最终阅读状态见 READING_PROVENANCE。

## RD-ViT

Renjie He，*RD-ViT: Recurrent-Depth Vision Transformer for Semantic Segmentation with Reduced Data Dependence*，副题 *Extending the Recurrent-Depth Transformer Architecture to Dense Prediction*。预处理输入下反复共享 transformer block，LTI injection、ACT、depth LoRA、可选 MoE；任务是 ACDC 心脏结构分割，还附有 ToothFairy2 CBCT 实验。不是 CISS 稀疏层恢复或病灶修正。

物理页5–9：3D输入128×128×16、patch16×16×2、512 tokens；2D224×224、196 tokens。标准注意力仍 O(N²d)。MoE 为8 routed experts、top-2，另1个全激活shared expert，不能按“只用2/8”把shared、router、attention、prelude/coda和decoder费用一起扣掉。ACT τ=.95，状态停止后仍参与其它token的attention，页7末尾明确省算主要来自FFN/LoRA，attention不省。

ACDC物理页9声明100患者、70/15/15患者划分，分别140/30/30 ED/ES volumes；所有结构Dice排除BG。主表训练100epochs、T4；数据效率实验前k患者、不随机取子集、50epochs、报告best validation Dice（页10）。不能把这些best-validation表当独立15 test患者效果，也不能把50与100epochs表合并。只有seed42，未报告患者级区间或多seed变异。

| 公开Table2（页10） | 参数数 | Best Dice | 训练秒 |
|---|---:|---:|---:|
| Standard ViT | 5,676,036 | .817 | 1123 |
| RD Tiny | 2,579,110 | .804 | 1154 |
| RD Tiny+MoE | 3,023,014 | .812 | 2189 |
| RD Tiny−ACT | 2,579,110 | .801 | 1158 |

CPU核表：MoE参数是标准基线53.2592%，Dice比例99.3880%，训练时间1.94924倍。ACT有无训练时间比1154/1158=.996546，只是公开训练时间，不是推理benchmark；论文页21也承认MoE约2倍慢。不能将参数压缩称实际速度提升。

页7估计mean ponder1.4对T8可得5.7倍 `C_eff` 降低；该公式把整个block当可跳算，而同页又保留所有attention。即便FFN真的只对active tokens执行，注意力、共享路径和路由仍需计费；作者是否真正gather/dispatch尚未核源码。页13的halting图可看到粗patch格、边界高ponder，不能证明实际执行量、Δ病灶收益或所有样本停止安全性。

页7和15的“ρ(A)<1保证整个递归为contraction”推论前提不足：递归还含 `f(h)`，需要对完整映射控制。论文自己给出 `ρ(A)+L<1`，但只称ViTBlock bounded，没有给L<.64证据。此次CPU标量反例 A=.36、f=.8*tanh(h) 有界且L=.8，0处导数1.16，并有三个不动点。反例只否定这个一般推断，不证明作者训练模型发散。实际depth-extrapolation图页15显示该样本/设置T6以后平台，属于经验结果，不能等同保证。

页14 Table4的2D优势为+1.2/+0.7/−3.6/+0.4/+1.0 pp；50%时反而较差。3D为−5.2/−8.4/−4.0/−1.5/−2.9 pp，页15“gap narrows monotonically”与表不一致。页14 Table3 .889和Table4 full .882分别位于不同训练协议，不自动当算术错误。页23 C1三结构 .753/.673/.875平均.767完全吻合，但未给它与Table2 .804的具体run/checkpoint映射，不替作者补身份。

附录B页23声称companion GitHub和“三个”notebooks，文字仅列NB1/NB3，未打印作者仓库地址。枚举整PDF URI为0；唯一文字GitHub是上游OpenMythos。四个有界GitHub查询返回metadata共9条，其中同名 `zhiruizz/RD-ViT` 描述是 *Recursive Dynamic-Dimension*，并非本篇 *Recurrent-Depth*；其余是前端或论文列表。不把它们认定为作者实现，没有读任何README/源码或执行作者代码。未命中不证明作者没有公开实现。

## HiFi-MambaV2

Pengcheng Fang、Hongli Chen等，*HiFi-MambaV2: Hierarchical Shared-Routed MoE for High-Fidelity MRI Reconstruction*。页3架构固定8groups，每group2units+DC；每unit有SE全局路径、SF-Lap频率分离、Mamba和shared/routed MoE。输入为undersampled k-space；虽然推理观测固定，物理动作域与本项目已有稀疏层CISS插值不同。

页4–5：shared experts全激活；pixel router softmax后hard top-1。Eq11写成所有expert输出乘mask后求和，数学表达不唯一指定实际sparse dispatch，可以dense算后mask，也可以gather后算。没有读作者代码，所以不能判定作者实现是假稀疏。字面hard argmax又未给门控幅度/STE；该式在非边界对router logits的重建路径梯度为0，源码需核。Eq14仅平均soft概率的平方balance也不保证hard assignment均衡：CPU例子概率(.2503,.2501,.2499,.2497)，loss1.0000008近最优1，但所有tokens均选expert0。这个是公式层面诊断，不是对作者训练collapse的实测。

页5–9报告PSNR/SSIM/NMSE，没有分割Dice、病灶漏检或体积误差。数据声明fastMRI1172 examinations（PDFS子集实际train/test个数未明确），CC35925train/10test，ACDC100/50，Prostate139/19；M4Raw正文1024/240volumes与附录139/19volumes不一致，不擅自解释为患者与volume单位不同。fastMRI首尾各5层和CC359首尾各15层被丢弃；ACDC中心crop128×128。不能把局部/过滤后视野结果当完整FOV性能。

| TableV（页7，320×320、A100） | 理论FLOPs(G) | fastMRI AF8 PSNR | SSIM |
|---|---:|---:|---:|
| ReconFormer | 270.60 | 30.42 | .728 |
| FpsFormer | 200.45 | 30.63 | .732 |
| LMO | 484.98 | 31.10 | .744 |
| V1 P1 | 270.37 | 31.81 | .762 |
| V2 P1 | 687.15 | 31.89 | .764 |
| V1 P2 | 67.87 | 31.38 | .758 |
| V2 P2 | 172.21 | 31.73 | .763 |

CPU核表：P1/P2相对同patch V1 FLOPs为2.54152/2.53735倍。V2 P2是LMO的35.5087%，但V2 P1是ReconFormer的2.53936倍、FpsFormer的3.42804倍；页7笼统“substantially more efficient”不对所有变体成立。“measured wall-clock latency增长更小”的段落没有给实际latency数、同步/warmup/分配/完整流程/失败路径，不能照搬为实测加速。

页6 TableIV M4Raw P1 AF8：V2−V1 PSNR−.06dB、SSIM−.002、NMSE+.001，三个方向均退化；P2有小幅改善。页6文字把V1 P1 AF4最高PSNR也写成31.82，表为31.81；保留表与文字。TableI的V1 P1/P2 fastMRI AF8 NMSE .020/.021与TableV .021/.020顺序不一致。页7 TableVII patch2 depth8×2是28.68/.841/.022，正文写28.28/.815/.026；patch1表29.05/.849/.020，正文又写28.68/.841/.022。视觉核读确认不是提取错列。TableVI视觉列显示无balance的MoE为28.50，而MoE-B+MoE为28.68；正文归因反过来。引用时不能挑最有利数字或说“所有表一致”。

整PDF实际URI仅参考/本篇链接；两个精确仓库查询0。未核作者代码，不声称复现或证明未开源。页眉仍是LaTeX模板，来源明确为arXiv v1。

## 本项目的贡献边界

这两篇足以说明“固定MRI输入下attention/共享循环/ACT/MoE/空间路由”都有公开先例。论文缺乏完整任务—成本证据，为本项目提出更严格评价要求，不自动意味着“没有人做过”或成立的算法首创。

保留的可证伪候选是：充分适配任务网之后，在固定CISS观测、合法局部动作和完整FOV下，预测真实病灶Δ任务收益，并在完整患者总成本内胜过同曝光强静态/risk/defer/cost策略。具体依赖与停止规则见 [后续控制](ACTION_VALUE_AND_ACTUAL_COMPUTE_CONTROLS.md)。
