# 病灶级集成原文的新公开 HTML 入口

仅请求 https://pmc.ncbi.nlm.nih.gov/articles/PMC13148016/ 一次，沿用标准TLS证书验证，最多3次HTTPS跳转、timeout30秒、正文≤500000 bytes。不重试之前BioC返回的无结果页面；其HTTP200不是论文全文取得成功。

保存原始HTML和响应头，以DOI 10.1007/978-3-032-16365-3_41和题名 Adaptable Segmentation Pipeline for Diverse Brain Tumors with Radiomic-guided Subtyping and Lesion-Wise Model Ensemble核身份。标准库DOM分段提取；提取时阅读完成数量保持0。后续实际逐段阅读记录覆盖范围、版本、正文限制、表格与项目差异。若访问失败保留失败，不把摘要或VINN引文代作原文。

CPU1/低优先级、stage5MB、8GB磁盘及RAM储备，零依赖安装、零模型/影像/GT读取、零外部写入、零其他PID干预。
