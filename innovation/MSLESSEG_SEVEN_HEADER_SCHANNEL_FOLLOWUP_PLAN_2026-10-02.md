# 首轮七个 TLS 失败头部：单次 Schannel 补查

执行前记录。首轮 117 个冻结 RAW T2 名单已有 110 个头部，7 个均是 Python TLS UNEXPECTED_EOF。没有因为扫描参数筛选文件；首轮失败原样保留，原脚本和禁止自动重试规则不改。

本次是单独有界的实现替代：对首轮 `attempt_01.json` 中所有七个失败成员，按原索引，使用系统 curl 8.16.0 / Schannel，执行一次 local-header、name/extra、8192 compressed bytes 前缀读取。无 --insecure，无自动 --retry；每请求 timeout 30s，最大接收 65536 bytes；精确 HTTP 206/Content-Range，否则记录失败。最多三线程，总请求预算 256 KiB。沿用已审本地 header_only / parse_header，仅解压 NIfTI 头，不解压体素。不会执行作者代码或安装库。

只有这些网络失败成员接受补查；原 110 个头不重取。每次网络请求保留 curl headers、原字节、退出码/stderr、SHA256；成功后按完整 117 名单合并资格，禁止覆盖首轮。后续独立核验脚本读取两份来源，并保持失败网络历史、完整 ZIP MD5/CRC 未认证的边界。
