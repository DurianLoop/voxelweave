# Continuous influence 扩展实验报告

在保留上一轮文件的独立目录内，新增测试五个已有实现；全表列出 13 模型、两个队列的 26 条记录。实际完成 7 模型、13 个模型/队列；数值 PASS 12 个，按新八模型家族区间同时满足稳定性与 beyond-count 支持 12 个。新增实现中满足两项要求 6/7 个模型/队列。

[完整大表](CONTINUOUS_INFLUENCE_BIG_TABLE.md) 和同名 CSV 包含所有失败、NA 和 legacy 区间。[修订主文](revised_manuscript/main.pdf) 与 [补充材料](revised_manuscript/supplement.pdf) 需结合 build_logs 的成功记录判断是否已完成重建；实际入口交付状态以 DELIVERY_STATUS.json 为准，未完成视觉检查不得声称投稿就绪。

主文使用新的八模型同时家族大表，补充材料列出全部三次稳定性检查、全幅度全端点和森林图。原三模型点估计没有变化；新旧多重比较区间分别保留。没有重训、增加数据集、改公式、选更有利阈值或删去负结果。

证据范围：Claims A/B 的原五核心相位矩阵不变；Claim C 的新增支持必须按模型/队列和稳定性界限读取；本轮没有新增协方差试验，Claim D 不扩大。Linear 是解析对照，ArSSR 为本地适配实现，不应将八个名称写成八次结构独立的神经验证。

限制：同一批检查被回顾性复用；置信区间不覆盖整个研究过程中的选择。数值 PASS 不等于通用 Jacobian 精确性，不保证校准可靠性、排名改进或临床效用。旧 SAINT 空结果、I3Net/CycleINR 历史 FAIL、126.4% 最坏近似误差和 guard 负结果均保留。真实数据/伦理/授权仍 NEEDS HUMAN CONFIRMATION。

工程记录：原始响应和其输入哈希在目标读取前记录；全部新响应以独立物理锚嵌入公式重算，bootstrap 与显式病例复制对照。详见 outputs/summary_*.json、SOURCE_MANIFEST.json、freeze.json、logs/ 和 PROTOCOL.md。
