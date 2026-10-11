# 本轮正文选择与阅读范围

五项索引返回18条题名记录；两条相同题名的MR设备专利不算两篇论文阅读。索引全文未计阅读。只选择下列三个此前未在本项目阅读笔记登记的合法公开正文，先验证DOI和body，再实际核读相关方法与结果。若公开XML不给body，保存失败，不把摘要当正文。

| key | 题名 | DOI | 公开PMC身份 | 选择理由 |
| --- | --- | --- | --- | --- |
| lazy_resampling | Lazy Resampling: Fast and information preserving preprocessing for deep learning | 10.1016/j.cmpb.2024.108422 | PMC11873007 | 合并变换减少重采样已有直接方法/任务先例，必须列为强对照 |
| epilepsy_morphometry | Machine learning-based reconstruction of 2D MRI for quantitative morphometry in epilepsy | 10.1162/imag.a.997 | PMC12603658 | 真实配对2D/3D采集、插值/合成与下游量化的独立实证 |
| vocal_tract | Super-Resolved Dynamic 3D Reconstruction of the Vocal Tract during Natural Speech | 10.3390/jimaging9100233 | PMC10607793 | 层间一致性与清晰度的具体取舍；动态异时采集与本项目不可混同 |

没有新增PDF要求；先取JATS与逐块抽取文本。公式、表格、图注只展平读取，视觉图像和supplement不在当前已完成范围；作者数字未由本项目复现。候选新意需要比“减少插值损失”“保持层间一致性”“任务与图像指标可能分离”更窄。
