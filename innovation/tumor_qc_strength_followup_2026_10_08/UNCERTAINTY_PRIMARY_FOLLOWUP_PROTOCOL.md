# 追溯脑肿瘤 uncertainty 强对照的原始来源

QCResUNet arXiv2412.07156v2 Appendix B将50次softmax概率均值写成UMap，却引用Jungo2020。因此补核原始论文 Analyzing the Quality and Challenges of Uncertainty Estimations for Brain Tumor Segmentation，DOI10.3389/fnins.2020.00282：识别mean probability、predictive entropy、variance和mutual information的区别，检查阈值来源、患者分组、绝对质量预测和纠错动作收益的边界。无完整原文不计已读。

本地受限Markdown查重使用rg，排除 **/tools/**、**/literature/source_cache/**、**/experiments/** 后9cb70c没有命中；不称全球查新或穷尽旧缓存。先仅一次Europe PMC精确DOI GET，最多3结果；身份匹配后一次公开fullTextXML GET。沿用现有client每请求30秒、2MB、HTTPS/TLS验证、最多三跳、无自动retry。若不能取公开XML，保存失败，停止这一来源，不安装依赖或爬取更多端点。

CPU1/below-normal；磁盘/RAM各8GB储备；本stage累计<=5MB。所有新增仍在本目录。仅标准库解析XML；不读取MRI/GT/model数组，不初始化CUDA，不import或执行作者代码。四分支训练session29823继续，不改源，不把中间loss用于选择；新验证和8未见确认仍关闭。
