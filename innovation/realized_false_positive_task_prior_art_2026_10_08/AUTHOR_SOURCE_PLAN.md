# 原文实际给出的作者实现

MIRTO物理页21实际Code availability打印 https://github.com/soumickmj/MIRTO ，同作者Soumick Chatterjee。只读取该明确仓库的metadata、完整git tree、README，不clone、不安装、不执行作者代码、不取得医学MRI/GT/权重。

正常TLS匿名GET，单响应≤3MB、30秒、最多3HTTPS重定向、最多上述3次请求，错误保存不自动重试。repo metadata确认后从它的API URL取default_branch tree；README取实际tree blob URL，保存blob SHA和完整解码文字，再选择直接相关单文件。不得把tree列出/README提及算成源码已经阅读。
