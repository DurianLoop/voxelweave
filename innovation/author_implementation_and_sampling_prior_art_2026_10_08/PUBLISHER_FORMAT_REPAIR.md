# 根据实际400响应改用另一条已索引表示

f8917e 的Xu text/plain请求实际HTTP400，原响应全文为 INVALID_INPUT / View parameter specified in request is not valid，不能称付费拒绝、认证失败或论文不存在。保留失败；不改原请求源码/记录。

下一步只尝试Crossref同记录已提供的另一条 text/xml URL，正常匿名GET一次/30秒/3MB，无凭证，不推测或添加view/认证参数，不自动重试。收到XML也须区分摘要/metadata/full body，不能把API响应等同完整原文。若再失败，记录本范围内取得状态后继续其它研究。
