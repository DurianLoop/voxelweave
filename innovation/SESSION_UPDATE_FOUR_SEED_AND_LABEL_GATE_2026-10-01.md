# 本次续作：四种子论文近邻与临床标签门槛

用户要求在 GPU 被既有任务占用期间持续批量读论文、结合既有 MRI 工作找创新点，能验证的先探索，不能验证的记录准备，并将本轮内容存于 `D:\MRI\innovation`。本次没有占用 GPU、操作既有训练会话或读取锁定 IXI test 图像；未改用户已有 `.gitignore` 修改。

- 延续运行前冻结的 [OpenAlex 四种子方案](literature/2026-10-01_mira_four_seed_citation_audit_plan.md)和 [原始响应索引](literature/search_snapshots/mira_four_seed_citations_2026-10-01/index.json)：Hu 11、Kuestner 19、NPB-REC 0、Radmanesh 32 条，共 62 条/61 个不同 ID。新增 [逐篇结果](literature/2026-10-01_four_seed_forward_citation_result.md)。两篇 arXiv HTML 全文可核实验合同：固定 k-space 下的病灶检出与健康 T1 结构体积不确定性；另三项重点工作仅为摘要级，不能据此排除方法重合。PDF 下载中断与失败路线已留原始索引，没有残缺 PDF。
- [MSValid 官方 ZIP 中央目录](literature/msvalid_remote_inventory.json)经本地结构化筛查：排除 macOS 附属目录后 398 个 NIfTI、六个 `.DS_Store`；全部 NIfTI 是 T1/T2/FLAIR，未见标签成员。整理 [临床任务标注来源门槛](CLINICAL_TASK_LABEL_SOURCE_GATE_2026-10-01.md)，明确该 ZIP 内无可直接同目标配对标签，尚不能运行临床病灶指标；不把“文件名无标签”外推为所有可能标注不存在。
- [创新优先级](INNOVATION_DECISION_MEMO_2026-10-01.md)和 [发表门槛](CLAIM_PUBLICATION_GATE_2026-09-30.md)已同步：三来源 `Delta O` 仍是窄的回顾性发布层观测，已读临床论文提高任务后果的证据要求。下一项真正可能提升稿件的是官方同目标层标注及严格空间/来源映射，或独立原始重复采集；后者仍受已有来源门槛限制。不要再把无标注队列的同类阳性结果当作临床或机制证明。
- 公开来源英文五页 PDF 仍是 MSValid/ReMIND 两来源旧快照；这次不将文献筛查或 UPENN 数字冒充已同步的投稿稿。外发前还需 Kuestner 合法全文、目标场合查新、IXI 衍生权重义务、清洁环境复现与作者/投稿审查。

本次归档验证：`D:\conda\envs\MRI\python.exe -B innovation\verify_archive.py --write` 后只读复跑，**29 份 PDF、181 份来源/阅读证据、895 个本地链接、零错误**。四组 OpenAlex 引用响应及两篇 HTML 的文件 SHA-256 均与来源索引匹配；[哈希清单](literature/archive_manifest.json)和所有原始文件均在 `innovation/literature/`。
