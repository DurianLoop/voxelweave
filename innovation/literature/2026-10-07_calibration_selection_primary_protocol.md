# 风险校准、选择性预测与修正收益：原文选读协议

在原19series训练尚未结束、未读取中间MRI效益时预选三篇一般方法文献，目录内精确关键词检索未找到三篇本身的阅读记录。此前已读MRI/endoscopic conformal应用、learning-to-defer和一般有限动作成本先例，因此本轮不是宣称发现新方法，而是核查后续病灶实验如何避免把校准/拒绝误写为修正收益。

1. Guo等，On Calibration of Modern Neural Networks，ICML2017/PMLR70；首选官方PMLR页面与PDF，核calibration定义、temperature scaling及accuracy变化。
2. Geifman/El-Yaniv，SelectiveNet: A Deep Neural Network with an Integrated Reject Option，ICML2019/PMLR97；核selective risk、coverage、训练选择头及任务范围。
3. Angelopoulos/Bates/Fisch/Lei/Zrnic，Conformal Risk Control，arXiv2208.02814；首先核arXiv题名/作者/实际version，核monotone bounded loss、exchangeability、finite-n修正和应用。没有原文支持时不声称患者级安全保证。

公开GET，最多2并发，每请求30秒、PDF<=32MB、每篇物理页<=60，总<=150；预算不通过保留失败并另选固定版本，不放宽上限。输出仅innovation/source_cache对应目录；既有环境工具pdfinfo/pdftotext/pdftoppm，不安装包。提取不是阅读；记录实际完整选读页，关键公式/结果页render/view，下载和阅读provenance分开。

接续问题：后续策略是否只属已知校准、selective prediction或cost-sensitive routing？4已见validation患者不足以当独立校准集；19series不等于19独立患者；8保留确认不得反复调阈值。每例Dice风险与修正联合动作不一定随阈值单调，不能把CRC的嵌套预测集合结论直接套到修正收益。

本轮可验证的CPU方向：用明确有限合成分布检查，即使baseline conditional error已精确校准，最高风险组也可能有负修正收益；同容量两路径风险比较是必要已知基线。另算CRC B=1的finite-n修正下限，与真实项目split数量并列；只作算术/假设检查，不当MRI结果或新理论。

