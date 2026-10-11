# Tanno公开全文补全：不同来源的一次检索

前阶段出版社TDM只有metadata、arXiv联合题名查询未返回Tanno、EuropePMC503与OpenAlex429，均保留。现在只尝试NCBI PMC的精确DOI索引一次（10.1016/j.neuroimage.2020.117366），若唯一命中再取一次公开efetch JATS XML。不是重复重试旧失败服务。仅公共HTTPS GET、TLS校验、不带凭据、不安装、不下载作者模型。每请求timeout30秒，重定向至多3次且仍须HTTPS；索引20kB、全文450kB，超过即记录失败，不保存截断文充当全文。

严格核正文article-title、DOI及第一作者；没有body或完整XML时只计metadata。获取成功也不自动算阅读，须实际分批核主文、公式、结果和限制，并另登记阅读范围。附录/supplement只有实际取得和读过才计入。与本项目相关的问题是uncertainty在高风险增强中的用途及其是否等于paired任务动作收益；不以图像重建不确定性替代病灶漏检指标。

全部写本stage，仍<=1.2MB，扣原强度/医学/开发预算并留8GB。失败不循环网络重试，不改变live协议或开启确认患者。
