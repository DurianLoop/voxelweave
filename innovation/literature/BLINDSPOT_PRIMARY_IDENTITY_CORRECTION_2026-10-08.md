# Noise2Same身份修正：保留错误ID，不计不相关论文阅读

初始`2010.12062`获取真实exit0，但首页是 *Post-CMOS Compatible Aluminum Scandium Nitride/2D Channel Ferroelectric Field-Effect-Transistor*，不是Noise2Same。原28页PDF、逐页提取和原receipt保留，只看第一页作身份排除；其获取页/文字不计新增相关原文阅读。Noise2Void的1811.10980v2（2019-04-05）题名/作者正确，9页。

OpenAlex公开查询Noise2Same收到HTTP429，工具4cd0eb实际exit1；原脚本保留，不重试同受限路线。这是服务器限流，不是自动审批拒绝。

转至NeurIPS2020官方公开索引，0a665e实际exit0，唯一匹配题名 *Noise2Same: Optimizing A Self-Supervised Bound for Image Denoising*；官方摘要[链接](https://proceedings.neurips.cc/paper_files/paper/2020/hash/ea6b2efbdd4255a9f1b3bbc6399b58f4-Abstract.html)，原HTML/响应SHA保留。仅选择其实际指向的`ea6b2efbdd4255a9f1b3bbc6399b58f4-Paper.pdf`，不读AuthorFeedback或Supplemental，也不猜另一个arXivID。另存正确来源子目录/获取源码/receipt，取得后再核首页作者题名和文字/视觉范围。

本修正不影响已经冻结的observed留出fold、预测或评分，不据任何任务效果修改方法。旧选择protocol不回改；错误ID、HTTP429和当前正式索引都进本轮账本/冻结清单。
