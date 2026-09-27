# full前核验：2026-09-23

**通过，可运行repair seed3407；助手未启动full。**

| 检查 | 结果 |
|---|---|
| train/val DICOM头 | 135个旧series均有匹配文件，层数吻合；仅113452254821_ax_t2含2个UID，未读test |
| 原始像素 | 32个不同像素层逐层匹配DICOM，两个16层序列像素不同，不丢弃任一序列 |
| 修复体积 | 两个新NIfTI均逐像素等于旧volume对应层的重排，原文件SHA不变 |
| 真实层序 | UID内物理位置单调、间距约5mm；全部12个区间的三目标phase约.25/.5/.75 |
| 归一化 | 两个新序列全部四种训练网格逐项核对anchors/target，仅用观测层极值 |
| 数据范围 | 只替换一个train record，其余records逐字段不变；patient集合与train/val隔离保持 |
| 样本量 | train113series/111患者/1356区间；validation23患者69区间 |
| 初始化 | 原control与repair模型在修复样本上的输出逐位相同，992179参数 |
| 修复病例真实反传 | 两个新UID各一个z4样本，3次完整原loss更新有限：0.031352→0.030642→0.030212 |
| 显存 | 修复样本19.6199/20.2949 GiB allocated/reserved；trainer smoke约19.62/20.31 |
| trainer smoke | 最终源码运行`smoke_repair_final`成功；同seed重复结果一致 |
| 恢复 | 实际从last加载model/EMA/AdamW/scaler/RNG，最后smoke轮完成；未追加更新，best/last SHA不变 |
| 指标 | 独立加载最佳smoke复算八项指标，差值全部0 |
| 效率 | 原control同合同、同参数、同Conv/Linear部分FLOPs；延迟比1.003378、显存比1.0 |
| 正式入口 | PowerShell `-Preflight`实际通过，1356/69区间和源码/数据哈希符合，full目录不存在 |
| 统计 | full报告拒绝smoke；旧control完整性检查通过；配对使用validation哈希，明确记录不同training哈希 |

validation记录哈希：`e9a9f2fda64b371df5984b370ebe0942bf237df8ea6473c18c1c34b495919901`。旧训练manifest：`ee471bd92e48696050a694f371a86483f86f832c5b26571c81137b5dcc6ad4df`；修复manifest：`149d29f43d132484d0d9a18c87e54c2075f6950f841a1c15e3e6f4451213e3f9`。两个训练哈希不同是预登记的数据变量，未伪造一致性。

初次检查发现Windows相对路径分隔符的查表问题，已修正并重新完整核验。协议补充“UID不证明独立重复采集”的措辞后，重新生成最终源码下的检查、smoke、恢复和复算记录。最终证据以`checks.json`、`full_preflight.json`和`final_verification.json`当前哈希为准。

数据正确性与模型晋级分开判定；修复是有UID/位置/像素证据的操作，不依据validation分数。候选若没有+0.10dB及质量守卫，不继续训练挽救。历史G086预训练和I3Net基线用过旧训练集合的限制仍保留，当前不能宣称SOTA。
