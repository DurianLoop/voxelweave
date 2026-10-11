# 三篇正文选择与公共替代路径

精确题名/DOI补查后，正文优先对象固定为：

- Ramani等2012，Regularization parameter selection for nonlinear iterative image restoration and MRI reconstruction using GCV and SURE-based methods，DOI10.1109/TIP.2012.2195015，PMC3411925。直接核投影风险与完整风险、无真值参数选择的早期先例。
- Aggarwal/Jacob等2021，ENSURE，DOI10.1109/ICASSP39728.2021.9414513，PMC8323317。OpenAlex的精确DOI记录公开指向该PMCID和arXiv2010.10631v1；不是猜测PMCID。
- Rep2Rep2026，DOI10.1002/mrm.70155，PMC13093144。直接核MRI重复观测、自监督及局部噪声假设；此前本项目曾缺独立重复T2来源，不能把不同噪声重复直接等同于缺层参考。

2012和2026的Europe PMC fullTextXML两请求均HTTP500，原150/151字节失败响应留存。现在改走公开NCBI EFetch xml，每文一次，不登录、不反复轮询原失败服务。新选择不包括其他摘要记录；eSURE精确题名未在Crossref首三结果中命中，不能计为读过其原论文。

阅读仅用于方法假设排重；若本文JATS不含完整显示公式或图像，只报告可读文字，不声称逐式/逐图视觉核查。全文缺失继续记录，不把取得响应等同于完成阅读。
