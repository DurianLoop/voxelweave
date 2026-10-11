# GIN作者公开v5正文取得及提取

arXiv精确题名API唯一返回2111.12525v5，七作者顺序与已核TMI DOI一致，v5 updated2023-04-21；仅访问该固定版本HTML，不冒充期刊final。同DOI OpenAlex429保留，不重试绕限流。正文请求https://arxiv.org/html/2111.12525v5，限原HTML1.2MB/新压缩source与提取总500KB，计既有family7MB metadata额度；原全family104156359bytes和其他42.8MB不减。

只取得公共HTML、可用原MathML和表格文本，不下载图像/代码/外部supplement。提取段/表/公式不计已读；实际工具范围核读后单独冻结provenance。本版本若HTML不可用，保留失败并另准备PDF路线，不补造正文。RAM/disk8GB、CPU1/below-normal、wall180s，未发患者信息，不运行作者代码。
