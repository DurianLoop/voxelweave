# 本轮结果：动态路由收益与下游模型适配的证据边界

新增核读TADT与医疗重建下游评估论文，两篇共34完整文字页（20主文/7相关附录/7附带文字）、15实际视觉页；完成CPU公开表格复核。没有MRI神经forward、医学训练或新病灶收益；goal active、可发表claim未成立。

主要结论是后续对照必须匹配任务训练分布和总训练曝光。TADT LIIF×2的20.893% FLOPs下降是相对SwinIR，相对自己的无路由backbone为6.274%；不能都归因路由，也不能换成完整患者秒。医疗论文固定诊断模型只训原始图像，MRI分割只评60–130slice且先slice→patient平均；它不回答各表示充分适配之后的完整FOV缺层病灶余量。

- [实际原文核读、公式/数据范围和创新碰撞](PRIMARY_READING.md)。
- [CPU数值复核](table_audit_attempt01/receipt.json)及[原表转录](PAPER_TABLE_TRANSCRIPTION.json)：×2固定β=.5比TARC高.01dB；医疗Table6 printed row147与cells247相差100，已视觉确认、不猜修复。
- [后续充分适配/固定任务网/全FOV准备](TASK_DISTRIBUTION_AND_FOV_CONTROL_PREPARATION.md)。

来源与失败完整保留：47bafb=1是受限环境Schannel凭据错误；927c4f=1中medical PDF成功、TADT超10MB。核headers10,036,939bytes后另定10.05MB尝试，587000=1网络HTTP200/curl0/长度完整，但正文数学编码不合法。TADT actual SHA不等ETag，明确按本地身份/实际字节来源绑定，不声称ETag通过。ce125f=1严格UTF16失败；bf92f7=0改用PDFium提取同一PDF，原pypdf字符串逐页ASCII JSON完整保留；无再次下载、无符号删除或PDF重导出。数学与表格按实际PNG核验，573451渲染=0、358e08算术=0；无自动审批拒绝。

原训练99542最近f2fbcd仍live，raw_pchip3267、invocation02 new23067、累计53149.46526530001s；不重启/迁移/控制其他PID。GPU授权保持但未新用GPU。原两臂final/真实退出→56FOV/六gates/strict→三臂真实资源→另冻正式充分适配→真实动作/完整费用/强静态→8未见确认的順序保持。

本轮公开对话/goal全文和真实退出会与来源一并归档，累计从4546 SHA校验，纳入前轮post五文件。成功以本目录ARCHIVE_PROOF.json/POST_ARCHIVE_OBSERVATIONS.json的真实退出为准；不覆盖已冻结源码、协议或结果。
