# 公开录用稿抓取 v2

继承PROTOCOL.md所有大小、剩余budget、CPU/RAM/disk、来源版本与阅读计数要求。v1实际3a2485 exit1，公开citation_pdf_url的UI download路由返回HTTP405，没有取得PDF。完整保留其代码与失败receipt。

公开landing的SSR缓存和REST链接明确含同一个bitstream的 /server/api/core/bitstreams/9f1f03f2-fac1-4402-8045-9f9455fdac2d/content；v2验证这个完整URL字面量在实际public HTML里，再按普通匿名GET读取。没有修改HTTP方法、cookies、认证、凭据或绕过资源授权。若正式content接口拒绝则记录并停止该来源，不猜其他私有路径。只读同一个公开仓储文件，非publisher staging。
