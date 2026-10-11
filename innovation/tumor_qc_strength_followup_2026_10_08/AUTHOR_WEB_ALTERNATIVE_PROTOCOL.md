# API限流后的单次公开网页替代

2efe53真实exit1：公开repo API取得200，但commit API返回403 rate limit exceeded；没有固定commit，作者代码读取0。原失败保留，不重试API、不添加身份认证或关闭TLS。

仅另GET论文已公开链接 https://github.com/sotiraslab/QCResUNet 的常规HTML，30秒/2MB/三HTTPS跳转。若页面的embedded repo identity/refInfo/currentOid可核实，用其固定commit；否则保存未决，不推断branch README等于论文实现。仍不clone、不安装、不执行代码，不加载医学/model数组。后续最多六个raw文本文件和5MB全目录预算保持，树路径仅从公开页面选择。
