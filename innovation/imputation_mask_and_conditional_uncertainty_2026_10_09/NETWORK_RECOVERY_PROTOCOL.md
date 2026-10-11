# 本地代理拒绝后的既有公开客户端恢复

原fetch真实c44fea exit1，两公开HTTPS GET均ConnectionRefused10061，未下载原文/索引。原两请求receipt和原脚本不改，不能把失败算阅读。已检查项目此前实际使用的公开客户端：retrieve_stronger_adaptation_primary.py使用ProxyHandler({})及ssl.create_default_context，开启hostname/CERT_REQUIRED并限制HTTPS redirect。

新增attempt02沿用已证明的direct HTTPS传输路径，不改系统或环境代理；每请求30秒/2MB，最多两个新增GET（加原失败总4次）。原和新输出分目录，selection也另存，原DOM/DOI/题名/canonical识别和全文提取不变；改动用建设diff登记。网络或解析失败继续保存，不能以重试当成功。TLS仍验证，不安装、不触及其他PID，不改变医学/数值句柄。
