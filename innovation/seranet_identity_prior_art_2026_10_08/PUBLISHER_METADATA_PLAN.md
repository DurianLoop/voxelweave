# 官方章节访问失败后的公开元数据读取

2a557b真实exit1：SADFN PDF取得HTTP200/16页；Acar官方PDF链接以303重定向循环失败，错误原headers/body保留。两个record的成功状态分别记录，不能把总体失败称都未取得，也不能把chapter称全文已读。

chapter实际303响应Location为/chapter/10.1007/978-3-031-17247-2_6，并给匿名trackid cookie。下一步只读取这个官方公开章节URL，标准库使用内存匿名CookieJar以处理正常重定向；不使用认证、不登录、不访问收费全文、仍正常TLS、最多3HTTPS跳转/30s/3MB。若返回HTML，只按title/abstract/可见链接记录，不作全文。原cookie不复制或手动构造；新HTTP客户端正常接收服务器匿名cookie，不持久化。失败不自动重试。
