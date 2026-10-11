# 已结束阶段交接，科研goal保持active

此文件更新更早live状态文档；不要重复poll已结束session或重训同一attempt。

- 原39996更新完整训练已结束，V3主评价结束但医学失败，旧strict22/56数值失败保留。
- V4 session70619真正exit0，全部56完整生产/functional FOV严格通过，最大概率误差5.960464477539063e-8、旧二值/医学结果变化0。实际退出和result绑定已保存。
- 配对pilot session80513真正exit0，共396CPU更新，用时758.79345秒。四个99-step branch cp/全部journal/99配对step核查真正0196e0=0。结果SHA b563eb2221614e7bc7d241115c32f85a1d73f7572cbf50320e8df92b204de759。
- 四分支评价session80828真正exit0，chunk3bfe08，全部36生产+36独立functional FOV/严格坐标与概率/无损reader/独立计数与患者聚合完成，用时1096.35309秒。capture890220=0、summary9c38e8=0；结果SHA c7706e40f683a117977901294cfc9f2e02048815b79787068ea10a8b9bc05d69。

四已见验证患者/9series full Dice（parent/basic/strong）：native .506632/.432088/.507813；raw .445159/.523190/.526725。四新分支均未通过全部六门槛，strong native2/6、raw3/6。rawstrong与rawbasicDice差仅.00353514，recall提升.0665364，但absRVE .487844较basic .451181差；native strongabsRVE .601841亦差于父.474591。不能用“strong优于basic”掩盖control/parent差异或宣称充分适配/SR保持/正净收益。

4篇原文文字范围不同的论文核读已登记，BigAug NCBI429/EuropePMC500未取得正文不计阅读，MC-RC复读不再计数。来源、对话、handoff、实际工具和失败均存本目录。原33个turn16 store已恢复；未知历史逐字对话不能编造。

重要范围纠正：MC-RC全队列是异质T2而非统一CISS。字面FIESTA开发12/19（9患者）、验证1/9（1患者）；SPC/SPACE开发3/19（2患者）、验证6/9（4患者）。患者可跨名称，物理序列类型未由字面名称临床确认。这是事后coverage诊断，不证明失败因果；后续要补强协议/强训练控制。全患者分母和六门槛不降。

无损日志：普通gzip预测四臂完整预算日志28.88MB，存储不足。共有日志V1因CRLF真实失败；V2实际da6af2=0，526001bytes→52354bytes，gzip/zlib各恢复四日志原始bytes完全相同，8次/792行。完整19998step四臂日志预测10.58MB，weights-only无optimizer恢复峰值预测43.33MB，按当前约64MB储备外可容纳；是预测且未实现完整writer/失败恢复，未启动正式长训练。CPUstep时间预测135763.66秒（约37.7h），不含cache/IO/评价。下一步先完善可复核writer与完整训练recipe（包含空间增强/适配、必要的普通协议静态控制），依据实测冻结新预算；不能把短99步的loss或再延长同配方自动当充分适配。

用户GPU授权有效，pilot启动free1394MiB未通过8192MiB门槛，故CPU；当前无需再请求授权。未控制任何其他PID、未委派代理。8未见确认患者/12series和lockedIXI继续关闭，根environment.yml/.gitignore保持原SHA。论文主候选仍任务能力合格后的具体病灶动作净收益与完整费用，当前未得可发表claim，goal不是complete。

已成功第一delta archive V4：前5535 SHA保持，新300，累计5835；indexSHA2ab94767fb49fa881af05e8a6df0357846a4dcc620341f9870e47a183b3d4cc9，proofSHA61aa64f3ff5bcc18ee8c3d382983a979ecaa32b4b7e99096df4b592e23284f18。归档V1旧外部link、V2旧历史live snapshot、V3输出字面匹配失败均保留；V4核查旧原bytes而不把历史观察重新绑定当前滚动文件。

后附工具、协议覆盖诊断、图、无损日志准备和真正完成的36评价待final delta纳入；下一stage以最终POST_ARCHIVE_APPEND_PROOF.json为最新数量，不重复制旧大manifest。尚未收到任何自动审批拒绝，不需要权限确认。
