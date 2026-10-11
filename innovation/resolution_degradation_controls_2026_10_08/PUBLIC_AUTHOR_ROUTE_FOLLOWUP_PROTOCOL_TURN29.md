# 等待完整医学任务期间的有限作者稿渠道核查

上一turn实质进展：完成独立强度40合成字段和5984参数metadata，开始完整真实35,904字段；本turn接入已真实poll74234/b9aacc和29823/6ddf1e，二者仍live，不重启/迁移，不枚举其他PID。当前检查不改变正在运行脚本、其冻结source和六医学门槛。

本次只核已知三篇直接相关论文的**不同公开渠道**OpenAlex exact DOI：Jiang 10.1016/j.jneumeth.2026.110834、Gou 10.1109/tmi.2026.3662706、Hsu 10.1016/j.compmedimag.2026.102786。旧EuropePMC已明确各无PMCID且subscription；不重试旧订阅/403路由、不绕访问控制、不联系作者。不作宽泛题名扫描或无穷查新。

每篇最多一次公开GET，无token，无用户影像/GT/项目特征外发；保留响应原字节gzip及SHA、日期、官方题名/DOI、公开可用位置与response status。OpenAlex仅作为发现公开作者稿的索引，不升级为原文或临床证据。取得正文后须另协议和实际完整核读，才记新增maintext；未取得则正文数量0，保留失败。

CPU1/本进程低优先级、墙钟180秒、每HTTP timeout30秒、单响应max500000bytes，三个gzip合计max80000bytes；本次输出总100000bytes预算。保存仅本目录public_author_routes_attempt01及必要后附文件。整个stage仍5MB，预留正在运行full journal余量到1.5MB、后审计150KB、后附100KB，磁盘/RAM8,000,000,000bytes不变。网络使用之前已确认不可用的环境代理以外的直接公开GET，仅本requests Session trust_env=False，不修改系统代理/TLS/访问权限，不安装依赖。

研究问题是原Jiang全文是否有充分3D任务网、真实层间降质定义、强插值基线与严格患者隔离/全费用；Gou/Hsu的伪健康counterfactual目标不能混成恢复原病灶。此前完整已读defer及SafeRestore证据说明有限动作相对收益选择本身已知；如无额外MRI机制及稳定净病灶收益，应定位为应用/评估研究或保留负结果，不申报“第一次预测收益”。8未见确认及lockedIXI保持关闭。
