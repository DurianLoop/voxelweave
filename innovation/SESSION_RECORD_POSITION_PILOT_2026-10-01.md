# 2026-10-01 对话与研究续作记录

用户本轮要求：“接着基于我的MRI项目读论文找创新点”；随后明确：“目前GPU正在被占用着，你批量地读论文和根据我之前的工作找创新点，能验证的先试着探索一下，不能验证的也做好记录和准备后续尝试，把这轮对话所有的内容放进D:\MRI\innovation里”。当前工作目录 `D:\MRI`，用户正在看 `.gitignore` 与 `environment.yml`。本记录保留本轮实质内容、结论和产物入口；既有长篇论文核读、原始响应和实验 CSV 仍以链接文件为准。

## 接续的已有工作

- [研究总索引](README.md)与[发表门槛](CLAIM_PUBLICATION_GATE_2026-09-30.md)保存旧 PAST/PAST-Net、MIRA 与外部来源工作的全景。IXI HAT/SwinIR 在 MSValid 84 人/479 目标的原 `Delta O=+24.1856` 点，在 TCIA ReMIND 62 人/248 目标为 `+26.3999` 点；均是指定模型对、发布层邻片切换的回顾性审计，不能称真实薄层恢复或临床安全。
- [线性伙伴负对照](PUBLIC_LINEAR_PARTNER_CONTROL_RESULT_2026-10-01.md)在两来源仍分别 `+20.5445/+22.9386` 点，反驳深度跨架构配对特有性；[目标错误排序](TWO_SOURCE_TARGET_ERROR_RANKING_RESULT_2026-10-01.md)在 ReMIND 的改善区间跨零，阻止可部署评分主张。
- [fastMRI 清单关联筛查](FASTMRI_MANIFEST_LINKED_PAIR_RESULT_2026-10-01.md)完成 61 病例、2,944 个非像素头的来源门槛扩展：64 对候选仅四对技术匹配，零对有充分独立采集时间证据。本轮没有读取这些目标像素，也没有将它们加入公开来源稿。
- [TCIA/DataCite 正式引文](literature/remind_official_citation_audit_2026-10-01.md)已经补齐；[公开来源科学内稿](PUBLIC_ONLY_MIRA_MANUSCRIPT_DRAFT_2026-10-01.md)及五页 PDF 已同步。PDF SHA-256 `DEC287340D40262C39BE2B7C2E64F6F908CCE6B72B8D72DF7AF125B92D6B61DA`。稿件仍待 IXI 衍生权重再分发、环境/代码、作者和目标场合审查。

## 本次执行与发现

1. 重跑 [归档校验器](verify_archive.py)的 `--write` 和只读复核：27 份 PDF、128 个原文提取/搜索证据文件、630 个相对链接，无错误。论文来源与 SHA-256 在[清单](literature/archive_manifest.json)；新增 Lee/Choi 2026、Bhutto 等 2023 的[全文核读](literature/2026-10-01_shared_context_neighbours_fulltext.md)及有界 arXiv 检索已存档。
2. 对 Guo 等 2026 的 MRI 正文 §5.2 与先前 Ribas/Tous 核读补做定向复核，形成[本轮排重和创新路线决策](RESEARCH_DECISION_AFTER_POSITION_PILOT_2026-10-01.md)。核心差异是同目标、固定参考、发布层邻片切换下的成对错误审计；“第一次 MRI 黑盒审计/响应式错误评分”、单纯 PSF/flow/门控均不成立。
3. 在推理前写定[位置通道方案](POSITION_CHANNEL_ONLY_PILOT_PLAN_2026-10-01.md)，随后运行[CPU 两线程脚本](experiments/position_channel_only_pilot.py)。只改 SwinIR 第四通道相对位置图，固定另三通道和输出粗图。MSValid 前三名及 ReMIND 前三名合格患者共 6 人、35 个目标全部完成，无失败；结果和解释见[报告](POSITION_CHANNEL_ONLY_PILOT_RESULT_2026-10-01.md)。`Delta O_map` 分别 +3.9182/+3.0666 个百分点，完整邻片切换同子集为 +25.5017/+23.9789 点；只换图的伴随 MAE 增加，不是因果份额分解。
4. [只读复核器](experiments/verify_position_channel_only_pilot.py)对固定患者/目标、原冻结指标、差值、比例与 residue 等权汇总返回 `PASS`。原实验文件未覆盖，GPU/CUDA 与锁定测试集未使用。工作树原有 `.gitignore` 修改未改动。

## 留给下一轮的工作

- 公开来源稿最接近可审主张，但权重分发、环境锁定、目标场合与真实作者确认未闭环；[发表门槛](CLAIM_PUBLICATION_GATE_2026-09-30.md)仍不能标为通过。当前位置消融是结果后六人的模型输入敏感性小试，不写入主稿独立确认表。
- 若要扩展位置消融，应先单独冻结 84/62 人全量脚本、失败和双分母指标；预计只是增强敏感性描述，无法隔离发布层邻片内容或原始采集身份。
- 独立原始采集身份方向等待来源授权、导出/采集时间和序列记录；在此之前停止本地 fastMRI 像素试验。未知 profile 方向等待可信薄层参考和训练内已知核的因素设计，需与 ESPRESO、固定核及后卷积基线比较。收益门控方向因旧动作对 oracle 空间与外部预测负结果而暂停。

本轮未启动新 GPU 训练、未运行 727 目标的位置消融全量，也未宣称已完成系统文献综述。当前完成的动作和未验证条件均保留在 `D:\MRI\innovation` 内，便于继续而不把假设误写成结果。
