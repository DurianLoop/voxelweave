# 空间自适应计算三篇原文：对MRI创新路线的约束

本轮新增核读3篇CVF正式会议稿，均核首页身份，各10物理页；30页PDF及逐物理页文本已保存。三篇主文页1–8的文字、方法、表格和图注全部实际阅读；SACT/DynConv页9–10参考文献也查看，SBNet页9–10参考文献未阅读。不把被引用论文算为已读。实际渲染并视觉核看7页：SACT5/7、DynConv4/8、SBNet4/6/8。没有取得补充材料、复现作者网络或完整视觉核看其他图页。本轮不是系统综述或截至2026年的穷尽查新。

| 论文 | 已核机制 | 与当前项目的重合 | 不能移植的结果 |
|---|---|---|---|
| Figurnov等，Spatially Adaptive Computation Time for Residual Networks，CVPR2017，pp1039–1048 | 每空间位置halting、任务loss加ponder cost、tile共享halting、膨胀依赖 | 区域选择、任务导向分配计算、早停与tile组织均有前例 | ImageNet/COCO FLOPs与精度，不是MRI总延迟或Dice |
| Verelst、Tuytelaars，Dynamic Convolutions: Exploiting Spatial Sparsity for Faster Inference，CVPR2020，pp2320–2329 | binary Gumbel门控、预算loss、gather/scatter和定制depthwise CUDA | 可学习局部门控、非均匀预算、实际稀疏实现均有前例 | MobileNet/ShuffleNet和MPII的2D结果，不等于本机IN3D U-Net |
| Ren等，SBNet: Sparse Blocks Network for Fast Inference，CVPR2018，pp8711–8720 | 预测低成本mask、固定block/halo、overlap-save、融合gather/scatter及重训 | 预测ROI后按窗口稀疏执行更直接碰撞；不能把它命名为新MRI路由模块就算首创 | 2D BEV网络的LiDAR三维对象检测，不是三维MRI卷积实验 |

SACT原文：[PDF](source_cache/spatial_compute_primary_2026-10-07/sact.pdf)；DynConv原文：[PDF](source_cache/spatial_compute_primary_2026-10-07/dynconv.pdf)；SBNet原文：[PDF](source_cache/spatial_compute_sbnet_2026-10-07/sbnet.pdf)。公开来源、HTTP、版本身份、SHA和逐页提取见两份acquisition_attempt01.json；阅读tool范围与图像登记见[provenance](spatial_compute_reading_provenance_2026-10-07.json)。

## SACT：区域计算分配与训练塌缩已经讨论

页3 Eq7–11以累计halting到1−epsilon决定N，remainder R使输出权重和为1；rho=N+R是几乎处处可微的计算量上界，并不是直接测量wall-clock。页4 Eq13用任务loss+tau·sum(rho)，Eq14门控同时用3×3局部卷积和全局pool。因此不能把本项目“局部+全局信息决定何时多算”“任务loss加入成本”列为宽新机制。

页5 Algorithm2对已停止位置保留前一层feature；第一1×1层需要3×3膨胀的active集合。另提出k×k tile共享halting、直接调用dense kernel，并明确tile太小会受kernel-call和重叠计算拖累。页5的“3D tensor H×W×C”指二维图像feature，不是3D MR体积。

页6解释dead residual unit：过早不执行使后层得不到训练、成本惩罚更容易继续不执行。作者以bias −3与dense预训练缓解。后续MRI收益门控不能将塌缩到全defer/少动作解释为已发现有效风险策略，也不能以新门控弱初始化比较充分训练直接任务。

页7 Table1需要同实现比较：SACT tau=.005有56.0±8.5% feature-extractor FLOPs/mAP27.61，作者ResNet101为100%/29.24。比较另一来源ResNet101的27.2并不足以支持“保精度省算”。本文只报卷积FLOPs，非线性/pool/混合输出另未计入该指标；没有本项目所需的完整资源计时。页8的saliency还混合center baseline，并用半个训练集调blur与multiplier，不能称毫无数据调参的任务无关自动定位。

## DynConv：门控与稀疏算子须分开核实

页3–4 Eq2–9门控每个residual block和pixel，训练用straight-through binary Gumbel；推断不加noise，最后20% epochs用零noise微调。gather将选中位置组成P×C×1×1的dense中间tensor；定制3×3 depthwise核通过索引恢复空间邻居，前1×1使用膨胀mask。这套kernel设计不能直接套到当前普通Conv3d+动态InstanceNorm3d。

页5 Eq10–17的预算按各层真实通道乘法数加权，并包含膨胀mask的前1×1开销。网络总预算loss与逐block预算loss不同；作者采用上下界退火，防止某层早期全开/全关。这约束本项目不能只按ROI面积或未膨胀支持当成本，也排除“全网络共享计算预算”这一泛化首创。

页6 Table1，MobileNetV2 theta=.25同148M MACs、同79.8准确率，binary版本724 images/s，标准Gumbel-softmax522。相同MACs仍差约39%吞吐，直接说明门控实现费用足以改变结论。基线宽度也有缩小对照，后续MRI应加入同总成本的便宜直接任务，避免只比过大的dense网络。

页8 Table2实际图像核读：baseline30images/s、PCKh88.1；theta=.5为48、88.2，theta=.125为85、86.7。caption写“2-stack models”，首row写“4-stack baseline”，保留此原文不一致，不自行认证统一stack条件。Table3 squeeze门控87.0/76images/s，1×1门控86.7/85：略高精度可能以门控开销换得；无需把其数字搬为MRI速度。

## SBNet：更直接的分块先例和成本口径

页3固定块大小以便批处理；按mask pooling构造block索引，overlap-save让输入重叠、输出责任区不重叠。页4对三个卷积的residual unit共享gather/scatter；明确稀疏BN统计改变，需要end-to-end重训。图3正文caption将k−s写作block stride，但图内标“Block Overlap Width”；不采用这个含混caption制定本项目几何规则。当前MRI原window/blend/batch保留，不把SBNet的overlap-save等同Gaussian平均或整图IN等价。

页5按相同cuDNN版本，并为dense基线用NCHW控制默认TensorFlow NHWC额外开销。较小block匹配mask更好，却增加halo；block尺寸是实测速度搜索，不能用患者GT挑最有利窗口后当部署结果。其输入800×1408×33是BEV高宽与高度bin通道，论文实现说明2D convolution，并不构成MRI3D卷积复现。

页6 Table1，90%稀疏的单层conv-5仍仅.88×，出现实际减速；同稀疏比例并不保证收益。整residual共享索引可提升速度，证明“按batch/union依赖计开销”比面积比例更合适，但不是新理论。

页8 Table5/7必须注明口径：Dense88.0ms，SBNet+PSP33.1ms，PSPNet另外3.2ms。Table5的2.66×数值与88/33.1相符；若顺序加上另列mask费，88/(33.1+3.2)=2.424×。这是根据表格的费用加总，不是复现作者端到端系统，也不能断言所有表都遗漏mask。PSP版AP73.01对Dense/no-mask73.28略降；Road版76.01对Dense/road-loss75.70，不能交叉比较两个不同训练loss基线。Table6 KITTI hard AP72.95→71.40，也不能把“almost no loss”写成所有条件零损伤。已有预测mask、计mask费用、弱精度下降/速度权衡都有明确前例。

## 项目决定

保留一个尚待MRI证明的具体问题：仅真实observed信息能否预测**具体修正动作带来的配对患者任务增益**，结合真实batch联合成本，在充分适配直接任务/强PCHIP/SR及成本、风险、随机、union-greedy、LTT/Pareto对照上仍有收益，并在冻结后的未见患者复现。SACT/DynConv/SBNet均未在本轮核读中提供这套MRI验证；这也不证明本候选领域首次。

本轮[真实标签支持诊断](../MC_RC_REAL_SUPPORT_CACHE_DIAGNOSTIC_RESULT_2026-10-07.md)只说明18/19系列存在条件窗口复用空间。oracle位置不能训练成部署输入；区域gate和cache继续作为已知方法/执行对照。下一步先完成原训练及能力验证，再检验预测ROI、真实修改差分与总延迟；只有MRI剩余收益支持新claim时才推进。当前新claim尚未确认。
