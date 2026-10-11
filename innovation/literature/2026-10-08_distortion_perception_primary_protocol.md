# 两篇失真／感知原文补读范围

在本项目全部既有 literature Markdown 检索 `Perception.Distortion|Blau` 无命中之后，新增选择两篇已知作者原文：Blau/Michaeli, The Perception-Distortion Tradeoff, arXiv1711.06077；The Rate-Distortion-Perception Tradeoff, arXiv1901.07821。先取得公开作者 PDF，核首页身份；若 ID/题名不匹配则保留获取记录但排除阅读计数，不用猜测正文。

目的是明确失真、输出分布与信息码率各自的数学定义，核这些理论是否支持或限制本项目的维数诊断、MRI 输入对照与任务增益选择。它们不是预期直接的 MRI 分割先例，也不以非 MRI 结果为本项目效果。此次不是系统查新或首次性证明。

仅公开 GET，不联系作者、不绕过访问控制，30秒超时、单 PDF 上限8MB、本阶段合计20MB。逐物理页提取；只把实际返回文字/实际 view_image 图页记已读，references/appendix若未读明确列出。取得文件不记已读，未复现作者训练。新增文件仅 innovation；不读取医学/模型数组，不跑神经/GPU、不启动训练。
