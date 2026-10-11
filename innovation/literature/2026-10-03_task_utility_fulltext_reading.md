# 任务效用查新：两个新正文与冻结评估器边界

本批固定Europe PMC查询返回26条题名，包含重复及不相关条目；四条重点摘要实际查看，取得并核读两个新正文，新增PDF为0。Morshuis正文来自精确题名arXiv索引给出的2508.18975v2；Wu正文为匹配DOI且有body的JATS。阅读范围为前者提取块8–125（118块，含标题、表格逐行及图注文字），后者段9–23及39–44（21段）。合计139个相关提取块，不将564个HTML提取块全部声称读完。未读补充、未视觉核图、未复现训练。

| 原文与范围 | 方法及证据 | 对本项目创新的约束 |
| --- | --- | --- |
| Morshuis、Hein、Baumgartner，*Understanding Benefits and Pitfalls of Current Methods for the Segmentation of Undersampled MRI Data*，[公开预印本2508.18975v2](https://arxiv.org/html/2508.18975v2)；Europe PMC记录DOI 10.1109/TBME.2026.3679957 | 七方法统一benchmark；K2S 300 scans排除1个标签错位，240/30/29划分；SKM-TEA155 samples，86/36/33 train/val/test。前者8–128×，后者8/16×。统一nnU-Net类结构、Dice+CE、训练预算/增强；部分原方法架构及loss被统一修改。CS-Rec与Unr-Rec分割较好，UNet-Rec重建分数较好；TwoDec16×在validation调λseg=10仍未占优 | “重建指标不代表任务质量”“联合任务不一定优于强简单基线”“任务权重折中”“完整评价benchmark”已有直接先例。不是通过换脑MRI或缺层算子就能建立独立贡献 |
| Wu等，*A critical assessment of artificial intelligence in magnetic resonance imaging of cancer*，DOI [10.1038/s44303-025-00076-0](https://doi.org/10.1038/s44303-025-00076-0)，PMC11981920；重建/分割及Discussion正文 | 已讨论采集与先验分离、protocol shift、生成先验、图像与诊断关联、分割测量误差传播、局部任务验证；Fig1图注给出FastMRI原案例中假血管，本批只读文字，未读原FastMRI新全文或看图 | 这是综述，不是本项目新实验。不能把hallucination/domain shift/UQ/局部验证的一般问题写成新发现，也不能用它替代某种病灶损伤因果证据 |

Morshuis Fig4文字给出若干方法的Spearman rho约0至−.20且p>.2；这支持该实验未检出正关联，不证明总体相关系数严格为0。其data-consistency解释是方法对照所支持的推测，不是仅改变该因素的因果消融。Unr-Rec只在SKM-TEA执行，K2S需要全3D Fourier路径，作者以计算约束排除它；不能写成七方法每格都齐全。K2S现在private也是其局限，不为我们的独立确认来源。

最重要的合同差异：本benchmark在每种方法/倍率的输入上训练相应分割网络，研究“最优适配任务pipeline”；我们的固定45CISS研究使用同一作者冻结分割器、同一观测层、完整缺层与两套病灶参考，研究“当前冻结pipeline的迁移行为”。即使本项目出现图像改善且Dice恶化，也不能单独判定真实解剖损伤：评估器对输入分布改变的响应仍是备择解释。若整体Dice改善，则必须保留并停止原负向主张，不能换模型或子组救结论。

所有方法保留真实anchors，不等于k-space一致性论文中的同一信息合同；观测层一致性本身也不能认证不可观测缺层正确。可保留的窄候选仍是可观测信息能否预测并限制局部有害修正、同时保留完整缺层收益，但SafeRestore、task guidance和误差/风险头先例保持，旧线性等价、岭失败、native/QDA定位失败均保持。

重复处理：Giannakopoulos *Pixel-Wise Uncertainty Quantification* 的DOI10.1002/mrm.70526对应此前已读arXiv2601.13236v3。本次只增加正式元数据线索，不重新计正文。15新生儿DLR仅摘要，研究自己明确未测诊断准确率，不作为任务效用确认。Kuestner原正文仍未取得，未重试被拒路径。

获取失败保留：GitHub默认分支README.md一次404；HTML提取首程序因环境无bs4失败且未访问网络，已备份脚本与错误记录，后改用既有stdlib HTMLParser，未安装包或修改环境。部分合并输出截断后，相关方法/结果段分块重读；阅读139块的范围以[provenance](source_cache/task_utility_fulltexts_2026-10-03/reading_provenance.json)为准。原始索引与访问响应、hash见[source_cache](source_cache/task_utility_fulltexts_2026-10-03/)及[查询记录](source_cache/task_utility_search_2026-10-03/attempt_01.json)。
