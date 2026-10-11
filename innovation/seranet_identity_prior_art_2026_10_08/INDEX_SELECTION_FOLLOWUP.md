# 实际索引所得身份与后续定位

65cf88真实exit0，标准库证书验证客户端取得三组响应。SERANet Crossref题名查询真实0；Segmentation-aware MRI reconstruction的模糊题名查询总848123，实际只返回8，不能宣称覆盖总数。8个题名/作者/DOI均已读，只有Motion Aware Deep Learning Accelerated MRI Reconstruction有摘要，其余没有。arXiv措辞查询总2，两个完整题名摘要均已读。因此实际筛10条题名、3条可用摘要，不称10条摘要。

重点实际身份：
- Acar/Çukur/Öksüz，Segmentation-Aware MRI Reconstruction，2022，DOI10.1007/978-3-031-17247-2_6。Crossref给官方PDF链接；尚未取正文，不能断言其中网络就是SERANet。
- Xu/Öksüz，Segmentation-aware MRI subsampling for efficient cardiac MRI reconstruction with reinforcement learning，2024-10，DOI10.1016/j.imavis.2024.105200。只题名/作者/DOI；选择采样会改变观测的信息量，与固定CISS观测动作不同，需全文核。
- Fan/Sun/Ding/Huang/Cai/Paisley，A Segmentation-aware Deep Fusion Network for Compressed Sensing MRI，1804.01210v1（2018），SADFN摘要使用segmentation特征指导重建，可限制“把语义放入重建”首创说法。

先另做两个arXiv公开GET定位Acar的题名/作者和Xu+Oksuz的MRI subsampling/segmentation preprint，不猜ID，max8/30s/3MB/最多3HTTPS重定向、无重试/登录/TLS关闭；来源绑定本次真实索引。根据返回实际身份选择最多两篇原文；如果没有preprint，才考虑Crossref实际官方PDF链接，访问失败原样保留。已执行的query源码/receipt不改。

其余只题名/可得摘要：Bayesian uncertainty-aware reconstruction、distribution-aware continual segmentation、protocol audit、motion-aware acceleration、difficulty-aware lesion segmentation、misalignment MRI-to-CT、DenseMP few-shot segmentation。本轮不凭title/abstract证明患者结果或原文实现，不称整体查新完成。已有全创新Markdown未找到上述三个新来源身份；最终去重仍按实际取得并核读的来源记录，不用命名相似判断。
