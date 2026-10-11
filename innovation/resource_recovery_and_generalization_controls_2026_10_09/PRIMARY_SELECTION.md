# 三篇主文选择（实际阅读前）

直连索引实际38968b通过三query；共有12/6/4命中，本次仅前三查询的各8/8/8上限，不称穷尽。选择三个直接回答当前泛化与创新边界的问题的公开原文：

1. Acquisition-invariant brain MRI segmentation with informative uncertainties，DOI 10.1016/j.media.2023.103058，PMC7617170：采集条件与不确定性已有近邻。
2. Adaptive multi-stage domain unlearning for white-matter lesion segmentation，DOI 10.3389/fmed.2026.1875760，PMC13474016：强nnU-Net与病灶跨扫描泛化。
3. Region-Wise Bézier Intensity Augmentation for Domain-Generalized Brain Tumor Segmentation with a Mamba U-Net，DOI 10.3390/jcm15145508，PMC13413108：保持病灶几何、改变相对组织对比度的普通增强近邻。

定向Markdown去重实际aa5847没有找到上述三DOI/题名的既有记录；不将此有限去重称整个历史文本穷尽。此前SynthSeg+命中已有全文记录，不重复计新论文。

从Europe PMC fullTextXML每篇取一次、TLS验证、直连、timeout25秒，每响应<=300kB，三响应总<=800kB；stage2MB并预留250kB归档，墙钟120秒、CPU1/低优先级。先核精确DOI/PMC/题名，再保存body/abstract块、table rows与公式原XML，下载/提取不计阅读。未取独立supplement、图像或作者代码，未执行作者模型。
