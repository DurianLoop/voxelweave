# 固定样本拟合期间的原始文献检索合同

仅补充直接关系小病灶拟合、Dice优化及归一化/滑窗行为的先例，不中途修改正在运行的512更新实验，不读取任何确认患者。已有nnU-Net、Revisited、3D U-Net、DeepMedic、Unified Focal、SynthSeg/TumorSynth不重复计新增阅读。

检索入口为Europe PMC原始JSON，三条固定TITLE_ABS查询：

1. `TITLE_ABS:"label-marginal" AND TITLE_ABS:segmentation`
2. `TITLE_ABS:"region-size" AND TITLE_ABS:segmentation`
3. `TITLE_ABS:"Dice loss" AND TITLE_ABS:optimization`

每条最多10个metadata结果，总命中数与返回条数分别记录。检索只提供选文线索；题名/摘要、下载、文本提取、真正核读分开登记。不以未命中证明首创。优先取得最直接的原始公开全文，记录URL、日期、版本、原始响应及SHA256；不追绕付费权限或安装依赖。
