# 保留归档V1失败，另立V2

2a41ab实际exit1。V1已完整核5460旧证据SHA并生成EXECUTION_LEDGER.json；随后扫描旧delta嵌套binding时，binding自身含document字段，与外层dict(document=...,**binding)冲突。没有生成APPEND_INDEX.json或APPEND_PROOF.json，不能称V1归档成功；原源码/ledger保留，不改科学读记、表格、CPU结果或旧证据。

新V2只改自己归档的binding上下文包装为binding_document+source_binding，并改三输出名EXECUTION_LEDGER_V2/APPEND_INDEX_V2/APPEND_PROOF_V2；两条字面替换各assert恰好一处。执行的是自己的归档代码，不是下载的作者源码。V1与V2均保存并纳入归档，后续以V2实际退出和proof为准。没有MRI/GT/权重加载、神经forward或环境修改。

新增公开消息：归档时遇到了重复字段错误，原5460份证据的哈希核验已通过，尚未生成新索引。我会在新版本中修复归档脚本，并保留这次失败记录。

V1RESULT提及APPEND_PROOF.json是当时计划输出名，保留；本修复与V2真实proof明确最新有效索引，不回改已绑定RESULT。没有自动审批拒绝，不需要用户确认此常规可逆修复。
